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

## 開始使用

裝好之後不用記任何指令，直接用自己的話說要做什麼，總控 `short-drama-director` 會自己分派給其他技能。

### 1. 說出需求

例如：

- 「幫我寫一部 3 集的古風懸疑短劇，每集 1 分鐘。」
- 「把這篇小說改編成短劇分鏡。」（貼上原文或附檔）
- 「我要對標《某某劇》做一部類似題材的。」
- 只想做其中一步也可以：「幫這段劇本出分鏡」「幫這個角色寫出圖提示詞」「檢查這份投餵稿」。

### 2. 回答開工確認卡

第一輪回覆它不會動筆，只會給你一張確認卡。**每一項都要回**，沒回的它會停下來再問：

| # | 項目 | 選項 |
|---|---|---|
| 1 | 素材來源 | 原創／改編／對標爆款／熱點速成 |
| 2 | 視頻模型 | Seedance 2.5（單段最長 30 秒）／Seedance 2.0（單段最長 15 秒） |
| 3 | 成片畫幅 | 16:9／9:16／21:9 |
| 4 | 交付形態 | 離線看板／md 文檔／兩者都要 |
| 5 | 段縫銜接（多段才問） | 末幀定格／換機位硬切／空鏡過渡／技巧型轉場 |
| 6 | 角色資產板式 | 16:9 四格／3:2 八格 |
| 7 | 場景站位方案 | 雙圖方案／二合一方案 |
| 8 | 畫風 | 從它給的推薦卡選一張，或回「按你的推薦走」 |
| 9 | 執行方式 | **只出提示詞**（預設）／**Lenmu 直出** |

可以一次回完，例如：

> 1 原創；2 Seedance 2.0；3 16:9；4 md；5 末幀定格；6 四格；7 二合一；8 按你的推薦走；9 Lenmu 直出

第一次用、不確定怎麼選：模型選 Seedance 2.0、畫幅 16:9 或 9:16、角色板選四格，這幾項在 Lenmu 上都能直接生成（見下方「Lenmu 的限制」）。

### 3. 它會依序交付

劇本 → 資產清單與出圖提示詞 → 分鏡 → 七段式投餵稿 → 機檢。每個階段做完會停下來給你看，確認後才往下。

### 4. 第 9 項選了「Lenmu 直出」會多做什麼

稿子寫完、機檢通過之後，它會用 Lenmu 實際生成，**每一批花錢前先報價，你同意才執行**：

1. 開一張設了預算上限的 Lenmu 畫布，之後每次回報都附畫布連結；
2. 分批出資產圖（場景、角色、道具），你逐張確認；
3. 先生成**第一段**影片給你看，確認角色和場景都對，才報其餘各段的總價；
4. 逐段生成、抽格檢查，最後組成一支成片。

沒選的話，交付到投餵稿為止，圖和影片由你自己拿提示詞去平台生成。中途想改也可以直接說「用 Lenmu 把這段跑出來」或「先不要生成了」。

### 5. 你自己要看的

- **聲音、口型、台詞**：AI 聽不到，每段影片都要你自己看一次。
- **花費**：以它當下報的價為準。價格依模型和秒數而定，短劇的費用幾乎都在影片上，一分鐘成片的影片費從幾美元到十幾美元都有可能。
- **儲存空間**：Lenmu 素材庫滿了的話，截幀和上傳會失敗，要先清出空間。

### 常用說法

| 你說 | 它做 |
|---|---|
| 寫劇本／做分鏡／生成視頻提示詞 | 做對應的那一個階段 |
| 用 Lenmu 直出／出資產圖／跑這段／組成片 | Lenmu 生成的各步驟（先報價） |
| 接線單／素材形態 | 列出每個圖號對應哪張圖、圖目前在哪 |
| 審查 | 對現有稿子跑機檢與門禁 |
| Lenmu 台賬 | 列出目前花了多少、各節點狀態 |

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
