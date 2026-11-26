#!/usr/bin/env python3
"""把一整條 TTS 旁白依 script.json 的段落切成 WAV。
用法：python3 split_narration.py narration.mp3 script.json out_dir/ [cues.json]
cues.json = Lenmu 字幕的句子時間（get_node 讀 film 節點的 subtitles.cues）。有它才切得準；
沒有時只能靠句間停頓估計，切點要請用戶聽過。"""
import json, re, subprocess, sys
from pathlib import Path
SR = 48000
WORD = r"[぀-ヿ一-鿿가-힯]|[A-Za-z0-9]+"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def duration_s(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)]).stdout.strip())

def silences(path, noise_db=-35, min_d=0.20):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                          f"silencedetect=noise={noise_db}dB:d={min_d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    e = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", err)]
    return [((a + b) / 2, b - a) for a, b in zip(s, e)]

def spoken_len(text):
    # 漢字、日文假名、韓文各算一個音節，英數算一個詞；句號類停頓算 2、逗號類算 1
    units = len(re.findall(WORD, text))
    return units + 2 * len(re.findall(r"[。．.！!？?…]", text)) + len(re.findall(r"[，,、；;：:]", text))

def norm(text):
    return "".join(re.findall(WORD, text)).lower()

def find_cues(obj):
    """從 cues.json 找出句子清單：可以直接是清單，也可以是 get_node 的整包輸出"""
    if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "text" in obj[0]:
        return obj
    for v in (obj.values() if isinstance(obj, dict) else obj if isinstance(obj, list) else []):
        r = find_cues(v)
        if r:
            return r
    return None

def cuts_from_cues(segs, cues, sil):
    """用字幕句子的時間定切點：切在上一句結束和下一句開始的正中間"""
    cs = [(norm(c["text"]), c.get("startMs", c.get("start_ms")) / 1000, c.get("endMs", c.get("end_ms")) / 1000)
          for c in cues]
    cat = "".join(t for t, _, _ in cs)
    key = next((k for k in ("say", "show") if "".join(norm(s.get(k, "")) for s in segs) == cat), None)
    if key is None:
        sys.exit("字幕文字和 script.json 的念稿、字幕稿都對不起來：確認 cues 是這條旁白的，或不帶 cues 改用停頓估計")
    cuts, pos, k, acc = [], 0, 0, 0
    for s in segs[:-1]:
        pos += len(norm(s[key]))
        while k < len(cs) and acc + len(cs[k][0]) <= pos:
            acc += len(cs[k][0]); k += 1
        if acc != pos:  # 段落結尾落在一句字幕中間：按字數比例估
            t, a, b = cs[k]
            cuts.append(a + (b - a) * (pos - acc) / len(t))
            print(f"注意：第 {len(cuts)} 個切點落在句子中間（「{cues[k]['text']}」），請聽過確認", file=sys.stderr)
            continue
        end, start = cs[k - 1][2], cs[k][1]
        mid = (end + start) / 2
        near = [m for m, d in sil if end - 0.15 <= m <= start + 0.15]  # 有實際停頓就切在停頓正中間
        cuts.append(min(near, key=lambda m: abs(m - mid)) if near else mid)
    return cuts

def cuts_from_silence(segs, sil, total):
    """沒有字幕時間時的估計：依字數比例找最長、最近的句間停頓"""
    weights = [max(1, spoken_len(s["say"])) for s in segs]
    cuts, prev = [], 0.0
    for k in range(len(weights) - 1):
        # 每切一刀就以剩餘長度重新估下一個切點，誤差不會累積
        target = prev + (total - prev) * weights[k] / sum(weights[k:])
        cand = [(d - 0.1 * abs(m - target), m) for m, d in sil
                if abs(m - target) <= 4.0 and m > prev + 4.0]
        if not cand:
            sys.exit(f"找不到 {target:.2f}s 附近的停頓：在念稿該處加句號重做旁白，或改用字幕時間（cues.json）")
        prev = max(cand)[1]
        cuts.append(prev)
    print("注意：沒有字幕時間，切點是用停頓估的，段落之間沒有停頓時會切錯。每段的頭尾要請用戶聽過。", file=sys.stderr)
    return cuts

def split(wav, segs, out, cues):
    total = duration_s(wav)
    sil = silences(wav)
    cuts = cuts_from_cues(segs, cues, sil) if cues else cuts_from_silence(segs, sil, total)
    bounds = [0] + [round(c * SR) for c in cuts] + [round(total * SR)]
    info = []
    for i, (a, b) in enumerate(zip(bounds[:-1], bounds[1:]), 1):
        if b <= a:
            sys.exit(f"第 {i} 段長度不是正數：檢查 script.json 的段落順序")
        f = out / f"seg{i:02d}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af",
             f"atrim=start_sample={a}:end_sample={b},asetpts=N/SR/TB", "-c:a", "pcm_s16le", str(f)])
        start_ms, end_ms = round(a * 1000 / SR), round(b * 1000 / SR)
        info.append({"seg": i, "file": f.name, "start_ms": start_ms,
                     "end_ms": end_ms, "duration_ms": end_ms - start_ms})
        if end_ms - start_ms < 4000:
            print(f"注意：第 {i} 段只有 {(end_ms - start_ms) / 1000:.2f}s，要做 OmniHuman 對嘴的段落至少 4 秒", file=sys.stderr)
    (out / "segments.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"全長 {round(total * 1000)} ms／各段加總 {sum(x['duration_ms'] for x in info)} ms"
          f"／切點來源：{'字幕時間' if cues else '停頓估計'}")

def main(src, script_path, out_dir, cues_path=None):
    for p in (src, script_path) + ((cues_path,) if cues_path else ()):
        if not Path(p).is_file():
            sys.exit(f"找不到檔案：{p}")
    segs = json.loads(Path(script_path).read_text(encoding="utf-8"))["segments"]
    cues = None
    if cues_path:
        cues = find_cues(json.loads(Path(cues_path).read_text(encoding="utf-8")))
        if not cues:
            sys.exit(f"{cues_path} 裡找不到字幕句子（要有 text、startMs、endMs）")
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    wav = out / "_full.wav"
    try:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), str(wav)])
        split(wav, segs, out, cues)
    except subprocess.CalledProcessError as e:
        sys.exit(f"{e.cmd[0]} 失敗：{(e.stderr or '').strip()}")
    finally:
        wav.unlink(missing_ok=True)

if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        sys.exit(__doc__)
    main(*sys.argv[1:])
