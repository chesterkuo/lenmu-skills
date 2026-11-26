#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_p45.py — P4.5 預演故事板結構機檢（交付門禁）

背景（2026-10-20 粉絲反饋）：
  P4.5 附件此前明確「不參與機檢」，交付時少段、少格、六問缺失、
  術語混入、甚至寫「同上」都能過——內容不對也沒人攔。
  本腳本把 P4.5 的結構做成可機械判定的門禁：**附件寫完必須跑，FAIL 清零才交付**。

用法：
  python sd-storyboard-engine/scripts/check_p45.py <預演故事板.md>
      [--segments N]   期望段數（從投餵稿/項目段數傳入）；不傳則只做內部一致性
      [--m2]           已入庫形態，允許「已核驗 / 看圖」類表述
      [--json]
      [--self-test]

規則碼：
  P450 文件命名（須以 -預演故事板.md 結尾）                        WARN
  P451 段結構：缺「本段要驗什麼 / 風險提示 / 故事板提示詞 / 看圖先看這三點」  ERROR
  P452 格數：聲明（N 格）與實際「第 k 格」數量/編號不一致              ERROR
  P453 六問：每格缺項（誰在哪/朝哪/看哪/做什麼/鏡頭在哪/光從哪來）      ERROR(缺≥2) / WARN(缺1)
  P454 術語汙染：九宮格/CLEAN_GRID/SHOT_TEXT/action_phase/D鎖/R1~R3/圖STB/七段式  ERROR
  P455 佔位與跨格引用：同上/見上/略/TBD/待補                        ERROR
  P456 圖片聲明：M0/M1 卻寫「已核驗/已看圖/圖面一致」                  ERROR
  P457 段覆蓋：--segments N 時缺段且未列 ⛔ 豁免範圍                  ERROR
  P458 交付清單行：缺 `預演故事板：段n~段m ✅ / ⛔未附（理由）`          WARN

退出碼：0 = PASS（允許 WARN）· 1 = 有 ERROR · 2 = 用法/讀取錯誤
"""

import json
import os
import re
import sys

SEG_RE = re.compile(r"^#{1,6}\s*\**\s*段\s*(\d+)", re.M)
PANEL_RE = re.compile(r"第\s*(\d+)\s*格\s*[：:]\s*(.*)")
GRID_DECL_RE = re.compile(r"故事板提示詞[^\n]*?[（(]\s*(\d+)\s*格\s*[）)]")

TERMS = ["九宮格", "CLEAN_GRID", "SHOT_TEXT", "action_phase", "D鎖", "D 鎖",
         "R1", "R2", "R3", "圖STB", "七段式", "投餵稿"]
PLACEHOLDERS = ["同上", "見上", "省略", "略過", "TBD", "待補", "此處略"]

SIX = {
    "誰在哪": ["在", "站", "坐", "靠", "蹲", "躺", "位於", "門口", "窗邊", "桌", "床邊", "角落", "中央"],
    "朝哪": ["朝", "面向", "背對", "側對", "轉身", "正對", "側身"],
    "看哪": ["看", "望", "盯", "視線", "目光", "注視", "抬眼"],
    "做什麼": ["走", "跑", "推", "拉", "抓", "握", "抬", "低", "伸", "轉", "拿", "放", "撞", "擋",
              "衝", "退", "停", "抱", "扶", "開", "關", "遞", "接", "笑", "哭", "皺眉", "咬牙",
              "揮手", "回頭", "俯身", "俯下", "起身"],
    "鏡頭在哪": ["鏡頭", "機位", "視平線", "俯拍", "仰拍", "俯視", "平視", "近景", "中景", "特寫",
               "全景", "遠景", "過肩", "正拍", "側拍"],
    "光從哪來": ["光", "光源", "燈", "月光", "日光", "窗光", "逆光", "側光", "頂光", "底光",
               "光從", "受光", "背光", "照亮"],
}


# ★P3 新增：格內鏡號標註 `〔鏡N 景別〕`，多鏡合寫 `〔鏡N+M 景別〕`
PANEL_SHOT_RE = re.compile(r'〔鏡\s*(\d+)(?:\s*[+＋]\s*(\d+))?\s*([^〕]*?)〕')
FEED_BLOCK_RE = re.compile(r'```text\n(.*?)```', re.S)
FEED_SHOT_RE = re.compile(r'- \d\d:\d\d-\d\d:\d\d \[鏡頭\s*(\d+)\] ([^・·]+)[・·]')


def parse_feed(text):
    """投餵稿 -> {段號: {鏡號: 景別}}（按 ```text 塊順序對段號）。"""
    out = {}
    for i, block in enumerate(FEED_BLOCK_RE.findall(text or ''), 1):
        d = {}
        for ln in block.split('\n'):
            m = FEED_SHOT_RE.match(ln.strip())
            if m:
                d[int(m.group(1))] = m.group(2).strip()
        out[i] = d
    return out


def split_segments(text):
    """按 `## 段 N` 切段，返回 [(段號, 標題行, 正文)]。"""
    matches = list(SEG_RE.finditer(text))
    out = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        heading = body.splitlines()[0] if body.splitlines() else ""
        out.append((int(match.group(1)), heading, body))
    return out


def prompt_block(segment_body):
    """取「故事板提示詞」標題到下一個標題之間的正文。"""
    idx = segment_body.find("故事板提示詞")
    if idx < 0:
        return ""
    rest = segment_body[idx:]
    m = re.search(r"\n#{1,6}\s", rest[len("故事板提示詞"):])
    if not m:
        return rest
    cut = len("故事板提示詞") + m.start() + 1
    return rest[:cut]


def check_text(text, path="", expected_segments=None, m2=False, feed_text=None):
    errors, warns, stats = [], [], {}

    if path and not os.path.basename(path).endswith("-預演故事板.md"):
        warns.append("P450 文件名未以 `-預演故事板.md` 結尾")

    segments = split_segments(text)
    stats["segments"] = len(segments)
    if not segments:
        errors.append("P451 未識別到任何 `## 段 N` 段——附件為空或標題格式不對")
        return errors, warns, stats

    for num, _heading, body in segments:
        tag = f"段{num}"
        for label in ["本段要驗什麼", "風險提示", "故事板提示詞"]:
            if label not in body:
                errors.append(f"P451 {tag} 缺「{label}」")
        if not (("看圖" in body and "三點" in body) or "看圖時先看這三點" in body):
            errors.append(f"P451 {tag} 缺「看圖先看這三點」")

        decl = GRID_DECL_RE.search(body)
        if not decl:
            errors.append(f"P452 {tag} 缺格數聲明「故事板提示詞（N 格）」")
            declared = None
        else:
            declared = int(decl.group(1))

        panels = PANEL_RE.findall(body)
        stats[f"段{num}_格"] = len(panels)
        if not panels:
            errors.append(f"P452 {tag} 未識別到「第 k 格：」提示詞")
        else:
            nums = sorted(int(n) for n, _ in panels)
            if declared is not None and len(panels) != declared:
                errors.append(f"P452 {tag} 聲明 {declared} 格，實際 {len(panels)} 格")
            if nums != list(range(1, len(nums) + 1)):
                errors.append(f"P452 {tag} 格號不連續/重複：{nums}")

        # ★P3 新增 P459：每格必須標投餵稿鏡號——治「故事板與投餵稿各寫各的」。
        #   病根：文戲故事板舊口徑上限 4 格，而文戲段常是 6 鏡，6 塞不進 4，
        #   又沒有"格↔鏡"映射契約 → 故事板的景別、主體、過肩方向和投餵稿全部對不上。
        for n, panel in panels:
            if not PANEL_SHOT_RE.search(panel):
                errors.append(
                    f"P459 {tag} 第{n}格未標投餵稿鏡號——須寫成「第{n}格：〔鏡N 景別〕…」，"
                    "N 就是投餵稿該段的鏡頭號；一格合併多鏡時寫〔鏡N+M 景別〕。"
                    "（沒有鏡號就無法核對，故事板會變成另一部片）")

        for n, panel in panels:
            # ★P6.3 空鏡格豁免：寫明「空鏡 / 無人物 / 一個人都沒有」的格不要求人相關四問
            #   （誰在哪 / 朝哪 / 看哪 / 做什麼），只查「鏡頭在哪 / 光從哪來」——
            #   否則每個空鏡過渡格都會被判缺兩問（用戶 2026-10-23 實測：段2 起手空鏡被誤報）。
            _empty_shot = any(w in panel for w in ("空鏡", "無人物", "一個人都沒有", "人物不入畫"))
            _need = {k: v for k, v in SIX.items()
                     if not (_empty_shot and k in ("誰在哪", "朝哪", "看哪", "做什麼"))}
            missing = [key for key, words in _need.items() if not any(w in panel for w in words)]
            if len(missing) >= 2:
                errors.append(f"P453 {tag} 第{n}格缺六問：{'、'.join(missing)}")
            elif missing:
                warns.append(f"P453 {tag} 第{n}格疑似缺：{missing[0]}")

        block = prompt_block(body)
        for term in TERMS:
            if term in block:
                errors.append(f"P454 {tag} 故事板提示詞出現本包術語「{term}」")
        for word in PLACEHOLDERS:
            if word in block:
                errors.append(f"P455 {tag} 故事板提示詞出現佔位/跨格引用「{word}」")

    if expected_segments:
        present = {n for n, _, _ in segments}
        missing = [n for n in range(1, expected_segments + 1) if n not in present]
        if missing:
            if "⛔" in text and ("未附" in text or "豁免" in text):
                warns.append(f"P457 缺段 {missing}，但存在 ⛔ 豁免說明（請核對範圍）")
            else:
                errors.append(f"P457 缺段 {missing}（期望 1~{expected_segments}）且無 ⛔ 豁免說明")

    if not m2:
        for claim in ["已核驗", "已看圖", "圖面一致", "確認過圖", "已核對圖面"]:
            if claim in text:
                errors.append(f"P456 非 M2 卻寫「{claim}」——M0/M1 不得聲稱看過圖")

    if "預演故事板" not in text:
        warns.append("P458 缺交付清單行「預演故事板：段n~段m ✅ / ⛔未附（理由）」")

    # ★P3 新增 P45A：傳了 --feed 就逐格核對景別與覆蓋（"故事板 = 投餵稿的畫面版"這道門）
    if feed_text:
        fmap = parse_feed(feed_text)
        for num, heading, body in segments:
            blk = prompt_block(body)
            tag = f"[段{num}]"
            covered = set()
            for n, panel in PANEL_RE.findall(blk):
                m = PANEL_SHOT_RE.search(panel)
                if not m:
                    continue
                shot = int(m.group(1))
                also = int(m.group(2)) if m.group(2) else None
                size = m.group(3).strip()
                covered.add(shot)
                if also:
                    covered.add(also)
                fed = fmap.get(num, {})
                if shot not in fed:
                    errors.append(f"P45A {tag} 第{n}格標了「鏡{shot}」，但投餵稿該段只有 "
                                  f"{sorted(fed) or '無'} 號鏡——鏡號對不上")
                    continue
                fsize = fed[shot]
                if size and size != fsize:
                    errors.append(
                        f"P45A {tag} 第{n}格寫「{size}」，而投餵稿鏡{shot}是「{fsize}」——"
                        "景別必須一致（故事板是投餵稿的畫面版，不是另一套分鏡）")
            n_panels = len(PANEL_RE.findall(blk))
            n_shots = len(fmap.get(num, {}))
            if n_shots and n_panels > n_shots:
                warns.append(f"P45B {tag} 故事板 {n_panels} 格 > 投餵稿 {n_shots} 鏡——"
                             "多出來的格沒有對應鏡（格數應等於鏡數；要加內容請先改投餵稿）")
            miss = sorted(set(fmap.get(num, {})) - covered)
            if miss:
                warns.append(f"P45A {tag} 投餵稿鏡 {miss} 沒有對應格——"
                             "要麼補格，要麼在某一格用〔鏡N+M〕合併標明")

    return errors, warns, stats


def run_self_test():
    good = """# 測試 · 預演故事板

## 段 1 · 雨夜門口，她堵住要走的他
**本段要驗什麼**：雙主體 · 站位不越軸
**風險提示**：兩人容易互換左右

### 故事板提示詞（3 格）
畫一張分鏡故事板，3 格，橫向排列，9:16，寫實電影感，畫面中沒有任何文字、數字、水印或邊框標註。
統一人物設定：阿嵐：28歲，短髮，黑色風衣，瘦高。陳默：30歲，寸頭，灰色夾克，中等身材。
場景：老樓門口，門內暖黃燈，門外冷藍雨夜。
第 1 格：〔鏡1 中景〕阿嵐站在門框內側，面朝陳默，目光盯著他的臉，右手抬起來擋在門把前，鏡頭在兩人側面平視中景，門內暖黃燈光從她背後照過來。
第 2 格：〔鏡2 中近景〕陳默站在門外台階下，身體朝門口，視線落在她擋門的手上，肩膀微微後撤，鏡頭在台階側前方仰拍中近景，冷藍路燈光從右上方打下來。
第 3 格：〔鏡3 近景〕阿嵐向前半步，正對陳默，抬眼看他，手仍按在門把上，鏡頭在門內側過肩近景，暖光從她左側漫過來。

### 看圖時先看這三點
1. 兩人是否始終一左一右，沒互換
2. 門內暖光、門外冷光是否分得清
3. 手是否一直擋在門把前
"""
    e, w, s = check_text(good, "測試-預演故事板.md")
    assert not e, e

    bad1 = good.replace("**風險提示**：兩人容易互換左右\n", "")
    e, _, _ = check_text(bad1, "測試-預演故事板.md")
    assert any("P451" in x for x in e), e

    bad2 = good.replace("### 故事板提示詞（3 格）", "### 故事板提示詞（4 格）")
    e, _, _ = check_text(bad2, "測試-預演故事板.md")
    assert any("P452" in x for x in e), e

    bad3 = good.replace("手仍按在門把上", "同上")
    e, _, _ = check_text(bad3, "測試-預演故事板.md")
    assert any("P455" in x for x in e), e

    bad4 = good.replace("門內暖黃燈光從她背後照過來", "九宮格佈局")
    e, _, _ = check_text(bad4, "測試-預演故事板.md")
    assert any("P454" in x for x in e), e

    bad5 = good + "\n已核驗，與資產圖一致。\n"
    e, _, _ = check_text(bad5, "測試-預演故事板.md")
    assert any("P456" in x for x in e), e

    # 空鏡格豁免（P6.3）：寫明「空鏡/無人物入畫」的格不要求人相關四問
    empty = good.replace(
        "第 1 格：〔鏡1 中景〕阿嵐站在門框內側，面朝陳默，目光盯著他的臉，右手抬起來擋在門把前，鏡頭在兩人側面平視中景，門內暖黃燈光從她背後照過來。",
        "第 1 格：〔鏡1 遠景〕空鏡，無人物入畫——只拍老樓門口的台階與門框，鏡頭在門外平視遠景，門內暖黃燈光從門縫裡漏出來。")
    e, _, _ = check_text(empty, "測試-預演故事板.md")
    assert not any("P453" in x for x in e), e
    e, _, _ = check_text(good, "測試-預演故事板.md", expected_segments=2)
    assert any("P457" in x for x in e), e

    print("[+] self-test PASSED (7 cases)")


def main(argv):
    if "--self-test" in argv:
        run_self_test()
        return 0

    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    path = args[0]

    feed_text = None
    if "--feed" in argv:
        i = argv.index("--feed")
        if i + 1 < len(argv):
            try:
                with open(argv[i + 1], encoding="utf-8-sig") as fh:
                    feed_text = fh.read()
            except (OSError, UnicodeDecodeError) as exc:
                print(f"[-] --feed 讀取失敗：{exc}")
                return 2

    expected = None
    if "--segments" in argv:
        i = argv.index("--segments")
        if i + 1 < len(argv):
            expected = int(argv[i + 1])

    try:
        with open(path, encoding="utf-8-sig") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[-] 讀取失敗：{exc}")
        return 2

    errors, warns, stats = check_text(text, path, expected, "--m2" in argv, feed_text)
    print(f"[i] {os.path.basename(path)} · 段 {stats.get('segments', 0)}")
    for warning in warns:
        print("[!] WARN: " + warning)
    for error in errors:
        print("[-] FAIL: " + error)
    if "--json" in argv:
        print(json.dumps({"stats": stats, "errors": errors, "warnings": warns},
                         ensure_ascii=False, indent=2))
    print(f"[+] PASSED P4.5 · FAIL {len(errors)} · WARN {len(warns)}"
          if not errors else f"[-] {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
