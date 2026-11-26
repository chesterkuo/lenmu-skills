#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lenmu 接線器：把一段七段式投餵稿 + 《資產圖冊》圖號表，換算成 Lenmu generate_video 的參數。

做三件事：
  1. 找出本段提示詞引用的 圖N / 視頻N / 音頻N，逐個查 media_id（查不到 = 該資產還沒在 Lenmu 生成，FAIL）；
  2. 按圖號升序排出 reference_media_ids，並把提示詞裡的全局圖號改寫成 Lenmu 的引用記號
     [Image k] / [Video k] / [Audio k]（k = 本次調用裡該類素材的第幾個）。
     Lenmu 只認這種記號：全局 圖1/圖2/圖5 掛三張 → 送出的提示詞寫 [Image 1]/[Image 2]/[Image 3]；
     提示詞沒引用到的素材，Lenmu 會自動在文末補一行「References: [Image k]」；
  3. 核對模型上限（參考數量 / 段長 / 畫幅 / 提示詞長度）。

用法：
    python3 lenmu_wiring.py --prompt 段01.txt --wiring 圖冊.json --model 2.5 --aspect 16:9 --duration 28
    python3 lenmu_wiring.py --self-test

圖冊.json 格式（鍵 = 全局編號，值 = Lenmu media_id 或帶 media_id 的對象）：
    {"圖1": {"media_id": "…", "name": "客棧大堂·場景母版"}, "圖3": "…", "視頻1": "…"}

輸出：JSON（ok / errors / warnings / args / mapping / prompt）。有 errors 時退出碼 1，此時不得調用 generate_video。
"""
import argparse
import json
import re
import sys

# list_models 2026-11 的數值；Lenmu 調整後以 list_models 為準，用 --limits 覆蓋
MODELS = {
    "2.5": {"id": "byteplus/seedance-2.5", "dur": (4, 30),
            "max": {"image": 30, "video": 10, "audio": 10, "total": 50}},
    "2.0": {"id": "byteplus/seedance-2.0", "dur": (4, 15),
            "max": {"image": 8, "video": 8, "audio": 3, "total": 8}},
}
SIZES = {("16:9", 720): "1280x720", ("16:9", 1080): "1920x1080",
         ("9:16", 720): "720x1280", ("9:16", 1080): "1080x1920"}
PROMPT_MAX = 4000
KINDS = (("image", "圖"), ("video", "視頻"), ("audio", "音頻"))
# 「構圖3」「地圖2」這類不是參考圖編號；繁簡兩種寫法、外層方括號與 @ 前綴都接受，
# 稿裡已經寫成 [Image N] 的也當作全局編號處理
REF_RE = {
    "image": re.compile(r"\[?@?(?:(?<![構构地藍蓝截插貼贴意試试企])[圖图]|Image)\s?(\d+)\]?"),
    "video": re.compile(r"\[?@?(?:[視视][頻频]|Video)\s?(\d+)\]?"),
    "audio": re.compile(r"\[?@?(?:音[頻频]|Audio)\s?(\d+)\]?"),
}
TOKEN = {"image": "Image", "video": "Video", "audio": "Audio"}
ALT = {"圖": "图", "視頻": "视频", "音頻": "音频"}
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")


def _media_id(entry):
    if isinstance(entry, dict):
        return entry.get("media_id") or ""
    return entry or ""


def wire(prompt, wiring, model="2.5", aspect="16:9", duration=None, res=720,
         model_id=None, limits=None):
    errors, warnings, mapping, ref_ids = [], [], [], []
    spec = MODELS[model]
    lim = dict(spec["max"], **(limits or {}))
    counts = {}
    new_prompt = prompt
    for kind, label in KINDS:
        nums = sorted({int(n) for n in REF_RE[kind].findall(prompt)})
        counts[kind] = len(nums)
        renum = {}
        for pos, n in enumerate(nums, 1):
            key = f"{label}{n}"
            entry = wiring.get(key) or wiring.get(ALT[label] + str(n))  # 圖冊鍵繁簡皆可
            mid = _media_id(entry)
            if not mid:
                errors.append(f"{key} 在圖冊裡沒有 media_id（資產尚未在 Lenmu 生成或未登記）")
            elif not UUID_RE.match(mid):
                errors.append(f"{key} 的 media_id 格式不對：{mid}")
            else:
                ref_ids.append(mid)
            renum[n] = pos
            mapping.append({"global": key, "call": f"[{TOKEN[kind]} {pos}]", "media_id": mid,
                            "name": entry.get("name", "") if isinstance(entry, dict) else ""})
        if renum:
            new_prompt = REF_RE[kind].sub(
                lambda m, r=renum, tk=TOKEN[kind]: f"[{tk} {r[int(m.group(1))]}]", new_prompt)
        if counts[kind] > lim[kind]:
            errors.append(f"{label}參考 {counts[kind]} 個，超過 Seedance {model} 在 Lenmu 的上限 {lim[kind]}")
    total = sum(counts.values())
    if total > lim["total"]:
        errors.append(f"參考素材合計 {total} 個，超過 Seedance {model} 在 Lenmu 的總上限 {lim['total']}")
    if total == 0:
        warnings.append("本段沒有引用任何參考素材（M0 寫法）：一致性只靠文字鎖")
    if mapping:
        warnings.append("圖號已改寫成 Lenmu 記號（見 mapping）；回報用戶時全局圖號與 [Image k] 兩套都要給")

    size = SIZES.get((aspect, res))
    if not size:
        errors.append(f"畫幅 {aspect}／{res}p 不在 Lenmu 的 Seedance 尺寸裡（只有 16:9、9:16 的 720p／1080p）"
                      "：21:9 需先和用戶改定畫幅或約定後期裁切")
    lo, hi = spec["dur"]
    if duration is None:
        errors.append("缺 --duration（本段整秒時長）")
    elif not lo <= duration <= hi:
        errors.append(f"段長 {duration}s 超出 Seedance {model} 的 {lo}~{hi}s")
    if len(new_prompt) > PROMPT_MAX:
        errors.append(f"提示詞 {len(new_prompt)} 字，超過 Lenmu 的 {PROMPT_MAX} 字上限：回 sd-feed-engine 壓字數或拆段")

    args = {"model": model_id or spec["id"], "prompt": new_prompt, "size": size,
            "duration_seconds": duration, "generate_audio": True}
    if ref_ids:
        args["reference_media_ids"] = ref_ids
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "args": args, "mapping": mapping, "prompt_chars": len(new_prompt)}


def self_test():
    a, b, c = ("00000000-0000-4000-8000-00000000000%d" % i for i in (1, 2, 5))
    wiring = {"圖1": {"media_id": a, "name": "場景"}, "圖2": b, "圖5": c}
    p = "【場景資產】@SCN-客棧（參考圖1）【核心人物】@林越（圖2）、@玉佩（圖5）鏡1：構圖1/3 留白，圖5 特寫"
    r = wire(p, wiring, "2.0", "9:16", 12)
    assert r["ok"], r["errors"]
    assert r["args"]["reference_media_ids"] == [a, b, c]
    assert r["args"]["prompt"].count("[Image 3]") == 2 and "圖5" not in r["args"]["prompt"]
    assert "（參考[Image 1]）" in r["args"]["prompt"] and "@林越（[Image 2]）" in r["args"]["prompt"]
    assert [m["call"] for m in r["mapping"]] == ["[Image 1]", "[Image 2]", "[Image 3]"]
    r2 = wire("[圖5] 與 图2、[Image 1]、視頻1", dict(wiring, 視頻1=a), "2.5", "16:9", 20)
    assert r2["args"]["prompt"] == "[Image 3] 與 [Image 2]、[Image 1]、[Video 1]", r2["args"]["prompt"]
    assert r2["args"]["reference_media_ids"] == [a, b, c, a]
    assert wire("圖1", {"图1": a}, "2.5", "16:9", 12)["ok"], "圖冊鍵應繁簡皆可"
    assert "構圖1/3" in r["args"]["prompt"], "構圖 不應被當作圖號"
    assert r["args"]["size"] == "720x1280" and r["args"]["model"] == "byteplus/seedance-2.0"
    r = wire("@林越（圖2）、@反派（圖9）", wiring, "2.5", "16:9", 28)
    assert not r["ok"] and "圖9" in r["errors"][0]
    r = wire("圖1", wiring, "2.0", "21:9", 20)
    assert len(r["errors"]) == 2, r["errors"]            # 畫幅 + 段長
    many = {f"圖{i}": a for i in range(1, 10)}
    r = wire("".join(f"圖{i} " for i in range(1, 10)), many, "2.0", "16:9", 10)
    assert any("上限 8" in e for e in r["errors"])
    r = wire("圖1" + "字" * 4000, wiring, "2.5", "16:9", 30)
    assert any("4000" in e for e in r["errors"])
    r = wire("純文字段", {}, "2.5", "16:9", 12)
    assert r["ok"] and "reference_media_ids" not in r["args"] and r["warnings"]
    print("[+] lenmu_wiring.py self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description="七段式投餵稿 → Lenmu generate_video 參數")
    ap.add_argument("--prompt", help="單段投餵稿文本文件（只含這一段的七段式）")
    ap.add_argument("--wiring", help="圖冊 JSON：全局圖號 → media_id")
    ap.add_argument("--model", choices=sorted(MODELS), default="2.5", help="A 鎖")
    ap.add_argument("--model-id", help="覆蓋 Lenmu 模型 id（同一版本的 flash / mini / fast 等）")
    ap.add_argument("--aspect", default="16:9", help="B 鎖")
    ap.add_argument("--res", type=int, default=720, choices=(720, 1080))
    ap.add_argument("--duration", type=int, help="本段整秒時長")
    ap.add_argument("--limits", help='覆蓋上限的 JSON，如 {"image":8,"total":8}')
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.prompt and a.wiring):
        ap.error("需要 --prompt 和 --wiring")
    with open(a.prompt, encoding="utf-8") as f:
        prompt = f.read().strip()
    with open(a.wiring, encoding="utf-8") as f:
        wiring = json.load(f)
    r = wire(prompt, wiring, a.model, a.aspect, a.duration, a.res, a.model_id,
             json.loads(a.limits) if a.limits else None)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
