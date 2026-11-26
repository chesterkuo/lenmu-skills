# 可選 JSON 項目包契約

## 邊界

本工具是一條**新生產鏈的可選入口**，不替換現有 Markdown 工作流，不修改舊編譯器或門禁，也不自動掛載到現有技能流程。**舊 md 不會自動遷移**；需要人工整理成 JSON 並複核後再使用。JSON 是本鏈唯一事實源，導出的 Markdown 是隻讀衍生物；改鏡頭請改 JSON 後導出到新目錄，不在兩份 md 中分別改稿。

僅使用 Python 標準庫，無第三方依賴。**包內不隨附示例工程文件**（P14 起案例示例整體剔除）：合規輸入由 `scripts/test_project_bundle.py` 內聯的測試夾具在運行期生成到系統臨時目錄，只服務於迴歸測試，不作為可參照的樣例交付物。

## JSON 字段

所有列出的字段必填，除 `segments[].transition` 外無可選字段。未知字段報 ERROR，避免拼寫錯誤被靜默忽略。文本字段必須為非空字符串；數組字段允許空數組，但 segments 和每段 shots 必須非空。文件採用 UTF-8（可帶 BOM）。拒絕重複 JSON 鍵、NaN、Infinity。

| 對象 | 字段與類型 |
|---|---|
| 根對象 | project 對象、characters 數組、assets 數組、segments 數組 |
| project | model 非空字符串；video_aspect 畫幅字符串；asset_aspect 固定 `16:9`；total_duration 有限正數，秒 |
| characters[] | id 穩定字符串；visual_age 非負整數（不接受 `28.0`、字符串或 bool）；description 非空字符串 |
| assets[] | id 穩定字符串；type 非空分類字符串；aspect 固定 `16:9`；prompt 非空字符串；refs 為角色或資產 ID 字符串數組 |
| segments[] | id 穩定字符串；duration 有限正數，秒；entry_state、exit_state 非空狀態字符串；shots 數組；可選 transition 非空字符串 |
| shots[] | id 全局穩定字符串；start、end 段內有限非負秒數；action、camera 非空字符串；dialogues 數組；asset_refs 資產 ID 數組 |
| dialogues[] | character_id 角色 ID；text 非空字符串 |

ID 在角色、資產、段落及全部鏡頭之間全局唯一，格式為 `[A-Za-z0-9_][A-Za-z0-9_.-]*`。鏡號由作者維護，不按數組索引重新編號；調整時間或排序不應修改既有鏡頭身份。工具能檢查單份項目內的唯一性，不能證明跨版本身份未漂移。

video_aspect 支持 `16:9 / 9:16 / 21:9 / 1:1 / 4:3 / 3:4`。視頻豎屏不改變資產橫屏約束。model 和資產 type 只登記非空標籤，不聲稱對應模型的能力、單段上限或官方投餵語法已核驗。

refs 只是登記關係，不遞歸展開，也不代表已上傳圖片。asset_refs 僅接受資產 ID；對白 character_id 僅接受角色 ID。action、camera、狀態和 prompt 內的自由文字不做實體識別，文字內的人名或資產描述需要人工複核。

## 機械校驗

- `DUPLICATE_ID`：全局 ID 重複，ERROR。
- `DANGLING_REF`：顯式引用不存在或指向錯誤類型，ERROR。
- `VISUAL_AGE`：視覺年齡不是非負整數，ERROR。
- `ASSET_ASPECT`：項目或任一資產不是 16:9，ERROR。
- `TOTAL_DURATION`：總時長不等於全部段長之和，ERROR。
- `SHOT_COVERAGE`：shots 按輸入數組順序從 0 到 duration 連續覆蓋；禁止間隙、重疊、倒序、零長、越界或尾部缺失，ERROR。不自動排序修復。秒數支持小數，比較絕對誤差容許 `1e-6` 秒。
- `STATE_TRANSITION`：前段 exit_state 與後段 entry_state 字符串不完全相等時，後段必須有非空 transition，ERROR。相等只是字符串一致；有 transition 只是聲明齊備，並不證明銜接合理。轉場發生在既有段與 shots 時間軸內，不自動增加時長或鏡頭。
- `DIALOGUE_BUDGET`：同鏡全部對白**累計**預算超過鏡長時報 WARN。每句估算為 `字母數字字符數 / 6 + 0.3 秒停頓`；不計標點和空白，同鏡按順序發聲，不假設多人同時說話。英語等語言的估算可能偏差很大；這不是聲音合成實測，也不是動作與對白共用預算的自動證明。
- `SCHEMA`：缺字段、未知字段、形狀或類型不符、非有限數等，ERROR。遇到首個結構類型錯誤停止深入檢查；已發現的問題保留，修正後重新運行。

結果 JSON 分開返回 `structural_status: valid|error`、`semantic_status: needs_review` 和 issues（level/code/path/message）。WARN 不阻止導出，但保留在兩份 Markdown 中；退出碼 0 只表示無機械 ERROR。

**所有語義一律 needs_review**，不輸出語義自動通過結論。包括空間/軸線/遮擋、人物外觀年齡是否可視、狀態轉場因果、對白可演性、動作物理、鏡頭充分性、資產圖像一致性、模型適配等。工具不看圖、不出圖，也不能阻止用戶在自由文本中自己寫入不實結論；這些仍需人工審查。

## 同源導出與階段

`export` 從同一份 `segments[].shots[]` 順序生成兩份文件：

1. `assets-prompts.md`：角色檔案、資產提示詞與引用關係，以及逐鏡畫面、攝影、時碼、對白、資產引用。
2. `P3CLEAN_GRID.md`：**P3 圖形化環 CLEAN_GRID** 故事板生圖計劃，不是 P4.5，不是最終模型七段式投餵稿，也不是已生成圖片。

兩份逐鏡內容共用同一個渲染片段，保留穩定鏡號和對白原文。每段一張網格，最小映射一鏡一格；列數為格數平方根向上取整，行數向上補齊，餘槽留白（四鏡工程即 2×2）。不憑空增加動作、鏡頭或剪輯點。複雜動作的相位拆分、默認格數與正式 P3 模板是否充分，仍須人工複核，本工具不宣稱完整 P3 已完成。

CLEAN_GRID 的圖面要求無文字、序號、對白框、箭頭、技術標籤或水印，純畫面加留白分隔。Markdown 裡的鏡號、時碼和對白是**圖外追溯信息**，不是讓生圖模型繪製的圖中文字。人物與資產依據由同包檔案、資產提示詞和顯式引用提供；素材形態聲明為 M0，沒有虛構圖片槽位。

## CLI 與失敗行為

從 `short-drama-director` 目錄運行（`python` 換成實際解釋器路徑）：

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/project_bundle.py validate <你的工程.json>
PYTHONDONTWRITEBYTECODE=1 python scripts/project_bundle.py export <你的工程.json> --output /existing-parent/new-bundle
PYTHONDONTWRITEBYTECODE=1 python scripts/test_project_bundle.py
```

本次指定 Windows Git Bash 解釋器用法：

```bash
PYTHONDONTWRITEBYTECODE=1 "C:/Users/李/.workbuddy/binaries/python/versions/3.13.12/python.exe" scripts/test_project_bundle.py
```

- validate 僅讀取並向 stdout 輸出 JSON，不寫文件。
- export 在完整校驗、內存渲染成功前不創建目錄或文件；有 ERROR 時不寫任何輸出。
- 輸出必須是**不存在的新目錄**，其父目錄必須已存在。已有目錄或文件一律拒絕，不覆蓋已有工作，也不能覆蓋輸入 JSON。
- 兩份文件先寫同父目錄下的臨時區，再整體重命名發佈；普通寫入/發佈異常會清理臨時區，不留下半份輸出。進程被強制終止、斷電等不承諾事務恢復；同一目標不支持併發導出。
- JSON/輸入 IO/輸出 IO 失敗退出 1，報告 semantic_status 仍為 needs_review。機械校驗有 ERROR 退出 1；無 ERROR（含 WARN）退出 0；CLI 參數用法錯誤由 argparse 退出 2。
- 不修改輸入 JSON、不自動修復、不創建緩存或遷移舊 md。測試設置 PYTHONDONTWRITEBYTECODE=1，臨時 JSON/導出件僅在系統臨時目錄中生成並自動清理。
