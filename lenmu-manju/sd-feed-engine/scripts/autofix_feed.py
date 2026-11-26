#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sd-feed-engine V8.2.0-SLIM 提示詞一鍵防穿幫清洗器（--autofix）

功能：
1. 自動清理【畫幅風格】【STYLE】【場景資產】【核心人物】【PERFORMANCE】【時間軸分鏡】【音效】前中段誤寫的「無文字水印/無字幕/無亂碼/針對性禁項/嚴禁…」等禁項，並全部歸攏到文末【強制禁止項】；
2. 自動校正【STYLE｜視覺風格】緊跟【畫幅風格】之下、【PERFORMANCE｜表演與動作】緊跟【核心人物】之下（不再放在文末）。

用法:
    python sd-feed-engine/scripts/autofix_feed.py <投餵稿.md> [-o fixed.md]
    python sd-feed-engine/scripts/autofix_feed.py --self-test
"""
import argparse
import re
import sys

EARLY_NEG_RE = re.compile(r"[，,、\s]*(?:無文字水印|無文字|無水印|無字幕|無亂碼)")


def autofix_text(text):
    collected_bans = []
    style_block = []
    perf_block = []
    other_lines = []

    cur_tag = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("【STYLE｜") or s.startswith("【STYLE|"):
            cur_tag = "STYLE"
            style_block.append(line)
            continue
        if s.startswith("【PERFORMANCE｜") or s.startswith("【PERFORMANCE|"):
            cur_tag = "PERF"
            perf_block.append(line)
            continue
        if s.startswith("【"):
            cur_tag = "OTHER"

        if cur_tag == "STYLE":
            if s.startswith("針對性禁項"):
                collected_bans.append(re.sub(r"^針對性禁項\s*[:：]\s*", "", s).replace(" / ", "、"))
                continue
            style_block.append(line)
            continue
        if cur_tag == "PERF":
            m_ban = re.search(r"[，,；;]?\s*(嚴禁[^，。；\n]+)", line)
            if m_ban:
                collected_bans.append(m_ban.group(1))
                line = line[:m_ban.start()] + line[m_ban.end():]
                line = line.rstrip("，,；; ")
            if line.strip():
                perf_block.append(line)
            continue

        other_lines.append(line)

    # Strip early negative words from non-ban lines & reorder STYLE/PERF right after 畫幅風格 / 核心人物
    out_lines = []
    in_ban_section = False
    removed_count = len(collected_bans)

    def _insert_after_section(lines_buf, target_prefix, block_to_insert):
        if not block_to_insert:
            return lines_buf
        res = []
        inserted = False
        i = 0
        while i < len(lines_buf):
            res.append(lines_buf[i])
            if not inserted and lines_buf[i].strip().startswith(target_prefix):
                i += 1
                while i < len(lines_buf) and not lines_buf[i].strip().startswith("【"):
                    res.append(lines_buf[i])
                    i += 1
                res.extend(block_to_insert)
                inserted = True
                continue
            i += 1
        if not inserted:
            res = block_to_insert + res
        return res

    for line in other_lines:
        s = line.strip()
        if s.startswith("【強制禁止項】"):
            in_ban_section = True
            if collected_bans:
                extra = "、".join(collected_bans)
                line = line.rstrip("。") + "，" + extra + "。"
            if "水印" not in line and "字幕" not in line:
                line = line.rstrip("。") + "，禁止任何字幕、文字、亂碼或水印。"
            out_lines.append(line)
            continue
        if s.startswith("【") and not s.startswith("【強制禁止項】"):
            in_ban_section = False
        if not in_ban_section and EARLY_NEG_RE.search(line):
            new_line = EARLY_NEG_RE.sub("", line)
            new_line = re.sub(r"([：:])[，,、\s]+", r"\1", new_line)
            if new_line != line:
                removed_count += 1
            out_lines.append(new_line)
        else:
            out_lines.append(line)

    if not in_ban_section and collected_bans and not any(l.strip().startswith("【強制禁止項】") for l in out_lines):
        out_lines.append("【強制禁止項】：" + "、".join(collected_bans) + "，禁止任何字幕、文字、亂碼或水印。")

    out_lines = _insert_after_section(out_lines, "【畫幅風格】", style_block)
    out_lines = _insert_after_section(out_lines, "【核心人物】", perf_block)

    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else ""), removed_count


def self_test():
    sample = (
        "【畫幅風格】：16:9 橫屏，電影寫實，無文字水印。\n"
        "【場景資產】：@SCN-破廟\n"
        "【核心人物】：@主角（30歲男）\n"
        "【時間軸分鏡】：00:00-00:03 特寫，紙面無亂碼。\n"
        "【強制禁止項】：禁止穿模。\n"
        "【STYLE｜視覺風格 · 全片鎖死】\n"
        "成像底層：虛幻5 CG\n"
        "針對性禁項：禁2D卡通描邊 / 禁現代建築元素\n"
        "【PERFORMANCE｜表演與動作 · 全片鎖死】\n"
        "每招必現真實發力重量感，嚴禁輕飄懸浮\n"
    )
    fixed, cnt = autofix_text(sample)
    assert cnt >= 4, f"應清理並歸攏至少4處禁項，實得 {cnt}"
    assert "針對性禁項" not in fixed.split("【強制禁止項】")[0]
    assert "嚴禁輕飄懸浮" not in fixed.split("【強制禁止項】")[0]
    assert fixed.index("【STYLE｜") < fixed.index("【場景資產】")
    assert fixed.index("【PERFORMANCE｜") < fixed.index("【時間軸分鏡】")
    assert "禁2D卡通描邊" in fixed.split("【強制禁止項】")[1]
    assert "嚴禁輕飄懸浮" in fixed.split("【強制禁止項】")[1]
    print("[+] autofix_feed.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="sd-feed-engine V8.2.0-SLIM 提示詞一鍵防穿幫清洗器")
    p.add_argument("feed_md", help="待清洗投餵稿 .md")
    p.add_argument("-o", "--out", default=None, help="輸出路徑（不傳則覆蓋原文件）")
    args = p.parse_args()
    txt = open(args.feed_md, encoding="utf-8").read()
    fixed, cnt = autofix_text(txt)
    target = args.out or args.feed_md
    with open(target, "w", encoding="utf-8").write(fixed) if False else open(target, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"[+] 已調整 STYLE/PERFORMANCE 落位並歸攏 {cnt} 處禁項至文末【強制禁止項】 -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
