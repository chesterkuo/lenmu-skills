---
name: lenmu-digitalhuman
description: 用 Lenmu MCP 做 AI 數字人口播影片（digital human、talking-head、AI presenter video）時使用：一張主持人圖＋一段主題，產出寫稿、配音、對嘴、B-roll、字幕、包裝到成片的完整流程，每一步花錢前先報價。
---

# Lenmu 數字人口播手冊

一張主持人圖＋一句主題 → 一支有字幕、有包裝、聲音一致的口播成片。
所有生成和剪接都在 Lenmu，結果留在同一張 Lenmu 畫布上，使用者隨時可以打開 canvas_url 接手。

> 流程設計參考 Berryxia 的開源專案 [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo)（MIT），
> 改寫成以 Lenmu MCP（`https://lenmu.ai/mcp`）為生成與剪接核心的版本；沒有使用原專案的程式、範本或素材。
> 這份只管「主持人對鏡頭說話」這一類。一般短片、廣告、MV、短劇不在範圍內（有另外安裝 `lenmu-video` skill 就用它）。

本文的 `scripts/…` 指這個 skill 資料夾裡的檔案。資料夾裡沒有時，照第 14 節的原始碼寫出來再用。

---

## 0. 核心做法（和一般「一段一段生成」的差別）

**先做一整條旁白，再讓臉去對它。**

1. 整份稿子用 Seed TTS 3.0 **一次**做成一條旁白 → 聲音、語氣、音量天生一致，不需要事後「統一音色」。
2. 在句間停頓把旁白切成幾段（每段 10–25 秒），每段丟給 **OmniHuman 2.0**（一張圖＋一段音訊 → 對嘴影片）。
3. 用 `assemble_film` 組裝時，**把各段影片的原聲關掉，改鋪那一整條旁白**。影片只負責畫面，所以中間可以插 B-roll、切近景（punch-in），嘴型都不會跑掉；字幕用 `from_narration` 直接從旁白產生（Seed TTS 3.0 旁白免費）。

這條路需要沙盒能從 Lenmu 下載檔案（`curl`）。下載不了時走第 12 節的備用路線。

---

## 1. 鐵則

1. **六道關卡，依序過，不能跳：**
   | 關卡 | 使用者要確認的 | 約略花費 |
   |---|---|---|
   | ① 稿子 | 念稿、字幕稿、段落、B-roll 與包裝點 | 免費 |
   | ② 聲音 | 試聽兩句 → 再做整條旁白並聽過 | 幾美分 |
   | ③ 主持人 | 從 4 張形象圖選一張 | 約 $0.1 |
   | ④ 第一段 | 看第一段對嘴影片（它就是正片第一段，不是額外試拍） | 約 $1–2 |
   | ⑤ 其餘 | 一次報總價：剩下的段落＋B-roll＋音樂音效 | 依長度 |
   | ⑥ 成片 | 看、聽成片 | 組裝免費 |
2. **花錢前你先報價。** 用 `list_models` 的 price_hint 算好金額告訴使用者，同意才呼叫。便宜的工作 Lenmu 可能不回 `requires_confirmation` 就直接扣款，不能只靠它攔；有回時再核對 `estimate_usd`，帶 `confirm_token` 重送。
3. **一案一畫布、先設預算。** 開工用 `set_budget`（不帶 canvas_id、帶 `name`）建一張已設上限的新畫布，之後每一步都帶這個 canvas_id。
4. **拿到 generation_id 就不要重送。** 逾時不等於失敗。輪詢 `get_generation`：影片 10–20 秒一次、音訊 5–10 秒一次。
5. **誠實說你沒看到、沒聽到的。** 你只看得到抽出來的靜態格，聽不到聲音、看不到真正的動態和對嘴。每次交付都寫「已看：…；沒看：嘴型同步、動態、聲音」，請使用者看和聽。
6. **成片一定標示 AI 數字人。** 見第 13 節。
7. **新版本存新檔**（`seg03_v2.mp4`），不覆蓋舊檔。有 `warning`（例如儲存空間快滿）原文轉告。每次回報附 canvas_url。

---

## 2. 開工

### 2.1 一次問完
1. 主題和素材（文章、網址、筆記、產品資料都可以）。
2. 發在哪：IG Reels／TikTok／YouTube Shorts（9:16）、YouTube 長片（16:9）、LinkedIn（1:1 或 9:16）。
3. 片長、總預算（USD）。
4. 主持人：**新建一位 AI 主持人**（預設）、沿用角色庫裡的人（`list_people`）、或使用者本人（見 13 節的條件）。
5. 語言和口音（台灣華語、粵語、英語、日語…），有沒有偏好的聲音或自己的複製聲音。
6. 風格：讀完素材後，從第 3 節**推薦兩種**讓使用者選一種。

### 2.2 檢查工具
- `list_models`（免費）：確認連得上、看價格與 `account.balance_usd`。
- `ffmpeg -version`、`ffprobe -version`、`python3 --version`。
- 用 `curl -sSL -o t.bin <get_generation 回傳的 url>` 試下載一個檔案。Python 的 urllib 常被擋，**一律用 curl**。
- 連不上 lenmu.ai：請使用者在平台設定裡允許沙盒對外連線並加入 `lenmu.ai`；暫時不行就走第 12 節。

### 2.3 專案資料夾
```
digitalhuman_<名稱>/
  brief.md          平台、畫幅、片長、預算、風格、主持人、聲音
  script.json       稿子（第 4 節格式）
  persona.md        主持人：person_id、state_id、voice_id、外型描述、形象 prompt
  audio/            narration.mp3、seg01.wav…、segments.json
  video/            seg01.mp4…、punch/（近景版）
  broll/  cards/    B-roll 圖與片、程式排版的資訊圖卡
  qa/               抽格拼圖、檢查紀錄
  final/            成片、分享版
  ids.csv           每個 media_id、node_id、用途、版本、花費
```

---

## 3. 風格（推薦兩種給使用者選）

| 代號 | 風格 | 畫幅 | 長度 | 節奏與包裝 |
|---|---|---|---|---|
| S1 | 直式快講 | 9:16 | 30–90 s | 每 4–6 秒換一次畫面（近景／B-roll／圖卡），字幕大而醒目（`strong`），開場 2 秒內給鉤子 |
| S2 | 直式陪聊 | 9:16 | 60–180 s | 節奏放慢、字幕柔和（`soft`）、少音效，像在跟朋友說話 |
| L1 | 知識解說 | 16:9 | 2–8 min | 章節卡、資訊圖卡、數字卡；主持人和圖卡交替 |
| L2 | 產品／新聞快評 | 16:9 或 9:16 | 30–120 s | B-roll 比主持人多，重點用數字卡 |
| L3 | 教學步驟 | 16:9 | 2–8 min | 使用者的螢幕錄影為主體，主持人只負責開場、轉段、結尾 |
| D | 雙主持／多語 | 任一 | 任一 | 兩位主持人各自做 OmniHuman，輪流切（正反打），不要兩人同框對嘴 |

推薦規則：素材是觀點或懶人包 → S1；故事、陪伴、心得 → S2；有數據和段落 → L1；有產品圖或新聞事件 → L2；有操作畫面 → L3；需要對話或兩種語言 → D。

---

## 4. 寫稿（關卡 ①）

### 4.1 兩份稿
- **念稿 `say`**：給 TTS 念的。數字寫成國字（「三成」「兩千四百元」）、英文縮寫照念法寫或加空格（「A I」），容易念錯的多音字換同音字。
- **字幕稿 `show`**：給觀眾看的。用阿拉伯數字、正確用字、正常英文。
- 兩份**逐句對應**，只差寫法，不差內容。

### 4.2 長度與段落
- 字數 ≈ 秒數 × 5（台灣華語大約每秒 4.5–5.5 字；試聽後用實際長度修正）。
- **每段 10–25 秒、在句尾切**。段落是 OmniHuman 的生成單位：越短，重做越便宜；但不能短於 4 秒。
- **每條旁白不超過 5 分鐘（300 秒，約 1,400 字）**：`from_narration` 字幕只收 300 秒以內的旁白；一次 TTS 也最多 2,000 字。超過就分章節，每章各自一條旁白、各自組一支片（第 11.4 節）。
- 開頭第一句就是鉤子：結論、反常識、數字或問題，不要寒暄。
- 結尾一句行動呼籲（收藏、追蹤、留言），不要拖。

### 4.3 `script.json`
```json
{
  "title": "一分鐘搞懂○○",
  "style": "S1",
  "aspect": "9:16",
  "segments": [
    {
      "id": 1,
      "say": "百分之八十的人都用錯了這個功能。今天花一分鐘，一次講清楚。",
      "show": "80% 的人都用錯了這個功能。今天花 1 分鐘，一次講清楚。",
      "broll": [{"sentence": 1, "what": "手機設定畫面特寫，手指快速滑動"}],
      "pack": [{"type": "hook", "text": "80% 的人都用錯", "sentence": 1}]
    }
  ]
}
```
`pack` 的 type：`hook`（開場大字）、`point`（重點字卡）、`number`（數字卡）、`chapter`（章節卡）、`lower`（人名條）、`sfx`（音效點）。

把稿子以表格（段號、秒數估計、念稿、字幕稿、B-roll、包裝）給使用者看，確認後才往下。

---

## 5. 聲音（關卡 ②）

1. `list_voices`（可加 `language`、`gender`、`scenario`；這裡的 `language` 是語言名稱，例如 `Chinese`、`Japanese`）。Seed TTS 3.0 每個聲音都能說所有支援的語言；列出的語言只是它最擅長的。台灣口音可先試名稱或說明含 taiwan 的聲音（加 `detail: true` 看說明）。念稿語言和聲音的主要語言不同時，在 `generate_audio` 帶語言代碼（`ja`、`en`…）；粵語一定要帶 `language: "yue"`。
2. **試聽**：用候選聲音各念稿子的頭兩句（`generate_audio`，model `byteplus/seed-tts-3.0`），每次幾分之一美分。可加 `instructions`（例如「自然、親切、語速稍快，像在跟朋友分享」）。
3. 情緒標籤（英文、方括號、放在要影響的那句前面）少量使用：開場 `[confident]`、驚訝點 `[surprised]` 就夠，整篇不超過 3–4 個。
4. 使用者選定後，把**所有段落的 `say` 串起來**（段與段之間換行）做成**一整條旁白**，存 `audio/narration.mp3`，記下 media_id。
5. 請使用者聽整條旁白，標出念錯的地方。念錯就改念稿重做整條（便宜），不要留到影片階段。
6. 量實際長度：`ffprobe` → 回寫每段秒數，算出實際語速，更新預算。

---

## 6. 主持人（關卡 ③）

### 6.1 新建 AI 主持人
`generate_image`，model `byteplus/seedream-5-5`，`count: 4`，size 依畫幅（9:16 用 `1152x2048`，16:9 用 `2048x1152`）。**OmniHuman 的畫面跟著這張圖走**，所以圖就要是成片的比例和構圖。

提示詞範本：
> 寫實攝影。一位[年齡]歲的[性別]主持人，[髮型、服裝、主色]。正面面對鏡頭，雙眼直視鏡頭，嘴巴自然閉合，表情親切放鬆。頭髮不遮住臉和眼睛。中近景（胸口以上），頭頂留約一成空間，雙手不入鏡。背景是[簡單有景深的場景，例如明亮工作室、虛化的書架]。柔和均勻的正面光，臉上沒有硬陰影。畫面沒有任何文字、Logo 或浮水印。

- 9:16：臉放在畫面上方三分之一，胸口以下留給字幕。
- 16:9（L1、L3）：人物放在畫面左或右三分之一，另一側留乾淨背景。
- 避免：墨鏡、帽沿、髮絲遮眼、張嘴笑露齒、手拿東西、複雜花紋（會閃）。
- 使用者選定後：
  1. `save_character`（免費；只收 Lenmu 直接生成的圖）。
  2. `update_character` 綁定選好的 `voice_id`，之後 `generate_audio` 可直接帶 `person_id`。
  3. 想換裝、換場景：用同一位當參考生新圖，`add_character_state` 存成新狀態（最多 12 個）。
  4. 把 person_id、state_id、voice_id、外型描述、prompt 寫進 `persona.md`。下一支片直接沿用，形象和聲音就一致。

### 6.2 沿用角色庫
`list_people`（`include_states: true`），讓使用者選人和狀態，確認狀態圖的比例符合這次的畫幅。

---

## 7. 切段與對嘴（關卡 ④ ⑤）

### 7.1 切旁白
```bash
curl -sSL -o audio/narration.mp3 "<旁白 url>"
python3 -I <skill>/scripts/split_narration.py audio/narration.mp3 script.json audio/
```
- 依各段字數比例（漢字、假名、韓文算字，英數算詞）估出切點，對齊到最近的句間停頓正中間；輸出 `seg01.wav…` 和 `segments.json`（各段 start_ms／end_ms／duration_ms，加總等於全長）。
- 找不到停頓：在念稿那裡加句號重做旁白。某段短於 4 秒：併到相鄰段。
- 上傳：`create_upload_url`（`count` = 段數，`filenames` 照順序；一次最多 10 個，超過就分批呼叫），每段 `curl -sS -T audio/segNN.wav <upload_url>`，記下每段 media_id。

### 7.2 第一段（關卡 ④）
`generate_video`：
- `model`：`byteplus/omnihuman-2.0`
- 主持人：`characters: [{character_id, state_id}]`（角色庫）或 `reference_media_ids: [形象圖]`
- `reference_media_ids` 加入該段音訊的 media_id
- 不要帶 `duration_seconds`、`size`、首尾幀、`generate_audio`、`count`
- 報價：段長秒數 × price_hint（2026-11 約 $0.08／秒）

提示詞範本（鏡頭固定，近景在後製做）：
> 主持人對著鏡頭自然地說話，嘴型與語音對齊，語氣[親切／專業]。說到重點時輕輕點頭，偶爾一隻手在胸前比個簡單手勢後放下。眼神看鏡頭，身體微微前傾。背景保持不動，鏡頭固定。

20 秒音訊約等 5–7 分鐘。完成後下載、做 7.4 的檢查，給使用者看第一段。**使用者滿意，這段就是正片**。

### 7.3 其餘段落（關卡 ⑤）
一次報總價（剩餘秒數 × 單價＋B-roll＋音樂音效），同意後逐段送出。同一張畫布一次跑一個生成，回 `canvas_busy` 就排隊，等待時間拿去檢查上一段、做 B-roll 和圖卡。

### 7.4 每段檢查
```bash
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of json video/seg01.mp4
ffmpeg -v error -i video/seg01.mp4 -vf "fps=1,scale=240:-2,tile=6x4" -frames:v 1 qa/seg01_sheet.png
```
- 放大看拼圖：臉有沒有變形或變成別人、牙齒和嘴角是否怪異、眼神飄走、手指數目、衣服和髮型有沒有漂移、背景扭曲、結尾突然重置。
- **長度對齊**：影片長度和 `segments.json` 的 duration_ms 比。影片較長 → 組裝時 `out_ms` = 音訊長度；較短超過 1 幀 → 該段用 `speed` = 影片長 ÷ 音訊長 拉齊。差距記進 `qa/`。
- 實際尺寸以 ffprobe 為準，不以 `get_canvas` 回報為準。
- 有問題：輕微的（頭尾一兩格）用 `out_ms`、`in_ms` 剪掉；嚴重的只重做那一段，先檢討圖或提示詞再送，不要原封重送。

---

## 8. B-roll 與圖卡

### 8.1 B-roll（AI 生成）
- 先 Seedream 5.5 出圖（同畫幅），再用 Seedance 以這張圖當 `first_frame_media_id` 做 4–5 秒微動（緩慢推近、手部動作、物件轉動），挑 `list_models` 裡支援所需尺寸、最便宜的 Seedance（例如 2.0 Mini／Fast）。
- **B-roll 一律 `generate_audio: false`**：聲音由旁白和配樂負責。
- B-roll 裡不要出現主持人以外的寫實人臉特寫、不要螢幕文字、不要品牌 Logo。
- 一個 B-roll 只放 2–4 秒，夠用就好。

### 8.2 資訊圖卡（程式排版）
**畫面上的字一律用程式排，不讓 AI 生圖寫字**（AI 寫中文常錯字）。
- 用 Pillow 排版成目標尺寸的 PNG（數字卡、重點條列、比較表、步驟編號），用使用者有權商用的中文字型（`fc-list :lang=zh` 找；沒有就請使用者提供字型檔）。
- 轉成影片：`ffmpeg -loop 1 -i cards/c01.png -t 3 -r 25 -vf "scale=W:H,format=yuv420p" -c:v libx264 cards/c01.mp4`
- 示意數據要在卡上標「示意」。

### 8.3 使用者素材
螢幕錄影、產品照：`create_upload_url` 上傳 →（照片先轉成影片）→ `add_media_to_canvas` 拿到 node_id。

### 8.4 近景（punch-in）
口播最常用的節奏手法：同一段切成「原景 ↔ 近景」交替。近景版和原片時間完全相同，所以在同一個時間點換過去，嘴型照樣對。
```bash
Z=1.15   # 放大倍率，720p 素材不要超過 1.2
ffmpeg -i video/seg02.mp4 -vf "crop=trunc(iw/$Z/2)*2:trunc(ih/$Z/2)*2:(iw-ow)/2:(ih-oh)*0.30,scale=<原寬>:<原高>:flags=lanczos,setsar=1" -c:v libx264 -crf 16 -preset veryfast -an video/punch/seg02_p.mp4
```
`0.30` 讓裁切偏上、保住臉。上傳 → `add_media_to_canvas`。

---

## 9. 包裝：對應到 `assemble_film`

| 包裝 | 做法 |
|---|---|
| 開場鉤子 | 第一句用 B-roll 或圖卡＋`texts`（`style: title`、`position: center`、`animation: zoomIn` 或 `springUp`），第二句才切回主持人。主持人在畫面上時大字放 `top`，不壓臉（那段時間 AI 標示要讓開，見最後一列） |
| 重點字卡 | `texts` `style: caption`、`position: top`、`animation: slideLeft`，1.5–2.5 秒 |
| 數字強調 | 程式排的數字卡當插入片段，或 `texts` 加 `animation: pulse` |
| 人名條 | `texts` `style: caption`、`position: bottom`，開場 3–5 秒（字幕要錯開時間） |
| 章節 | `texts` `style: title`、`position: top`，或程式排的章節卡片段 |
| 字幕 | `subtitles: {from_narration: true, script: <所有 show 串起來>, preset}`；S1 用 `strong`，S2 用 `soft`，L 系列用 `outline` |
| 音效 | `generate_audio` model `byteplus/seed-audio-1.0`，`duration_seconds: 1–2`，例如「短促的 whoosh 轉場聲」「清脆的 pop 提示音」；放在切 B-roll 和字卡出現的時間點，`volume_db` −6 左右 |
| 配樂 | Lyria（`vertex/lyria-3-clip-preview` 或 `-pro-`），instrumental，「輕快、無人聲、適合口播背景」；`music_volume` 0.08–0.12。先看生成長度，不夠長就換 Pro |
| AI 標示 | `texts`：「本影片由 AI 數字人呈現」，`style: caption`、`position: top`、`animation: none`，從 0 到片尾（第 13 節）。**`top` 同一時間只放一張字**：有其他 `top` 字卡（鉤子、重點、章節）的時段，把標示拆成幾張、跳過那些時段，字卡一結束就接回來；片頭前 3 秒和片尾最後 3 秒一定要有標示，所以這兩段的其他字卡改放 `center` |

上限：最多 20 個片段（含同一段切開的）、600 秒、60 張字卡、16 個音效；音樂＋旁白＋音效合計最多 8 個不同音檔。**排時間軸前先算片段數**，超過 20 就減少切換或分章節。

---

## 10. 時間軸怎麼排

以旁白時間為準：主持人第 k 段在成片裡的起點 = 該段 `start_ms`。要在旁白 t 毫秒處插 d 毫秒的 B-roll，就把那段主持人切開：

```
主持人段 k：in 0 → out (t − start_k)
B-roll   ：in 0 → out d
主持人段 k：in (t − start_k + d) → 段尾
```
同一個 node 可以出現兩次、切法不同。近景交替也一樣，只是把 B-roll 換成近景版 node、in／out 用相同的時間。

範例（第二段 6203–16050 ms，在旁白 8000–11000 ms 插 3 秒 B-roll）：
```json
{
  "canvas_id": "<canvas>",
  "segments": [
    {"node_id": "<P1>", "out_ms": 6203},
    {"node_id": "<P2>", "out_ms": 1797},
    {"node_id": "<B1>", "in_ms": 0, "out_ms": 3000},
    {"node_id": "<P2>", "in_ms": 4797},
    {"node_id": "<P3>"}
  ],
  "keep_original_audio": false,
  "narration": {"media_id": "<整條旁白>"},
  "subtitles": {"from_narration": true, "script": "<字幕稿全文>", "preset": "strong"},
  "music_media_id": "<配樂>", "music_volume": 0.1,
  "texts": [{"text": "本影片由 AI 數字人呈現", "at_ms": 0, "duration_ms": 60000, "style": "caption", "position": "top", "animation": "none"}],
  "output": {"aspect": "9:16", "resolution": 1080}
}
```
- **主線一律硬切，不用 `transition_out`。** 交叉轉場可能吃掉時間，讓後面的嘴型和旁白錯開；要轉場感就用音效＋B-roll。
- `keep_original_audio: false` 一定要關，否則每段原聲會和整條旁白疊在一起。
- 每段的時間軸長度＝(out − in) ÷ speed，全部加起來要等於旁白全長；送出前用程式加總核對。
- node_id 從 `get_canvas` 取；`out_ms` 不能超過該段 `duration_ms`；每一刀（含近景和 B-roll）至少 0.5 秒。
- 每段主持人的最後一刀都帶 `out_ms` = 該段音訊長度（範例的 `<P1>`）；只有確認影片和音訊等長（7.4）才能省略（範例的 `<P3>`）。
- AI 標示的 `duration_ms` 填旁白全長（範例的 60000 只是示意）；有其他 `top` 字卡時照第 9 節拆開。

---

## 11. 成片（關卡 ⑥）

### 11.1 組裝
`assemble_film` 免費。帶 `from_narration` 時會先做字幕再背景算圖：輪詢 `get_generation`，有 `warning`（字幕要檢查）原文轉告。成片也是畫布上的 film 節點，使用者可以在 Lenmu 片編輯器繼續改；要改時間軸就帶 `film_node_id` 重送。

### 11.2 檢查
1. 下載成片，`ffprobe` 看長度是否等於旁白全長（差 ≤ 1 幀）。
2. 每個剪接點前後各抽 3 幀，看有沒有黑幀、跳色、字幕壓臉、字卡和字幕重疊。
3. 用旁白的已知時間抽幾個點（例如每段第一個字），看嘴是不是張開的；這只能抓大錯，嘴型細節請使用者看。

### 11.3 響度
社群平台目標 −14 LUFS（講座、Podcast 感可用 −16）。量整片、算差值、**固定增益＋限幅**，不用動態響度標準化（會把停頓裡的雜音拉高）：
```bash
ffmpeg -hide_banner -i final/film.mp4 -af ebur128=peak=true -f null - 2>&1 | grep "I:" | tail -1
# 例如量到 -19.3 → 增益 +5.3 dB
ffmpeg -i final/film.mp4 -af "volume=5.3dB,alimiter=limit=0.89:level=false" -c:v copy final/film_-14LUFS.mp4
```
再量一次確認。另存一個分享版（`-crf 23`，< 50 MB）。

### 11.4 長片
超過 20 個片段或 600 秒：按章節各自組裝，再在沙盒用 ffmpeg concat 接起來（重新編碼），或用 `export_premiere` 交給剪輯軟體。

### 11.5 交付訊息
附：成片、canvas_url、總花費（對照 ids.csv）、已看／沒看清單，並請使用者特別聽：念錯字、停頓是否自然、配樂是否蓋過人聲；看：嘴型、手勢、字幕是否擋臉。

---

## 12. 備用路線（沙盒下載不了 Lenmu 檔案）

先告訴使用者：這條路做不了近景交替、精準字幕、響度檢查。
1. 每段各自 `generate_audio`（同一個 voice_id、同一段 `instructions`），使用者試聽。
2. 每段 OmniHuman，`reference_media_ids` 帶該段音訊。
3. `assemble_film`：`keep_original_audio: true`、不帶 narration；B-roll 只能放在**段與段之間**當 1–2 秒的過場（插在段內會把聲音切掉）。
4. 字幕改用 `texts`（`style: subtitle`、`position: bottom`），時間依字數比例在每段內估算；請使用者在 Lenmu 片編輯器微調。

---

## 13. 責任使用

- **主持人預設是 Lenmu 生成的虛構人物。**
- 使用者**本人**要當主持人：本人同意、本人的正面照（正面、平光、閉嘴、頭髮不遮臉），以 `reference_media_ids` 給 OmniHuman；上傳照片不能存進角色庫。平台拒絕就停，**不用馬賽克或任何手法繞過審核**。
- 不使用名人、政治人物、親友或網路上的照片和聲音；不模仿特定真人的聲音。聲音只用內建聲音，或使用者本人的複製聲音。
- **每支成片都要有「AI 數字人」標示**（第 9 節的 AI 標示字卡，只在其他 `top` 字卡出現時短暫讓開），並提醒使用者發布文案也註明。
- 示意數據要標「示意」。B-roll 不用影視截圖、網路梗圖、品牌 Logo、知名角色。
- 角色同意聲明（例如 `register_character_avatar`、`publish_play`）要原文給使用者看，由使用者決定。

---

## 14. `scripts/split_narration.py` 原始碼

skill 資料夾裡沒有這個檔案時，照下面寫出來：

```python
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
```

---

## 15. 範例：60 秒直式快講（S1）的花費

2026-11 的 price_hint，實際以 `list_models` 為準：

| 項目 | 數量 | 約略 |
|---|---|---|
| 試聽＋整條旁白（約 300 字） | Seed TTS 3.0 | $0.01 |
| 主持人形象 | Seedream 5.5 × 4 | $0.09 |
| 對嘴 | OmniHuman 2.0 × 60 秒（分 4 段） | $4.83 |
| B-roll | Seedream × 3 ＋ Seedance 便宜款 5 秒 × 3 | $0.4–1.0 |
| 配樂、音效 | Lyria Clip × 1、Seed Audio 2 秒 × 3 | $0.07 |
| 組裝、字幕（TTS 旁白） | `assemble_film` | 免費 |
| **合計** | | **約 $5.5–6** |

對嘴占了八成以上的費用，所以**第一段過了關卡 ④ 才批次**，重做時也只重做出問題的那一段。

---

## 16. 常見問題

| 狀況 | 原因與處理 |
|---|---|
| 嘴型越後面越對不上 | 各段影片長度和音訊長度有差、或用了交叉轉場。照 7.4 對齊長度、主線改硬切 |
| 聲音重疊、有回音 | 忘了 `keep_original_audio: false` |
| 某個詞念錯 | 改念稿（同音字、國字數字）重做旁白；字幕稿不動 |
| 主持人的臉在段落間不一樣 | 每段都用同一個 state 圖；換裝要用 `add_character_state` 的新狀態，不要每段重生形象 |
| 長段落手勢或衣服漂移 | 段落縮短到 10–15 秒；提示詞減少動作 |
| 字幕壓到臉或和字卡打架 | 9:16 臉放上三分之一；字卡放 `top`，人名條避開字幕時間 |
| AI 標示和字卡疊在一起 | `top` 同一時間只放一張字：把標示拆開、跳過字卡的時段（第 9 節） |
| `from_narration` 被拒（旁白太長） | 旁白超過 300 秒：按章節拆成幾條旁白、各自組片，或改給 `subtitles.cues` |
| 片段超過 20 個 | 減少近景切換、把相鄰 B-roll 合併，或分章節組裝 |
| 生成被內容審核擋 | 改提示詞或素材，不要原封重送；真人照片被拒就改用 AI 主持人 |
