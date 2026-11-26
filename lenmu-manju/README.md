# lenmu-manju · 漫劇老李短劇導演套裝（Lenmu MCP 版）

![規則庫](https://img.shields.io/badge/規則庫-53%20份-blue)
![文件](https://img.shields.io/badge/文件-170-blue)
![機檢](https://img.shields.io/badge/機檢-C1~C41-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

[lixiaoxiao9888-create/manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill)
（V8.2.0-SLIM，MIT）的 fork，加上一層 **Lenmu 執行層**。

- **原套裝**：1 個總控＋10 個子技能，把劇本一路做到可投餵 Seedance 2.5／2.0 的七段式提示詞，
  只出提示詞，圖和影片由使用者到外部平台自己跑。
- **這個 fork 多了什麼**：第 12 個同級技能 `sd-lenmu-engine`。使用者明確選擇「Lenmu 直出」時，
  用 [Lenmu MCP](https://lenmu.ai/mcp) 實際生成資產圖（Seedream）、逐段生成影片（Seedance）、
  組成成片（`assemble_film`），每一步花錢前先報價。沒選擇時，行為和原套裝完全一樣。

全部內文（規則庫、技能說明、機檢腳本的訊息與比對字串）已由簡體轉為繁體中文，沒有改動任何創作判據。
機檢腳本比對的是繁體關鍵字（如「素材接線單」「【畫幅風格】」），所以**稿子也要用繁體寫**才過得了機檢。
改了哪些地方見 [NOTICE.md](NOTICE.md)。

## 結構

```
lenmu-manju/
├── short-drama-director/     L0 總控（入口）
├── sd-decision-engine/       L1 決策
├── sd-recon-engine/          L2 採風
├── sd-script-engine/         L2 劇本
├── sd-asset-engine/          L2 資產提示詞
├── sd-storyboard-engine/     L2 文戲分鏡
├── sd-combat-engine/         L2 打戲
├── sd-xuanhuan-engine/       L2 玄幻打戲
├── sd-real-engine/           L2 寫實打戲
├── sd-feed-engine/           L3 投餵稿
├── sd-qc-engine/             L3 質檢
├── sd-lenmu-engine/          L4 Lenmu 執行層（fork 新增）
├── run_all_checks.py         全套自檢
├── run_stage.py              階段門禁入口
├── LICENSE                   上游 MIT 授權
└── NOTICE.md                 fork 來源與改動清單
```

## 安裝

12 個技能目錄要**同級**放進助理的 skills 目錄，入口是 `short-drama-director`；兩支門禁腳本放在同一層。

```bash
git clone https://github.com/chesterkuo/lenmu-skills.git
cd lenmu-skills

# Claude Code：~/.claude/skills　｜　OpenAI Codex：~/.agents/skills
DEST=~/.claude/skills
mkdir -p "$DEST"
cp -r lenmu-manju/short-drama-director lenmu-manju/sd-*-engine "$DEST"/
cp lenmu-manju/run_stage.py lenmu-manju/run_all_checks.py "$DEST"/
```

- 接上 Lenmu MCP 的指令、claude.ai 與 Codex 的細節見[倉庫根的 README](../README.md#安裝)。
- **不建議**裝在 claude.ai 網頁版／桌面版：那裡每個 skill 是各自獨立的上傳，套裝內互相引用的同級路徑不保證對得上。
- 機檢腳本互相用相對路徑呼叫：`run_all_checks.py`／`run_stage.py` 要在 12 個技能目錄的上一層執行（也就是上面的 `$DEST`，或本 repo 的 `lenmu-manju/`）。

## 需求

- 只出提示詞：不需要任何外部服務。
- Lenmu 直出：已連接 Lenmu MCP（生成使用你的 Lenmu 點數）；沙盒有 `python3`、`curl`、`ffmpeg`、`ffprobe`，
  並且能連到 `lenmu.ai`。

## 自檢

```bash
cd lenmu-manju && python3 run_all_checks.py
```

## Lenmu 的限制（和原套裝的差異）

| 項目 | 原套裝 | Lenmu 直出時 |
|---|---|---|
| 畫幅 | 16:9／9:16／21:9 | 只有 16:9、9:16；21:9 要先和使用者改定或後期裁切 |
| 角色板 | 16:9 四格／3:2 八格 | 只有 16:9 四格能直接出圖 |
| Seedance 2.0 參考素材 | 圖 ≤9 | 合計 ≤8 |
| 單段提示詞 | 依平台 | ≤4000 字 |
| 首尾幀 | 僅 2.5 | 同左（2.0 仍按上游契約禁用） |

`sd-lenmu-engine/SKILL.md` §十三 列出了尚未用真實生成驗證的假設，第一段影片要專門核對。
