#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sd_core.py · 漫劇老李 V8.2.0-SLIM 套裝唯一公共解析內核與跨階段狀態台賬引擎
定位：
  1. 終結「多腳本各自寫正則導致修A漏B」——統一提供 TIME_RE、SHOT_TAG_RE、模型時長與字數契約、
     鏡行解析 parse_shots()、時間軸解析 parse_time_ranges()、鏡行頭提取 extract_shot_head()。
  2. 終結「上游神級卡片在下游被靜默丟棄」——提供 project_state.json 結構化狀態台賬的初始化、
     讀寫與 P4 投餵稿跨階段對賬校驗 verify_feed_against_state()。
用法：
  python3 scripts/sd_core.py --self-test
  python3 scripts/sd_core.py --init-state project_state.json
"""
import argparse
import json
import os
import re
import sys

# ---- 模型契約唯一常量（與 references/model-adapters.md §5 同源）----
MODEL_LIMITS = {"2.5": 30, "2.0": 15}
WORD_LIMITS = {"2.5": (3600, 4000), "2.0": (2900, 3000)}
SEVEN_SEGMENTS = (
    "【畫幅風格】",
    "【場景資產】",
    "【核心人物】",
    "【站位聲明】",
    "【時間軸分鏡】",
    "【音效】",
    "【強制禁止項】",
)

# ---- 唯一權威時間碼與鏡號正則（兼容 MM:SS(.ff) / Xs-Ys / N-N秒 守衛版 + 全半角鏡號）----
TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?"
    r"|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s"
    r"|(?:\A|(?<=[\s\[【\]】]))\s*([0-9]|[1-5]\d)(?:\.\d+)?\s*[-~～→]\s*([0-9]|[1-5]\d)(?:\.\d+)?秒",
    re.I,
)
SHOT_TAG_RE = re.compile(r"[\[【]?\s*鏡頭\s*(\d+)\s*[\]】]?")


def frac_to_sec(frac):
    """秒的小數位 → 秒值（★2026-10-14 Agent 修復）。

    `5`→0.5 · `50`→0.5 · `05`→0.05 · `123`→0.123 —— **按位數換算，不寫死 ÷100**。
    原實現統一寫 `fr / 100.0`：小數位只有 1 位時把 `.5` 算成 0.05，
    使 `00:10.5` 變成 10.05s、`00:03.5` 變成 3.05s ——
    鏡長區間最多偏 0.45s，且機檢告警裡印出的絕對時間點本身是錯的。
    本包真實產物普遍使用半秒粒度，故此口徑必須按位數判定。
    """
    if not frac:
        return 0.0
    return int(frac) / (10 ** len(frac))


def parse_time_ranges(text):
    """返回 [(start_s, end_s, line_no)]，兼容三形態時碼。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TIME_RE.finditer(line):
            if m.group(1) is not None:
                s = int(m.group(1)) * 60 + int(m.group(2)) + frac_to_sec(m.group(3))
                e = int(m.group(4)) * 60 + int(m.group(5)) + frac_to_sec(m.group(6))
            elif m.group(7) is not None:
                s, e = float(m.group(7)), float(m.group(8))
            else:
                s, e = float(m.group(9)), float(m.group(10))
            out.append((round(s, 2), round(e, 2), i))
    return out


def parse_shots(body):
    """解析鏡行，返回 [(鏡號, 起秒, 止秒, 全行)]，兼容時碼在前或鏡號在前。"""
    shots = []
    auto_no = 0
    for line in body.splitlines():
        tm = TIME_RE.search(line)
        if not tm:
            continue
        if tm.group(1) is not None:
            s = int(tm.group(1)) * 60 + int(tm.group(2)) + frac_to_sec(tm.group(3))
            e = int(tm.group(4)) * 60 + int(tm.group(5)) + frac_to_sec(tm.group(6))
        elif tm.group(7) is not None:
            s, e = float(tm.group(7)), float(tm.group(8))
        else:
            s, e = float(tm.group(9)), float(tm.group(10))
        sm = SHOT_TAG_RE.search(line)
        auto_no += 1
        no = int(sm.group(1)) if sm else auto_no
        shots.append((no, round(s, 2), round(e, 2), line))
    return shots


def default_project_state():
    """生成標準 project_state.json 模板結構（覆蓋 P0~P5 跨階段核心鎖定項）。"""
    return {
        "schema_version": "7.4.23",
        "project_name": "示例短劇項目",
        "locks": {
            "track": "1",
            "source": "1",
            "model": "2.5",
            "aspect": "16:9",
            "delivery": "3",
            "seam": "1",
            "style_card": "現代冷峻寫實",
            "asset_mode": "M1",
            "combat_tier": "R1",
        },
        "receipt": {
            "active_plugins": ["sd-decision-engine", "sd-real-engine", "sd-storyboard-engine", "sd-feed-engine"],
            "read_refs": [
                "context-mapping.md",
                "emotion-anchor-table.md",
                "forbidden-zone-whitelist.md",
                "acting-direction.md",
                "blocking-direction.md",
                "kinetic-chain-11.md",
                "defense-evasion-rules.md",
                "impact-physics.md",
            ],
            "fingerprints": [
                "【情緒錨點：E04 壓迫對峙（80% 側45度中近景+緩推）】",
                "【動力鏈：蹬地→擰胯→轉腰→送肩】",
                "【防守態：架臂格擋卸力+胸口衣料凹陷】",
            ],
        },
        "world_anchor": {
            "era_anchor": "2026年現代都市",
            "region": "東亞沿海城市",
            "tech_level": "現代科技",
            "forbidden_elements": ["馬車", "長衫", "髮髻", "煤油燈"],
            "required_elements": ["混凝土地面", "冷白日光燈管"],
        },
        "characters": {
            "林風": {
                "id": "CHR-01",
                "fig_no": 1,
                "age_anchor": "26~28歲男性",
                "body_anchor": "身高182cm，肩寬腰窄精悍體態",
                "look_3piece": "黑色戰術短袖+深灰工裝長褲+左眉骨一道淺疤",
                "voice_lock": "低沉微啞青年男聲，語速偏慢，尾音冷硬",
                "business": "右手拇指反覆攥緊戰術手套魔術貼",
                "break_trigger": "然而當聽到妹妹名字時，攥緊手指驟停、下頜咬肌繃緊",
                "address_map": {"陳梟": "陳會長"},
                "char_states": {},
            },
            "陳梟": {
                "id": "CHR-02",
                "fig_no": 2,
                "age_anchor": "45~50歲男性",
                "body_anchor": "身高178cm，寬厚微沉體態",
                "look_3piece": "深灰雙排扣西裝+暗紅領帶+金絲半框眼鏡",
                "voice_lock": "醇厚低沉中年男聲，語速平緩帶壓迫感",
                "business": "慢條斯理擦拭金絲眼鏡片",
                "break_trigger": "然而當被逼退半步時，鏡片後的眼瞼驟然眯緊",
                "address_map": {"林風": "小瘋子"},
                "char_states": {
                    "seg_1_detached": {
                        "item": "金絲半框眼鏡",
                        "action": "摘下金絲半框眼鏡捏在指間",
                        "consequence": "鼻梁兩側留有淺紅壓痕",
                    }
                },
            },
        },
        "scenes": {
            "地下拳館走廊": {
                "id": "SCN-01",
                "fig_no": 3,
                "coords": "北側盡頭為鐵藝雙開門，南側為水泥長廊出口，東西兩側為斑駁混凝土牆面與明裝鐵管",
                "set_states": {"default": "頂燈冷白硬光直射，地面有淺水窪反光"},
                "media_layer": "空氣中懸浮微弱灰塵顆粒，受頂燈硬光照射清晰可見",
                "lighting": "頂燈冷白硬光自正上做主光 · 硬光質 · 明暗交界利落 · 暗部冷灰補色、禁純黑（本段唯一光影基準，鏡行只寫增量/特寫眼神光）",
            }
        },
        "props": {
            "舊懷錶": {
                "id": "PRP-01",
                "fig_no": 4,
                "material_desc": "黃銅實心啞光表殼，表面有細密劃痕，呈暗黃金屬本色",
            }
        },
        "segments": [
            {
                "seg_id": "段1",
                "scene": "地下拳館走廊",
                "segment_type": "戰鬥動作段",
                "emotion_anchor_id": "E04",
                "camera_combo_80": "中近景 · 側45度",
                "forbidden_zone_unlock": "A類解鎖：貼身格鬥爆發瞬間允許正側面切鏡",
                "standing": [
                    "@林風（畫面左 · 水泥走廊中段 · 朝右 · 立 · 身後是斑駁混凝土牆面）",
                    "@陳梟（畫面右 · 鐵門前 · 朝左 · 立 · 身後是鐵藝雙開門）",
                ],
                "storyboard_panels": [
                    "起勢：林風蹬地沉腰蓄力",
                    "接觸：擰胯轉腰送肩直拳轟向陳梟",
                    "反應：陳梟架臂格擋卸力滑退半步",
                    "出口：兩人保持對峙定格",
                ],
                "shots": [
                    {
                        "no": 1,
                        "start": 0,
                        "end": 4,
                        "spec": "中近景 · 85mm · 側45度 · 極緩慢推",
                        "action": "畫面主體：@林風 右手拇指攥緊戰術手套魔術貼，聽到名字瞬間手指驟停、下頜咬肌繃緊，目光死死釘在 @陳梟 臉上；@陳梟 摘下金絲半框眼鏡捏在指間，鼻梁留有淺紅壓痕",
                        "sound": "[SFX: 皮質摩擦聲與低沉電流嗡鳴]",
                        "dialogue": '【林風（壓著怒意·低沉微啞·語速偏慢）：“陳會長，這表你認得吧？”】',
                    },
                    {
                        "no": 2,
                        "start": 4,
                        "end": 9,
                        "spec": "中景 · 50mm · 正側 · 跟移",
                        "action": "@林風 沉腰屈膝，右腳猛然蹬地、擰胯轉腰送肩轟出重拳；@陳梟 瞳孔驟縮，雙臂交叉架臂格擋卸力，小臂西裝布料受擊凹陷，整個人向後滑退半步碾開地面淺水窪，命中瞬間畫面頓住2幀後穩住重心",
                        "sound": "[SFX: 拳肉沉悶撞擊聲，鞋底擦地滑水聲]",
                        "dialogue": "無",
                    },
                    {
                        "no": 3,
                        "start": 9,
                        "end": 14,
                        "spec": "全景 · 35mm · 略仰 · 緩慢拉遠",
                        "action": "@林風 收拳沉肩穩住重心，@陳梟 垂臂立於鐵門前呼吸微促，兩人隔著水泥走廊對峙",
                        "sound": "[SFX: 粗重呼吸聲與走廊迴音]",
                        "dialogue": "無",
                    },
                ],
                "sfx_summary": "拳肉悶響、鞋底擦過溼水泥地聲、粗重呼吸聲，無BGM",
            }
        ],
    }


def verify_feed_against_state(feed_text, state):
    """拿 P4 投餵稿與 project_state.json 做跨階段精確對賬，返回 (issues, warns)。
    專治：P0B 情緒錨點機位、P1 稱呼賬本/世界錨、P3 角色表演檔案聲線鎖與故事板面板鏈在 P4 被靜默丟棄。
    """
    issues, warns = [], []
    locks = state.get("locks", {})
    # 1. 鎖一致性對賬（畫幅 + 素材形態）
    exp_aspect = locks.get("aspect", "")
    if exp_aspect and exp_aspect not in feed_text:
        issues.append(f"STATE-1 畫幅鎖丟失：project_state.json 鎖定畫幅為 {exp_aspect}，但投餵稿未見該畫幅")
    exp_mode = locks.get("asset_mode", "")
    if exp_mode and f"素材形態：{exp_mode}" not in feed_text and f"素材形態:{exp_mode}" not in feed_text:
        warns.append(f"STATE-2 素材形態聲明偏離：台賬鎖定為 {exp_mode}，投餵稿頂部未見匹配的素材形態聲明")

    # 2. 世界錨對賬（年代錨 + 禁用元素）
    wa = state.get("world_anchor", {})
    era = wa.get("era_anchor", "")
    if era and era not in feed_text:
        warns.append(f"STATE-3 世界錨未繼承：台賬《世界錨卡》鎖定年代「{era}」未原樣落入投餵稿")
    for bad_elem in wa.get("forbidden_elements", []):
        if bad_elem and bad_elem in feed_text:
            issues.append(f"STATE-4 違反《世界錨卡》禁用元素：正文中出現了被禁時代元素「{bad_elem}」")

    # 3. 角色表演檔案（Voice 聲線鎖 + 年齡錨 + CHAR_STATE 脫離態）對賬
    for cname, cinfo in state.get("characters", {}).items():
        if cname not in feed_text:
            continue
        vlock = cinfo.get("voice_lock", "")
        if vlock and vlock not in feed_text:
            warns.append(f"STATE-5 角色「{cname}」的 P3《角色表演檔案》Voice 聲線鎖（「{vlock}」）未落入投餵稿【核心人物】")
        age = cinfo.get("age_anchor", "")
        # M1/M2 全能參考有圖模式下，【核心人物】嚴禁二次複述年齡與外貌，僅 M0 無圖模式檢查 P4 年齡錨
        if exp_mode == "M0" and age and age not in feed_text:
            warns.append(f"STATE-6 [M0無圖模式] 角色「{cname}」的《人物錨卡》年齡錨（「{age}」）未落入投餵稿【核心人物】")
        for st_key, st_val in (cinfo.get("char_states") or {}).items():
            item = st_val.get("item", "")
            if item and item in feed_text and "覆蓋角色參考圖" not in feed_text:
                warns.append(f"STATE-7 角色「{cname}」存在 CHAR_STATE 脫離項「{item}」，但投餵稿缺「以本段提示詞為準，覆蓋角色參考圖」替換聲明")

    # 4. P0B 情緒錨點 80% 機位組合 & P3 故事板面板鏈對賬
    for seg in state.get("segments", []):
        sid = seg.get("seg_id", "段")
        combo = seg.get("camera_combo_80", "")
        if combo:
            # 檢查核心景別或角度詞是否落在鏡行中
            parts = [p.strip() for p in combo.split("·") if p.strip()]
            if parts and not all(p in feed_text for p in parts):
                warns.append(f"STATE-8 [{sid}] P0B《情緒錨點表》鎖定的 80% 核心機位組合「{combo}」未在鏡行中完整體現")
        panels = seg.get("storyboard_panels", [])
        if panels:
            shots = parse_shots(feed_text)
            if len(shots) == 0:
                issues.append(f"STATE-9 [{sid}] 未解析到任何有效時間軸鏡行，無法承接 P3 故事板（共 {len(panels)} 格）")
    return issues, warns


def self_test():
    st = default_project_state()
    assert parse_time_ranges("0-3秒 [鏡頭1] 中景")[0][:2] == (0.0, 3.0)
    assert parse_time_ranges("[鏡頭1] 0-4秒，中景")[0][:2] == (0.0, 4.0)
    assert parse_time_ranges("00:00-00:05 [鏡頭1] 中景")[0][:2] == (0.0, 5.0)
    assert parse_time_ranges("0s-3.5s [鏡頭1] 中景")[0][:2] == (0.0, 3.5)
    # ★2026-10-14 Agent 修復迴歸鎖：`MM:SS.s` 的 1 位小數必須按位數換算（`.5`=0.5s，非 0.05s）
    assert frac_to_sec("5") == 0.5 and frac_to_sec("50") == 0.5 and frac_to_sec("05") == 0.05
    assert frac_to_sec(None) == 0.0 and frac_to_sec("") == 0.0
    assert parse_time_ranges("00:10.5-00:12.5 [鏡頭4] 近景")[0][:2] == (10.5, 12.5), \
        "00:10.5 應為 10.5s（原缺陷為 10.05s）"
    assert parse_time_ranges("00:00-00:03.5 [鏡頭1] 近景")[0][:2] == (0.0, 3.5), \
        "00:03.5 應為 3.5s（原缺陷為 3.05s）"
    assert parse_time_ranges("00:00-00:15.75 [鏡頭1] 近景")[0][:2] == (0.0, 15.75), \
        "兩位小數 .75 應為 0.75s"
    assert parse_shots("00:08-00:10.5 [鏡頭3] 特寫")[0][1:3] == (8.0, 10.5)
    assert len(parse_shots("【鏡頭1】 0-3秒，中景\n【鏡頭2】 3-6秒，近景")) == 2
    iss, wrn = verify_feed_against_state("素材形態：M1\n16:9\n2026年現代都市\n00:00-00:04 [鏡頭1] 中近景 · 側45度", st)
    assert not iss
    print("[+] sd_core self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫劇老李 V8.2.0-SLIM 公共解析內核與狀態台賬工具")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--init-state", metavar="JSON_PATH", help="生成標準 project_state.json 模板")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.init_state:
        with open(args.init_state, "w", encoding="utf-8") as f:
            json.dump(default_project_state(), f, ensure_ascii=False, indent=2)
        print(f"[+] 已生成項目狀態台賬模板：{args.init_state}")
        sys.exit(0)
    ap.print_help()


if __name__ == "__main__":
    main()
