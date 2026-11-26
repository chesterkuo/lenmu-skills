#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 抗上下文壓縮滾動遞進狀態包生成器

用法:
    python scripts/rolling_checkpoint.py <劇本目錄> [--ledger 台賬.md] [--out rolling-state.md]
    python scripts/rolling_checkpoint.py --self-test
"""
import argparse
import os
import re
import sys

EP_NAME_RE = re.compile(r"^(?:EP|ep|第)?0*(\d+)(?:集)?\.md$")


def find_episodes(script_dir):
    eps = []
    if not os.path.isdir(script_dir):
        return eps
    for fn in os.listdir(script_dir):
        m = EP_NAME_RE.match(fn)
        if m:
            eps.append((int(m.group(1)), os.path.join(script_dir, fn)))
    eps.sort(key=lambda x: x[0])
    return eps


def extract_ep_summary(ep_num, text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    scenes = [re.sub(r"^(?:\[場景\]|【場景】|##?\s*場景)\s*[:：]?\s*", "", l)
              for l in lines if l.startswith(("[場景]", "【場景】"))]
    chars = []
    for l in lines:
        if l.startswith(("[人物]", "【人物】")):
            raw = re.sub(r"^(?:\[人物\]|【人物】)\s*[:：]?\s*", "", l)
            for c in re.split(r"[、,，/]", raw):
                c = re.sub(r"（[^）]*）|\([^)]*\)", "", c).strip()
                if c and c not in chars:
                    chars.append(c)
    hook = ""
    m = re.search(r"【本集斷章卡點】\s*[:：]?\s*(.+)", text)
    if m:
        hook = m.group(1).strip()
    money = re.findall(r"\d+(?:\.\d+)?\s*(?:萬|億|千|百)?(?:元|兩|塊)", text)
    tail_actions = [l for l in lines if l.startswith("△")][-2:]
    return {
        "ep": ep_num,
        "scenes": scenes,
        "chars": chars,
        "hook": hook,
        "money": list(dict.fromkeys(money))[:8],
        "tail_actions": tail_actions,
    }


def build_checkpoint(script_dir, ledger_path=None):
    eps = find_episodes(script_dir)
    if not eps:
        return "# 滾動遞進狀態包\n\n> 未在目錄中發現已寫單集劇本（支持 `EP01.md` / `1.md` / `第1集.md`）。\n"

    summaries = []
    all_chars = []
    all_money = []
    for num, path in eps:
        txt = open(path, encoding="utf-8-sig").read()
        s = extract_ep_summary(num, txt)
        summaries.append(s)
        for c in s["chars"]:
            if c not in all_chars:
                all_chars.append(c)
        for m in s["money"]:
            if m not in all_money:
                all_money.append(m)

    ep_range = f"第 {summaries[0]['ep']}~{summaries[-1]['ep']} 集（共 {len(summaries)} 集）"
    recent = summaries[-2:]

    out = [
        f"# 抗上下文壓縮滾動遞進狀態包（{ep_range}）",
        "",
        "> 批量連寫時，僅掛載本狀態包 + 最近 1~2 集尾段即可續寫，嚴禁把前序全部正文塞進上下文。",
        "",
        "## 一、全局硬事實錨定",
        f"- **已寫集數**：{ep_range}",
        f"- **已出場具名角色**：{'、'.join(all_chars) if all_chars else '（未標註 [人物] 行）'}",
        f"- **出現過的關鍵金額/數值**：{'、'.join(all_money) if all_money else '（暫無）'}",
    ]
    if ledger_path and os.path.isfile(ledger_path):
        out.append(f"- **關聯台賬**：`{os.path.basename(ledger_path)}`（已掛載）")

    out += ["", "## 二、最近兩集尾態與接續接口（下一集開頭必接）"]
    for s in recent:
        out.append(f"### 第 {s['ep']} 集")
        out.append(f"- **末場空間**：{s['scenes'][-1] if s['scenes'] else '（未標註）'}")
        out.append(f"- **尾段動作**：{' / '.join(s['tail_actions']) if s['tail_actions'] else '（無）'}")
        out.append(f"- **斷章卡點**：{s['hook'] or '（缺失）'}")
        out.append("")

    return "\n".join(out)


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ep1 = os.path.join(td, "EP01.md")
        ep2 = os.path.join(td, "EP02.md")
        open(ep1, "w", encoding="utf-8").write(
            "第【1】集\n[場景]：內景·正堂·日\n[人物]：甲（主角）、乙\n△ 甲把二十萬兩銀票拍在桌上。\n【本集斷章卡點】：門被踹開。（黑屏）\n"
        )
        open(ep2, "w", encoding="utf-8").write(
            "第【2】集\n[場景]：內景·庫房·夜\n[人物]：甲、丙\n△ 甲鎖上庫房銅鎖。\n【本集斷章卡點】：火把亮起。（黑屏）\n"
        )
        md = build_checkpoint(td)
        assert "第 1~2 集" in md, "應識別集數範圍"
        assert "甲" in md and "丙" in md, "應彙總出場角色"
        assert "二十萬兩" in md or "20" in md or "庫房" in md, "應提取關鍵尾態"
    print("[+] rolling_checkpoint.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="short-drama-factory v5.1 滾動遞進狀態包生成器")
    p.add_argument("script_dir", help="已寫單集劇本目錄")
    p.add_argument("--ledger", default=None, help="台賬路徑")
    p.add_argument("--out", default=None, help="輸出文件路徑（默認打印到 stdout）")
    args = p.parse_args()
    md = build_checkpoint(args.script_dir, args.ledger)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] 已生成滾動狀態包: {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
