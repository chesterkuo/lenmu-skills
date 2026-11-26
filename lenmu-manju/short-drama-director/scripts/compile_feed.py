#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile_feed.py · P4 投餵提示詞自動裝配編譯器（AI 寫戲 · 腳本封裝）
設計動機：
  在 P4 階段讓大模型手工拼裝七段式，極易漏寫「Voice 聲線鎖」「年齡錨/三件套」「CHAR_STATE 偏離替換語」
  「末鏡末 1 秒定格收束句」或「M1 素材接線單」。
  本編譯器讀取 project_state.json，自動將結構化分鏡編譯為 100% 符合 C1~C30 與六道閘門的七段式投餵稿。
用法：
  python3 scripts/compile_feed.py --state project_state.json [--out feed.md]
  python3 scripts/compile_feed.py --self-test
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import sd_core


# ★P9 修（C33 缺口）：焦段是鏡行**頭**的元數據槽，不是鏡行正文的「相機說明書廢話」。
#   C20m 禁的是正文裡寫「焦平面死鎖面部無漂移 / 淺景深陰影側取景」這類理論廢話；
#   C33 要求每個鏡頭標註焦段。兩碼作用域不同（頭 vs 正文），此前編譯器把兩者混為一談，
#   導致所有產物每鏡必報 C33。本表照抄 `sd-storyboard-engine/references/short-drama-camera-system.md` §二。
_FOCAL_RULES = [
    # (匹配詞, 兜底焦段) —— 按景別從緊到松匹配，先中近景再中景，避免「中景」吃掉「中近景」
    ("大特寫", "100mm"), ("特寫", "85mm"), ("中近景", "85mm"),
    ("近景", "85mm"), ("中景", "50mm"), ("全景", "35mm"),
    ("遠景", "28mm"), ("大全景", "24mm"), ("空鏡", "35mm"),
]
_FOCAL_RE = re.compile(r"\d{1,3}\s*(?:-\s*\d{1,3})?\s*mm|1\s*:\s*1|魚眼|微距", re.I)


def _ensure_focal(spec, fallback="35mm"):
    """spec 缺焦段時按景別補齊，插入位置固定為「景別 · 焦段 · 角度 · 運鏡」——
    焦段是景別的直接屬性，插在末尾會讀成運鏡的修飾語。已有焦段則原樣返回（尊重作者判斷）。"""
    if not spec:
        spec = "中景 · 平視 · 固定"
    if _FOCAL_RE.search(spec):
        return spec
    fl = fallback
    for kw, f in _FOCAL_RULES:
        if kw in spec:
            fl = f
            break
    parts = [p.strip() for p in spec.split("·") if p.strip()]
    if parts:
        return " · ".join([parts[0], fl] + parts[1:])
    return f"中景 · {fl} · 平視 · 固定"


def _is_crowd_class_c(seg, seg_type=""):
    """C 類判定（crowd-behavior-direction.md §2.1）：密閉雙人 / 打戲 / 純特寫 / 聲明無人。
    C 類段必須顯式寫 `除 @XX 外無其他人物`，且機檢只查這一句（C40d），不查群像事務。"""
    blob = f"{seg_type} {seg.get('type','')} {seg.get('note','')} {seg.get('sfx_summary','')}"
    if re.search(r"打鬥|打戲|動作段|戰鬥|對決|格鬥|衝突動作", blob):
        return True
    if re.search(r"四下無人|空無一人|無人|密室|密閉|獨處", blob):
        return True
    shots = seg.get("shots", [])
    if shots and all(("特寫" in (s.get("spec") or "")) for s in shots):
        return True
    # 密閉雙人：僅兩名角色且無群像字段
    chars = re.findall(r"@([^\s（(；;、,]+)", " ".join(seg.get("standing", [])))
    if len(set(chars)) == 2 and not seg.get("crowd"):
        return True
    return False


def _orientation_word(aspect):
    """畫幅 → 朝向詞。★P11 新增（2026-10-24）。

    病根：舊版把「橫屏」寫死在【畫幅風格】模板裡 —— `f"【畫幅風格】{aspect} 橫屏，…"`。
    於是選 9:16（豎屏短劇的主用畫幅）編出來是 **「9:16 橫屏」**：一條自相矛盾的指令，
    而且它出現在**每段第一行**，是模型讀到的第一個畫幅信號。
    （實測：`--aspect` 並不存在，畫幅來自 `state["locks"]["aspect"]`，所以這個錯誤
     對每一個豎屏項目都成立，只是沒人把產物讀回來驗一遍。）
    """
    try:
        w, h = [float(x) for x in re.split(r"\s*[:：]\s*", str(aspect))[:2]]
    except Exception:
        return "橫屏"
    if h > w:
        return "豎屏"
    if w / h >= 2.2:
        return "寬銀幕"
    return "橫屏"


def compile_project_to_feed(state):
    locks = state.get("locks", {})
    mode = locks.get("asset_mode", "M1").upper()
    aspect = locks.get("aspect")
    model = locks.get("model")
    seam = str(locks.get("seam", ""))
    if model not in ("2.0", "2.5"):
        raise ValueError("編譯器僅支持顯式鎖定 model=2.0/2.5")
    if not aspect or not re.fullmatch(r"[1-9]\d*[:：][1-9]\d*", str(aspect)):
        raise ValueError("必須顯式鎖定有效 aspect，例如 16:9")
    if seam not in ("1", "2", "3", "4"):
        raise ValueError("必須顯式鎖定 seam=1/2/3/4，不代選 D 鎖")
    style_card = locks.get("style_card", "電影級寫實質感")
    wa = state.get("world_anchor", {})
    era = wa.get("era_anchor", "現代")
    receipt = state.get("receipt", {})
    plugins = receipt.get("active_plugins", ["sd-storyboard-engine", "sd-feed-engine"])
    read_refs = receipt.get("read_refs", ["model-adapters.md", "segment-splicing.md"])
    fps = receipt.get("fingerprints", ["【默認鏡頭策略】"])

    out_lines = [
        f"> 模型鎖：{model}；畫幅鎖：{aspect}；D 鎖：{seam}",
        f"> 素材形態：{mode}",
        f"> 激活外掛：{' + '.join(plugins)}",
        f"> 已讀子庫：{' / '.join(read_refs)}",
        f"> 本段調用外掛指紋：{'｜'.join(fps)}",
        "",
    ]

    # ★P9 修（CT2 缺口）：M1/M2 形態下資產由 P2 另冊交付，投餵稿只做接線。
    #   但 audit_contract.py 的 CT2-CHR/SCN/PRP 只認稿內寫了「資產另冊：…」才豁免，
    #   編譯器此前從不寫 → 它自己產的 M1 稿必然 CT2 三條 FAIL ——鏈在自己包的門口斷掉。
    #   這裡按素材形態自動補聲明；文件名可由 receipt.asset_book 指定。
    _asset_book = receipt.get("asset_book", "")
    if not _asset_book and mode in ("M1", "M2"):
        _asset_book = "P2-資產提示詞.md"
    if _asset_book:
        out_lines.insert(-1, f"> 資產另冊：{_asset_book}（角色四格/場景母版+五宮格/道具四格由 P2 另冊交付，本稿只做接線）")

    chars = state.get("characters", {})
    scenes = state.get("scenes", {})
    props = state.get("props", {})
    segments = state.get("segments", [])
    total_segs = max(len(segments), 1)
    used_figs = []

    for idx, seg in enumerate(segments, 1):
        sid = seg.get("seg_id", f"段{idx}")
        seg_type = seg.get("segment_type", "對話戲")
        scn_name = seg.get("scene", "")
        scn = scenes.get(scn_name, {})
        scn_fig = scn.get("fig_no")
        if mode != "M0" and scn_fig:
            used_figs.append((scn_fig, f"場景·{scn_name}", "鎖定空間幾何、建築材質與主光源方向", "不控制人物站位與動作"))
            scn_tag = f"@{scn_name}（參考圖{scn_fig}）"
        else:
            scn_tag = f"@{scn_name}（{scn.get('coords', '')}；{scn.get('set_states', {}).get('default', '')}；{scn.get('media_layer', '')}）"
        # ★時段光影基準（2026-10-15 · model-adapters §5.0.5b）：場景資產立唯一光影基準，鏡行只寫增量
        _lt = scn.get("lighting", "")
        if _lt:
            scn_tag += f"；時段光影：{_lt}"

        # 組裝【核心人物】（自動注入年齡錨 + 三件套 + Voice 聲線鎖 + CHAR_STATE 脫離替換語）
        cast_parts = []
        for cname, cinfo in chars.items():
            cfig = cinfo.get("fig_no")
            age = cinfo.get("age_anchor", "")
            body = cinfo.get("body_anchor", "")
            look = cinfo.get("look_3piece", "")
            vlock = cinfo.get("voice_lock", "")
            # 檢查本段是否有 CHAR_STATE 脫離聲明
            dev_clauses = []
            for _k, st_v in (cinfo.get("char_states") or {}).items():
                item = st_v.get("item", "")
                act = st_v.get("action", "")
                cons = st_v.get("consequence", "")
                if item:
                    dev_clauses.append(
                        f"⚠️資產狀態偏離聲明：本段{cname}{act}（{cons}），關於「{item}」的佩戴狀態以本段提示詞為準，覆蓋角色參考圖"
                    )
            dev_str = "；" + "；".join(dev_clauses) if dev_clauses else ""
            if mode != "M0" and cfig:
                used_figs.append((cfig, f"角色·{cname}", f"鎖定{cname}面部五官、頭身比與基礎服裝形制", "不控制本段動作姿態與已聲明偏離的配飾狀態"))
                cast_parts.append(
                    f"@{cname}（參考圖{cfig}，聲線鎖：{vlock}{dev_str}）"
                )
            else:
                cast_parts.append(
                    f"@{cname}：{age}，{body}，{look}（同一張臉跨鏡鎖定），聲線鎖：{vlock}{dev_str}"
                )

        # 組裝道具錨點（如有）
        for pname, pinfo in props.items():
            pfig = pinfo.get("fig_no")
            mdesc = pinfo.get("material_desc", "")
            if mode != "M0" and pfig:
                used_figs.append((pfig, f"道具·{pname}", f"鎖定{pname}外觀形制與材質", "不控制持握人物與運動軌跡"))
                scn_tag += f"；@PRP-{pname}（參考圖{pfig}）"
            else:
                scn_tag += f"；@PRP-{pname}（{mdesc}）"

        standing_str = "；".join(seg.get("standing", []))
        # ★P9 修（C40d 缺口）：C 類段必須顯式寫「除 @X 外無其他人物」——
        #   crowd-behavior-direction.md §2.1 原文：C 類（密閉雙人/打戲/純特寫/聲明無人）
        #   「必須寫」這句，且機檢對 C 類只查這一句聲明。此前編譯器從不寫，
        #   於是它自己產的每一段打戲稿都必然踩 C40d「群像開關沉默」。
        #   A/B 類反過來禁寫（同一事務派了人又說沒人 = 自相矛盾指令，模型二選一必崩一邊）。
        _c_decl = ""
        if _is_crowd_class_c(seg, seg_type):
            _names = [n for n in re.findall(r"@([^\s（(；;、,]+)", standing_str)]
            if _names:
                _c_decl = f"；{('、'.join('@' + n for n in _names))} 之外無其他人物"
            else:
                _c_decl = "；畫面內無其他人物"
        shots = seg.get("shots", [])
        shot_lines = []
        for s_i, sh in enumerate(shots):
            no = sh.get("no", s_i + 1)
            st_t = int(sh.get("start", 0))
            ed_t = int(sh.get("end", st_t + 4))
            t_str = f"{st_t // 60:02d}:{st_t % 60:02d}-{ed_t // 60:02d}:{ed_t % 60:02d}"
            spec = _ensure_focal(sh.get("spec", "中景 · 平視 · 固定"))
            act = sh.get("action", "").rstrip("。； ")
            # 遵循 C20m 鐵律：鏡行正文嚴禁默認塞入「85mm F1.4極淺景深陰影側取景（焦平面全程死鎖面部無漂移）/ 10-15釐米 / 極細微規律呼吸式微動」等攝影機說明書廢話，100% 留給人物與道具純物理動作
            opt_lock = sh.get("optics_and_camera_lock", "").strip("。； ")
            if opt_lock and opt_lock not in act:
                act += f"；{opt_lock}"
            # 末鏡自動注入「前置 0.5 秒收束窗 + 末 1 秒整秒硬定格」標準句
            if seam == "1" and s_i == len(shots) - 1 and "定格" not in act and "空鏡" not in act:
                settle_t = max(st_t, ed_t - 1.5)
                act += f"；第 {settle_t:g} 秒起運動收束，末 1 秒全體人物保持姿態與站位、動作完全靜止、畫面定格"
            snd = sh.get("sound", "環境音").rstrip("。 ")
            dlg = sh.get("dialogue", "無").rstrip("。 ")
            shot_lines.append(f"{t_str} [鏡頭{no}] {spec}。{act}。聲音：{snd}。台詞：{dlg}。")

        sfx_sum = seg.get("sfx_summary", "自然環境音，對白清晰置頂")
        # 遵循 C19 粉色大象效應鐵律：不在【強制禁止項】裡重複寫具體道具名詞（如「禁止同時出現兩個眼鏡」反會誘發雙眼鏡），全靠【核心人物】正向替換語鎖死
        ban_extra = ""

        # ★P11 修（2026-10-24 · 編譯器多段產物必被自家 C38 攔）：
        #   病根：P9 只用**單段** state 驗過編譯器，所以「段縫橋接」這件事從未被觸發過。
        #   一旦編譯 ≥2 段，`## 【投餵單元 2/N】` 與 ``` 之間什麼都沒有 → C38 報
        #   「段間缺橋接聲明」。編譯器自己的產物過不了自己包的門禁，與 P9 是同一類錯。
        #   修法：第 2 段起自動在段縫說明區寫橋接行（承接 + 聲音先入 + 情緒遞進），
        #   這三樣都在 C38 的橋接詞表內。橋接選擇是**默認值**，不是替用戶拍板——
        #   真要跳切，把這一行改成「硬切跳」即可（C38 同樣認）。
        _bridge = []
        if idx > 1:
            bridge = seg.get("bridge", "").strip()
            if not bridge:
                raise ValueError(f"段{idx}缺少 bridge：須由上游提供真實段縫方案，不自動推斷尾幀、換場或聲音")
            _bridge = [f"> 段縫橋接（段{idx - 1}→段{idx}，D鎖{seam}）：{bridge}"]
        out_lines.extend([
            f"## 【投餵單元 {idx}/{total_segs} · {sid}】",
            *_bridge,
            "```text",
            f"【畫幅風格】{aspect} {_orientation_word(aspect)}，{era}，{style_card}，{seg_type}（aspect_ratio={aspect}）",
            f"【場景資產】{scn_tag}",
            f"【核心人物】{'；'.join(cast_parts)}",
            f"【站位聲明】{standing_str}{_c_decl}" + (f" 機位側={seg.get('camera_side', '基準機位側')} | 固定可見錨={seg.get('fixed_anchor', '房間主牆與固定傢俱')}" if (total_segs >= 2 and "機位側=" not in standing_str and "固定可見錨=" not in standing_str) else ""),
            "【時間軸分鏡】",
            *shot_lines,
            f"【音效】{sfx_sum}",
            # ★P11 修（2026-10-24 · 寫法與權威口徑脫節）：
            #   舊句「禁止角色面部變形或肢體穿模」是 P6.2 已廢止的備用負面詞庫寫法，
            #   權威口徑（prompt-feeding-checklist.md §負向詞 + model-adapters §5）是
            #   **段7 只寫四項極簡句**：「畫面：禁字幕、禁水印（含 Logo）；音頻：禁背景音樂、禁旁白」。
            #   理由：長負面清單有害——被禁詞根即畫面詞，「禁止角色面部變形」等於把
            #   「面部變形」這個詞餵給模型（粉色大象）。編譯器卻在每一段都寫它。
            f"【強制禁止項】畫面：禁字幕、禁水印（含 Logo）；音頻：禁背景音樂、禁旁白{ban_extra}。",
            "```",
            "",
        ])

    # M1 模式下自動編譯《素材接線單》
    if mode == "M1" and used_figs:
        seen_f = set()
        uniq_figs = []
        for item in used_figs:
            if item[0] not in seen_f:
                seen_f.add(item[0])
                uniq_figs.append(item)
        uniq_figs.sort(key=lambda x: x[0])
        out_lines.extend([
            "## 素材接線單（M1 編號佔位必備 · 平台掛圖指南）",
            "",
            "| 圖號 | 對應資產 | 你該掛哪張 | 只控制什麼 | 不控制什麼 |",
            "|---|---|---|---|---|",
        ])
        for fno, aname, ctrl, no_ctrl in uniq_figs:
            out_lines.append(f"| 圖{fno} | {aname} | 掛載 P2 產出的「{aname}」設定圖 | {ctrl} | {no_ctrl} |")
        out_lines.append("")

    return "\n".join(out_lines)


def self_test():
    # ★P11 升級（2026-10-24 · P9 的漏網之魚就是「只用單段自測」）：
    #   P9 拿 default_project_state() 的**單段**樣例驗編譯器全綠，於是這兩個問題
    #   一直沒被測出來：① 多段產物段縫沒有橋接聲明 → 自家 C38 必報；
    #   ② 兩段各雙人 → C40c 把人數跨段累加（擺位 4 人）→ 自家 C40c 必報。
    #   自測的輸入形態必須覆蓋**真實生產形態**（3 分鐘劇 ≈14 段），否則綠燈不成立。
    st = sd_core.default_project_state()
    import copy as _copy
    _seg2 = _copy.deepcopy(st["segments"][0])
    _seg2["seg_id"] = "段2"
    _seg2["bridge"] = "承接上段末鏡；本例為同場示例，實際尾幀待生成後核驗。"
    _seg2["shots"][0]["spec"] = "全景 · 35mm · 略仰 · 緩拉"   # 與段1 末鏡同景別，排除 C18m 干擾
    st["segments"] = [st["segments"][0], _seg2]
    feed_md = compile_project_to_feed(st)

    # 0. 多段產物形態斷言（P11 新增：把「編譯器產物必須長什麼樣」寫死）
    assert feed_md.count("【畫幅風格】") == 2, \
        f"多段編譯產物段數不對：{feed_md.count('【畫幅風格】')} 段"
    assert "段縫橋接" in feed_md, "第 2 段未生成段縫橋接聲明（C38 必報）"
    _asp = st["locks"].get("aspect", "16:9")
    assert f"【畫幅風格】{_asp} {_orientation_word(_asp)}" in feed_md, \
        f"畫幅朝向詞與 aspect 不一致：{_asp} 應寫「{_orientation_word(_asp)}」"
    assert "禁止角色面部變形或肢體穿模" not in feed_md, \
        "【強制禁止項】仍是廢止的長負面清單（權威口徑是四項極簡句）"

    # 0b. 豎屏不得寫成橫屏（P11 修的 Bug，必須鎖死防復發）
    _st9 = _copy.deepcopy(st)
    _st9["locks"]["aspect"] = "9:16"
    _md9 = compile_project_to_feed(_st9)
    assert "9:16 豎屏" in _md9, "豎屏畫幅被寫成非豎屏（P11 Bug 復發）"
    assert "9:16 橫屏" not in _md9, "「9:16 橫屏」自相矛盾文案復發"

    # 1. 對賬校驗
    iss_s, wrn_s = sd_core.verify_feed_against_state(feed_md, st)
    assert not iss_s and not wrn_s, f"state verify failed: {iss_s} / {wrn_s}"
    # 2. 跑 validate_prompt.py 與 gate_check.py 實測
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(feed_md)
        tmp_path = f.name
    try:
        vp_script = os.path.join(SCRIPT_DIR, "validate_prompt.py")
        # 用 --model 2.5 直接調用 validate_prompt.py
        r1 = subprocess.run(
            [sys.executable, vp_script, tmp_path, "--model", "2.5"],
            capture_output=True,
            text=True,
        )
        assert r1.returncode == 0, f"validate_prompt failed on compiled feed: {r1.stdout}\n{r1.stderr}"
        # ★P9 修：舊斷言只看 returncode==0，而 C17f/C33/C40d 全是 WARN ——
        #   自測全綠，產物卻帶 5 條 WARN 出廠。編譯器承諾「編譯出 100% 合規的七段式」，
        #   那就必須斷言 WARN 也歸零，否則這句承諾是空話。
        _vp_warns = [ln for ln in r1.stdout.splitlines() if ln.startswith("[!] WARN:")]
        assert not _vp_warns, (
            "編譯產物帶 WARN，編譯器未履行「100% 合規」承諾：\n  "
            + "\n  ".join(_vp_warns[:10])
        )
        gc_script = os.path.join(os.path.dirname( os.path.dirname(SCRIPT_DIR) ), "sd-feed-engine", "scripts", "gate_check.py")
        r2 = subprocess.run(
            [sys.executable, gc_script, tmp_path, "--model", "2.5"],
            capture_output=True,
            text=True,
        )
        assert r2.returncode == 0, f"gate_check failed on compiled feed: {r2.stdout}\n{r2.stderr}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    print("[+] compile_feed self-test PASSED (0 FAIL across validate_prompt & gate_check)")
    return 0



def build_g7_mount_table(segments_meta):
    """V8.2.0-SLIM：為多段投餵稿自動生成《逐段參考圖掛載表》（G7-MOUNT）"""
    if not segments_meta:
        return ""
    lines = [
        "",
        "## 逐段參考圖掛載表（G7-MOUNT · 投餵平台逐段核對）",
        "",
        "| 段號 | 本段必掛參考圖 | 資產就緒態 |",
        "| --- | --- | --- |",
    ]
    for seg_id, figs in segments_meta:
        fig_str = " + ".join(figs) if figs else "（純文本/M0態）"
        lines.append(f"| 段{seg_id} | {fig_str} | ✅ 已就緒 |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="漫劇老李 V8.2.0-SLIM P4 投餵自動裝配編譯器")
    ap.add_argument("--state", help="project_state.json 路徑")
    ap.add_argument("--out", help="輸出投餵稿 .md 路徑（不指定則打印到標準輸出）")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if not args.state:
        ap.print_help()
        sys.exit(2)
    state = json.load(open(args.state, encoding="utf-8"))
    md = compile_project_to_feed(state)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] 已編譯生成投餵稿：{args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
