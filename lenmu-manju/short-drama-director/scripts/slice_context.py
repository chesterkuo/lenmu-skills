#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
slice_context.py · 動態原文切片器（Phase Context Slicer · 非手寫摘要！）
設計動機：
  全包 140 份 Markdown 合計 2.46MB。若一次性塞進上下文，大模型必然發生「中間注意力坍塌（Lost in the Middle）」。
  而此前刪除「運行態微核 agent-system-core.md」是因為手寫摘要不隨原文同步。
  本腳本直接從**權威原文**按「當前階段 P0~P5 + 打戲檔 R1~R3 + 模型版本 2.5/2.0 + 素材形態 M0~M2」
  動態解析必讀文件，以完整章節分頁輸出原文與 coverage/未加載範圍；不預填已讀回執。
用法：
  python3 scripts/slice_context.py --stage P3 --combat R1 --model 2.5 --mode M1
  python3 scripts/slice_context.py --self-test
"""
import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SUITE_DIR = os.path.dirname(BASE_DIR)

STAGE_FILES = {
    "P0": [
        "short-drama-director/references/asset-first-pipeline.md",
        "short-drama-director/references/asset-delivery-modes.md",
        "short-drama-director/references/aspect-ratio-adaptation.md",
        "sd-decision-engine/SKILL.md",
        "sd-decision-engine/references/context-mapping.md",
        "sd-decision-engine/references/emotion-anchor-table.md",
        "sd-decision-engine/references/forbidden-zone-whitelist.md",
    ],
    "P1": [
        "sd-script-engine/SKILL.md",
        "sd-script-engine/references/six-stage-pipeline.md",
        "sd-script-engine/references/dialogue-naturalization.md",
        "short-drama-director/references/dialogue-doctor-7d.md",
        "sd-script-engine/references/story-bible-and-ip.md",
        "sd-script-engine/references/episode-planning.md",
    ],
    "P2": [
        "sd-asset-engine/SKILL.md",
        "sd-asset-engine/references/three-list-extraction.md",
        "sd-asset-engine/references/scene-grid-template.md",
        "sd-asset-engine/references/character-portrait-templates.md",
        "sd-asset-engine/references/character-diversity-engine.md",
        "sd-asset-engine/references/prop-template.md",
        "short-drama-director/references/asset-spatial-ledger.md",
        "short-drama-director/references/asset-delivery-modes.md",
    ],
    "P3": [
        "short-drama-director/references/acting-direction.md",
        "short-drama-director/references/blocking-direction.md",
        "short-drama-director/references/wenxi-wuxi-storyboard-logic.md",
        "short-drama-director/references/cross-segment-spatial-handoff.md",
        "short-drama-director/references/blooper-prevention-playbook.md",
        "sd-storyboard-engine/SKILL.md",
        "sd-storyboard-engine/references/short-drama-camera-system.md",
        "sd-storyboard-engine/references/shot-economy-and-acting.md",
        "sd-storyboard-engine/references/storyboard-sheet-template.md",
        "sd-storyboard-engine/references/plot-deduction-grid.md",
    ],
    "P4": [
        "sd-feed-engine/SKILL.md",
        "sd-feed-engine/references/feed-mode-and-gates.md",
        "sd-feed-engine/references/asset-mapping-and-rules.md",
        "short-drama-director/references/model-adapters.md",
        "short-drama-director/references/segment-splicing.md",
        "short-drama-director/references/prompt-feeding-checklist.md",
    ],
    "P5": [
        "sd-qc-engine/SKILL.md",
        "sd-qc-engine/references/machine-check-manual.md",
        "sd-qc-engine/references/continuity-ledger.md",
        "short-drama-director/references/quality-gate-review.md",
        "short-drama-director/references/storyboard-board-lite.md",
    ],
}

COMBAT_FILES = {
    "R1": [
        "sd-real-engine/SKILL.md",
        "sd-real-engine/references/r1-combat-core.md",
        "sd-real-engine/references/kinetic-chain-11.md",
        "sd-real-engine/references/defense-evasion-rules.md",
        "sd-real-engine/references/impact-physics.md",
        "sd-real-engine/references/camera-action-specs.md",
        "sd-real-engine/references/render-adapters.md",
    ],
    "R2": [
        "sd-combat-engine/SKILL.md",
        "sd-combat-engine/references/combat-iron-laws.md",
        "sd-combat-engine/references/combat-construction.md",
        "sd-combat-engine/references/eight-sentence-masters.md",
        "sd-combat-engine/references/combat-intensity-guardrails.md",
        "sd-combat-engine/references/combat-rhythm-and-load-guardrails.md",
        "sd-combat-engine/references/tier-and-finisher-system.md",
    ],
    "R3": [
        "sd-xuanhuan-engine/SKILL.md",
        "sd-xuanhuan-engine/references/core-combat-laws.md",
        "sd-xuanhuan-engine/references/xuanhuan-elements-vfx.md",
        "sd-xuanhuan-engine/references/grand-scale-domains.md",
        "sd-xuanhuan-engine/references/camera-specs-15modes.md",
        "sd-combat-engine/references/combat-intensity-guardrails.md",
        "sd-combat-engine/references/combat-rhythm-and-load-guardrails.md",
    ],
}


def resolve_files(stage, combat="none", model="2.5", source="1", previs=False):
    files = list(STAGE_FILES.get(stage.upper(), STAGE_FILES["P3"]))
    if source in ("3", "4") and stage.upper() in ("P0", "P1"):
        files.extend([
            "sd-recon-engine/SKILL.md",
            "sd-recon-engine/references/source-ladder.md",
            "sd-recon-engine/references/recon-evidence.md",
            "sd-recon-engine/references/intel-card.md",
        ])
    if stage.upper() in ("P3", "P4") and combat.upper() in COMBAT_FILES:
        files.extend(COMBAT_FILES[combat.upper()])
    if previs:
        files.append("sd-storyboard-engine/references/p45-previs-storyboard.md")
    # 去重保序
    seen = set()
    out = []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def chapter_pages(raw_lines, line_budget=40):
    """按最外層正文標題分章；預算是軟限，不拆章節、代碼圍欄或表格。"""
    if line_budget < 1:
        raise ValueError("--lines 必須為正整數")
    headings = []
    fence = None
    frontmatter = bool(raw_lines and raw_lines[0] == "---")
    for i, line in enumerate(raw_lines):
        if frontmatter:
            if i and line == "---":
                frontmatter = False
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is None:
            heading = re.match(r"^(#{1,6})\s+", line)
            if heading:
                headings.append((i, len(heading[1])))
    # 單一文檔標題歸入前言；多個一級標題則各自成章。
    if headings and headings[0][1] == 1 and sum(level == 1 for _, level in headings) == 1:
        headings = headings[1:]
    level = min((level for _, level in headings), default=0)
    starts = sorted({0, *(i for i, depth in headings if depth == level)})
    boundaries = starts + [len(raw_lines)]
    pages = []
    for start, end in zip(boundaries, boundaries[1:]):
        if start == end:
            continue
        if pages and end - pages[-1][0] <= line_budget:
            pages[-1] = (pages[-1][0], end)
        else:
            pages.append((start, end))
    return pages


def build_slice(stage, combat="none", model="2.5", mode="M1", max_lines_per_file=45,
                source="1", previs=False, page=1):
    if page < 1 or max_lines_per_file < 1:
        raise ValueError("--page 與 --lines 必須為正整數")
    files = resolve_files(stage, combat, model, source, previs)
    records = []
    for rel in files:
        full_p = os.path.join(SUITE_DIR, rel)
        if not os.path.isfile(full_p):
            records.append((rel, None, []))
            continue
        with open(full_p, encoding="utf-8") as handle:
            raw = handle.read().splitlines()
        records.append((rel, raw, chapter_pages(raw, max_lines_per_file)))
    page_count = max((len(pages) for _, _, pages in records), default=0)
    if page > max(1, page_count):
        raise ValueError(f"頁碼越界：本次路由共 {page_count} 頁")
    lines = [
        f"# {stage.upper()} 階段完整章節原文分頁 · 第 {page}/{max(1, page_count)} 頁",
        f"> 素材形態：{mode}；來源：{source}；預演：{'啟用' if previs else '未啟用'}",
        "> coverage 僅表示本次實際輸出範圍，不代表已讀或已執行。未加載內容須續頁讀取。",
        "> 不記錄歷史閱讀狀態；前頁也不自動算已讀。回執須由執行者實際閱讀後填寫，不能直接粘貼為已讀證明。",
        "",
        "## coverage / 未加載清單",
    ]
    bodies = []
    for rel, raw, pages in records:
        if raw is None:
            lines.append(f"- `{rel}`：coverage=0；缺失；未加載=全文（無法確定行數）")
            continue
        selected = pages[page - 1] if page <= len(pages) else None
        start, end = selected or (0, 0)
        unread = []
        if start:
            unread.append(f"L1-L{start}")
        if end < len(raw):
            unread.append(f"L{end + 1}-L{len(raw)}")
        span = f"L{start + 1}-L{end}" if selected else "無"
        lines.append(f"- `{rel}`：coverage={end - start}/{len(raw)} 行；本頁範圍={span}；"
                     f"文件頁數={len(pages)}；未加載={'、'.join(unread) or '無'}")
        if selected:
            bodies.extend([f"\n## 原文 `{rel}` · {span}", *raw[start:end]])
    command = (f"python scripts/slice_context.py --stage {stage.upper()}"
               f" --combat {combat} --model {model} --mode {mode} --source {source}"
               f" --lines {max_lines_per_file}" + (" --previs" if previs else ""))
    lines.append(f"\n續頁：`{command} --page {page + 1}`" if page < page_count
                 else "\n已到最後一頁；這不代表此前頁已讀，按 --page N 回讀未加載範圍。")
    return "\n".join(lines + bodies)


# 各階段「每集」經驗產出字數（報賬默認值 · 用戶可用 --chars-per-episode 覆蓋）
STAGE_OUTPUT_CHARS = {
    "P0": 2000,   # 立項基準表
    "P1": 4500,   # 一集劇本正文
    "P2": 6000,   # 一集所需資產提示詞（角色/場景/道具）
    "P3": 12000,  # 一集分鏡（鏡數 × 每鏡字段）
    "P4": 11000,  # 一集投餵稿（分組 + 七段式）
    "P5": 3000,   # 一集質檢卡
}
BATCH_TOKEN_LIMIT = 8000  # 預算鐵律第 3 條：單批輸出上限


def estimate_tokens(text):
    """保守估算 token 數（不追求精確，只用於報賬）：CJK ≈ 1.05 token/字，其餘 ≈ 3.6 字符/token。"""
    cjk = 0
    for ch in text:
        o = ord(ch)
        if 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
            cjk += 1
    return int(cjk * 1.05 + (len(text) - cjk) / 3.6)


def build_estimate(stage, combat="none", model="2.5", mode="M1",
                   lines=40, episodes=1, chars_per_episode=0, source="1", previs=False, page=1):
    """預算報賬：輸入側真實佔用 + 輸出側應切幾批（預算鐵律第 1 條）。"""
    files = resolve_files(stage, combat, model, source, previs)
    slice_tok = estimate_tokens(build_slice(stage, combat, model, mode, lines, source, previs, page))
    full_tok = 0
    for rel in files:
        fp = os.path.join(SUITE_DIR, rel)
        if os.path.isfile(fp):
            with open(fp, encoding="utf-8") as handle:
                full_tok += estimate_tokens(handle.read())

    stg = stage.upper()
    per_ep_chars = chars_per_episode or STAGE_OUTPUT_CHARS.get(stg, 6000)
    per_ep_tok = int(per_ep_chars * 1.05)
    per_ep_batches = max(1, -(-per_ep_tok // BATCH_TOKEN_LIMIT))
    total_tok = per_ep_tok * episodes
    total_batches = per_ep_batches * episodes
    hard_cut = max(1, -(-total_tok // BATCH_TOKEN_LIMIT))

    out = [
        "=" * 58,
        f"💰 預算報賬 · {stg} 階段（預算鐵律第 1 條 · 禁止心算）",
        "=" * 58,
        f"必讀權威文件      : {len(files)} 份（已按打戲檔/模型/素材形態解析）",
        f"切片後輸入        : ≈ {slice_tok:,} token   ← 當前頁輸出估算，不是全文已讀證明",
        f"若通讀本階段全文  : ≈ {full_tok:,} token   ← 可分章節續頁通讀，僅作預算對照（{full_tok // max(slice_tok,1)}× 倍）",
        "",
        f"預計產出          : {episodes} 集 × {per_ep_chars:,} 字 = {episodes * per_ep_chars:,} 字"
        f" ≈ {total_tok:,} token",
        f"單批上限          : {BATCH_TOKEN_LIMIT:,} token（≈ {int(BATCH_TOKEN_LIMIT / 1.05):,} 漢字）",
        f"按 token 硬切      : {hard_cut} 批 ← ⛔ 僅參考，硬切會劈開整場戲",
        f"按結構切（推薦）   : 每集 ≈ {per_ep_tok:,} token → 每集拆 {per_ep_batches} 批"
        f" → 共 {total_batches} 批（集/場邊界切）",
        "",
        "確認策略          : ① 自動續跑（默認，僅 P1/P2/P3/P4 階段門停）",
        "                    ② 逐批確認（長劇集精修時選）",
        "                    強制停：超預算 1.5 倍 / 機檢 FAIL / 需拍板岔路",
        "=" * 58,
    ]
    return "\n".join(out)


def self_test():
    for stg in ("P0", "P1", "P2", "P3", "P4", "P5"):
        out = build_slice(stg, combat="R1" if stg == "P3" else "none", max_lines_per_file=10)
        assert "coverage / 未加載清單" in out and "；缺失；" not in out, f"{stg} slice failed"
        assert "> 已讀子庫：" not in out, f"{stg} 虛假已讀"
    est = build_estimate("P3", combat="R1", episodes=10)
    assert "預算報賬" in est and "按結構切" in est, "estimate failed"
    print("[+] slice_context self-test PASSED（slice 6/6 + estimate 1/1）")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫劇老李 V8.2.0-SLIM 動態原文切片器")
    ap.add_argument("--stage", default="P3", choices=["P0", "P1", "P2", "P3", "P4", "P5", "p0", "p1", "p2", "p3", "p4", "p5"])
    ap.add_argument("--combat", default="none", choices=["none", "R1", "R2", "R3", "r1", "r2", "r3"])
    ap.add_argument("--model", default="2.5", choices=["2.5", "2.0"])
    ap.add_argument("--mode", default="M1", choices=["M0", "M1", "M2"])
    ap.add_argument("--lines", type=int, default=40, help="每文件每頁軟行數預算；完整章節可超限，不截斷")
    ap.add_argument("--page", type=int, default=1, help="讀取第 N 頁；不自動累計已讀狀態")
    ap.add_argument("--source", default="1", choices=["1", "2", "3", "4"], help="素材來源鎖")
    ap.add_argument("--previs", action="store_true", help="加載 P4.5 預演故事板權威原文")
    ap.add_argument("--estimate", action="store_true", help="預算報賬模式：算輸入佔用與應切批數（預算鐵律第 1 條）")
    ap.add_argument("--episodes", type=int, default=1, help="預計集數（配合 --estimate）")
    ap.add_argument("--chars-per-episode", type=int, default=0, help="每集預計產出字數（0=用階段經驗值）")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.lines < 1 or args.page < 1 or args.episodes < 1 or args.chars_per_episode < 0:
        ap.error("lines/page/episodes 必須為正整數，chars-per-episode 不得為負")
    try:
        if args.estimate:
            print(build_estimate(args.stage, args.combat, args.model, args.mode,
                                 args.lines, args.episodes, args.chars_per_episode,
                                 args.source, args.previs, args.page))
        else:
            print(build_slice(args.stage, args.combat, args.model, args.mode,
                              args.lines, args.source, args.previs, args.page))
    except ValueError as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
