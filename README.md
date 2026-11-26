# lenmu-skills

給 AI 助理（Claude、Codex 等）使用的 [Lenmu](https://lenmu.ai) skill。
Agent skills for making videos with the Lenmu MCP server.

## Skills

| Skill | 用途 |
|---|---|
| [`lenmu-digitalhuman`](lenmu-digitalhuman/SKILL.md) | AI 數字人口播影片：一張主持人圖＋一段主題 → 寫稿、配音、對嘴、B-roll、字幕、包裝到成片。每一步花錢前先報價。 (AI presenter / talking-head videos.) |
| [`lenmu-manju`](lenmu-manju/README.md) | 短劇／漫劇導演套裝（12 個技能）：劇本 → 資產 → 分鏡 → 七段式投餵稿 → 質檢，可選用 Lenmu 直接出圖、出片、組成片。[manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) 的 fork。 (Short-drama director suite with a Lenmu execution layer.) |

## 需求

- 已連接 Lenmu MCP：`https://lenmu.ai/mcp`（生成會使用你的 Lenmu 點數）
- 沙盒裡有 `ffmpeg`、`ffprobe`、`python3`、`curl`，並且能連到 `lenmu.ai`
  （連不上時 skill 會改走功能較少的備用路線）

## 安裝

把 skill 資料夾複製到助理的 skills 目錄，例如 Claude Code（`lenmu-manju` 是套裝，安裝方式見它自己的 README）：

```bash
git clone https://github.com/chesterkuo/lenmu-skills.git
cp -r lenmu-skills/lenmu-digitalhuman ~/.claude/skills/
```

## 維護

`lenmu-digitalhuman/SKILL.md` 第 14 節內嵌了 `scripts/split_narration.py` 的原始碼
（給只拿到 SKILL.md 的環境用）。改腳本時兩處要一起改。

## 授權

[MIT](LICENSE)。`lenmu-manju` 是 MIT 專案的 fork，保留上游授權，見 [lenmu-manju/LICENSE](lenmu-manju/LICENSE) 與 [NOTICE](lenmu-manju/NOTICE.md)。
`lenmu-digitalhuman` 的流程設計參考
[andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo)（MIT），
沒有使用該專案的程式、範本或素材。
