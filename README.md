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

分兩步：先把 Lenmu MCP 接上，再把 skill 放進助理的 skills 目錄。先取得這個 repo：

```bash
git clone https://github.com/chesterkuo/lenmu-skills.git
cd lenmu-skills
```

### Claude Code

```bash
# 1. 接上 Lenmu MCP（加 --scope user 表示所有專案都能用），然後在 Claude Code 裡輸入 /mcp 完成登入
claude mcp add --transport http --scope user lenmu https://lenmu.ai/mcp

# 2. 安裝 skill（個人層級；只給單一專案用就改放該專案的 .claude/skills/）
mkdir -p ~/.claude/skills
cp -r lenmu-digitalhuman ~/.claude/skills/
```

不用重開，Claude Code 會自動偵測；沒出現就輸入 `/reload-skills`。

`lenmu-manju` 是 12 個技能的套裝，要**同級**放在一起，兩支門禁腳本也一起複製：

```bash
cp -r lenmu-manju/short-drama-director lenmu-manju/sd-*-engine ~/.claude/skills/
cp lenmu-manju/run_stage.py lenmu-manju/run_all_checks.py ~/.claude/skills/
```

### Claude（claude.ai 網頁版／桌面版）

1. **接上 Lenmu MCP**：Customize → Connectors → 「+ Add」→ 「Add custom connector」，
   網址填 `https://lenmu.ai/mcp`，照畫面完成登入。
2. **開啟程式碼執行**：Settings → Capabilities 裡的「Code execution and file creation」要開著，skill 才能用。
3. **上傳 skill**：先打包，skill 資料夾必須在 zip 的最上層：

   ```bash
   zip -r lenmu-digitalhuman.zip lenmu-digitalhuman/
   ```

   然後 Customize → Skills → 「+」→ 「Create skill」→ 「Upload a skill」，選這個 zip。
   （選單位置以你看到的介面為準，舊版介面在 Settings → Capabilities。）

`lenmu-manju` **不建議**用這種方式裝：這裡每個 skill 是各自獨立的上傳，套裝內 12 個技能互相用同級路徑引用檔案與腳本，
官方文件沒有保證跨 skill 的路徑能對上。這個套裝請用 Claude Code 或 Codex。

### OpenAI Codex（CLI／IDE 擴充／ChatGPT 桌面版）

```bash
# 1. 接上 Lenmu MCP 並登入
codex mcp add lenmu --url https://lenmu.ai/mcp
codex mcp login lenmu

# 2. 安裝 skill（個人層級；只給單一 repo 用就改放該 repo 的 .agents/skills/）
mkdir -p ~/.agents/skills
cp -r lenmu-digitalhuman ~/.agents/skills/

# lenmu-manju 套裝：12 個技能同級放在一起
cp -r lenmu-manju/short-drama-director lenmu-manju/sd-*-engine ~/.agents/skills/
cp lenmu-manju/run_stage.py lenmu-manju/run_all_checks.py ~/.agents/skills/
```

Codex 會自動偵測新的 skill，沒出現就重開 Codex。`lenmu-digitalhuman/agents/openai.yaml` 已宣告它需要 Lenmu MCP。

ChatGPT 的一般聊天介面目前沒有「上傳 skill 資料夾／zip」的官方做法，這兩個 skill 沒有在那裡測過。

### 確認裝好了

對助理說「用 Lenmu 做一支數字人口播影片」或「幫我寫一部短劇」，它應該會載入對應的 skill，
並在開工時先呼叫 `list_models` 確認 Lenmu 連得上。

> 以上步驟依 Claude 與 OpenAI 的官方文件整理（2026-11）。Claude Code 的安裝方式實際用過；
> claude.ai 上傳與 Codex 的步驟沒有逐一實機驗證，介面若有更動請以官方文件為準。

## 維護

`lenmu-digitalhuman/SKILL.md` 第 14 節內嵌了 `scripts/split_narration.py` 的原始碼
（給只拿到 SKILL.md 的環境用）。改腳本時兩處要一起改。

## 授權

[MIT](LICENSE)。`lenmu-manju` 是 MIT 專案的 fork，保留上游授權，見 [lenmu-manju/LICENSE](lenmu-manju/LICENSE) 與 [NOTICE](lenmu-manju/NOTICE.md)。
`lenmu-digitalhuman` 的流程設計參考
[andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo)（MIT），
沒有使用該專案的程式、範本或素材。
