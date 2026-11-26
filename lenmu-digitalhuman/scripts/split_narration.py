#!/usr/bin/env python3
"""把一整條 TTS 旁白依 script.json 的段落切成 WAV（切在句間停頓正中間）。
用法：python3 split_narration.py narration.mp3 script.json out_dir/"""
import json, re, subprocess, sys
from pathlib import Path
SR = 48000

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
    # 漢字、日文假名、韓文各算一個音節，英數算一個詞
    return len(re.findall(r"[぀-ヿ一-鿿가-힯]|[A-Za-z0-9]+", text))

def split(wav, segs, out):
    total = duration_s(wav)
    weights = [max(1, spoken_len(s["say"])) for s in segs]
    sil = silences(wav)
    cuts, acc = [], 0
    for w in weights[:-1]:
        acc += w
        target = total * acc / sum(weights)
        cand = [m for m, d in sil if abs(m - target) <= 3.0 and (not cuts or m > cuts[-1] + 4.0)]
        if not cand:
            sys.exit(f"找不到 {target:.2f}s 附近的停頓：在念稿該處加句號，重做旁白")
        cuts.append(min(cand, key=lambda m: abs(m - target)))
    bounds = [0] + [round(c * SR) for c in cuts] + [round(total * SR)]
    info = []
    for i, (a, b) in enumerate(zip(bounds[:-1], bounds[1:]), 1):
        if (b - a) / SR < 4.0:
            sys.exit(f"第 {i} 段只有 {(b - a) / SR:.2f}s，OmniHuman 至少 4 秒：併到相鄰段")
        f = out / f"seg{i:02d}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af",
             f"atrim=start_sample={a}:end_sample={b},asetpts=N/SR/TB", "-c:a", "pcm_s16le", str(f)])
        start_ms, end_ms = round(a * 1000 / SR), round(b * 1000 / SR)
        info.append({"seg": i, "file": f.name, "start_ms": start_ms,
                     "end_ms": end_ms, "duration_ms": end_ms - start_ms})
    (out / "segments.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"全長 {round(total * 1000)} ms／各段加總 {sum(x['duration_ms'] for x in info)} ms")

def main(src, script_path, out_dir):
    for p in (src, script_path):
        if not Path(p).is_file():
            sys.exit(f"找不到檔案：{p}")
    segs = json.loads(Path(script_path).read_text(encoding="utf-8"))["segments"]
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    wav = out / "_full.wav"
    try:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), str(wav)])
        split(wav, segs, out)
    except subprocess.CalledProcessError as e:
        sys.exit(f"{e.cmd[0]} 失敗：{(e.stderr or '').strip()}")
    finally:
        wav.unlink(missing_ok=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
