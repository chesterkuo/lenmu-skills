#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成短劇全片 12 節拍情緒張力曲線 PNG。

用法：
    python3 generate_emotion_curve.py [-o OUT] [-i BEATS_JSON]

示例：
    python3 generate_emotion_curve.py                      # 默認 12 節拍 → emotion_beat_curve.png
    python3 generate_emotion_curve.py -o curve.png         # 指定輸出文件
    python3 generate_emotion_curve.py -i beats.json        # 自定義節拍（[{"name":"起勢","value":3.5}, ...]）
"""
import argparse
import json
import os
import sys

# matplotlib 為可選依賴（缺依賴給安裝指引，不拋裸 Traceback）
# ★P11 修（2026-10-24）：舊版在 import 失敗處直接 sys.exit(2)，於是 `--self-test`
#   在無 matplotlib 的環境裡**根本跑不起來**——本腳本因此既沒有自測，
#   也沒人發現它沒有自測（check_package 的舊 ◑25 只查源碼裡有沒有 "--self-test" 字符串）。
#   改為「模塊恆可加載、繪圖時再報錯」：讓節拍解析這部分純邏輯在任何環境下都能被驗證，
#   繪圖部分在依賴缺失時明確標 SKIP，而不是假裝通過。
_MPL_OK = True
_MPL_ERR = ""
try:
    import matplotlib
    matplotlib.use("Agg")          # 無顯示環境（服務器 / CI）也能出圖
    import matplotlib.pyplot as plt
except Exception as _exc:          # ImportError 及後端初始化異常都歸這裡
    plt = None
    _MPL_OK = False
    _MPL_ERR = f"{type(_exc).__name__}: {_exc}"

_MPL_HINT = ("[-] 缺少依賴：本腳本需要 matplotlib 才能出圖。安裝：pip install matplotlib\n"
             "    （不影響包內其餘機檢與投餵鏈路——情緒曲線為可選交付物，"
             "節拍數據仍可按 12 節拍手寫進投餵稿）")

# ── 中文字體檢測與配置（macOS/常見 Linux 路徑回退）──
def _setup_cjk_font():
    """為 matplotlib 配置可用的中文字體，避免圖形中文變方塊。"""
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",   # macOS
        "/System/Library/Fonts/STHeiti Light.ttc",       # macOS
        "/System/Library/Fonts/Supplemental/Songti.ttc", # macOS
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",          # Linux
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                from matplotlib import font_manager
                font_manager.fontManager.addfont(path)
                name = font_manager.FontProperties(fname=path).get_name()
                matplotlib.rcParams["font.family"] = name
                matplotlib.rcParams["axes.unicode_minus"] = False
                return name
            except Exception:
                continue
    return None

_setup_cjk_font()

def plot_emotion_curve(beats=None, output_png="emotion_beat_curve.png"):
    """
    繪製 12 節拍短劇全片情緒張力曲線
    """
    if not _MPL_OK:
        raise RuntimeError("matplotlib 不可用：" + _MPL_ERR)
    if beats is None:
        beats = [
            ("1.起勢", 3.5),
            ("2.衝突", 5.0),
            ("3.硬剛", 6.5),
            ("4.對峙", 7.2),
            ("5.蓄勢", 4.2),
            ("6.危機", 8.2),
            ("7.高潮", 9.0),
            ("8.絕境", 6.2),
            ("9.反殺", 9.6),
            ("10.終局", 8.0),
            ("11.餘波", 7.2),
            ("12.收尾", 4.5)
        ]
    
    names = [b[0] for b in beats]
    scores = [b[1] for b in beats]
    n = len(beats)
    idx = list(range(1, n + 1))

    plt.figure(figsize=(max(8, n * 0.85), 5), dpi=150)
    plt.plot(idx, scores, marker="o", color="#C23B22", linewidth=2.5, markersize=8)

    for i, (name, val) in enumerate(beats):
        plt.text(i + 1, val + 0.25, f"{val}\n{name}", ha="center", fontsize=9, fontweight="bold")

    plt.axhspan(8.5, 10.0, color="#C23B22", alpha=0.15, label="高潮/反殺區")
    plt.axhspan(6.5, 8.5, color="#E67E22", alpha=0.10, label="動作/對峙區")
    plt.axhspan(0, 6.5, color="#3498DB", alpha=0.08, label="發展/蓄勢區")

    plt.title(f"短劇全片 {n} 節拍情緒張力曲線 (Emotion Beat Curve)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("節拍序號 (Beat Index)", fontsize=11)
    plt.ylabel("戲劇張力 / 情緒值 (0~10)", fontsize=11)
    plt.ylim(0, 11)
    plt.xticks(idx)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_png)
    print(f"[+] Emotion curve saved successfully to: {output_png}")


def _load_beats(path):
    """從 JSON 文件讀取自定義節拍：支持 [{"name":..,"value":..}] 或 [["name", value], ...]。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        sys.exit(f"[X] 節拍文件不存在：{path}")
    except json.JSONDecodeError as e:
        sys.exit(f"[X] 節拍 JSON 解析失敗：{e}")
    beats = []
    try:
        for item in raw:
            if isinstance(item, dict):
                beats.append((str(item["name"]), float(item["value"])))
            else:
                beats.append((str(item[0]), float(item[1])))
    except (KeyError, IndexError, TypeError, ValueError) as e:
        sys.exit(f"[X] 節拍格式錯誤（需 name/value 或 [name, value]）：{e}")
    if not beats:
        sys.exit("[X] 節拍列表為空")
    return beats


def self_test():
    """★P11 新增（2026-10-24）：本腳本此前完全游離在自測體系外。
    分兩層驗：① 節拍解析（純邏輯，任何環境都驗）；② 出圖（需 matplotlib，缺失則 SKIP 不冒充通過）。"""
    import tempfile
    ok = True
    dm = tempfile.mkdtemp()
    p1 = os.path.join(dm, "beats_dict.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump([{"name": "起勢", "value": 3.5}, {"name": "高潮", "value": 9}], f)
    b1 = _load_beats(p1)
    if b1 != [("起勢", 3.5), ("高潮", 9.0)]:
        print("FAIL self-test: dict 形態節拍解析錯誤", b1); ok = False
    p2 = os.path.join(dm, "beats_list.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump([["起勢", 3.5]], f)
    if _load_beats(p2) != [("起勢", 3.5)]:
        print("FAIL self-test: 數組形態節拍解析錯誤", _load_beats(p2)); ok = False
    p3 = os.path.join(dm, "beats_empty.json")
    with open(p3, "w", encoding="utf-8") as f:
        json.dump([], f)
    try:
        _load_beats(p3)
        print("FAIL self-test: 空節拍列表未被攔截"); ok = False
    except SystemExit:
        pass
    if _MPL_OK:
        out = os.path.join(dm, "curve.png")
        try:
            plot_emotion_curve(output_png=out)
        except Exception as exc:
            print(f"FAIL self-test: 繪圖異常 {type(exc).__name__}: {exc}"); ok = False
        else:
            if not os.path.exists(out) or os.path.getsize(out) < 2000:
                print("FAIL self-test: PNG 未生成或體積異常"); ok = False
        out2 = os.path.join(dm, "curve2.png")
        try:
            plot_emotion_curve(beats=[("A", 3.0), ("B", 9.0)], output_png=out2)
            if not os.path.exists(out2):
                print("FAIL self-test: 自定義節拍未生成 PNG"); ok = False
        except Exception as exc:
            print(f"FAIL self-test: 自定義節拍繪製失敗 {type(exc).__name__}"); ok = False
    else:
        print(f"[SKIP] matplotlib 不可用（{_MPL_ERR[:70]}）——僅驗證節拍解析，繪圖路徑未驗證")
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


def main():
    if not _MPL_OK:
        print(_MPL_HINT)
        sys.exit(2)
    ap = argparse.ArgumentParser(
        prog="generate_emotion_curve.py",
        description="生成短劇全片情緒張力曲線 PNG（默認 12 節拍）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("-o", "--out", default="emotion_beat_curve.png",
                    help="輸出 PNG 路徑（默認 emotion_beat_curve.png）")
    ap.add_argument("-i", "--input", default=None,
                    help="自定義節拍 JSON 文件（[{\"name\":\"起勢\",\"value\":3.5}, ...]）")
    args = ap.parse_args()

    out = args.out
    if out in ("-h", "--help"):
        ap.error("輸出路徑不能是 -h/--help")
    if not out.lower().endswith(".png"):
        out += ".png"
    out_dir = os.path.dirname(os.path.abspath(out))
    if not os.path.isdir(out_dir):
        sys.exit(f"[X] 輸出目錄不存在：{out_dir}")

    beats = _load_beats(args.input) if args.input else None
    plot_emotion_curve(beats=beats, output_png=out)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    main()
