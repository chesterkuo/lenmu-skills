# -*- coding: utf-8 -*-
"""build_board_lite.py — 輕量離線分鏡看板編譯器（輕量版 · 簡化自 7.3.0 模塊 K）

用法:
    python scripts/build_board_lite.py <項目.md> [--out <看板.html>]

產出:
    單文件離線 HTML 看板（CSS/JS 全內嵌，雙擊瀏覽器即開，零依賴/零數據庫/零端口）

看板區塊（與 6.8.3 同構，砍掉 N1~N11 檢查層 / validate 依賴 / json 快照）:
    創作藍圖層: Ⅰ 創作基準(P0A) · Ⅱ 劇本層(P1) · Ⅲ 視聽聖經(P1)
    分鏡生產層: ① 時間軸泳道 · ② 鏡頭卡矩陣(拆解) · ③ 投餵提示詞原文(成品)
                ④ 資產總表(P2) · ⑤ 資產出圖提示詞(P2.5·與③必同板) · ⑥ 發佈文案(P6·可選)

輸入 md 最小契約:
    # 項目標題
    【畫幅】：16:9        【模型版本】：2.5        ← A/B 雙鎖回顯
    ## P0A · 創作基準     ← 可選表格: 項 | 內容
    ## P1 · 劇本          ← 可選，正文照錄
    ## P1 · 視聽聖經      ← 可選表格或正文
    ## P2 · 資產清單      ← 表格: 編碼 | 名字 | 視圖 | @圖片N
    ## P2.5 · 資產出圖提示詞
    ### CHR-001 · 林越 · 主角 4 View 資產板
    ```text 出圖提示詞 ```
    ## P4 · 投餵提示詞    ← 分鏡提示詞（與 ⑤ 必同板呈現）
    ### 段1
    【核心人物】：…        ← 段級欄（可選，顯示為標籤）
    ```text 投餵提示詞 ```
    [0-3秒] 鏡頭內容      ← 逐鏡拆解行
    ## P6 · 發佈文案      ← 可選: 【標題】【封面文案】【正文】【話題標籤】

輕量鐵律（簡化自 6.8.3 K1~K7，只留 4 條）:
    K-lite-1  md 是唯一真相，看板只讀不回寫；改稿改 md 後重編譯
    K-lite-2  缺字段降級不中斷：缺什麼顯示"未解析到"並記 WARN，看板永遠出得來
    K-lite-3  拆解視圖與原文並存：逐鏡表/鏡頭卡用於定位問題，圍欄原文可整段複製投餵
    K-lite-4  ⑤ 資產出圖提示詞與 ③ 分鏡投餵提示詞必須同板呈現（缺 P2.5 → WARN）
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 兼容三種鏡行寫法：本包原生 `00:00-00:05 [鏡頭1] …` / `[00:00-00:05] …` / `[0-3秒] …`
TS_RE = re.compile(
    r"^\s*(?:[\[【]?\s*鏡頭\s*\d+\s*[\]】]?\s*[,，]?\s*)?"
    r"\[?\s*(\d{1,2}(?::\d{2})?(?:\.\d+)?)\s*s?\s*[-~～—→]\s*"
    r"(\d{1,2}(?::\d{2})?(?:\.\d+)?)\s*(?:秒|s)?\s*\]?\s*[,，]?\s*(.*)$", re.I)
SHOT_NO_RE = re.compile(r"^[\[【]?\s*鏡頭\s*\d+\s*[\]】]?\s*[,，]?\s*")


def shot_text(s: str) -> str:
    """鏡行文本：剝掉 `[鏡頭N] ` 前綴，卡片上只留景別·運鏡·動作。"""
    return SHOT_NO_RE.sub("", (s or "").strip())
FENCE_RE = re.compile(r"```(?:text|prompt)?\s*\n(.*?)```", re.S)
FIELD_RE = re.compile(r"^【([^】]{2,8})】\s*[:：]\s*(.+)$")


def to_seconds(tok: str) -> float:
    """時碼 → 秒。兼容 MM:SS / MM:SS.s / MM:SS.ss 與純秒。

    ⚠️ 秒位必須 float()（2026-10-14 Agent 修復）：
    原實現寫 `int(s)`，遇半秒時碼 `00:10.5` 直接拋 ValueError，
    該鏡行隨即被調用點的 `except ValueError: continue` **靜默跳過**——
    實測《鹽梟劫-60s測試局》源稿 17 鏡只解析出 10 鏡（丟 7 鏡 / 41%），
    看板與 SRT·CSV·JSON 三導出的全片時間軸隨之出現 7 秒空洞，而 CLI 零告警。
    本包真實產物普遍使用半秒粒度（`00:10.5` / `00:03.5`），故此處必須收 float。
    """
    tok = tok.strip().replace("：", ":")
    if ":" in tok:
        m, s = tok.split(":", 1)
        return int(m) * 60 + float(s)
    return float(tok)


def table_rows(lines):
    rows = []
    for l in lines:
        if l.startswith("|") and "---" not in l:
            cells = [c.strip() for c in l.strip("|").split("|")]
            if cells and cells[0]:
                rows.append(cells)
    return rows


# ── 寬容章節識別：不要求 md 照抄「## P2 · 資產清單」這類標題，按關鍵詞歸區 ──
def zone_of(title: str) -> str:
    t = title or ""
    if re.search(r"發佈文案|P6", t) and not re.search(r"投餵", t):
        return "publish"
    if re.search(r"出圖提示詞|P2\.5|P2c|資產出圖", t):
        return "ap"
    if re.search(r"投餵提示詞|P4|分鏡提示詞", t):
        return "seg"
    if re.search(r"視聽聖經|風格聖經", t):
        return "bible"
    if re.search(r"劇本|故事|梗概", t):
        return "script"
    if re.search(r"資產清單|資產表|P2", t):
        return "assets"
    if re.search(r"創作基準|P0A", t):
        return "p0a"
    return ""


# 資產表頭別名 → 標準字段（兼容「類 | 編碼 | 類型 | 出圖 | 複用單元」這類自定義列序）
HEAD_ALIAS = {
    "code": ["編碼", "code", "資產編碼", "id", "資產id"],
    "name": ["名字", "名稱", "角色", "人物", "資產", "name", "資產名"],
    "view": ["視圖", "出圖", "出圖類型", "規格", "類型", "view"],
    "img":  ["@圖片n", "圖號", "圖片", "參考圖", "img", "綁定圖"],
}


def map_head(cells):
    """表頭行 → {標準字段: 列索引}；返回 None 表示不像表頭，退回按位置取。
    按「標準字段 × 別名優先級」掃描（而非按列順序），保證"出圖"優先於"類型"命中 view。"""
    norm = [re.sub(r"[\s*`_@]", "", c).lower() for c in cells]
    idx = {}
    for std, aliases in HEAD_ALIAS.items():
        for a in aliases:
            an = re.sub(r"[\s*`_@]", "", a).lower()
            if an in norm:
                idx[std] = norm.index(an)
                break
    return idx or None


def clean_code(s: str) -> str:
    """子標題裡的資產編碼清洗：`1. `@CHR-沈硯`` → `@CHR-沈硯`"""
    s = (s or "").strip()
    s = re.sub(r"^\d+[.、)]\s*", "", s)     # 去前導序號
    s = s.replace("`", "").strip()
    return s


def parse_md(md_text: str) -> dict:
    lines = md_text.splitlines()
    data = {"title": "分鏡看板",
            "meta": {"畫幅": "未鎖定", "模型版本": "未鎖定"},
            "p0a": [], "script": [], "bible": [],
            "assets": [], "asset_prompts": [], "publish": [],
            "segments": [], "warnings": [], "_head": None, "extras": []}

    section = ""          # 當前 ## 章節
    seg = None            # 當前段
    ap = None             # 當前資產出圖條目
    sub_head = ""         # 當前 ### 子標題
    in_fence = False
    plain = []            # 當前章節的普通正文行

    def _extra_block(title, block):
        """未歸區章節的內容塊（K-lite-6：md 裡寫的每一樣東西都必須出現在看板上）。"""
        if not data["extras"] or data["extras"][-1]["title"] != title:
            data["extras"].append({"title": title, "body": []})
        data["extras"][-1]["body"].append(block)

    pending_tbl = []      # 劇本區/未歸區的待歸組表格行（按 markdown 分隔行切成多張表）

    def _push_tbl(rows, z):
        block = {"t": "tbl", "rows": rows}
        if z == "script":
            data["script"].append(block)
        else:
            _extra_block(section, block)

    def flush_tbl():
        nonlocal pending_tbl
        if pending_tbl:
            rows, pending_tbl = pending_tbl, []
            _push_tbl(rows, zone_of(section) if section else "")

    def flush_plain():
        nonlocal plain
        if not plain:
            return
        text = "\n".join(plain).strip()
        plain = []
        if not text:
            return
        z = zone_of(section) if section else ""
        if not section:
            _extra_block("（卷首說明）", {"t": "p", "v": text})
        elif "劇本" in section or z == "script":
            data["script"].append({"t": "p", "v": text})
        elif z == "bible":
            data["bible"].append(text)
        elif "P0A" in section or z == "p0a" or "創作基準" in section:
            data["p0a"].append({"k": section, "v": text})
        elif z == "":
            _extra_block(section, {"t": "p", "v": text})

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()

        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if ap is not None:
                ap.setdefault("fence_body", []).append(line)
            elif seg is not None:
                seg.setdefault("fence_body", []).append(line)
            continue

        if pending_tbl and not (s.startswith("|") and section):
            flush_tbl()          # 表格被正文/標題/圍欄打斷 → 先落表，保原文順序

        if s.startswith("# ") and data["title"] == "分鏡看板":
            flush_plain()
            data["title"] = s[2:].strip()
            continue

        m_sec = re.match(r"^##\s+(.+)$", s)
        if m_sec:
            flush_plain()
            section = m_sec.group(1).strip()
            seg, ap, sub_head = None, None, ""
            data["_head"] = None            # 表頭映射不跨章節
            if re.match(r"^【?投餵單元", section) or re.match(r"^段\s*\d", section):
                seg = {"no": len(data["segments"]) + 1, "name": section,
                       "raw": "", "shots": [], "fields": {}, "warnings": []}
                data["segments"].append(seg)
                continue
            if zone_of(section) == "":
                data["extras"].append({"title": section, "body": []})
            continue

        m_sub = re.match(r"^#{3,4}\s+(.+)$", s)
        if m_sub:
            flush_plain()
            sub_head = m_sub.group(1).strip()
            z_sec = zone_of(section)
            # 段標題寬容：`### 段1` / `### U01 · …` / `### 第1段` 都認
            if re.match(r"^段\s*\d", sub_head) or re.match(r"^U\d+\b", sub_head) \
               or re.match(r"^第\s*\d+\s*段", sub_head):
                seg = {"no": len(data["segments"]) + 1, "name": sub_head,
                       "raw": "", "shots": [], "fields": {}, "warnings": []}
                data["segments"].append(seg)
                ap = None
            elif z_sec == "ap":
                parts = [p.strip() for p in sub_head.split("·")]
                ap = {"code": clean_code(parts[0]) if parts else sub_head,
                      "_match": sub_head,
                      "name": clean_code(parts[1]) if len(parts) > 1 else "",
                      "desc": parts[2] if len(parts) > 2 else "",
                      "raw": ""}
                data["asset_prompts"].append(ap)
                seg = None
            else:
                ap = None
            continue

        # ★P9 修：七段式的畫幅寫在【畫幅風格】**行內**且不帶冒號，形如
        #   `【畫幅風格】16:9 橫屏，…（aspect_ratio=16:9）`。
        #   FIELD_RE 要求 `】:` 故永遠匹配不到 → B 鎖對外回顯「未鎖定」，
        #   與稿內已鎖定的事實矛盾（看板是交付物，這個失真會直接誤導人）。
        m_aspect = re.match(r"^【畫幅風格】\s*(.+)$", s)
        if m_aspect and data["meta"]["畫幅"] == "未鎖定":
            _body = m_aspect.group(1)
            _m = (re.search(r"aspect_ratio\s*=\s*(\d{1,2}\s*[:：]\s*\d{1,2})", _body)
                  or re.search(r"(\d{1,2}\s*[:：]\s*\d{1,2})", _body))
            if _m:
                data["meta"]["畫幅"] = re.sub(r"\s", "", _m.group(1)).replace("：", ":")

        fm_meta = FIELD_RE.match(s)
        if fm_meta:
            key, val = fm_meta.group(1), fm_meta.group(2).strip()
            if key in ("畫幅", "模型版本"):        # A/B 雙鎖：任意位置聲明都認
                data["meta"][key] = val
                continue
            if seg is not None:
                seg["fields"][key] = val
                continue
            if zone_of(section) == "publish":
                data["publish"].append({"k": key, "v": val})
                continue

        if s.startswith("|") and section:
            z = zone_of(section)
            if "---" in s and z in ("script", ""):
                # markdown 分隔行＝表頭確認：把已收的「表頭+數據」落表，末行留給下一張表當表頭
                if len(pending_tbl) > 1:
                    head = pending_tbl[-1]
                    _push_tbl(pending_tbl[:-1], z)
                    pending_tbl = [head]
                continue
            rows = table_rows([s])
            if rows:
                cells = rows[0]
                k0 = re.sub(r"[*`]", "", cells[0]).strip()
                # meta 兜底：從 A/B 雙鎖表等任意表格里撈模型版本/畫幅
                if data["meta"]["模型版本"] == "未鎖定" and "模型版本" in k0 and len(cells) > 1:
                    m = re.search(r"Seedance\s*[\d.]+|\d+(?:\.\d+)?", re.sub(r"[*`]", "", cells[1]))
                    if m:
                        data["meta"]["模型版本"] = m.group(0).strip()
                if data["meta"]["畫幅"] == "未鎖定" and "畫幅" in k0 and len(cells) > 1:
                    m = re.search(r"\d{1,2}\s*:\s*\d{1,2}", cells[1])
                    if m:
                        data["meta"]["畫幅"] = re.sub(r"\s", "", m.group(0))
                if z in ("script", ""):
                    flush_plain()            # 先落之前掛著的正文，保原文順序
                    pending_tbl.append(cells)
                elif z == "assets":
                    head = map_head(cells)   # 表頭探測只在資產區生效（防止吞掉劇本區表頭行）
                    if head is not None:
                        data["_head"] = head
                        continue
                    h = data.get("_head")
                    if h:
                        g = lambda f: cells[h[f]] if f in h and h[f] < len(cells) else ""
                        row = {"code": g("code") or cells[0], "name": g("name"),
                               "view": g("view"), "img": g("img"), "extra": []}
                        used = set(h.values())
                        row["extra"] = [c for i, c in enumerate(cells)
                                        if i not in used and c and c not in ("類", "編碼")]
                    else:
                        row = {"code": cells[0], "name": cells[1] if len(cells) > 1 else "",
                               "view": cells[2] if len(cells) > 2 else "",
                               "img": cells[3] if len(cells) > 3 else "", "extra": []}
                    if row["code"] and row["code"] not in ("編碼",):
                        data["assets"].append(row)
                elif z == "p0a":
                    if cells[0] not in ("項",):
                        data["p0a"].append({"k": cells[0], "v": " | ".join(cells[1:])})
                elif z == "bible":
                    data["bible"].append(" | ".join(cells))
                continue

        if seg is not None:
            fmt = TS_RE.match(s)
            if fmt:
                try:
                    start, end = to_seconds(fmt.group(1)), to_seconds(fmt.group(2))
                except ValueError:
                    seg["warnings"].append(
                        f"鏡行時碼無法解析、該鏡已被跳過（看板與三導出會缺此鏡）：{s[:40]}")
                else:
                    seg["shots"].append({"no": len(seg["shots"]) + 1,
                                         "start": start, "end": end,
                                         "text": shot_text(fmt.group(3))})
                continue
        plain.append(line)

    flush_tbl()
    flush_plain()

    # ★P9 修（B 鎖失真）：七段式的畫幅寫在【畫幅風格】**行內**且不帶冒號，
    #   形如 `【畫幅風格】16:9 橫屏，…（aspect_ratio=16:9）`。
    #   而該行位於 ```text 圍欄內，主循環遇到圍欄體會直接 continue，
    #   FIELD_RE 又要求 `】:` —— 兩道都過不去 → 畫幅永遠「未鎖定」，
    #   看板對外回顯與稿內已鎖定的事實矛盾。故在全文層面單獨掃一次。
    if data["meta"]["畫幅"] == "未鎖定":
        for _mf in re.finditer(r"^【畫幅風格】\s*(.+)$", md_text, re.M):
            _body = _mf.group(1)
            _m = (re.search(r"aspect_ratio\s*=\s*(\d{1,2}\s*[:：]\s*\d{1,2})", _body)
                  or re.search(r"(\d{1,2}\s*[:：]\s*\d{1,2})", _body))
            if _m:
                data["meta"]["畫幅"] = re.sub(r"\s", "", _m.group(1)).replace("：", ":")
                break

    # 圍欄原文歸屬：段 / 資產出圖
    parts = re.split(r"^#{2,4}\s+", md_text, flags=re.M)
    def fence_of(body):
        fs = FENCE_RE.findall(body)
        return max(fs, key=len).strip() if fs else ""
    def _body_of(chunk):
        return fence_of("\n".join(chunk.splitlines()[1:]))

    def _locate(name):
        """按標題把段落回它的 ```text 圍欄原文。

        ⚠️ 2026-11-25 修（看板整段串味）：原實現用 `name.split()[0]` 當 token，
        形如 `【投餵單元 2/5 · 段2】` 的標題 split 出來是 `【投餵單元`——
        5 段共用一個前綴 → **每段都命中第 1 段**，看板 5 段全部顯示段1 的內容，
        鏡數 35（7×5）、總時長 130（26×5）全是重複計數，而 CLI 只報數字不報錯。
        改為三級匹配：① 標題完全相等 → ② 段號 token（段N/第N段/UN）唯一命中 →
        ③ 首 token 前綴兜底。命中不唯一即視為定位失敗，交給下方 WARN 報警。
        """
        # ① 標題完全相等
        for chunk in parts[1:]:
            if chunk.splitlines()[0].strip() == name.strip():
                return _body_of(chunk)
        # ② 段號 token 唯一命中
        m = re.search(r"段\s*(\d+)|第\s*(\d+)\s*段|\bU0*(\d+)\b", name)
        for tok in ([g for g in (m.groups() if m else ()) if g] or []):
            pat = re.compile(r"(?:段\s*%s(?!\d)|第\s*%s\s*段|U0*%s(?!\d))" % (tok, tok, tok))
            hits = [c for c in parts[1:] if pat.search(c.splitlines()[0].strip())]
            if len(hits) == 1:
                return _body_of(hits[0])
        # ③ 首 token 前綴兜底（僅在唯一命中時採用，避免再次整段串味）
        token = name.split()[0] if name.split() else name
        hits = [c for c in parts[1:] if c.splitlines()[0].strip().startswith(token)]
        if len(hits) == 1:
            return _body_of(hits[0])
        return ""

    for seg in data["segments"]:
        seg["raw"] = _locate(seg["name"])
    # 串味安全網：兩段拿到同一份圍欄原文 = 定位失敗（正常不可能），必須報
    _seen_raw = {}
    for seg in data["segments"]:
        _sig = (seg["raw"] or "").strip()
        if not _sig:
            continue
        if _sig in _seen_raw:
            data["warnings"].append({"seg": seg["no"],
                "msg": f"{seg['name']}：與 {_seen_raw[_sig]} 拿到同一份投餵原文——"
                       f"段標題定位失敗，看板內容不可信，請檢查段標題是否重複或前綴同形"})
        else:
            _seen_raw[_sig] = seg["name"]
    for ap in data["asset_prompts"]:
        for chunk in parts[1:]:
            first = chunk.splitlines()[0].strip()
            if first == ap.get("_match") or first.startswith(ap.get("_match", "\0")):
                ap["raw"] = fence_of("\n".join(chunk.splitlines()[1:]))
                break

    # 校驗（輕量 WARN 層）
    for seg in data["segments"]:
        if not seg["raw"]:
            seg["warnings"].append("未找到 ```text 圍欄投餵原文（無法直接複製投餵）")
        _skipped = []
        if not seg["shots"]:
            for l in seg["raw"].splitlines():     # K-lite-2 降級：從圍欄內提取時間戳
                fm = TS_RE.match(l.strip())
                if fm:
                    try:
                        a, b = to_seconds(fm.group(1)), to_seconds(fm.group(2))
                    except ValueError:
                        # ★2026-10-14 Agent 修復：原為裸 `continue` —— 丟鏡不留痕。
                        # 靜默丟鏡會讓看板與三導出悄悄缺鏡（實測曾丟 41%），必須記賬。
                        _skipped.append(l.strip()[:48])
                        continue
                    seg["shots"].append({"no": len(seg["shots"]) + 1,
                                         "start": a, "end": b, "text": shot_text(fm.group(3))})
        # ★丟鏡安全網（2026-10-14 Agent 新增）：以「原文帶時碼的行數」為基準對賬，
        #   任何解析器缺陷造成的靜默丟鏡都會被這一條兜住，不必逐類枚舉病因。
        _tc_lines = [l for l in seg["raw"].splitlines() if TS_RE.match(l.strip())]
        if _skipped:
            seg["warnings"].append(
                f"有 {len(_skipped)} 行鏡行時碼無法解析、該鏡已被跳過"
                f"（看板與 SRT/CSV/JSON 三導出會缺這些鏡）：{'；'.join(_skipped[:4])}"
                + ("…" if len(_skipped) > 4 else ""))
        if len(_tc_lines) > len(seg["shots"]):
            _lost = len(_tc_lines) - len(seg["shots"])
            seg["warnings"].append(
                f"丟鏡告警：原文帶時碼的鏡行 {len(_tc_lines)} 行，僅解析出 {len(seg['shots'])} 鏡，"
                f"缺 {_lost} 鏡——請核對鏡行時碼寫法（支持 `MM:SS` / `MM:SS.s` / `Xs-Ys` / `N-N秒`）")
        if not seg["shots"]:
            seg["warnings"].append("未解析到 [起-止秒] 逐鏡時間戳行")
        else:
            prev = None
            for sh in seg["shots"]:
                if prev is not None and sh["start"] < prev - 0.01:
                    seg["warnings"].append(f"鏡頭時間碼回跳：{sh['start']:g}s 早於上鏡結束 {prev:g}s")
                    break
                prev = sh["end"]
        for w in seg["warnings"]:
            data["warnings"].append({"seg": seg["no"], "msg": f"{seg['name']}：{w}"})

    for ap in data["asset_prompts"]:
        if not ap["raw"]:
            data["warnings"].append({"seg": 0, "msg": f"資產出圖提示詞 {ap['code']} 未找到 ```text 圍欄原文"})
    if not data["segments"]:
        data["warnings"].append({"seg": 0, "msg": "全檔未解析到「### 段N」分鏡段——請檢查標題契約"})
    # ★P9：M0/M1/M2 形態下資產另冊交付，稿內本就沒有 P2.5 章節——
    #   只要稿內寫了「資產另冊：…」聲明，缺 P2.5 就是**合法形態**，不是漏寫，不該報。
    #   否則純投餵稿永遠帶一條假 WARN，看板一開就"飄紅"。
    _asset_by_book = bool(re.search(r"資產另冊\s*[:：]", md_text))
    if not data["asset_prompts"] and not _asset_by_book:
        data["warnings"].append({"seg": 0,
            "msg": "未解析到「## P2.5 · 資產出圖提示詞」——⑤ 資產出圖提示詞與 ③ 分鏡投餵提示詞必須同板呈現（K-lite-4）"})
    else:
        for _it in data["asset_prompts"]:
            _bd = (_it.get("raw") or "").strip()
            _cd = (_it.get("code") or _it.get("name") or "").upper()
            _missing_fp = (
                len(_bd) < 150
                or "同板四視圖" in _bd or "T-pose" in _bd or "九機位小圖" in _bd or "詳見 P2" in _bd or "不另寫文字描述" in _bd
                or ("CHR" in _cd and not ("無臉全身" in _bd or "featureless face" in _bd or "八格拼版" in _bd))
                or ("SCN" in _cd and not ("五宮格" in _bd or "九宮格" in _bd or "攝影機矩陣" in _bd))
            )
            if _missing_fp:
                data["warnings"].append({
                    "seg": 0, "lvl": "WARN", "code": "K-lite-4b",
                    "msg": f"K-lite-4b 資產「{_it.get('code') or _it.get('name', '')}」出圖提示詞疑似簡筆空殼（僅 {len(_bd)} 字或未落權威模板指紋）——須按 sd-asset-engine 權威模板寫滿（角色四格無臉+聲紋錨 / 場景母版+五宮格8字段 / 道具4格）"
                })
    if data["meta"]["畫幅"] == "未鎖定":
        data["warnings"].append({"seg": 0, "msg": "未聲明【畫幅】——B 鎖未鎖定（用戶未指定 ≠ 默認 9:16）"})
    if data["meta"]["模型版本"] == "未鎖定":
        data["warnings"].append({"seg": 0, "msg": "未聲明【模型版本】——A 鎖未鎖定（用戶未指定 ≠ 默認 2.5）"})

    # 時間軸排布：段內獨立計時 → 按累計偏移鋪成整片時間軸（泳道才讀得出 57s 成片節奏）
    off = 0.0
    for seg in data["segments"]:
        seg["off"] = off
        if seg["shots"]:
            off += max(sh["end"] for sh in seg["shots"])

    # 資產引用段：用編碼在段原文裡回查（如 @CHR-沈硯 出現在哪些段）
    for a in data["assets"]:
        code = a.get("code", "")
        a["refs"] = refs_of(code, data["segments"])
    return data


def total_duration(data):
    """各段獨立計時（每段都從 0 起）→ 累加成整片時長；連續時間軸 → 取最大 end。"""
    segs = [s for s in data["segments"] if s["shots"]]
    if not segs:
        return 0
    starts = [s["shots"][0]["start"] for s in segs]
    if starts and all(abs(x - starts[0]) < 0.01 for x in starts) and starts[0] == 0:
        return sum(max(sh["end"] for sh in s["shots"]) for s in segs)
    return max(max(sh["end"] for sh in s["shots"]) for s in segs)


def build_html(d: dict) -> str:
    payload = {
        "meta": {"model": d["meta"]["模型版本"], "aspect": d["meta"]["畫幅"],
                 "seg_count": len(d["segments"]),
                 "shot_count": sum(len(s["shots"]) for s in d["segments"]),
                 "total": total_duration(d),
                 "built_at": datetime.now().strftime("%Y-%m-%d %H:%M")},
        "p0a": d["p0a"], "script": d["script"], "bible": d["bible"],
        "assets": d["assets"], "aprompts": d["asset_prompts"], "publish": d["publish"],
        "segments": d["segments"], "warnings": d["warnings"], "extras": d["extras"],
    }
    safe_json = (json.dumps(payload, ensure_ascii=False)
                 .replace("<", "\\u003c").replace(">", "\\u003e")
                 .replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    return TEMPLATE.replace("@@DATA@@", safe_json) \
                   .replace("@@TITLE@@", html.escape(d["title"], quote=True))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@ · 分鏡看板</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#F7F6F2;color:#1F1E1B;
 font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
h1{font-size:19px;font-weight:600;margin:0 0 4px}
h2{font-size:15px;font-weight:600;margin:26px 0 10px;padding-bottom:6px;border-bottom:1px solid #E2E0D9}
.sub{color:#6B6963;font-size:12px;font-weight:400}
.bar{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}
.chip{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:6px 10px;font-size:12px}
.chip b{font-weight:600}
.chip.k{color:#0C447C}.chip.warn{color:#854F0B;border-color:#EF9F27}
.seg-f{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.seg-f button{cursor:pointer;background:#fff;border:1px solid #E2E0D9;border-radius:999px;padding:4px 12px;font-size:12px}
.seg-f button.on{background:#185FA5;border-color:#185FA5;color:#fff}
.f{border:1px solid #E2E0D9;background:#fff;border-radius:8px;padding:8px 10px;margin:6px 0;font-size:12.5px}
.f .code{font-family:ui-monospace,Consolas,monospace;font-weight:600;margin-right:6px;color:#854F0B}
.lane{margin:8px 0}
.lane .nm{font-size:12px;color:#6B6963;margin-bottom:3px}
.lane .track{position:relative;height:32px;background:#fff;border:1px solid #E2E0D9;border-radius:6px}
.blk{position:absolute;top:3px;height:26px;border-radius:4px;background:#E6F1FB;border:1px solid #85B7EB;
 font-size:11px;color:#0C447C;text-align:center;line-height:24px;overflow:hidden;cursor:default}
.blk.s1{background:#E1F5EE;border-color:#5DCAA5;color:#085041}
.blk.s2{background:#FAEEDA;border-color:#EF9F27;color:#633806}
.blk.s3{background:#EEEDFE;border-color:#AFA9EC;color:#3C3489}
.blk:hover{outline:2px solid #185FA5}
.ruler{position:relative;height:16px;margin-top:2px}
.ruler span{position:absolute;top:4px;font-size:10.5px;color:#888780;transform:translateX(-50%)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:8px}
.card{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:9px 10px;font-size:12px}
.card .hd{display:flex;justify-content:space-between;font-weight:600;margin-bottom:5px;font-size:12.5px}
.card .row{color:#444441;margin:3px 0}
.card .row i{color:#888780;font-style:normal;margin-right:3px}
table{width:100%;border-collapse:collapse;font-size:12px;background:#fff}
th,td{border:1px solid #E2E0D9;padding:5px 7px;text-align:left;vertical-align:top}
th{background:#F1EFE8;font-weight:600}
td.num{text-align:center;font-family:ui-monospace,Consolas,monospace}
.aimg{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;background:#E6F1FB;
 border:1px solid #85B7EB;color:#0C447C;font-weight:600;white-space:nowrap}
.asegs{font-size:11.5px;color:#185FA5}
details.pbox{background:#fff;border:1px solid #E2E0D9;border-radius:8px;margin:8px 0;padding:10px 12px}
details.pbox>summary{cursor:pointer;font-size:12.5px;color:#33312C;list-style:none}
details.pbox>summary::-webkit-details-marker{display:none}
details.pbox>summary::before{content:"▸ ";color:#888780}
details.pbox[open]>summary::before{content:"▾ "}
.cpbtn{float:right;font-size:11.5px;padding:2px 9px;border-radius:5px;border:1px solid #85B7EB;
 background:#E6F1FB;color:#0C447C;cursor:pointer}
.cpbtn:hover{background:#D6E9FA}
pre{white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,Consolas,"Courier New",monospace;
 font-size:12px;line-height:1.68;color:#33312C;background:#FAF9F5;border:1px solid #E2E0D9;
 border-radius:6px;padding:10px 12px;margin:8px 0 2px}
.note{font-size:11.5px;color:#888780;margin-top:6px}
.zone{font-size:12px;font-weight:600;letter-spacing:.06em;background:#E6F1FB;color:#0C447C;
 border:1px solid #85B7EB;border-radius:6px;padding:5px 10px;margin:26px 0 2px}
.zone.prod{background:#F1EFE8;border-color:#D3D1C7;color:#6B6963}
.kv{margin:9px 0}
.kv .k2{font-size:11px;color:#888780;letter-spacing:.04em;margin-bottom:2px}
.kv .v2{font-size:12.5px;line-height:1.72;color:#33312C;white-space:pre-wrap;word-break:break-word}
.script .sc{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:9px 11px;margin:7px 0}
.script .sc .bd{font-size:12.5px;line-height:1.72;color:#33312C;white-space:pre-wrap}
.chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:2px}
.chips .c2{font-size:11px;padding:1px 7px;border-radius:999px;background:#F7F6F2;border:1px solid #E2E0D9;color:#6B6963}
.hide{display:none}
.bline{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:10px 12px;margin:8px 0}
.bline .bt{font-size:11px;color:#888780;letter-spacing:.04em;margin-bottom:3px}
.bline .bv{font-size:12.5px;color:#33312C;line-height:1.7;white-space:pre-wrap}
footer{text-align:center;color:#9A968C;font-size:11.5px;padding:16px 0 26px}
</style></head><body><div class="wrap">
<h1>@@TITLE@@</h1>
<div class="sub" id="hdr"></div>
<div class="bar" id="bar"></div>
<div class="seg-f" id="filters"></div>
<div id="alerts"></div>
<div class="zone">創作藍圖層 · P0~P1 —— 先看這裡（故事 / 基準 / 風格）</div>
<h2>Ⅰ · 創作基準 <span class="sub">（P0A · 表格項 → 看板行）</span></h2><div id="p0a"></div>
<h2>Ⅱ · 劇本層 <span class="sub">（P1 產出物 · 正文照錄）</span></h2><div id="script"></div>
<h2>Ⅲ · 視聽聖經 <span class="sub">（P1 一次鎖定 · 全片繼承）</span></h2><div id="bible"></div>
<div class="zone prod">分鏡生產層 · P2~P6 —— 拿去幹活的那一份（資產 / 分鏡 / 投餵 / 文案）</div>
<h2>① 時間軸泳道</h2><div id="lanes"></div>
<h2>② 鏡頭卡矩陣 <span class="sub">（拆解視圖 — 逐鏡欄位）</span></h2><div class="cards" id="cards"></div>
<h2>③ 投餵提示詞原文 <span class="sub">（成品視圖 — 照錄未改寫，可整段複製直接投餵）</span></h2><div id="prompts"></div>
<h2>④ 資產總表 <span class="sub">（人物 / 場景 / 道具 → 圖號 → 引用段 · 來自 P2 資產清單）</span></h2><div id="assets"></div>
<h2>⑤ 資產出圖提示詞 <span class="sub">（成品視圖 — 生成人物 / 場景 / 道具資產圖用，可整段複製；<b>不是</b>視頻投餵提示詞，與 ③ 必同板）</span></h2><div id="aprompts"></div>
<h2>⑥ 發佈文案</h2><div id="copy"></div>
<h2>⑦ 其他章節 <span class="sub">（md 內未被歸區的章節 · 原文照錄，K-lite-6 信息零丟失）</span></h2><div id="extras"></div>
<div class="note" id="foot"></div>
<footer>由 scripts/build_board_lite.py 生成 · 源 md 是唯一真相，本看板只讀不回寫 · 雙擊即開，零依賴</footer>
</div>
<script>
const D = @@DATA@@;
let curSeg = 0, onlyBad = false;
const esc = s => (s==null?'':String(s)).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const segBad = n => D.warnings.some(w=>w.seg===n);
// 內容塊渲染：連續 row 合併成表格，p 塊照錄（K-lite-6 信息零丟失）
function renderBlocks(bl){
  let out='', tbl=null;
  const flushT=()=>{ if(tbl){ out+='<table>'+tbl.map((r,i)=>'<tr>'+r.map(c=>(i?'<td>':'<th>')+esc(c)+'</td>').join('')+'</tr>').join('')+'</table>'; tbl=null; } };
  (bl||[]).forEach(b=>{
    if(b.t==='row'){ (tbl=tbl||[]).push(b.cells||[]); }
    else if(b.t==='tbl'){ flushT(); out+='<table>'+(b.rows||[]).map((r,i)=>'<tr>'+r.map(c=>(i?'<td>':'<th>')+esc(c)+'</td>').join('')+'</tr>').join('')+'</table>'; }
    else { flushT(); out+='<div class="bd">'+esc(b.v)+'</div>'; }
  });
  flushT();
  return out;
}

function hdr(){
  const p = D.meta;
  document.getElementById('hdr').textContent =
    `模型 ${p.model} · 畫幅 ${p.aspect} · ${p.seg_count} 段 / ${p.shot_count} 鏡 / 總時長 ${p.total}s · 編譯於 ${p.built_at}`;
  document.getElementById('bar').innerHTML =
    `<div class="chip k"><b>輕量校驗</b> ${D.warnings.length} WARN / 0 ERROR</div>`
    + `<button class="chip" onclick="toggleOnly()" id="btnOnly">只看告警</button>`
    + `<button class="chip" onclick="exportSRT()">⬇ 導出 SRT 字幕</button>`
    + `<button class="chip" onclick="exportTimelineCSV()">⬇ 導出剪輯時間線 CSV</button>`
    + `<button class="chip" onclick="exportPayloadJSON()">⬇ 導出 API 載荷 JSON</button>`;
}
function toggleOnly(){ onlyBad=!onlyBad; document.getElementById('btnOnly').classList.toggle('on',onlyBad);
  document.getElementById('btnOnly').classList.toggle('warn',onlyBad); paint(); }

function segBtns(){
  document.getElementById('filters').innerHTML =
    `<button class="${curSeg===0?'on':''}" onclick="setSeg(0)">全部段</button>`
    + D.segments.map(s=>`<button class="${curSeg===s.no?'on':''}" onclick="setSeg(${s.no})">${esc(s.name)}</button>`).join('');
}
function setSeg(n){ curSeg=n; segBtns(); paint(); }
const vis = n => (!onlyBad || segBad(n)) && (curSeg===0 || curSeg===n);

function paint(){
  hdr(); segBtns();
  // 告警區
  const al = D.warnings.map(w=>`<div class="f"><span class="code">WARN</span>${esc(w.msg)}</div>`).join('');
  document.getElementById('alerts').innerHTML = al || '';
  // Ⅰ 創作基準
  document.getElementById('p0a').innerHTML = D.p0a.length
    ? '<table><tr><th style="width:150px">項</th><th>內容</th></tr>'
      + D.p0a.map(x=>`<tr><td>${esc(x.k)}</td><td>${esc(x.v)}</td></tr>`).join('') + '</table>'
    : '<div class="f">未解析到「## P0A · 創作基準」章節</div>';
  // Ⅱ 劇本
  document.getElementById('script').innerHTML = (D.script && D.script.length)
    ? `<div class="script"><div class="sc">${renderBlocks(D.script)}</div></div>`
    : '<div class="f">未解析到「## P1 · 劇本」章節</div>';
  // Ⅲ 視聽聖經
  document.getElementById('bible').innerHTML = D.bible.length
    ? D.bible.map(b=>`<div class="bline"><div class="bv">${esc(b)}</div></div>`).join('')
    : '<div class="f">未解析到「## P1 · 視聽聖經」章節</div>';
  // ① 時間軸泳道
  const total = Math.max(D.meta.total, 1);
  document.getElementById('lanes').innerHTML = D.segments.map(s=>{
    const cls = ['','s1','s2','s3'];
    const off = s.off||0;
    const blocks = s.shots.map((sh,i)=>{
      const a=sh.start+off, b=sh.end+off;
      const L=(a/total*100).toFixed(2), W=Math.max((b-a)/total*100,1.2).toFixed(2);
      return `<div class="blk ${cls[i%4]}" style="left:${L}%;width:${W}%"
        title="段內 ${sh.start}-${sh.end}s（整片 ${a}-${b}s） ${esc(sh.text)}">鏡${sh.no}</div>`;
    }).join('');
    const ticks = Array.from({length:5},(_,i)=>{
      const t=Math.round(total*i/4);
      return `<span style="left:${i*25}%">${t}s</span>`;
    }).join('');
    return `<div class="lane ${vis(s.no)?'':'hide'}"><div class="nm">${esc(s.name)} · ${esc(String(s.shots.length))} 鏡 · 整片 ${off}s 起</div>
      <div class="track">${blocks}</div><div class="ruler">${ticks}</div></div>`;
  }).join('') || '<div class="f">未解析到分鏡段</div>';
  // ② 鏡頭卡矩陣
  document.getElementById('cards').innerHTML = D.segments.filter(s=>vis(s.no)).flatMap(s=>
    s.shots.map(sh=>`<div class="card"><div class="hd"><span>${esc(s.name)} · 鏡${sh.no}</span>
      <span class="ph">[${sh.start}-${sh.end}s] · ${Math.max(sh.end-sh.start,0).toFixed(1).replace(/\.0$/,'')}s</span></div>
      <div class="row">${esc(sh.text)||'—'}</div></div>`)).join('')
    || '<div class="f">無鏡頭卡</div>';
  // ③ 投餵原文
  document.getElementById('prompts').innerHTML = D.segments.filter(s=>vis(s.no)).map((s,i)=>{
    const chips = Object.entries(s.fields||{}).map(([k,v])=>`<span class="c2">${esc(k)}：${esc(v)}</span>`).join('');
    return `<details class="pbox" open><summary>${esc(s.name)} · ${s.shots.length} 鏡
      <button class="cpbtn" onclick="cp('p${s.no}',event)">複製投餵原文</button></summary>
      ${chips?`<div class="chips">${chips}</div>`:''}
      <pre id="p${s.no}">${esc(s.raw||'（未解析到圍欄原文）')}</pre></details>`;
  }).join('') || '<div class="f">無投餵原文</div>';
  // ④ 資產總表
  document.getElementById('assets').innerHTML = D.assets.length
    ? '<table><tr><th>編碼</th><th>名字</th><th>視圖 / 出圖</th><th>@圖片N</th><th>附加信息</th><th>引用段</th></tr>'
      + D.assets.map(a=>`<tr><td>${esc(a.code)}</td><td>${esc(a.name||'—')}</td><td>${esc(a.view||'—')}</td>
        <td><span class="aimg">${esc(a.img||'未綁圖')}</span></td>
        <td class="asegs">${esc((a.extra||[]).join(' · '))||'—'}</td>
        <td class="asegs">${(a.refs||[]).length?('段 '+a.refs.join('、')):'—'}</td></tr>`).join('') + '</table>'
    : '<div class="f">未解析到「## P2 · 資產清單」表格</div>';
  // ⑤ 資產出圖提示詞（與 ③ 必同板）；同一場景資產的連排條目（①②③）聚合為一張卡
  const _grp=[];
  D.aprompts.forEach((a,i)=>{
    const g=_grp[_grp.length-1];
    if(g&&g.code===a.code&&a.code.indexOf('@SCN-')===0){g.items.push([a,i]);}
    else{_grp.push({code:a.code,items:[[a,i]]});}
  });
  document.getElementById('aprompts').innerHTML = _grp.length
    ? _grp.map(g=>{
        if(g.items.length===1){
          const [a,i]=g.items[0];
          return `<details class="pbox" open><summary>${esc(a.code)} · ${esc(a.name)}
            <button class="cpbtn" onclick="cp('a${i}',event)">複製出圖提示詞</button></summary>
            ${a.desc?`<div class="note">${esc(a.desc)}</div>`:''}
            <pre id="a${i}">${esc(a.raw||'（未解析到圍欄原文）')}</pre></details>`;
        }
        return `<details class="pbox" open><summary>${esc(g.code.replace(/^@/,''))} · ${g.items.map(x=>esc(x[0].name)).join('+')} · ${g.items.length} 條複製全部
            <button class="cpbtn" onclick="cpall('${g.items.map(x=>'a'+x[1]).join('|')}',event)">複製全部</button></summary>
            ${g.items.map(([a,i])=>`<div class="note">${esc(a.name)}
              <button class="cpbtn" onclick="cp('a${i}',event)">複製本條</button></div>
              <pre id="a${i}">${esc(a.raw||'（未解析到圍欄原文）')}</pre>`).join('')}
          </details>`;
      }).join('')
    : '<div class="f">未解析到「## P2.5 · 資產出圖提示詞」（K-lite-4：與 ③ 必同板，請補齊章節）</div>';
  // ⑥ 發佈文案
  document.getElementById('copy').innerHTML = D.publish.length
    ? D.publish.map(x=>`<div class="kv"><div class="k2">${esc(x.k)}</div><div class="v2">${esc(x.v)}</div></div>`).join('')
    : '<div class="f">未解析到「## P6 · 發佈文案」（可選章節）</div>';
  // ⑦ 其他章節（未歸區原文照錄）
  document.getElementById('extras').innerHTML = (D.extras && D.extras.length)
    ? D.extras.map(x=>`<details class="pbox"><summary>${esc(x.title)}</summary>${renderBlocks(x.body)||'<div class="f">（空）</div>'}</details>`).join('')
    : '<div class="note">（無未歸區章節）</div>';
  document.getElementById('foot').textContent =
    `本看板為輕量版：無 N1~N11 深度檢查層與狀態快照；深度質檢請走 P0~P2 質檢門禁與改動後複驗鐵律。`;
}

function cp(id,e){
  const t=document.getElementById(id).innerText;
  const done=()=>{e.target.innerText='已複製 ✓';setTimeout(()=>{e.target.innerText='複製';},1200);};
  const fail=()=>{e.target.innerText='複製失敗·請手動全選';setTimeout(()=>{e.target.innerText='複製';},2000);};
  const legacy=()=>{try{const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand('copy');document.body.removeChild(ta);ok?done():fail();}catch(err){fail();}};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done).catch(legacy);}
  else{legacy();}
}

function cpall(ids,e){
  const t=ids.split('|').map(id=>document.getElementById(id).innerText).join('\\n\\n');
  const done=()=>{e.target.innerText='已複製全部 ✓';setTimeout(()=>{e.target.innerText='複製全部';},1500);};
  const fail=()=>{e.target.innerText='複製失敗·請手動全選';setTimeout(()=>{e.target.innerText='複製全部';},2000);};
  const legacy=()=>{try{const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand('copy');document.body.removeChild(ta);ok?done():fail();}catch(err){fail();}};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done).catch(legacy);}
  else{legacy();}
}
function dlBlob(filename, content, mime){
  const blob = new Blob([content], {type: mime});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); document.body.removeChild(a); }, 300);
}
function fmtSrtTime(sec){
  // ★2026-10-15 修復：原 `ms=Math.round((sec%1)*1000)` + `totalS=Math.floor(sec)` 分立取整，
  //   小數位進位到 1000ms 時印出非法 `,1000` 且秒位不結轉。改為「總毫秒一次取整再拆分」。
  let totalMs = Math.round(sec * 1000); if (totalMs < 0) totalMs = 0;
  const ms = totalMs % 1000;
  const totalS = Math.floor(totalMs / 1000);
  const s = totalS % 60;
  const m = Math.floor(totalS / 60) % 60;
  const h = Math.floor(totalS / 3600);
  const pad = (n, w=2) => String(n).padStart(w, '0');
  return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
}
function exportSRT(){
  let idx = 1, lines = [];
  (D.segments||[]).forEach(seg=>{
    const off = seg.off || 0;
    (seg.shots||[]).forEach(sh=>{
      const m = (sh.text||'').match(/台詞：【([^】]+)】/);
      if(m && !m[1].startsWith('無')){
        lines.push(`${idx++}\n${fmtSrtTime(off + sh.start)} --> ${fmtSrtTime(off + sh.end)}\n${m[1]}\n`);
      }
    });
  });
  dlBlob((D.meta&&D.meta.title||'short_drama') + '.srt', lines.join('\n') || '1\n00:00:00,000 --> 00:00:02,000\n（無對白）\n', 'text/plain;charset=utf-8');
}
function exportTimelineCSV(){
  const escCsv = v => '"' + String(v==null?'':v).replace(/"/g, '""') + '"';
  const rows = [['段落', '鏡號', '段內起秒', '段內止秒', '全片起秒', '全片止秒', '時長(s)', '鏡頭內容與台詞']];
  (D.segments||[]).forEach(seg=>{
    const off = seg.off || 0;
    (seg.shots||[]).forEach(sh=>{
      rows.push([seg.name, '鏡'+sh.no, sh.start, sh.end, off+sh.start, off+sh.end, Math.max(sh.end-sh.start,0), sh.text||'']);
    });
  });
  const csv = '\uFEFF' + rows.map(r=>r.map(escCsv).join(',')).join('\r\n');
  dlBlob((D.meta&&D.meta.title||'short_drama') + '_timeline.csv', csv, 'text/csv;charset=utf-8');
}
function exportPayloadJSON(){
  dlBlob((D.meta&&D.meta.title||'short_drama') + '_payload.json', JSON.stringify(D, null, 2), 'application/json;charset=utf-8');
}
paint();
</script></body></html>"""


def export_srt_text(data):
    idx, lines = 1, []
    def _fmt(sec):
        # ★2026-10-15 修復：原 `ms=int(round((sec%1)*1000))` + `ts=int(sec)` 分立取整，
        #   當小數位進位到 1000ms（如 4.9995→round(999.5)=1000）會印出非法 `,1000`
        #   且秒位不結轉 → 00:00:04,1000（SRT 毫秒須 000~999）。改為「總毫秒一次取整再拆分」。
        total_ms = max(int(round(sec * 1000)), 0)
        ms = total_ms % 1000
        ts = total_ms // 1000
        return f"{ts // 3600:02d}:{(ts // 60) % 60:02d}:{ts % 60:02d},{ms:03d}"
    for seg in data.get("segments", []):
        off = seg.get("off", 0)
        for sh in seg.get("shots", []):
            m = re.search(r"台詞：【([^】]+)】", sh.get("text", ""))
            if m and not m.group(1).startswith("無"):
                lines.append(f"{idx}\n{_fmt(off + sh['start'])} --> {_fmt(off + sh['end'])}\n{m.group(1)}\n")
                idx += 1
    return "\n".join(lines)


def export_timeline_csv_text(data):
    def _esc(v):
        return '"' + str(v if v is not None else "").replace('"', '""') + '"'
    rows = [["段落", "鏡號", "段內起秒", "段內止秒", "全片起秒", "全片止秒", "時長(s)", "鏡頭內容與台詞"]]
    for seg in data.get("segments", []):
        off = seg.get("off", 0)
        for sh in seg.get("shots", []):
            rows.append([
                seg.get("name", ""),
                f"鏡{sh.get('no', '')}",
                sh.get("start", 0),
                sh.get("end", 0),
                off + sh.get("start", 0),
                off + sh.get("end", 0),
                round(max(sh.get("end", 0) - sh.get("start", 0), 0), 2),
                sh.get("text", ""),
            ])
    return "\ufeff" + "\r\n".join(",".join(_esc(c) for c in r) for r in rows)


def self_test():
    sample = (
        "# 測試劇目\n"
        "## 【投餵單元 1/1 · 段1】\n"
        "```text\n"
        "【畫幅風格】16:9 橫屏\n"
        "【場景資產】@走廊\n"
        "【核心人物】@甲\n"
        "【站位聲明】@甲（畫面左）\n"
        "【時間軸分鏡】\n"
        "[鏡頭1] 0-4秒，中景·平視·固定。甲開口。聲音：無。台詞：【甲（低沉）：“你好。”】\n"
        "[鏡頭2] 4-8秒，近景·平視·緩推。甲定格。聲音：無。台詞：無。\n"
        "【音效】環境音\n"
        "【強制禁止項】無字幕\n"
        "```\n"
    )
    d = parse_md(sample)
    assert len(d["segments"]) == 1 and len(d["segments"][0]["shots"]) == 2
    srt = export_srt_text(d)
    csv_txt = export_timeline_csv_text(d)
    html = build_html(d)
    assert "00:00:00,000 --> 00:00:04,000" in srt and "你好" in srt
    assert "鏡1" in csv_txt and "exportSRT()" in html and "exportTimelineCSV()" in html

    # ---- 2026-10-14 Agent 修復迴歸鎖：半秒時碼 MM:SS.s 必須被正確解析，且不得丟鏡 ----
    for _tok, _exp in (("00:10.5", 10.5), ("00:03.5", 3.5), ("00:12.5", 12.5),
                       ("00:04", 4.0), ("12.5", 12.5), ("0-3秒", None)):
        if _exp is not None:
            _got = to_seconds(_tok)
            assert abs(_got - _exp) < 1e-9, f"to_seconds({_tok!r}) = {_got}，應為 {_exp}"
    sample2 = (
        "# 半秒時碼迴歸用例\n"
        "## 【投餵單元 1/1 · 段1】\n"
        "```text\n"
        "【畫幅風格】16:9 橫屏\n"
        "【場景資產】@走廊\n"
        "【核心人物】@甲\n"
        "【站位聲明】@甲（畫面左）\n"
        "【時間軸分鏡】\n"
        "00:00-00:04 [鏡頭1] 中景 · 平視 · 固定。甲開口。聲音：無。台詞：【甲（低沉）：“一。”】\n"
        "00:04-00:08 [鏡頭2] 近景 · 平視 · 緩推。甲轉頭。聲音：無。台詞：無。\n"
        "00:08-00:10.5 [鏡頭3] 特寫 · 平視 · 固定。甲眨眼。聲音：無。台詞：無。\n"
        "00:10.5-00:12.5 [鏡頭4] 近景 · 斜角 · 極緩慢推。甲抬手。聲音：無。台詞：無。\n"
        "00:12.5-00:15 [鏡頭5] 中景 · 正面 · 緩拉。甲定格。聲音：無。台詞：無。\n"
        "【音效】環境音\n"
        "【強制禁止項】無字幕\n"
        "```\n"
    )
    d2 = parse_md(sample2)
    _shots2 = d2["segments"][0]["shots"]
    assert len(_shots2) == 5, f"半秒時碼稿應解析出 5 鏡，實得 {len(_shots2)} 鏡（丟鏡即本用例攔截目標）"
    assert abs(_shots2[2]["end"] - 10.5) < 1e-9 and abs(_shots2[3]["start"] - 10.5) < 1e-9, \
        "半秒時碼應解為 10.5s（原缺陷為 10.05s）"
    assert not any("丟鏡" in w["msg"] or "跳過" in w["msg"] for w in d2["warnings"]), \
        f"半秒時碼稿不應報丟鏡告警：{[w['msg'] for w in d2['warnings']]}"

    # ---- 2026-10-15 Agent 修復迴歸鎖：SRT 毫秒進位 ----
    #   原 `_fmt` 用 `ms=int(round((sec%1)*1000))` + `ts=int(sec)` 分立取整，
    #   小數位進位到 1000ms（如 4.9995→round(999.5)=1000）會印出非法 `,1000` 且秒位不結轉。
    #   改為「總毫秒一次取整再拆分」後，4.9995s 必須結轉為 00:00:05,000。
    _d3 = parse_md(
        "# SRT進位\n"
        "## 【投餵單元 1/1 · 段1】\n"
        "```text\n"
        "【畫幅風格】16:9 橫屏\n"
        "【場景資產】@走廊\n"
        "【核心人物】@甲\n"
        "【站位聲明】@甲（畫面左）\n"
        "【時間軸分鏡】\n"
        "0-4.9995s [鏡頭1] 中景。甲。台詞：【甲：“進位測試。”】\n"
        "```\n"
    )
    _srt3 = export_srt_text(_d3)
    assert ",1000" not in _srt3, f"SRT 毫秒不得進位成非法 ,1000：{_srt3!r}"
    assert "00:00:05,000" in _srt3, f"4.9995s 應結轉為 00:00:05,000：{_srt3!r}"
    assert "00:00:00,000 --> 00:00:05,000" in _srt3, f"進位後起止應連續：{_srt3!r}"

    # ---- 2026-11-25 迴歸鎖：多段同前綴標題不得串味 ----
    #   原 `name.split()[0]` 取 `【投餵單元` 當 token → 5 段全落到段1，
    #   鏡數變 7×5=35、總時長變 26×5=130，且 CLI 零告警。
    _unit = ("## 【投餵單元 %d/3 · 段%d】\n```text\n【畫幅風格】16:9 橫屏\n"
             "【時間軸分鏡】\n00:00-00:0%d [鏡頭1] 段%d首鏡。聲音：無。台詞：無。\n```\n")
    _d4 = parse_md("# 多段\n" + "".join(_unit % (i, i, i, i) for i in (1, 2, 3)))
    _cnt = [len(s["shots"]) for s in _d4["segments"]]
    assert _cnt == [1, 1, 1], f"每段應各解析 1 鏡，實得 {_cnt}（串味即本用例攔截目標）"
    assert len({s["raw"] for s in _d4["segments"]}) == 3, "三段應各自拿到不同投餵原文（禁共用段1）"
    assert not any("同一份投餵原文" in w["msg"] for w in _d4["warnings"]), \
        f"正常三段不應報串味告警：{[w['msg'] for w in _d4['warnings']]}"

    # ---- 2026-11-25 迴歸鎖：資產另冊掛載（看板「資產 0」事故）----
    #   M1 形態資產按冊另交，主檔只有「資產另冊：xx.md」一行聲明；
    #   原實現拿這行**只用來抑制 WARN**，不讀冊 → C 鎖選離線看板時 ④⑤ 兩欄全空。
    _side = (
        "## 一、素材清單狀態彙總表\n"
        "| 序號 | 圖號 | 素材類型 | 內容 | 狀態 | 備註 |\n"
        "|---|---|---|---|---|---|\n"
        "| 1 | 圖1 | 場景母版 | 禮堂（內·日） | ⏳待生成 | 基準件 |\n"
        "| 2 | 圖2 | 角色四格純圖板 | 陳墨（男主） | ⏳待生成 | S 級 |\n"
        "\n### 圖1 · 禮堂（場景母版）\n\n```text\n生成一張 16:9 無人空鏡場景母版。\n```\n"
        "\n## 五、群像資產卡 GRP-1（圖3 · 人工自檢）\n\n"
        "```text\n【群像資產 GRP-1】七字段：制式/年齡/體態/辨識度/密度/場景/狀態。\n```\n"
        "```text\n生成一張 16:9 B 級群像參考圖，全圖共 3 格。\n```\n"
    )
    _sa, _sp = load_sidecar_assets(_side)
    assert [x["code"] for x in _sa] == ["圖1", "圖2"], \
        f"彙總表應解出 圖1/圖2，實得 {[x['code'] for x in _sa]}"
    assert [x["code"] for x in _sp] == ["圖1", "圖3"], \
        f"圖號小節應解出 圖1/圖3，實得 {[x['code'] for x in _sp]}"
    assert "生成" in _sp[1]["raw"] and "七字段" not in _sp[1]["raw"], \
        "群像卡必須取出圖圍欄，不得取七字段圍欄"
    assert not _sp[1]["name"].startswith("五"), \
        f"圖號在括號裡的標題不得把「五、」序號當資產名：{_sp[1]['name']!r}"
    assert _sidecar_decl("> 資產另冊：02_資產交付_EP001.md（角色/場景/道具）") == "02_資產交付_EP001.md", \
        "「資產另冊：」聲明路徑解析失敗"
    print("[+] build_board_lite self-test PASSED")
    return 0


def refs_of(code, segments):
    """資產編碼 → 引用段號。

    ⚠️ 2026-11-25 修：原為 `code in seg["raw"]` 子串匹配，`圖1` 會命中 `圖10`~`圖19`、
    `圖2` 會命中 `圖20` —— 資產一多，④ 資產總表的「引用段」列就整片虛高（實測圖1 被判到全部 5 段）。
    改為「編碼 + 其後不得緊跟數字」的邊界匹配。
    """
    if not code:
        return []
    pat = re.compile(re.escape(code) + r"(?![0-9])")
    return [seg["no"] for seg in segments if pat.search(seg.get("raw") or "")]


def _sidecar_decl(md_text: str):
    """讀主檔裡的「資產另冊：xxx.md」聲明，返回聲明路徑（原樣字符串）。"""
    m = re.search(r"資產另冊\s*[:：]\s*([^\s|，,（()）)」]+?\.md)", md_text)
    return m.group(1) if m else ""


def load_sidecar_assets(side_text: str):
    """從「資產另冊」文檔讀出資產總表與出圖提示詞。

    ⚠️ 2026-11-25 新增（看板資產 0 事故）：M1 形態下資產按冊另交（`資產另冊：02_資產交付_xx.md`），
    主檔只留摘要 —— 結果 C 鎖選「離線看板」時，看板 ④ 資產總表 / ⑤ 出圖提示詞**整塊是空的**，
    資產被交付了卻不在交付物裡。原實現只把「資產另冊」用來**抑制 WARN**（`_asset_by_book`），
    識別到聲明就閉嘴，卻不把冊裡的東西讀進來 —— 等於「承認資產存在，但不給你看」。
    本函數按聲明把另冊讀回：彙總表出 ④，`### 圖N · 名稱（類型）` 小節的圍欄出 ⑤。
    """
    assets, prompts = [], []
    # ④ 資產總表：找表頭含「圖號」的表格，逐行取 圖號/類型/內容/狀態/備註
    lines = side_text.splitlines()
    hdr_i = None
    for i, l in enumerate(lines):
        if l.strip().startswith("|") and "圖號" in l:
            hdr_i = i
            break
    if hdr_i is not None:
        cells_h = [c.strip() for c in lines[hdr_i].strip().strip("|").split("|")]
        ci = {k: (cells_h.index(k) if k in cells_h else -1) for k in ("圖號", "素材類型", "內容", "狀態", "備註")}
        for l in lines[hdr_i + 1:]:
            s = l.strip()
            if not s.startswith("|"):
                break
            if "---" in s:
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            g = lambda k: cells[ci[k]] if ci[k] >= 0 and ci[k] < len(cells) else ""
            code = g("圖號")
            if not re.fullmatch(r"圖\s*\d+", code):
                continue
            extra = [x for x in (g("狀態"), g("備註")) if x]
            assets.append({"code": code.replace(" ", ""), "name": g("內容"),
                           "view": g("素材類型"), "img": code.replace(" ", ""), "extra": extra})
    # ⑤ 出圖提示詞：按 `圖N` 小節切，取該節最長圍欄（群像卡有「七字段 + 出圖」兩段，長的那個才是提示詞）
    #   兼容兩種標題寫法：`### 圖1 · 第七烙紋禮堂（場景母版）`（圖號在頭）
    #                     `## 五、群像資產卡 GRP-1 執法隊員（圖15 · …）`（圖號在括號裡）
    heads = list(re.finditer(r"^(#{2,3})\s+(.+)$", side_text, re.M))
    for k, hm in enumerate(heads):
        head = hm.group(2).strip()
        m1 = re.match(r"^(?:[一二三四五六七八九十]+、)?\s*圖\s*(\d+)\s*[·、.．\-]?\s*(.*)$", head)
        m2 = re.search(r"[（(]\s*圖\s*(\d+)", head)
        if m1:
            code, rest = "圖" + m1.group(1), m1.group(2)
        elif m2:
            # 圖號在括號裡（群像卡式標題）：去掉「五、」序號 + 去掉只含圖號的括號，別把序號當資產名
            code = "圖" + m2.group(1)
            rest = re.sub(r"^[一二三四五六七八九十]+、\s*", "", head)
            rest = re.sub(r"[（(]\s*圖\s*\d+[^）)]*[）)]", "", rest).strip(" ·、")
        else:
            continue
        end = heads[k + 1].start() if k + 1 < len(heads) else len(side_text)
        body = side_text[hm.start():end]
        fences = FENCE_RE.findall(body)
        # 出圖提示詞的判形標誌是「生成一張…」；群像卡的「七字段」圍欄不帶這句，
        # 只按長度取會偶發取錯塊，故先按標誌詞篩，篩不到再退回最長。
        _gen = [f for f in fences if "生成" in f]
        raw = (max(_gen, key=len) if _gen else (max(fences, key=len) if fences else "")).strip()
        desc = ""
        dm = re.search(r"[（(]([^）)]*)[）)]", rest)
        nm = rest
        if dm:
            desc = dm.group(1)
            nm = (rest[:dm.start()] + rest[dm.end():]).strip(" ·、")
        nm = nm.strip(" ·、")
        prompts.append({"code": code, "name": nm or code, "desc": desc, "raw": raw})
    return assets, prompts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("--out", default=None)
    ap.add_argument("--export-srt", default=None, help="同時導出 .srt 字幕文件")
    ap.add_argument("--export-csv", default=None, help="同時導出剪輯時間線 .csv 文件")
    ap.add_argument("--export-json", default=None, help="同時導出結構化 API 載荷 .json 文件")
    # ★P9：A 鎖（模型）在 P0 階段由用戶選定，七段式稿內通常不寫；看板作為回顯面
    #   需要能承接外部傳入，否則永遠報「A 鎖未鎖定」，與已鎖定的事實矛盾。
    ap.add_argument("--model", default=None, help="A 鎖模型版本（2.5 / 2.0），稿內未寫時用於回顯")
    ap.add_argument("--aspect", default=None, help="B 鎖畫幅（9:16 / 16:9 / 21:9），稿內未寫時用於回顯")
    ap.add_argument("--assets-from", default=None,
                    help="資產另冊路徑（主檔未寫「資產另冊：」或路徑不可解析時顯式指定）")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.src:
        ap.print_help()
        sys.exit(2)
    src = Path(a.src)
    if not src.exists():
        print(f"[X] 源文件不存在：{src}")
        sys.exit(1)
    data = parse_md(src.read_text(encoding="utf-8"))
    # 資產另冊掛載（M1）：聲明瞭另冊就把冊讀進來，否則看板 ④⑤ 兩欄是空的
    side_rel = a.assets_from or _sidecar_decl(src.read_text(encoding="utf-8"))
    if side_rel:
        base_real = src.parent.resolve()
        cand_path = Path(side_rel)
        if cand_path.is_absolute():
            side = None
            data["warnings"].append({"seg": 0,
                "msg": f"資產另冊路徑越界已攔截（禁止絕對路徑：{side_rel}）"})
        else:
            resolved = (base_real / cand_path).resolve()
            try:
                resolved.relative_to(base_real)
                side = resolved
            except ValueError:
                side = None
                data["warnings"].append({"seg": 0,
                    "msg": f"資產另冊路徑越界已攔截（禁止跳出項目目錄：{side_rel}）"})
        if side is not None and side.exists():
            s_assets, s_prompts = load_sidecar_assets(side.read_text(encoding="utf-8"))
            have = {x.get("code") for x in data["assets"]}
            data["assets"] += [x for x in s_assets if x["code"] not in have]
            have_p = {x.get("code") for x in data["asset_prompts"]}
            data["asset_prompts"] += [x for x in s_prompts if x["code"] not in have_p]
            for x in data["assets"]:                      # 引用段回查按合併後的段正文重算
                code = x.get("code", "")
                x["refs"] = refs_of(code, data["segments"])
            print(f"[i] 資產另冊已掛載：{side.name} → 資產 {len(s_assets)} · 出圖提示詞 {len(s_prompts)}")
        else:
            data["warnings"].append({"seg": 0,
                "msg": f"主檔聲明瞭「資產另冊：{side_rel}」，但該文件不存在——看板 ④⑤ 兩欄會是空的"})
    # 外部傳入的 A/B 鎖參數只在稿內未聲明時兜底（稿內聲明優先，絕不覆蓋稿內事實）
    if a.model and data["meta"]["模型版本"] == "未鎖定":
        data["meta"]["模型版本"] = str(a.model)
        data["warnings"] = [w for w in data["warnings"] if "未聲明【模型版本】" not in w["msg"]]
    if a.aspect and data["meta"]["畫幅"] == "未鎖定":
        data["meta"]["畫幅"] = str(a.aspect).replace("：", ":")
        data["warnings"] = [w for w in data["warnings"] if "未聲明【畫幅】" not in w["msg"]]
    out = Path(a.out) if a.out else src.with_name(src.stem + "_分鏡看板.html")
    out.write_text(build_html(data), encoding="utf-8")
    n_shots = sum(len(s["shots"]) for s in data["segments"])
    print(f"[+] 段落：{len(data['segments'])} · 鏡頭：{n_shots} · 資產：{len(data['assets'])} · 出圖提示詞：{len(data['asset_prompts'])}")
    print(f"[+] 總時長：{total_duration(data):g}s · WARN：{len(data['warnings'])}")
    for w in data["warnings"]:
        print(f"    ⚠ {w['msg']}")
    print(f"[+] 看板：{out}")
    if a.export_srt:
        Path(a.export_srt).write_text(export_srt_text(data), encoding="utf-8")
        print(f"[+] SRT 字幕：{a.export_srt}")
    if a.export_csv:
        Path(a.export_csv).write_text(export_timeline_csv_text(data), encoding="utf-8")
        print(f"[+] 剪輯時間線 CSV：{a.export_csv}")
    if a.export_json:
        Path(a.export_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] API 載荷 JSON：{a.export_json}")


if __name__ == "__main__":
    main()
