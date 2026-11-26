#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鎖憑證機檢 (check_locks.py) · V8.2.0-SLIM-rev2

為什麼存在這個腳本（2026-11-25 用戶追責事故）：
    包規第 61/112/248 行寫明「五道前置鎖 + I 畫風鎖全部必須彈出讓用戶選」，
    但全套機檢裡沒有任何一條斷言「鎖值來自用戶」。
    audit_contract.py 的 CT1-P0A 只在契約表裡聲明、未寫實現（幽靈項），
    於是「執行者自己寫一張鎖表 → 自己宣佈 PASS」的自我認證路徑完全暢通，
    連續三次出現「按默認值代填鎖、把門停的『繼續』當鎖確認」。

本腳本的存在意義：把「鎖必須由用戶勾選」變成機器可判定的斷言。
沒有 src=user 的憑證行 = FAIL，代填在物理上過不了門。

用法：
    python check_locks.py <項目文件.md> [--multi-segment] [--self-test]
    python check_locks.py <項目文件.md> --format   # 打印台賬模板

台賬格式（寫在 00_立項包.md 或 05_項目主檔.md 內）：

    <!-- LOCK-LEDGER:BEGIN -->
    [LOCK] name=A | value=2.5 | src=user | ev=卡片勾選「① Seedance 2.5」 | ts=2026-11-25T14:20
    <!-- LOCK-LEDGER:END -->

必需項：〇·1 素材來源 / A 模型 / B 畫幅 / C 交付 / 板式 / I 畫風
    D 段縫：多段任務（--multi-segment）必填；單段任務可省

判定項：
    L1 台賬塊在位（含 BEGIN/END 標記）
    L2 六項必需鎖齊全（多段任務加 D 共七項）
    L3 每項 src=user —— 出現 default/agent/infer/preset 即 FAIL（這就是「代填」）
    L4 ev 為用戶憑證（含「」/""/勾選/用戶回 之一），且不含 默認/代填/推斷/假設/推測
    L5 ts 為 YYYY-MM-DD 或 ISO 時間
    L6 值域合法（A ∈ 2.5/2.0；B ∈ 16:9/9:16/21:9；板式 四格/八格 二選一）
    L7 無重複鎖項（同一鎖寫兩行 = 後寫覆蓋前寫，屬靜默改鎖）
"""
import os
import re
import sys
import tempfile

REQUIRED = [
    ("〇·1", ("〇·1", "〇1", "素材來源")),
    ("A", ("A", "A 模型", "模型版本")),
    ("B", ("B", "B 畫幅", "畫幅")),
    ("C", ("C", "C 交付", "交付形態")),
    ("板式", ("板式", "角色資產板式")),
    ("場景方案", ("場景方案", "場景站位方案", "場景站位", "場景")),
    ("I", ("I", "I 畫風", "畫風鎖")),
]
REQUIRED_MULTI = ("D", ("D", "D 段縫", "段縫銜接"))

BAD_SRC = ("default", "agent", "infer", "inferred", "preset", "auto", "assume")
# 只禁「以默認/推斷充當憑證」的強信號詞。不能把「默認」「代填」二字一律禁掉：
#   · 包規 Step4 的合法選項原文就叫「不疊加（默認）」；
#   · 彈卡 label 歷史上寫過「（當前代填值）」，照抄勾選項屬合法憑證。
# 真正的判據是「有沒有用戶證據」= EVIDENCE_MARKS，兩者同時滿足才算過。
FORBIDDEN_EV = ("按默認走", "默認值走", "按默認執行", "自行判定", "未問用戶", "未彈卡", "推斷得出", "假設", "推測")
EVIDENCE_MARKS = ("「", "」", "\"", "勾選", "用戶回", "用戶原話", "用戶指定", "用戶確認")

BEGIN_MARK = "<!-- LOCK-LEDGER:BEGIN -->"
END_MARK = "<!-- LOCK-LEDGER:END -->"

TEMPLATE = """<!-- LOCK-LEDGER:BEGIN -->
[LOCK] name=〇·1 | value=③對標爆款 | src=user | ev=用戶原話「（原句照抄）」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=A | value=2.5 | src=user | ev=卡片勾選「① Seedance 2.5」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=B | value=16:9 | src=user | ev=卡片勾選「① 16:9 橫屏」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=C | value=①離線看板 | src=user | ev=卡片勾選「① 離線看板」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=D | value=②換機位硬切 | src=user | ev=卡片勾選「② 換機位硬切」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=板式 | value=①16:9 四格純圖板 | src=user | ev=卡片勾選「① 16:9 四格純圖板」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=場景方案 | value=①雙圖方案C+（模板圖+白模圖） | src=user | ev=卡片勾選「① 雙圖方案 C+」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=I | value=真人實拍+諾蘭向·T7 | src=user | ev=卡片勾選「C 諾蘭向」+Step4「不疊加」 | ts=YYYY-MM-DDTHH:MM
<!-- LOCK-LEDGER:END -->"""


def _parse_rows(block):
    """解析台賬塊內的 [LOCK] 行 → [{name, value, src, ev, ts}, ...]"""
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("[LOCK]"):
            continue
        body = line[len("[LOCK]"):]
        row = {}
        for part in body.split("|"):
            part = part.strip()
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            row[k.strip().lower()] = v.strip()
        if row:
            rows.append(row)
    return rows


def _match_name(row_name, aliases):
    n = (row_name or "").strip()
    for a in aliases:
        if n == a:
            return True
    for a in aliases:
        if a and a in n and len(a) >= 2:
            return True
    # A / B / C / D / I 這類單字母鎖：只允許完全相等，避免子串誤命中
    return False


def audit_text(text, multi_segment=False):
    """返回 (passed:list[str], fails:list[str], warns:list[str])"""
    passed, fails, warns = [], [], []

    # L1 台賬塊
    if BEGIN_MARK not in text or END_MARK not in text:
        fails.append(
            "L1 缺失鎖台賬塊（須在 00_立項包 / 05_項目主檔 內寫 %s … %s）——" % (BEGIN_MARK, END_MARK)
            + "無台賬 = 無法證明鎖值來自用戶 = 視為代填"
        )
        return passed, fails, warns
    start = text.index(BEGIN_MARK) + len(BEGIN_MARK)
    end = text.index(END_MARK)
    block = text[start:end]
    rows = _parse_rows(block)
    if not rows:
        fails.append("L1 台賬塊為空（BEGIN/END 之間沒有任何 [LOCK] 行）")
        return passed, fails, warns

    # L7 重複鎖項
    seen = {}
    for r in rows:
        nm = (r.get("name") or "").strip()
        if nm in seen:
            fails.append("L7 鎖項重複：`%s` 出現兩次以上（後寫覆蓋前寫 = 靜默改鎖）" % nm)
        seen[nm] = seen.get(nm, 0) + 1

    need = list(REQUIRED) + ([REQUIRED_MULTI] if multi_segment else [])
    for canonical, aliases in need:
        hit = None
        for r in rows:
            if _match_name(r.get("name"), aliases):
                hit = r
                break
        if hit is None:
            tip = "（多段任務必填）" if canonical == "D" else ""
            fails.append("L2 缺失鎖項 `%s`%s：台賬裡沒有這一行" % (canonical, tip))
            continue

        src = (hit.get("src") or "").strip().lower()
        ev = (hit.get("ev") or "").strip()
        ts = (hit.get("ts") or "").strip()
        val = (hit.get("value") or "").strip()

        # L3 來源
        if src != "user":
            if any(b in src for b in BAD_SRC) or src == "":
                fails.append(
                    "L3 `%s` 來源不是用戶（src=%s）——這就是「代填」。"
                    "鎖值只能來自用戶勾選或用戶原話，禁止 default/agent/infer/preset" % (canonical, src or "空")
                )
            else:
                fails.append("L3 `%s` 來源非法（src=%s），唯一合法值 = user" % (canonical, src))
        else:
            passed.append("L3 `%s` src=user" % canonical)

        # L4 憑證
        if not ev:
            fails.append("L4 `%s` 缺用戶憑證 ev（須照抄用戶勾選/原話）" % canonical)
        else:
            bad = [t for t in FORBIDDEN_EV if t in ev]
            if bad:
                fails.append("L4 `%s` 憑證含代填詞 %s（ev=%s）——憑證必須是用戶原話或勾選項原文" % (canonical, bad, ev))
            elif not any(m in ev for m in EVIDENCE_MARKS):
                fails.append("L4 `%s` 憑證不像用戶證據（ev=%s）：須含「」/\"\"/勾選/用戶回 之一" % (canonical, ev))
            else:
                passed.append("L4 `%s` 憑證在位" % canonical)

        # L5 時間戳
        if not re.search(r"\d{4}-\d{2}-\d{2}", ts):
            fails.append("L5 `%s` 缺時間戳 ts（YYYY-MM-DD 或 ISO）" % canonical)

        # L6 值域（A/B 兼容帶選項前綴或型號全名寫法，但嚴禁同時出現兩個值）
        if canonical == "A":
            a_hits = re.findall(r"(?<!\d)(2\.5|2\.0)(?!\d)", val)
            if len(set(a_hits)) != 1:
                fails.append("L6 `A` 值非法（value=%s）：只允許唯一指定 2.5 或 2.0" % val)
        elif canonical == "B":
            b_hits = re.findall(r"(16:9|9:16|21:9)", val)
            if len(set(b_hits)) != 1:
                fails.append("L6 `B` 值非法（value=%s）：只允許唯一指定 16:9 / 9:16 / 21:9" % val)
        elif canonical == "板式":
            quad = "四格" in val
            octa = "八格" in val
            if quad == octa:
                fails.append("L6 `板式` 值非法（value=%s）：四格/八格必須二選一（互斥鐵律）" % val)
        elif canonical == "場景方案":
            has_c2 = any(k in val for k in ("二合一", "C++", "c++", "單張實景"))
            has_c1 = any(k in val for k in ("雙圖", "C+", "c+", "模板圖", "白模", "五視圖")) and not any(k in val for k in ("C++", "c++"))
            both = has_c2 and any(k in val for k in ("雙圖", "模板圖"))
            if both or (not has_c1 and not has_c2):
                fails.append("L6 `場景方案` 值非法（value=%s）：①雙圖方案C+ / ②二合一方案C++ 必須二選一（互斥鐵律）" % val)
        elif canonical == "C":
            if not any(k in val for k in ("看板", "md", "MD", "兩者")):
                fails.append("L6 `C` 值非法（value=%s）：須含 看板/md/兩者" % val)
        elif canonical == "D":
            if not re.search(r"[①②③④]", val) and not any(k in val for k in ("定格", "硬切", "空鏡", "轉場")):
                fails.append("L6 `D` 值非法（value=%s）：須為四選項之一" % val)
        elif canonical == "I":
            if not val:
                fails.append("L6 `I` 值為空：須寫 影像基底 + 導演卡")
            elif not re.search(r"真人|3D|2D", val):
                warns.append("L6 `I` 未寫影像基底（真人/3D/2D）——I 鎖 Step1 必確認，建議補全")

    if not fails:
        passed.append("鎖台賬機檢通過（%d 項鎖 · 全部 src=user）" % len(need))
    return passed, fails, warns


def _self_test():
    filled = TEMPLATE.replace("YYYY-MM-DDTHH:MM", "2026-11-25T14:20")
    ok_text = "前文\n" + filled + "\n後文"
    bad_text = "前文\n" + filled.replace("src=user", "src=default", 1) + "\n後文"
    no_block = "# 立項包\n| 鎖 | 值 |\n|---|---|\n| A 模型 | Seedance 2.5（默認） |"

    p1, f1, _ = audit_text(ok_text, multi_segment=True)
    p2, f2, _ = audit_text(bad_text, multi_segment=True)
    p3, f3, _ = audit_text(no_block, multi_segment=True)

    checks = [
        ("正常台賬應 PASS", not f1),
        ("src=default 應 FAIL", bool(f2) and any("L3" in x for x in f2)),
        ("無台賬塊應 FAIL", bool(f3) and any("L1" in x for x in f3)),
    ]
    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("[+] " if ok else "[-] ") + name)
    if f2:
        print("    └ 捕獲：" + f2[0][:110])
    return 0 if not bad else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--format" in flags:
        print(TEMPLATE)
        return 0
    if "--self-test" in flags:
        return _self_test()
    if not args:
        print("[!] 用法：python check_locks.py <項目文件.md> [--multi-segment] [--self-test]")
        return 2

    path = args[0]
    if not os.path.exists(path):
        print("[!] 文件不存在：%s" % path)
        return 2
    text = open(path, encoding="utf-8").read()
    passed, fails, warns = audit_text(text, multi_segment="--multi-segment" in flags)

    for p in passed:
        print("[+] " + p)
    for w in warns:
        print("[~] " + w)
    for f in fails:
        print("[-] " + f)

    print("\n=== 鎖憑證機檢：%s ===" % os.path.basename(path))
    print("PASS %d · WARN %d · FAIL %d" % (len(passed), len(warns), len(fails)))
    if fails:
        print("[-] FAILED —— 鎖未取得用戶憑證，禁止進入 P1（寫劇本）及之後任何階段")
        return 1
    print("[+] PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
