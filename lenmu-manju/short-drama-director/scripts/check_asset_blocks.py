#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_asset_blocks.py — 資產提示詞結構自檢（P2 出稿門禁）

背景（2026-10-19 實戰回寫）：
  實際交付中反覆出現四類硬傷，全部是**結構性**的、機器可判的，卻被人工目檢漏掉：
    ① 跨條引用（"同規格""見母版""同圖2""降級條款同圖2"）——單條複製出去就是殘缺指令；
    ② 角色同時寫"立繪/全身完整入畫"+"四格"——模型做加法，出成 5 格（正面被畫兩次）；
    ③ 九宮格缺模板字段（【場景定位】【九宮格內容分配】【參考場景鎖定模式】）——
       出圖後無法判斷哪格是哪個機位，也約束不住建築漂移；
    ④ 道具四格字段名不統一（"正面/45°側視/頂部俯視" vs "正面視圖/45°側視圖/頂部俯視圖"），
       缺"道具設定圖"標識 → 模型不知道該出設定板還是單張圖。
  本腳本把這些做成可機械判定的門禁，**資產段寫完必須跑一次，FAIL 清零再進分鏡**。

用法：
  python scripts/check_asset_blocks.py <含資產提示詞的 md>
      [--min-blocks 3] [--json]

判定單元：以 `#### 圖N · 名稱（類型）`（# 數不限，圖N 開頭）為塊起點，到下一個同級或更高級標題為止。

規則碼：
  A1 塊內出現跨條引用（不自包含）              ERROR
  A2 塊內未寫明 16:9 整板比例                  ERROR
  A3 九宮格缺字段 / 缺 9 格聲明 / 缺標註降級    ERROR
  A4 角色缺"全圖共 4 格"/"五官 10 項鎖定"/聲紋/負向詞   ERROR
  A5 角色塊出現舊稱"主圖"（易出 5 格）          ERROR
  A6 道具缺四格字段名 / 缺"道具設定圖" / 未禁手持  ERROR
  A7 塊類型無法判定                          WARN
  A8 整份資產塊數少於 --min-blocks            WARN

退出碼：0 = 全 PASS（允許 WARN）· 1 = 有 ERROR · 2 = 用法/讀取錯誤
"""

import json
import os
import re
import sys

BLOCK_RE = re.compile(r"^#{1,6}\s*\*{0,2}\s*圖\s*(\d+)\s*[*]{0,2}\s*[·:：\-—]?\s*(.*)$", re.M)
HEAD_RE = re.compile(r"^(#{1,6})\s", re.M)

# 跨條引用：單條提示詞複製出去即斷
CROSS_REF_PATTERNS = [
    (r"同上", "同上"),
    (r"同規格", "同規格"),
    (r"見母版", "見母版"),
    (r"同圖\s*\d", "同圖N"),
    (r"見第[一二三四五六七八九十0-9]+部分", "見第X部分"),
    (r"參見[^，。；\n]{0,12}", "參見…"),
    (r"按上述", "按上述"),
    (r"同前", "同前"),
    (r"沿用上文", "沿用上文"),
    (r"降級條款同", "降級條款同X"),
]

SCENE_GRID_FIELDS = ["【場景定位】", "【五宮格內容分配】", "【參考場景鎖定模式】"]
SCENE_GRID_FIELDS_LEGACY = ["【場景定位】", "【九宮格內容分配】", "【參考場景鎖定模式】"]
PROP_FIELDS = ["正面視圖", "45° 側視圖", "頂部俯視圖", "關鍵細節特寫"]
PROP_FIELDS_ALT = ["正面視圖", "45°側視圖", "頂部俯視圖", "關鍵細節特寫"]


def split_blocks(text):
    """按 `圖N` 標題切塊，返回 [(圖號, 標題, 正文)]。

    塊的右邊界 = **下一個同級或更高級標題**，不是「下一個圖N」。
    否則最後一個資產塊會一路吞到文末（把分鏡段、說明段全算進資產塊，
    既漏判該塊自身，又會把別處的「同上」誤報成資產塊的跨條引用）。
    """
    lines = text.split("\n")
    offsets, cursor = [], 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line) + 1

    heading_levels = []
    for line in lines:
        match = re.match(r"^(#{1,6})\s", line)
        heading_levels.append(len(match.group(1)) if match else 0)

    blocks = []
    for index, line in enumerate(lines):
        match = BLOCK_RE.match(line)
        if not match:
            continue
        level = heading_levels[index]
        end = len(text)
        for later in range(index + 1, len(lines)):
            if heading_levels[later] and heading_levels[later] <= level:
                end = offsets[later]
                break
        body = text[offsets[index]:end]
        blocks.append((match.group(1), match.group(2).strip(), body))
    return blocks


def classify(title, body):
    """按標題關鍵詞 + 必備字段判定塊類型。

    判定順序有講究：**道具必須先判**——道具也是四格版式，正文裡同樣寫「全圖共 4 格」，
    若先判角色會把全部道具塊誤當角色，報出一串「缺五官/缺聲紋」的假 FAIL。
    """
    if "道具設定圖" in body or "道具設定" in body or "道具" in title:
        return "道具"
    if "五宮格" in title or re.search(r"全圖共\s*5\s*格", body):
        return "五宮格"
    if "白模軸測" in title or "軸測站位" in title or "白模軸測" in body or "軸測空間站位" in body:
        return "白模軸測站位圖"
    if "九宮格" in title or re.search(r"全圖共\s*9\s*格", body):
        return "九宮格"
    if ("八格拼版" in body or "八格拼版" in title or re.search(r"全圖共\s*4\s*格", body) or "立繪" in body
            or "五官" in body or "聲紋" in body
            or re.search(r"[SABC]\s*級|男主|女主|主角|反派", title)):
        return "角色"
    if re.search(r"四格|4\s*格", body) and re.search(r"視圖|材質|尺寸參照|設定", body):
        return "道具"
    if "母版" in title or "無人空鏡" in body:
        return "場景母版"
    return "未知"


def check_block(number, title, body, kind):
    errors, warns = [], []
    tag = f"圖{number}"

    # A1 自包含
    for pattern, label in CROSS_REF_PATTERNS:
        if re.search(pattern, body):
            errors.append(f"A1 {tag} 出現跨條引用「{label}」——單條複製出去即斷，必須把內容逐條寫死")

    # A2 畫幅：常規資產板固定 16:9；可選角色八格拼版允許 3:2 橫版
    _is_char_8grid = (kind == "角色" and ("八格拼版" in body or "八格拼版" in title))
    if _is_char_8grid:
        if not re.search(r"3\s*[:：]\s*2", body):
            errors.append(f"A2 {tag} 角色八格拼版未寫明「3:2」橫版比例")
    elif not re.search(r"16\s*[:：]\s*9", body):
        errors.append(f"A2 {tag} 未寫明「16:9」整板比例（資產板固定 16:9，不隨成片畫幅變）")

    if kind == "白模軸測站位圖":
        if not re.search(r"@[^\s]+母版|參考圖\s*@|基於參考圖|場景母版", body):
            errors.append(f"A8 {tag} 白模軸測站位圖未預留「@場景母版」參考底圖位——必須先出場景母版再墊圖生成，防兩圖空間打架")

    if kind == "五宮格":
        for field in SCENE_GRID_FIELDS:
            if not re.search(re.escape(field[:-1]) + r"[^】]*】", body):
                errors.append(f"A3 {tag} 五宮格缺模板字段 {field}（八字段硬性，缺一即不合規）")
        if not re.search(r"全圖共\s*5\s*格", body):
            errors.append(f"A3 {tag} 五宮格未顯式聲明「全圖共 5 格」")
        if "僅允許攝影機移動" not in body and "允許按子區域切換機位" not in body and "關" not in body:
            errors.append(f"A3 {tag} 五宮格缺【參考場景鎖定模式】正文（關 / 僅允許攝影機移動 / 允許按子區域切換機位）")
        if not re.search(r"1\s*[~～-]\s*5", body) or "對照表" not in body:
            errors.append(f"A3 {tag} 五宮格缺標註降級條款（格內編號 1~5 + 圖外對照表）")

    if kind == "九宮格":
        for field in SCENE_GRID_FIELDS_LEGACY:
            # 字段名允許帶後綴（如「【參考場景鎖定模式 · 模式A 檔 · 僅允許攝影機移動】」）
            if not re.search(re.escape(field[:-1]) + r"[^】]*】", body):
                errors.append(f"A3 {tag} 九宮格缺模板字段 {field}（八字段硬性，缺一即不合規）")
        if not re.search(r"全圖共\s*9\s*格", body):
            errors.append(f"A3 {tag} 九宮格未顯式聲明「全圖共 9 格」")
        if "僅允許攝影機移動" not in body and "允許按子區域切換機位" not in body:
            errors.append(f"A3 {tag} 九宮格缺【參考場景鎖定模式】正文（模式A檔或模式B檔原文）")
        if not re.search(r"1\s*[~～-]\s*9", body) or "對照表" not in body:
            errors.append(f"A3 {tag} 九宮格缺標註降級條款（中文崩字 → 格內編號 1~9 + 圖外對照表）")

    if kind == "角色":
        if _is_char_8grid:
            if "面部標記" not in body:
                errors.append(f"A4 {tag} 角色八格拼版缺必填唯一「面部標記」")
            if "聲線錨定" not in body and "Voice Description" not in body:
                errors.append(f"A4 {tag} 角色八格拼版缺「聲線錨定」")
        else:
            if not re.search(r"全圖共\s*4\s*格", body):
                errors.append(f"A4 {tag} 角色未聲明「全圖共 4 格」——模型會做加法出成 5 格")
            if "五官 10 項鎖定" not in body and "五官10項鎖定" not in body:
                errors.append(f"A4 {tag} 角色缺「五官 10 項鎖定」（模板字段名，勿改寫）")
            if "聲紋" not in body and "波形" not in body:
                errors.append(f"A4 {tag} 角色缺圖底聲紋錨（圖底波形，非文字）")
            if "Voice Description" not in body and "音色速覽" not in body:
                errors.append(f"A4 {tag} 角色缺「≤8 詞音色速覽標籤」")
            if not re.search(r"fifth panel|extra panel|第\s*5\s*格", body, re.I):
                errors.append(f"A4 {tag} 角色負向詞缺 fifth panel / extra panel（防第 5 格）")
            if not re.search(r"different face|second face|second recognizable face|第二張臉", body, re.I):
                errors.append(f"A4 {tag} 角色負向詞缺「防第二張臉」（different face / second face）")

    if kind == "道具":
        if "道具設定圖" not in body:
            errors.append(f"A6 {tag} 道具缺「道具設定圖」標識（模板標題字段）")
        missing = [f for f in PROP_FIELDS if f not in body and f.replace(" ", "") not in body.replace(" ", "")]
        is_single_prop = any(k in body for k in ("單體靜物", "單張", "唯一一件", "唯一一柄", "單一物體"))
        if missing and not is_single_prop:
            errors.append(f"A6 {tag} 道具四格字段名不全，缺：{'、'.join(missing)}（須用模板原名）")
        if not re.search(r"禁止手持|不得手持|不出現手", body):
            errors.append(f"A6 {tag} 道具未禁手持（道具圖必須無人、無手）")

    if kind == "未知":
        message = (f"A7 {tag} 塊類型無法判定——正文含分格表述，但缺少模板標識字段"
                   "（場景寫「母版/全圖共 9 格」、角色寫「全圖共 4 格」、道具寫「道具設定圖」）")
        if re.search(r"四格|五宮格|九宮格|\d\s*×\s*\d|全圖共\s*\d+\s*格", body):
            errors.append(message)
        else:
            warns.append(message)

    return errors, warns


def self_test():
    """內置正反例（★P9 補：本腳本此前是全包唯一沒有 --self-test 的門禁腳本，
    按慣例跑 `--self-test` 會掉進「無文件名 → 打印說明」分支，看起來像"不支持"，
    實際是**根本沒實現**——自檢三件套在這裡少了一件，包級自檢也發現不了。）"""
    ok = True

    # 1) classify 四類判定順序（道具必須先於角色，否則四格道具被當角色要五官/聲紋）
    cases = [
        ("圖1 · 道具·舊懷錶（道具設定圖）", "全圖共 4 格，①正面視圖…禁止手持展示", "道具"),
        ("圖2 · 場景·堂屋（場景母版）", "16:9 無人場景母版…", "場景母版"),
        ("圖3 · 林風（角色四格立繪）", "全圖共 4 格，①面部特寫…五官…聲紋…", "角色"),
        ("圖4 · 堂屋九宮格", "全圖共 9 格，九宮格攝影機矩陣…", "九宮格"),
    ]
    for title, body, want in cases:
        got = classify(title, body)
        if got != want:
            print(f"FAIL self-test: classify「{title[:20]}」應判 {want}，實判 {got}")
            ok = False

    # 2) 跨條引用必須被抓（單條複製出去就是殘缺指令）
    _e, _w = check_block(1, "圖1 · 林風（角色四格立繪）",
                         "全圖共 4 格，同規格見圖2，①面部特寫…五官…聲紋…", "角色")
    if not any("跨條引用" in x or "同圖" in x or "見母版" in x for x in _e):
        print("FAIL self-test: 跨條引用「同規格見圖2」應報錯", _e)
        ok = False

    # 3) 角色同時寫「立繪/全身完整入畫」+「四格」→ 模型做加法出 5 格，必須攔
    _e2, _w2 = check_block(2, "圖2 · 陳梟（角色四格立繪）",
                           "全圖共 4 格，全身完整入畫，①面部特寫…五官…聲紋…", "角色")
    if not _e2:
        print("FAIL self-test: 「四格 + 全身完整入畫」應報錯（會出成 5 格）")
        ok = False

    # 4) 九宮格缺三字段 → 必須報
    _e3, _w3 = check_block(4, "圖4 · 堂屋九宮格", "全圖共 9 格，隨便畫九張", "九宮格")
    if not _e3:
        print("FAIL self-test: 九宮格缺【場景定位】等字段應報錯")
        ok = False

    print("[+] check_asset_blocks self-test", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        sys.exit(self_test())
    files = [a for a in argv if not a.startswith("-")]
    if not files:
        print(__doc__)
        sys.exit(2)
    path = files[0]
    if not os.path.exists(path):
        print(f"[-] 文件不存在：{path}")
        sys.exit(2)
    min_blocks = 3
    if "--min-blocks" in argv:
        try:
            min_blocks = int(argv[argv.index("--min-blocks") + 1])
        except (IndexError, ValueError):
            print("[-] --min-blocks 需要整數")
            sys.exit(2)
    try:
        with open(path, encoding="utf-8-sig") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[-] 讀取失敗：{exc}")
        sys.exit(2)

    blocks = split_blocks(text)
    if not blocks:
        # ★P2：零資產塊是**硬失敗**，不是提示。舊文案只有一行「[!] 未識別到…」，
        #   讀起來像"沒東西可查"而不是"該有的東西沒有"，實測被當成通過放行過。
        print("[-] FAIL: A0 零資產塊——本稿一個「圖N」資產提示詞都沒有。")
        print("    若這本來只該是投餵稿，請確認資產是否已另冊交付，並在主稿寫明「資產另冊：{文件名}」；")
        print("    若資產根本沒寫，先回 P2 補齊（角色四格立繪 / 場景母版+九宮格 / 道具四格板），再進 P3。")
        print("    塊標題形如 `## 圖1 · 場景名（場景母版）`，1~6 級標題均可。")
        sys.exit(1)

    errors, warns, stats = [], [], {}
    print(f"[i] 識別到 {len(blocks)} 個資產塊（{os.path.basename(path)}）")
    for number, title, body in blocks:
        kind = classify(title, body)
        stats[kind] = stats.get(kind, 0) + 1
        block_errors, block_warns = check_block(number, title, body, kind)
        errors.extend(block_errors)
        warns.extend(block_warns)
        state = "FAIL" if block_errors else "PASS"
        print(f"[{'x' if block_errors else '+'}] 圖{number:<3} {kind:<5} {state}  {title[:40]}")

    if len(blocks) < min_blocks:
        warns.append(f"A8 資產塊僅 {len(blocks)} 個，少於預期 {min_blocks} 個——若本冊是單場景/單角色分冊可忽略；若是全集資產冊，核對是否有漏出的資產")

    print("[i] 分類統計：" + " · ".join(f"{k}{v}" for k, v in sorted(stats.items())))
    for warning in warns:
        print("[!] WARN: " + warning)
    for error in errors:
        print("[-] FAIL: " + error)
    if "--json" in argv:
        print(json.dumps({"blocks": len(blocks), "stats": stats,
                          "errors": errors, "warnings": warns}, ensure_ascii=False, indent=2))
    print(f"[+] PASSED 資產塊 {len(blocks)} · FAIL {len(errors)} · WARN {len(warns)}"
          if not errors else f"[-] {len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
