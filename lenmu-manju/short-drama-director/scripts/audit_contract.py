#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_contract.py — 漫劇老李 Short-Drama Director Suite 全流程交付契約與權威源核銷器 (V7.5.0-SLIM · 沿革見 CHANGELOG)

專治外部 Agent 三大通病（2026-10-14 實測根因封堵）：
  1. 「拿 validate_prompt.py 機檢全綠當任務完成」——只寫 P4 投餵稿，漏掉 P0B 情緒錨點表、P1 表演檔案/世界錨/人物錨、P3 場面調度/故事板圖、P5 連續性台賬/素材接線單；
  2. 「按當下最小口徑糊弄過關，不按權威源落字」——P2/P2.5 資產提示詞寫成幾行簡筆摘要（未回 sd-asset-engine 三大模板落 4 格無臉立繪 / 母版+九宮格 8 字段 / 道具 4 格板），I 鎖美學短語憑常識手搓（未回 style-bible 取 72 卡正主短語與 11 槽位）；
  3. 「你抓一次我修一次，擠牙膏式被動返工」——開工前不建契約清單，交付前不逐項核銷。

修復記錄（2026-10-14 · 實測《北境隱王》迴歸發現）：
  • P1：auto 模式誤判——滿配檔案含 P2.5 即被降級 board-lite，靜默跳過 CT1/CT4/CT6-LED 六項；改為先探滿配階段標記，無標記才降級。
  • P2：指紋匹配空白歸一化——「3×3 九宮格」「45° 側視圖」「Voice Description」等空格/大小寫變體不再誤殺；CT6-WIR 放寬「只控制什麼」為「控制什麼+不控制什麼」等價變體。

用法：
  1. 開工前生成《交付契約核銷表》（含每階段硬產出 + 權威源文件路徑 + 必現結構指紋 + 指定導演卡正主短語）：
     python3 short-drama-director/scripts/audit_contract.py --init [--mode full|board-lite] [--director 07|路陽|33|樸贊鬱]
  2. 交付前對稿件執行全流程契約與權威源指紋審計（未通過嚴禁宣佈「任務完成」）：
     python3 short-drama-director/scripts/audit_contract.py <稿件.md> [--mode auto|full|board-lite] [--director 07|路陽]
  3. 自測：
     python3 short-drama-director/scripts/audit_contract.py --self-test
"""

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SUITE_DIR = os.path.dirname(BASE_DIR)

# 10 張滿配主力導演卡正主短語與關鍵指紋（與 style-bible/director-param-library.md & style-prefix-blocks.md 同源）
CANONICAL_DIRECTOR_CARDS = {
    "01": {"name": "張藝謀", "keywords": ("濃烈色塊", "高飽和", "儀式對稱", "大遠景", "1:8", "冷暖對沖")},
    "03": {"name": "王家衛", "keywords": ("霓虹", "抽幀", "前景遮擋", "淺景深", "1:6", "暗綠", "暖黃")},
    "04": {"name": "徐克", "keywords": ("廣角", "斜角", "高速", "急推", "1:8", "冷青", "16mm", "18mm")},
    "06": {"name": "烏爾善", "keywords": ("神話", "重工業", "金青", "火光", "1:8", "圖騰", "厚重")},
    "07": {"name": "路陽", "keywords": ("冷青", "暖橙", "燭火", "火折", "淺景深", "1:8", "1:10", "硬切", "冷峻")},
    "12": {"name": "袁和平", "keywords": ("硬橋硬馬", "中景", "全景", "拳腳", "力道", "竹林", "青灰")},
    "33": {"name": "樸贊鬱", "keywords": ("幽綠", "暗紅", "對稱", "俯拍", "折磨", "冷冽", "1:8", "1:10", "高反差")},
    "39": {"name": "大衛·芬奇", "keywords": ("冷黃綠", "青灰", "陰鬱", "機械", "定焦", "1:6", "1:8", "精準")},
    "52": {"name": "羅傑·狄金斯", "keywords": ("單源", "實用光", "剪影", "冷青灰", "陰影側", "1:6", "1:8", "35~85mm")},
    "64": {"name": "MAPPA", "keywords": ("高對比", "粗黑邊", "速度線", "衝擊幀", "廣角透視", "粒子")},
    "65": {"name": "國漫3D仙俠", "keywords": ("國漫3D", "半寫實", "PBR", "絲綢", "丁達爾", "流光劍氣")},
    "66": {"name": "暗黑神話遊戲CG", "keywords": ("虛幻5", "遊戲CG", "PBR", "甲冑", "暗黑", "丁達爾")},
    "71": {"name": "國漫3D進階水墨", "keywords": ("三渲二", "水墨", "枯筆", "飛白", "墨韻", "硃砂")},
    "72": {"name": "東方神話3D奇幻", "keywords": ("東方神話", "3D", "次表面散射", "青綠", "赤金", "法相")},
}

CONTRACT_ITEMS_FULL = [
    ("CT1-P0A", "P0A 前置五道鎖基準表", "short-drama-director/SKILL.md §〇",
     "含 〇·1 素材來源 / A 模型 / B 畫幅 / C 交付 / D 段縫 / I 畫風鎖 / M 素材形態"),
    ("CT1-P0B", "P0B 導演決策《情緒錨點表》", "sd-decision-engine/references/emotion-anchor-table.md + forbidden-zone-whitelist.md",
     "含 情境 ID (E01~E15) + 80/15/5 機位組合鎖 + 構圖雷區 A 類解鎖 / B 類規避"),
    ("CT1-P1A", "P1 《世界錨卡》與《人物錨卡》", "sd-script-engine/references/story-bible-and-ip.md §1.11",
     "世界錨卡含年代/地域/禁用與必現元素；人物錨卡含年齡錨 + 體型錨(身高/頭身比) + 身份外觀三件套 + 反漂移清單"),
    ("CT1-P1B", "P1 《因果與關係表》與《稱呼賬本》", "sd-script-engine/references/dialogue-naturalization.md",
     "因果表每場必寫明確「潰敗方」（公理7）；稱呼賬本含前態/後態/禁稱"),
    ("CT1-P1C", "P1/P3 《角色表演主檔案》", "short-drama-director/references/acting-direction.md",
     "每位主要角色一份：含內在驅動引擎 + Voice Lock 英文聲線標籤 + 習慣動作賬本 + 眼神生命 + 「然而，當…」破功句"),
    ("CT2-P2L", "P2 資產三清單與狀態彙總表", "sd-asset-engine/references/three-list-extraction.md",
     "文檔A 角色清單 / 文檔B 道具清單 / 文檔C 場景清單 + Step 3.5 素材清單狀態彙總表"),
    ("CT2-CHR", "P2 角色四格無臉立繪提示詞（防簡筆糊弄）", "sd-asset-engine/references/character-portrait-templates.md",
     "每角色必含：全圖共 4 格 + ①面部特寫唯一清晰臉 + ②③④無臉全身(featureless face,含頭含鞋) + 身份外觀三件套 + 五官10項鎖定 + 圖底聲紋錨 + Voice Description 英文標籤 + 負向詞"),
    ("CT2-SCN", "P2 場景母版 + 3×3 九宮格 8 字段提示詞（防簡筆糊弄）", "sd-asset-engine/references/scene-grid-template.md + asset-spatial-ledger.md §四",
     "必含：場景空間事實五件事(座標系/SET_STATE/空氣介質/尺度/年代錨) + ① 16:9 無人場景母版 + ② 3×3 九宮格完整 8 字段(含攝影機矩陣與標註降級條款)"),
    ("CT2-PRP", "P2 道具四格設定圖提示詞（防簡筆糊弄）", "sd-asset-engine/references/prop-template.md",
     "每個核心道具必含：全圖共 4 格(①正面/②45°側視/③頂部俯視/④細節特寫) + 禁止出現手/人物剪影 + negative prompt"),
    ("CT3-STY", "I 鎖畫風正主出處核驗（防常識手搓假短語）", "short-drama-director/references/style-bible/director-param-library.md + style-prefix-blocks.md",
     "選定導演卡時必須原樣提取 style-bible 對應卡號的正主美學短語與 11 槽位段8/段9，嚴禁憑印象手搓近似詞"),
    ("CT4-BLK", "P3 場面調度層（座標系·權力幾何·道具台賬）", "short-drama-director/references/blocking-direction.md",
     "含全場唯一空間座標系文字平面圖 + 各段初始位與位移增量 + 權力幾何演進表 + 關鍵道具持有/手位/落點台賬"),
    ("CT4-SBD", "P3 九字段分鏡與故事板圖 CLEAN_GRID + 圖形化交付清單", "sd-storyboard-engine/SKILL.md §五 + storyboard-sheet-template.md",
     "逐鏡九字段標準分鏡 + 每段一張故事板圖 CLEAN_GRID(文戲2×2四宮格/打戲2×3六宮格，面板1~4/6) + P3 圖形化交付清單"),
    ("CT5-P4F", "P4 相鄰段邊界推薦表 + 七段式投餵詞 + 外掛回執頭", "short-drama-director/references/segment-splicing.md + model-adapters.md §5",
     "頂部三行【外掛激活回執頭】+ 相鄰段邊界推薦表(含段縫景別差) + N 組完整七段式投餵詞"),
    ("CT5-P45", "P4.5 《預演故事板》· 條件必出（★審計補丁P1 新增）", "sd-storyboard-engine/references/p45-previs-storyboard.md",
     "觸發條件（任一命中）：① 單段【站位聲明】具名 ≥3 人同框 ② 全集 ≥2 個不同 @//scn/ 場景（跨空間）③ 單段內跨 2 場。"
     "觸發則必附 {項目名}-預演故事板.md，並在主稿交付清單列「預演故事板：段n~段m ✅ / ⛔未附（理由）」；未觸發須顯式寫豁免理由"),
    ("CT6-P5Q", "P5 《素材接線單》+ 機檢報告 + 《跨鏡連續性台賬》", "short-drama-director/references/asset-delivery-modes.md + sd-qc-engine/references/continuity-ledger.md",
     "M1 必附《素材接線單》(含只控制什麼/不控制什麼) + 雙門機檢結果 + 逐段《跨鏡連續性台賬》(SET_STATE/CHAR_STATE/出口幀)"),
]


def print_init_checklist(mode="full", director=None, delivery=None):
    print("# 📋 Short-Drama Director 全流程交付契約核銷表（開工必建 · 交付必核）")
    print("")
    print("> **鐵律**：`validate_prompt.py` 報 `PASSED` 只代表「P4 投餵塊語法合格」，**絕不代表全流程交付完成**！")
    print("> 開工前必須先建本表；每寫完一節必須回對照「權威源文件路徑」與「必現結構指紋」打 `[x]`；")
    print("> 交付前必須跑 `python3 short-drama-director/scripts/audit_contract.py <稿件.md>` 全綠放行。")
    print("")
    print("| 狀態 | 契約碼 | 階段交付物 | 唯一權威源文件（必須回讀，禁憑印象手搓） | 必現結構指紋（機檢核銷項） |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    print(f"> 檢查範圍：{delivery or mode}；本工具僅檢查結構指紋，不證明語義核銷。")
    for code, title, ref_path, fp in CONTRACT_ITEMS_FULL:
        if delivery == "feed-only" and code not in ("CT5-P4F", "CT6-P5Q"):
            continue
        if delivery == "agent-bundle" and not code.startswith(("CT2-", "CT3-", "CT5-", "CT6-")):
            continue
        if delivery in ("feed-only", "agent-bundle") and code == "CT6-P5Q":
            code, title = "CT6-WIR", "M1 素材接線單"
            fp = "僅檢查素材接線單及控制什麼/不控制什麼指紋；不要求完整 P5 台賬"
        if mode == "board-lite" and code in ("CT1-P0B", "CT1-P1B", "CT4-BLK"):
            continue
        print(f"| `[ ]` | `{code}` | **{title}** | `{ref_path}` | {fp} |")
    if director:
        print("\n## 🎨 指定導演卡正主參數提取指引（嚴禁憑常識手搓）")
        d_key = str(director).strip().zfill(2) if str(director).strip().isdigit() else str(director).strip()
        matched = None
        for k, v in CANONICAL_DIRECTOR_CARDS.items():
            if d_key == k or d_key in v["name"] or v["name"] in d_key:
                matched = (k, v)
                break
        if matched:
            k, v = matched
            print(f"- **鎖定卡號**：`{k} {v['name']}`")
            print(f"- **權威源位置**：`short-drama-director/references/style-bible/director-param-library.md` + `style-prefix-blocks.md`")
            print(f"- **必現正主指紋詞**：`{' / '.join(v['keywords'])}`")
            print(f"- **自動提取命令**：`python3 short-drama-director/scripts/style-lock-ladder.py --card {k}`")
        else:
            print(f"- 請運行 `python3 short-drama-director/scripts/style-lock-recommend.py` 或查閱 `director-style-catalog-74.md` 提取 `{director}` 的正主槽位。")


# ★P2 補丁：投餵單元默認也要帶資產提示詞（SKILL L141「md 正文只放兩樣：資產提示詞 + 分鏡提示詞」）。
#   只有在主稿顯式聲明"資產已另冊"時才免核 CT2——否則"另冊"和"根本沒寫"在文字上無法區分。
ASSET_ELSEWHERE_RE = re.compile(
    r"資產另冊|資產提示詞見|資產提示詞分|人物立繪提示詞|場景提示詞\.md|人物與場景提示詞")


def _asset_elsewhere(text):
    return bool(ASSET_ELSEWHERE_RE.search(text or ""))


def _audit_p0a_locks(text, mode="full", base_dir=None):
    """CT1-P0A 實現（2026-11-25 補 · 原為僅聲明無實現的幽靈項）。

    核銷口徑：P0A 鎖台賬必須存在，且每項鎖 src=user（用戶勾選/用戶原話憑證）。
    代填（src=default/agent/infer/preset）、無憑證、值域非法 → FAIL。
    board-lite 模式（單文件看板稿）降級為 WARN，不阻斷歷史短稿。

    單一事實源：台賬只寫一份（00_立項包）。主檔/其它分冊寫「鎖台賬見：00_立項包.md」
    即可按路徑解析，避免同一份鎖表抄兩處、抄出兩個口徑（SKILL.md L533 記錄的
    摘要層漂移事故，就是副本層先被讀到導致規則失效）。
    """
    try:
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        import check_locks
    except Exception as exc:  # pragma: no cover
        return [], ["CT1-P0A 無法加載 check_locks.py（%s）——鎖憑證核銷不可用" % exc], []

    ledger_text = text or ""
    if "<!-- LOCK-LEDGER:BEGIN -->" not in ledger_text:
        ref = re.search(r"鎖台賬見[:：]\s*([^\s|，,（）()」]+)", ledger_text)
        if ref and base_dir:
            cand_raw = ref.group(1)
            base_real = os.path.realpath(base_dir)
            if os.path.isabs(cand_raw):
                return [], [f"CT1-P0A 鎖台賬路徑越界（禁止絕對路徑：{cand_raw}）"], []
            cand_real = os.path.realpath(os.path.join(base_real, cand_raw))
            if os.path.commonpath([base_real, cand_real]) != base_real:
                return [], [f"CT1-P0A 鎖台賬路徑越界（禁止跳出項目目錄：{cand_raw}）"], []
            if os.path.isfile(cand_real):
                try:
                    ledger_text += "\n" + open(cand_real, encoding="utf-8").read()
                except Exception:
                    pass

    multi = bool(
        re.search(r"投餵單元\s*[2-9]", ledger_text)
        or re.search(r"段\s*[2-9]\s*[·:：]", ledger_text)
        or re.search(r"段\s*[2-9]\s*\(", ledger_text)
    )
    ok, fails, warns = check_locks.audit_text(ledger_text, multi_segment=multi)

    passed, issues, out_warns = [], [], []
    for w in warns:
        out_warns.append("CT1-P0A " + w)

    if not fails:
        lock_cnt = sum(1 for x in ok if x.startswith("L3 "))
        passed.append("CT1-P0A P0A 鎖台賬憑證核銷通過（%d 項鎖全部 src=user）" % lock_cnt)
        return passed, issues, out_warns

    if mode == "board-lite":
        for f in fails:
            out_warns.append("CT1-P0A（board-lite 降級告警）" + f)
    else:
        for f in fails:
            issues.append("CT1-P0A " + f)
    return passed, issues, out_warns


def audit_markdown(text, mode="auto", director=None, delivery=None, base_dir=None):
    """僅檢查結構指紋；不證明內容正確、逐項完整或語義核銷。"""
    if delivery not in (None, "full-project", "agent-bundle", "feed-only"):
        raise ValueError(f"未知交付範圍：{delivery}")
    if mode not in ("auto", "full", "board-lite"):
        raise ValueError(f"未知審計模式：{mode}")
    if delivery == "full-project":
        mode = "full"
    issues = []
    warns = []
    passed = []

    if mode == "auto":
        # Detect whether this is a board-lite single-file doc or a full production archive
        # 2026-10-14 修復（P1 級 · 實測《北境隱王》迴歸發現）：滿配生產檔案同樣含 P2.5——
        # 舊邏輯「見 P2.5 即 board-lite」會靜默跳過 CT1-P0B/P1A/P1B/P1C、CT4-BLK/SBD、CT6-LED 六項，
        # 恰好放走「漏 P1/P3/P5」這類最典型的漏項。改為：檢出任一滿配階段標記即按 full 審計，
        # 僅當全文缺失所有滿配標記且含 P2.5/看板標記時才降級 board-lite（寧可多查，不可靜默漏查）。
        _full_markers = (
            "世界錨卡", "人物錨卡", "表演主檔案", "故事板圖",
            "連續性台賬", "場面調度", "空間座標系", "場景座標系",
        )
        _has_full_marker = any(m in text for m in _full_markers) or bool(
            re.search(r"^##\s*P[135]\b", text, re.M) or re.search(r"^###\s*P3-", text, re.M)
        )
        if not _has_full_marker and ("P2.5" in text or ("導演參考塊" in text and "【時間軸分鏡】" in text)):
            mode = "board-lite"
        else:
            mode = "full"

    # 1. CT1: P0 & P1 anchors and acting profiles
    # ★ 2026-11-25 補實現：CT1-P0A 原為「幽靈項」——契約表第 1 條聲明 P0A 前置五道鎖基準表，
    #   但全文件只有聲明、沒有一行實現代碼，於是「執行者自己寫一張鎖表就 PASS」。
    #   用戶連續三次追責「強制鎖未彈卡、按默認值代填」的根因即在於此。現改由 check_locks.py 硬核銷。
    _p0a_p, _p0a_i, _p0a_w = _audit_p0a_locks(text, mode, base_dir)
    passed.extend(_p0a_p)
    issues.extend(_p0a_i)
    warns.extend(_p0a_w)

    if mode == "full":
        if "情緒錨點表" in text and re.search(r"E0[1-9]|E1[0-5]", text) and "80%" in text:
            passed.append("CT1-P0B P0B《情緒錨點表》（含情境ID與80/15/5機位鎖）在位")
        else:
            issues.append("CT1-P0B 缺失 P0B《情緒錨點表》（須含情境 ID E01~E15 與 80/15/5 機位鎖，權威見 sd-decision-engine）")

        if "世界錨卡" in text and "人物錨卡" in text and "身份外觀三件套" in text:
            passed.append("CT1-P1A P1《世界錨卡》與《人物錨卡》（含身份外觀三件套）在位")
        else:
            issues.append("CT1-P1A 缺失 P1《世界錨卡》或《人物錨卡》（須含年齡錨/體型錨/身份外觀三件套，權威見 story-bible-and-ip.md §1.11）")

        if ("角色表演" in text or "表演主檔案" in text or "表演檔案" in text) and "然而，當" in text:
            passed.append("CT1-P1C 《角色表演主檔案》（含 Voice 聲線鎖與「然而，當…」破功句）在位")
        else:
            issues.append("CT1-P1C 缺失《角色表演主檔案》或漏寫「然而，當…」破功句（權威見 acting-direction.md）")

    # 2. CT2: P2 / P2.5 Asset Prompts — strictly block sketchy 1-line summaries!
    # 2026-10-14 修復（P2 級）：指紋匹配統一做空白歸一化（_tn=去全半角空白 / _tnl=再轉小寫），
    # 「全圖共 4 格 / 3×3 九宮格 / 45° 側視圖 / Voice Description」等空格與大小寫變體不再誤殺，
    # 與 CHR 檢查原有的雙變體口徑對齊（SCN/PRP 此前只認單一帶空格寫法，口徑不一）。
    _tn = re.sub(r"[\s\u3000]+", "", text)
    _tnl = _tn.lower()
    has_chr_template = (
        (
            "全圖共4格" in _tn
            and ("無臉全身" in _tn or "featurelessface" in _tnl)
            and "五官10項" in _tn
            and ("voicedescription" in _tnl or "圖底音色速覽標籤" in _tn)
        )
        or (
            "八格拼版" in _tn
            and "面部標記" in _tn
            and ("聲線錨定" in _tn or "voicedescription" in _tnl)
        )
    )
    if has_chr_template:
        passed.append("CT2-CHR 角色四格無臉立繪提示詞命中結構指紋（4格/無臉全身/五官10項/Voice標籤；不證明模板完整性）")
    else:
        issues.append(
            "CT2-CHR 角色資產提示詞未按權威模板展開（疑似簡筆糊弄版！）——必須回讀 "
            "`sd-asset-engine/references/character-portrait-templates.md`，寫出「全圖共 4 格 + ①面部特寫唯一清晰臉 + "
            "②③④無臉全身(featureless face,含頭含鞋) + 身份外觀三件套 + 五官10項鎖定 + 圖底聲紋錨 + Voice Description 英文標籤 + 負向詞」"
            "；若資產已拆冊交付，請在本稿寫明「資產另冊：{文件名}」"
        )

    has_scn_template = (
        ("場景母版" in _tn or "無人空鏡基準圖" in _tn)
        and (
            "五宮格攝影機矩陣" in _tn
            or ("五宮格" in _tn and "參考場景鎖定模式" in _tn)
            or "九宮格攝影機矩陣" in _tn
            or ("3×3九宮格" in _tn and "參考場景鎖定模式" in _tn)
        )
        and ("標註降級條款" in _tn or "畫面純淨要求" in _tn or "對照表" in _tn)
    )
    if has_scn_template:
        passed.append("CT2-SCN 場景母版 + 3×3 九宮格 8 字段提示詞命中結構指紋（不證明模板完整性）")
    else:
        issues.append(
            "CT2-SCN 場景資產提示詞未按權威模板展開（疑似簡筆糊弄版！）——必須回讀 "
            "`sd-asset-engine/references/scene-grid-template.md` 與 `asset-spatial-ledger.md §四`，"
            "同時產出「① 16:9 無人場景母版」與「② 16:9 五宮格完整 8 字段（左2/3鳥瞰+右1/3四向，含【五宮格攝影機矩陣】、【參考場景鎖定模式】、標註降級條款）」"
            "；若資產已拆冊交付，請在本稿寫明「資產另冊：{文件名}」"
        )

    has_prp_template = (
        ("道具設定圖" in _tn or "道具提示詞" in _tn)
        and ("單體靜物" in _tn or "單張" in _tn or "正面視圖" in _tn and "45°側視圖" in _tn and "俯視圖" in _tn)
        and ("禁止手持" in _tn or "不出現人物、人手" in _tn)
    )
    if has_prp_template:
        passed.append("CT2-PRP 道具四格設定圖提示詞命中結構指紋（不證明模板完整性）")
    else:
        issues.append(
            "CT2-PRP 道具資產提示詞未按權威模板展開（疑似簡筆糊弄版或缺失！）——必須回讀 "
            "`sd-asset-engine/references/prop-template.md`，寫出「全圖共 4 格（①正面視圖/②45°側視圖/③頂部俯視圖/④關鍵細節特寫）+ 禁止手持展示 + negative prompt」"
            "；若資產已拆冊交付，請在本稿寫明「資產另冊：{文件名}」"
        )

    # 3. CT3: Style-Bible canonical verification
    detected_card = director
    if not detected_card:
        m_card = re.search(r"(?:導演卡|風格卡|I\s*鎖)[^\n]{0,30}?\b(0[13467]|12|33|39|52|64)\b", text)
        if m_card:
            detected_card = m_card.group(1)
        else:
            for k, v in CANONICAL_DIRECTOR_CARDS.items():
                if v["name"] in text:
                    detected_card = k
                    break
    if detected_card:
        d_key = str(detected_card).strip().zfill(2) if str(detected_card).strip().isdigit() else str(detected_card).strip()
        for k, v in CANONICAL_DIRECTOR_CARDS.items():
            if d_key == k or d_key in v["name"] or v["name"] in d_key:
                hits = [kw for kw in v["keywords"] if kw in text]
                if len(hits) >= 2:
                    passed.append(f"CT3-STY I 鎖畫風命中 style-bible 結構指紋（非語義核銷） [{k} {v['name']}] 正主槽位詞 {hits[:4]}")
                else:
                    issues.append(
                        f"CT3-STY I 鎖畫風疑似手搓近似詞：檢測到導演卡 [{k} {v['name']}]，但正文未命中 style-bible 正主槽位指紋詞 "
                        f"{v['keywords']}（僅命中 {hits}）——嚴禁憑常識手搓風格詞，必須從 `director-param-library.md` / `style-prefix-blocks.md` 取正主！"
                    )
                break

    # 4. CT4: P3 Blocking, Storyboard Sheet CLEAN_GRID & Graphical Delivery Checklist
    if mode == "full":
        if ("場景座標系" in text or "空間座標系" in text) and "權力幾何" in text:
            passed.append("CT4-BLK P3 場面調度層（空間座標系 + 權力幾何）在位")
        else:
            issues.append("CT4-BLK 缺失 P3 場面調度層（須含空間座標系文字平面圖與權力幾何演進表，權威見 blocking-direction.md）")

        if "故事板圖" in text and "面板 1" in text and "圖形化交付清單" in text:
            passed.append("CT4-SBD P3 故事板圖 CLEAN_GRID 與《P3 圖形化交付清單》在位")
        else:
            issues.append(
                "CT4-SBD 缺失 P3《故事板圖 CLEAN_GRID》（每段一張，含面板 1~4/6 相位拆解）或《P3 圖形化交付清單》"
                "（權威見 sd-storyboard-engine/references/storyboard-sheet-template.md）"
            )

    # 5. CT5: P4 Feed blocks & segment boundary table
    if "【時間軸分鏡】" in text and "【站位聲明】" in text:
        passed.append("CT5-P4F P4 七段式投餵提示詞主體在位")
    else:
        issues.append("CT5-P4F 缺失 P4 七段式投餵提示詞主體")

    # 5b. CT5-P45 預演故事板（★審計補丁P1 新增 · 治「規則寫了但沒有任何門，永遠不出」）
    #   舊態：P4.5 在 SKILL.md 裡被定義為「可選附加件 · 默認不附」，契約 14 項裡沒有它，
    #   機檢也不數同框人數 → 用戶不點名就 100% 不出（實測漏出）。
    #   現態：把它的三個觸發條件**機檢化**，命中不出即 FAIL。
    _p45_names, _p45_scns, _p45_crossseg = set(), set(), 0
    for _blk45 in re.findall(r"【站位聲明】[：:]?([^\n]*)", text):
        _ns45 = set(re.findall(r"@([^\s@（）()【】，、；;：:]+)", _blk45))
        if len(_ns45) >= 3:
            _p45_names.add(frozenset(_ns45))
    # ★P4：場景識別不再只認 `@//scn/ - ` 前綴。
    #   `@//scn/` 僅在平台真掛載了 chr/scn/prp 資產文件夾時使用；未掛載（資產還是
    #   md 待出圖）時，投餵稿寫「場景名（圖N / 圖M）」純圖號雙掛形態——舊正則對後者
    #   返回空集，「跨 N 個場景」觸發器靜默失效（2026-10-22 實測：《三天》3 個場景
    #   識別為 0，全靠「≥3 人同框」另一條觸發兜著，2 人 2 場景劇本會整條漏殺）。
    #   場景 = 雙掛（母版 + 九宮格），道具 = 單掛，故按「（圖N / 圖M）」判場景。
    _p45_scns = set(re.findall(r"@//scn/\s*-\s*([^（(；;\n]+)", text))  # 舊語法兼容
    for _sblk45 in re.findall(r"【場景資產】[：:]?([^\n]+)", text):
        for _sn45 in re.findall(r"([^；;。，、\n]+?)（圖\s*\d+\s*/\s*圖\s*\d+", _sblk45):
            _p45_scns.add(_sn45.strip())
    _p45_crossseg = text.count("【畫幅風格】")
    _p45_hit = []
    if _p45_names:
        _p45_hit.append("單段≥3 人同框")
    if len(_p45_scns) >= 2:
        _p45_hit.append(f"跨 {len(_p45_scns)} 個場景")
    if _p45_crossseg >= 2 and _p45_hit:
        pass
    if _p45_hit:
        if ("預演故事板" in text) and ("要看" in text or "本段要驗" in text):
            passed.append("CT5-P45 《預演故事板》在位（觸發：" + "、".join(_p45_hit) + "）")
        else:
            issues.append(
                "CT5-P45 缺《預演故事板》（觸發：" + "、".join(_p45_hit) + "）——"
                "P4.5 是**條件必出**，不是可選：≥3 人同框 / 跨 2 場景 / 跨段長鏡 任一命中就要附，"
                "體例見 sd-storyboard-engine/references/p45-previs-storyboard.md"
                "（一段一節 = 本段要驗什麼 + 敘述體故事板提示詞 + 看圖先看這三點）。"
                "確實不需要時，在主稿顯式寫「預演故事板：⛔未附（理由）」"
            )

    # 6. CT6: P5 M1 Wiring Table & Continuity Ledger
    # 2026-10-14 修復（P2 級）：「只控制什麼」放寬為「控制什麼+不控制什麼」等價變體
    # （「只控制什麼」是「控制什麼」的超集串，權威正主寫法仍優先命中，不再因少一個「只」字誤殺）。
    if "素材接線單" in text and "控制什麼" in text and "不控制什麼" in text:
        passed.append("CT6-WIR M1《素材接線單》（含只控制什麼/不控制什麼）在位")
    elif "M0" not in text[:400]:
        issues.append("CT6-WIR 缺失 M1《素材接線單》（須含圖號、引用段落、只控制什麼、不控制什麼，權威見 asset-delivery-modes.md）")

    if mode == "full":
        if ("連續性台賬" in text or "Continuity Ledger" in text) and "SET_STATE" in text:
            passed.append("CT6-LED P5《跨鏡連續性台賬（Continuity Ledger）》在位")
        else:
            issues.append("CT6-LED 缺失 P5《跨鏡連續性台賬（Continuity Ledger）》（須逐段登記 SET_STATE / CHAR_STATE / 道具落點 / 出口幀，權威見 continuity-ledger.md）")

    # 精簡交付只核對其承諾範圍，不要求 P0/P1/P3/P5 全項目檔案。
    if delivery in ("feed-only", "agent-bundle"):
        prefixes = ("CT5-", "CT6-WIR")   # CT5- 前綴已含 CT5-P4F 與 CT5-P45
        if delivery == "agent-bundle":
            prefixes += ("CT2-", "CT3-")
        elif not _asset_elsewhere(text):
            # ★P2：投餵單元的正文按 SKILL L141 必須含資產提示詞；未聲明"資產另冊"就照核 CT2。
            #   舊行為把 CT2 一併過濾 → 「只交投餵稿」永遠 PASS（2026-10-22 實測漏出資產層）。
            prefixes += ("CT2-",)
        issues = [item for item in issues if item.startswith(prefixes)]
        warns = [item for item in warns if item.startswith(prefixes)]
        passed = [item for item in passed if item.startswith(prefixes)]
    return issues, warns, passed


def _self_test():
    # 1. Verify init checklist generation works
    from io import StringIO
    old_stdout = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    try:
        print_init_checklist("full", "33")
    finally:
        sys.stdout = old_stdout
    out = buf.getvalue()
    assert "CT2-CHR" in out and "樸贊鬱" in out, "init checklist self-test failed"

    # 2. Verify full compliant sample passes 0 issues
    #    ★ 2026-11-25：compliant 樣本必須帶鎖台賬，否則 CT1-P0A 會（正確地）判 FAIL
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    import check_locks as _cl
    _ledger = "\n" + _cl.TEMPLATE.replace("YYYY-MM-DDTHH:MM", "2026-11-25T14:20") + "\n"
    compliant_sample = (
        "素材形態：M1\n情緒錨點表 E04 80%\n世界錨卡 人物錨卡 身份外觀三件套\n"
        "角色表演主檔案 然而，當\n"
        "全圖共 4 格 無臉全身 featureless face 五官 10 項 Voice Description\n"
        "場景母版 九宮格攝影機矩陣 3×3 九宮格 參考場景鎖定模式 標註降級條款\n"
        "道具設定圖 正面視圖 45° 側視圖 俯視圖 禁止手持\n"
        "場景座標系 權力幾何 故事板圖 面板 1 圖形化交付清單\n"
        "【站位聲明】 【時間軸分鏡】\n"
        "素材接線單 只控制什麼 不控制什麼 連續性台賬 SET_STATE\n"
        + _ledger
    )
    iss, _, pas = audit_markdown(compliant_sample, mode="full")
    assert not iss and len(pas) >= 8, f"compliant sample should pass, got {iss}"

    # 3. Verify sketchy / incomplete sample is caught on CT1, CT2, CT3, CT4, CT6
    sketchy_sample = (
        "# 某劇分鏡看板\n"
        "導演卡：33 樸贊鬱（高對比冷藍深紅）\n"
        "## P2.5 資產提示詞\n- 霍擎：50歲，穿緋袍。\n"
        "【站位聲明】@霍擎（畫面左）\n【時間軸分鏡】\n"
    )
    iss2, _, _ = audit_markdown(sketchy_sample, mode="full", director="33")
    codes = " ".join(iss2)
    for req_code in ("CT1-P0B", "CT2-CHR", "CT2-SCN", "CT2-PRP", "CT3-STY", "CT4-SBD", "CT6-WIR", "CT6-LED"):
        assert req_code in codes, f"sketchy sample should trigger {req_code}, got {iss2}"

    print("[+] audit_contract.py self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description="全流程交付契約與權威源核銷器")
    ap.add_argument("file", nargs="?", help="待核銷的 Markdown 稿件路徑")
    ap.add_argument("--init", action="store_true", help="開工前輸出《全流程交付契約核銷表》")
    ap.add_argument("--mode", default="auto", choices=["auto", "full", "board-lite"], help="交付模式")
    ap.add_argument("--director", default=None, help="鎖定的導演卡編號或姓名（如 07 / 路陽 / 33 / 樸贊鬱）")
    ap.add_argument("--delivery", choices=["full-project", "agent-bundle", "feed-only"],
                    help="結構指紋範圍：全項目 / 資產加投餵與接線 / 僅投餵與接線；省略保留舊模式")
    ap.add_argument("--self-test", action="store_true", help="運行內置自測")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(_self_test())

    if args.init or not args.file:
        print_init_checklist(mode="full" if args.mode == "auto" or args.delivery == "full-project" else args.mode,
                             director=args.director, delivery=args.delivery)
        sys.exit(0)

    if not os.path.isfile(args.file):
        print(f"[-] 文件不存在: {args.file}", file=sys.stderr)
        sys.exit(2)

    with open(args.file, "r", encoding="utf-8") as f:
        txt = f.read()

    # ★審計補丁P1：CLI 自動識別「投餵單元」，否則一份純投餵稿會被按項目交付包核銷、
    #   一次誤報 9 項（情緒錨點表/人物錨卡/調度/故事板/台賬），與 validate_prompt 口徑不一致。
    if args.delivery is None and (txt.count("【畫幅風格】") >= 2) and not re.search(
            r"資產提示詞|角色四格板|八格拼版|場景母版|五宮格提示詞|九宮格提示詞", txt):
        args.delivery = "feed-only"
        print("[i] 識別為「投餵單元」（≥2 組七段式、無資產模板段）→ 按 feed-only 核銷（核 CT5-/CT6-WIR + 資產 CT2-*）；"
              "若資產已拆冊交付，請在稿內寫明「資產另冊：{文件名}」以豁免 CT2；"
              "要做全項目核銷請顯式加 --delivery full-project")
    issues, warns, passed = audit_markdown(txt, mode=args.mode, director=args.director, delivery=args.delivery,
                                           base_dir=os.path.dirname(os.path.abspath(args.file)))
    print(f"=== 📋 全流程交付契約核銷報告 ({os.path.basename(args.file)} | mode={args.mode}) ===")
    for p in passed:
        print(f"  [PASS] {p}")
    for w in warns:
        print(f"  [WARN] {w}")
    for i in issues:
        print(f"  [FAIL] {i}")
    if issues:
        print(f"\n[-] 交付契約未通過：共 {len(issues)} 項契約/權威源缺失！嚴禁把 validate_prompt 格式全綠當成任務完成！")
        sys.exit(1)
    print(f"\n[+] 交付契約結構指紋檢查通過（共 {len(passed)} 項；不代表語義核銷、模板完整或全流程完成）")
    sys.exit(0)


if __name__ == "__main__":
    main()
