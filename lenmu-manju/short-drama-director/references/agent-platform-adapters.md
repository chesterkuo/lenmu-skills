# 多平台 Agent 架構與國產工作流適配規範 (Multi-Agent Platform Adapters)

本規範專為解決不同 Agent 運行平台（如 **OpenClaw**、**WorkBuddy**、**豆包智能體 / 釦子 Coze**、**Dify**）在交互協議、狀態機、文件掛載與上下文長度等方面的差異，提供全平台無縫兼容方案。

---

## 一、 平台差異與核心適配機制

```text
               ┌──> OpenClaw (命令行 / Tool-Call / 完整 Skill 目錄掛載)
               ├──> WorkBuddy (卡片式 Action Card / 側邊欄產出冊 / 會話狀態機)
[導演 Skill 總控] ├──> 豆包智能體 / 釦子 Coze (節點式工作流 / 插件輸入輸出 / JSON 契約)
               └──> Dify / 通用 LLM (單文件 Prompt 模式 / 標準 Markdown 輸出)
```

---

## 二、 平台專屬適配規範

### 1. WorkBuddy 平台專屬適配
- **會話狀態機驅動（P1 ~ P4 階段流轉）**：
  - `P0 立項鎖定階段`：鎖定畫幅（16:9/9:16）、風格預設、平台模型、目標時長（見 `aspect-ratio-adaptation.md`）；
  - `P1 劇本門控階段`：輸入劇本大綱，輸出前提與節拍表，自動生成側邊欄《劇組_資產圖冊.md》骨架與《劇組_全片情緒曲線.png》；
  - `P2 數字資產包階段`（本 skill 核心）：
    - P2a 從劇本自動提取全部 CHR/SCN/PRP/AUD 實體；
    - P2b 輸出《完整資產清單》（16 項五官 + 6 項材質 + 親緣推導表）→ 用戶確認無遺漏；
    - P2c 分批出圖：①角色（T1→T2→T3 4 View 資產板，Action Card 出圖確認）②場景（核心場景按序：母版 → 九宮格；複雜場景加機位調度版/戰鬥站位版）③道具（關鍵道具圖），每批鎖定；
    - P2d 交付《資產圖冊》（CHR/SCN/PRP 全附資產參考圖 + 短錨點 @名）；
  - `P3 空間調度與分鏡階段`：輸出 2x2 頂視圖（`主體頂視圖_演員機位_Ep1-4.png`）與文武雙模分鏡，**每個鏡頭引用已鎖定的 @資產圖**；
  - `P4 批量投餵與成片階段`：自動導出解耦提示詞與執行載荷（綁定資產圖）；
  - `P5 質檢與交付階段`：P0/P1/P2 門禁 + 資產一致性檢查（畫幅/臉型/服裝與資產圖一致）。
- **文件交互與側邊欄渲染**：
  - 產出文件統一命名為標準規範（如 `劇組_資產圖冊.md`、`劇組_全片情緒曲線_v1.png`、`主體頂視圖_演員機位_Ep1-4.png`）；
  - 支持 WorkBuddy 在線預覽、一鍵複製與本地 Download 自動歸檔。

### 2. 豆包智能體 / 釦子 (Coze) 工作流專屬適配
- **節點化入參與出參契約（Node Payload Contract）**：
  - 針對豆包工作流的節點流轉，輸出標準 JSON 格式數據塊，便於上游節點抓取字段：
    ```json
    {
      "episode_id": "EP01",
      "shot_index": "U01",
      "duration": 15,
      "model": "seedance-2.5",
      "positive_prompt": "[主體] ... [環境] ... [運鏡] ...",
      "negative_prompt": "blurry, low quality, distorted",
      "character_ids": ["CHR-楚靈風-戰損", "CHR-厲絕-幽冥"],
      "camera_id": "CAM1",
      "speech_speed_check": {
        "word_count": 0,
        "status": "PASS"
      }
    }
    ```
- **上下文分塊與長文本流式防護（Chunking Protocol）**：
  - 遇到長篇劇本時，自動啟用分集分塊處理（Chunking），單次響應控制在 2000 Tokens 以內，避免豆包對話上下文截斷。

### 3. OpenClaw 平台適配
- **標準 Skill 規範**：完整保留 `SKILL.md`、`references/` 規則庫與 `scripts/` 校驗腳本；
- **命令行快速安裝**：支持 `openclaw skills install ./short-drama-director --as short-drama-director` 一鍵部署。

### 4. Dify / FastGPT / 通用大模型適配
- **免依賴單文件 Prompt 模式**：
  - 用戶輸入 `導出全量 Prompt` 或直接複製 `SKILL.md` 時，自動內嵌核心規則摘要，無需本地讀取 references 子文件即可獨立運行。

---

## 三、 全平台通用指令路由一覽

無論在哪個 Agent 平台，以下指令均可統一觸發：
- `/寫劇本` / `初始化項目`：啟動門控編劇與台賬初始化
- `/劇組產出冊`：輸出標準化 Markdown 台賬（兼容 WorkBuddy 掛載）
- `/情緒曲線`：輸出 12 節拍張力分析（支持豆包 JSON 與圖片繪製）
- `/頂視圖`：輸出機位調度與 180° 軸線方案
- `/生成視頻提示詞`：輸出 Seedance 2.5 / 2.0 解耦提示詞
- `/導出工作流參數`：輸出豆包工作流 / API 標準 JSON 載荷
