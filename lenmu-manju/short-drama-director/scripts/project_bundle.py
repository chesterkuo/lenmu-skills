"""可選 JSON 事實源：結構校驗與同源 Markdown 導出，僅依賴標準庫。"""
import argparse
import json
import math
from pathlib import Path
import re
import sys
import tempfile


ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\Z")
ASPECTS = {"16:9", "9:16", "21:9", "1:1", "4:3", "3:4"}
DIALOGUE_RATE = 6
DIALOGUE_PAUSE = 0.3
EPSILON = 1e-6


class BundleError(ValueError):
    pass


def load_project(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BundleError(f"JSON 重複鍵：{key}")
            result[key] = value
        return result

    def constant(value):
        raise BundleError(f"非有限 JSON 數值：{value}")

    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=pairs, parse_constant=constant)


def validate(data):
    issues = []

    def issue(code, path, message, level="ERROR"):
        issues.append(dict(level=level, code=code, path=path, message=message))

    def require(ok, path, message):
        if not ok:
            raise BundleError(f"{path}: {message}")

    def obj(value, keys, path, optional=()):
        require(isinstance(value, dict), path, "必須是對象")
        require(set(keys) <= value.keys(), path, "缺少必填字段")
        require(value.keys() <= set(keys) | set(optional), path, "存在未定義字段")

    def text(value, path):
        require(isinstance(value, str) and bool(value.strip()), path, "必須是非空字符串")

    def array(value, path, nonempty=False):
        require(isinstance(value, list), path, "必須是數組")
        require(not nonempty or bool(value), path, "數組不得為空")

    def number(value, path, positive=False):
        require(type(value) in (int, float), path, "必須是數值，不能是布爾值")
        require(math.isfinite(value) and (value > 0 if positive else value >= 0),
                path, "必須是有限的正數" if positive else "必須是有限的非負數")

    seen = set()

    def identifier(value, path):
        require(isinstance(value, str) and ID.fullmatch(value) is not None,
                path, "ID 僅允許字母、數字、下劃線、點和短橫線")
        if value in seen:
            issue("DUPLICATE_ID", path, f"全局 ID 重複：{value}")
        seen.add(value)

    def refs(values, allowed, path):
        array(values, path)
        for i, value in enumerate(values):
            text(value, f"{path}[{i}]")
            if value not in allowed:
                issue("DANGLING_REF", path, f"引用不存在或類型不符：{value}")

    try:
        obj(data, ("project", "characters", "assets", "segments"), "root")
        p = data["project"]
        obj(p, ("model", "video_aspect", "asset_aspect", "total_duration"), "project")
        for key in ("model", "video_aspect", "asset_aspect"):
            text(p[key], f"project.{key}")
        require(p["video_aspect"] in ASPECTS, "project.video_aspect", "不支持的畫幅")
        if p["asset_aspect"] != "16:9":
            issue("ASSET_ASPECT", "project.asset_aspect", "資產畫幅必須是 16:9")
        number(p["total_duration"], "project.total_duration", True)
        for key in ("characters", "assets", "segments"):
            array(data[key], key, key == "segments")
        character_ids = set()
        asset_ids = set()
        for i, character in enumerate(data["characters"]):
            path = f"characters[{i}]"
            obj(character, ("id", "visual_age", "description"), path)
            identifier(character["id"], path + ".id")
            character_ids.add(character["id"])
            if type(character["visual_age"]) is not int or character["visual_age"] < 0:
                issue("VISUAL_AGE", path + ".visual_age", "視覺年齡必須是非負整數，不能是布爾值")
            text(character["description"], path + ".description")
        for i, asset in enumerate(data["assets"]):
            path = f"assets[{i}]"
            obj(asset, ("id", "type", "aspect", "prompt", "refs"), path)
            identifier(asset["id"], path + ".id")
            asset_ids.add(asset["id"])
            for key in ("type", "aspect", "prompt"):
                text(asset[key], path + "." + key)
            if asset["aspect"] != "16:9":
                issue("ASSET_ASPECT", path + ".aspect", "資產畫幅必須是 16:9")
        for i, asset in enumerate(data["assets"]):
            refs(asset["refs"], character_ids | asset_ids, f"assets[{i}].refs")
        previous = None
        total = 0
        for i, segment in enumerate(data["segments"]):
            path = f"segments[{i}]"
            obj(segment, ("id", "duration", "entry_state", "exit_state", "shots"), path,
                ("transition",))
            identifier(segment["id"], path + ".id")
            number(segment["duration"], path + ".duration", True)
            total += segment["duration"]
            for key in ("entry_state", "exit_state"):
                text(segment[key], path + "." + key)
            if "transition" in segment:
                text(segment["transition"], path + ".transition")
            if previous is not None and previous != segment["entry_state"] and "transition" not in segment:
                issue("STATE_TRANSITION", path, "跨段狀態不一致，須在後段聲明非空 transition")
            previous = segment["exit_state"]
            array(segment["shots"], path + ".shots", True)
            cursor = 0
            for j, shot in enumerate(segment["shots"]):
                sp = f"{path}.shots[{j}]"
                obj(shot, ("id", "start", "end", "action", "camera", "dialogues", "asset_refs"), sp)
                identifier(shot["id"], sp + ".id")
                for key in ("start", "end"):
                    number(shot[key], sp + "." + key)
                for key in ("action", "camera"):
                    text(shot[key], sp + "." + key)
                if (abs(shot["start"] - cursor) > EPSILON or shot["end"] <= shot["start"]
                        or shot["end"] > segment["duration"] + EPSILON):
                    issue("SHOT_COVERAGE", sp, "鏡頭須按數組順序無縫、無重疊、正時長地覆蓋段內時間軸")
                cursor = shot["end"]
                refs(shot["asset_refs"], asset_ids, sp + ".asset_refs")
                array(shot["dialogues"], sp + ".dialogues")
                budget = 0
                for k, dialogue in enumerate(shot["dialogues"]):
                    dp = f"{sp}.dialogues[{k}]"
                    obj(dialogue, ("character_id", "text"), dp)
                    text(dialogue["text"], dp + ".text")
                    refs([dialogue["character_id"]], character_ids, dp + ".character_id")
                    budget += sum(c.isalnum() for c in dialogue["text"]) / DIALOGUE_RATE + DIALOGUE_PAUSE
                if budget > shot["end"] - shot["start"] + EPSILON:
                    issue("DIALOGUE_BUDGET", sp, f"同鏡對白累計估算 {budget:.2f}s 超過鏡長；需人工複核", "WARN")
            if abs(cursor - segment["duration"]) > EPSILON:
                issue("SHOT_COVERAGE", path, "末鏡未覆蓋至段末")
        if abs(total - p["total_duration"]) > EPSILON:
            issue("TOTAL_DURATION", "project.total_duration", "總時長不等於各段時長之和")
    except (BundleError, OverflowError) as exc:
        issue("SCHEMA", "root", str(exc))
    return {"structural_status": "error" if any(x["level"] == "ERROR" for x in issues) else "valid",
            "semantic_status": "needs_review", "issues": issues}


def md(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("\r", " ").replace("\n", "<br>")


def render(data, report):
    p = data["project"]
    header = ["素材形態：M0 純提示詞；未生成或核驗圖片。", "",
              "語義狀態：needs_review；結構有效不代表語義、畫面或模型適配自動通過。", "",
              f"模型：{md(p['model'])}；視頻：{p['video_aspect']}；資產：16:9；總長：{p['total_duration']}s。", ""]
    assets = header + ["# 資產與鏡頭提示詞", "", "## 角色檔案", ""]
    for c in data["characters"]:
        assets.append(f"- {c['id']}｜視覺年齡 {c['visual_age']}｜{md(c['description'])}")
    assets += ["", "## 資產提示詞", ""]
    for a in data["assets"]:
        assets += [f"### {a['id']} · {md(a['type'])} · 16:9", "",
                   f"引用：{', '.join(a['refs']) or '無'}", "", md(a["prompt"]), ""]
    board = header + ["# P3CLEAN_GRID 故事板", "", "階段：P3；不是 P4.5。以下為待生圖的 Markdown 計劃，不是已生成的故事板圖。",
                      "每段一張純畫面網格，按數組順序從左至右、從上至下閱讀。畫面無文字、序號、對白框、箭頭、技術標籤或水印；各格留白分隔。",
                      "鏡號、時碼、對白僅屬於圖外追溯表，不應繪入圖中。面板不新增剪輯點；複雜動作是否需拆相位仍為 needs_review。", ""]
    for segment in data["segments"]:
        shared = [f"## {segment['id']} · {segment['duration']}s", "",
                  f"入口：{md(segment['entry_state'])}", f"出口：{md(segment['exit_state'])}",
                  f"轉場：{md(segment.get('transition', '連續接續'))}", ""]
        assets += shared
        count = len(segment["shots"])
        columns = math.ceil(math.sqrt(count))
        rows = math.ceil(count / columns)
        board += shared + [f"佈局：{rows} 行 × {columns} 列，共 {count} 個有效格；多餘槽位留白（最小一鏡一格映射；構圖與相位充分性 needs_review）。", ""]
        for shot in segment["shots"]:
            # 兩種交付共享同一行，不從 Markdown 反解析或重寫鏡頭。
            row = [f"### {shot['id']} [{shot['start']}-{shot['end']}s]", "",
                   f"畫面：{md(shot['action'])}", f"攝影：{md(shot['camera'])}",
                   f"資產引用：{', '.join(shot['asset_refs']) or '無'}", ""]
            dialogues = "；".join(f"{d['character_id']}：{md(d['text'])}" for d in shot["dialogues"]) or "無"
            assets += row + [f"對白：{dialogues}", ""]
            board += row + [f"圖外對白記錄（不繪入畫面）：{dialogues}", ""]
    warnings = ["## 機械告警", ""] + [f"- {x['level']} {x['code']} {x['path']}：{md(x['message'])}" for x in report["issues"]]
    if not report["issues"]:
        warnings += ["無機械告警；語義狀態仍為 needs_review。"]
    return {"assets-prompts.md": "\n".join(assets + warnings) + "\n",
            "P3CLEAN_GRID.md": "\n".join(board + warnings) + "\n"}


def export_bundle(data, output):
    report = validate(data)
    if report["structural_status"] == "error":
        raise BundleError(json.dumps(report, ensure_ascii=False))
    documents = render(data, report)
    output = Path(output).absolute()
    if output.exists():
        raise BundleError("輸出目錄已存在；拒絕覆蓋，請指定不存在的新目錄")
    if not output.parent.is_dir():
        raise BundleError("輸出目錄的父目錄必須已存在")
    # 全部渲染和校驗完成後才暫存；失敗清理暫存，整目錄發佈避免半份交付。
    with tempfile.TemporaryDirectory(prefix=".project-bundle-", dir=output.parent) as temp:
        staging = Path(temp) / "bundle"
        staging.mkdir()
        for name, content in documents.items():
            (staging / name).write_text(content, encoding="utf-8")
        if output.exists():
            raise BundleError("輸出目錄已存在；拒絕覆蓋")
        staging.rename(output)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="可選 JSON 項目校驗及 P3 同源導出")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "export"):
        child = sub.add_parser(command)
        child.add_argument("source", type=Path)
        if command == "export":
            child.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        data = load_project(args.source)
        report = export_bundle(data, args.output) if args.command == "export" else validate(data)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["structural_status"] == "error" else 0
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({"structural_status": "error", "semantic_status": "needs_review",
                          "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


def self_test():
    """★P11 新增（2026-10-24）：本腳本此前完全游離在自測體系外。
    它是「項目 JSON → assets-prompts.md / P3CLEAN_GRID.md」的導出器，
    導出物直接給人看，所以這裡釘兩條：Markdown 轉義必須做（否則 `|` 會劈開表格列）、
    空項目必須判結構錯誤（結構有效 ≠ 語義通過，這條口徑不能松）。"""
    ok = True
    if md("a<b>c|d&e") != "a&lt;b&gt;c&#124;d&amp;e":
        print("FAIL self-test: md 轉義錯誤", repr(md("a<b>c|d&e"))); ok = False
    r = validate({})
    if r.get("structural_status") != "error":
        print("FAIL self-test: validate({}) 未判結構錯誤"); ok = False
    if not r.get("issues"):
        print("FAIL self-test: validate({}) 未產出任何 issue"); ok = False
    if r.get("semantic_status") != "needs_review":
        print("FAIL self-test: 語義狀態應恆為 needs_review（結構有效≠語義通過）"); ok = False
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    sys.exit(main())
