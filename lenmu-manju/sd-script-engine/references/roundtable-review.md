# 五席圓桌審核制與敘事連續性

> 精編自《靈境AI劇本改編 skill》（6階段編劇鏈）

本文件覆蓋階段⑥五席圓桌審核制的全部規範（五席角色與協議、評分等級與門禁、市場基準、交付模板），以及三個配套契約：敘事連續性與反碎片化、單集獨立開場與相鄰集過橋契約、全上下文深讀與權威順序（供精修階段執行）。

# 第一部分 · 五席圓桌審核制

## 1.1 核心結果

把「大家覺得好不好看」變成可追溯的批次質量門。每批必須先取得五份互相獨立的審讀意見，再討論分歧和計算綜合結論；不能讓五個席位重複同一個答案，也不能用平均分掩蓋來源跑偏、故事斷裂或合規風險。

圓桌只判斷劇本層競爭力。`S` 表示具備強爆款劇本潛力，不表示已經成為爆款；實際表現仍取決於演員、導演、製作、宣發、分發、檔期和觀眾數據。

所有最終報告必須寫入邊界常量：`SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION`。

## 1.2 門禁與輸入

只消費已經完成階段⑤基礎校驗的連續批次：

- 本批所有乾淨 `EP###_SCRIPT.md`
- `SCRIPT_SET_MANIFEST.json`
- `SERIES_SCRIPT_STRATEGY.md`
- `SOURCE_ADAPTATION_MAP.md`
- `SOURCE_DIALOGUE_LEDGER.md`
- `CONTINUITY_LEDGER.json`
- 對應的IP、故事聖經與分集版本
- 上一批末集和下一集分集卡

若劇本文件缺失、版本不一致、階段⑤失敗標記非空或本批不是連續集數，輸出 `BLOCKED_REPORT`，不先打分。

`STEPWISE` 與 `FULL_SCRIPT_PIPELINE` 都在每批評審結束後停止。`S/A/B/NOT_READY` 只決定推薦動作，不自動繼續，也不自動返修。所有等級統一寫 `decision: AWAITING_USER_DECISION`，等待用戶明確選擇：

1. `PROCEED_CURRENT`：接受當前版本，進入下一批或下一階段。
2. `REFINE_OR_REWRITE`：交給獨立精修/重寫階段，只生成一個新正式版本後再開下一輪評審。

`B/NOT_READY` 選擇繼續時必須另外記錄質量風險接受；不得因此把等級改成 `A/S`。

## 1.3 固定五席

五席不得合併，全部屬於 `AI_ROLE_SIMULATION`，必須顯式標註。沒有真實用戶樣本時，不得寫「真實觀眾一致認為」。

### EDITOR-01 故事主編（權重 25%）

優先回答：

- 小說事實、人物動機、關係責任和關鍵台詞功能是否保真。
- 批次能否用「因為—但是—於是—結果」連續複述。
- 每集是否有目標、反制、換策、代價和局部結果。
- 人物弧、關係弧、知識邊界、時間和鉤子是否累積而非復位。
- 刪除或重排是否損傷後續因果。

不得因為「更刺激」寬恕來源跑偏。

### EDITOR-02 商業主編（權重 25%）

優先回答：

- 前10秒是否有可見爆點、人物處境、行動問題和緊迫性。
- 衝突是否升級，主角是否主動，反派或環境是否有效反制。
- 爽點、笑點、甜點、虐點、燃點或懸念是否完成建立、延遲、見證和兌現。
- 集尾是否在局部支付後留下具體下一動作。
- 同一衝突公式、羞辱方式和鉤子類型是否過度重複。
- 賣點是否能用一句具體故事表達，而不是題材標籤。

不得把吵鬧、打臉次數或反轉數量直接當作節奏。

### VIEWER-01 題材核心觀眾（權重 17%）

按項目目標受眾和題材替換具體畫像，但職責固定：判斷類型期待、角色喜愛、情緒回報、名場面潛力和追更欲。必須說明「期待被滿足/被破壞」的具體位置。

### VIEWER-02 信息流新觀眾（權重 17%）

假設沒有看簡介和上一集。重點記錄：前10秒能否知道誰遇到什麼麻煩；人名、關係、時空和規則是否一次可懂；哪一處必須倒回去看；哪一處會划走；單集結束能否複述主要事件和所得。

### VIEWER-03 連刷挑剔觀眾（權重 16%）

假設已經連續看過上一批。重點記錄：上集結尾是否由本集第一動作支付；信息、關係、傷勢、道具和情緒是否復位；連續三至五集是否重複同一套路；鉤子是否按期兌現，是否不斷拖答案；本批結束後是否仍信任編劇會支付承諾。

主編的 `continue_intent` 使用 `NOT_APPLICABLE`，另寫個人判定 `PASS/REVISE/REWRITE`。

## 1.4 獨立評審協議

### 為什麼先獨立再討論

圓桌一開始就共享觀點，會產生從眾、權威壓制和重複措辭。五席必須先凍結個人意見，再進入討論。每份個人表都記錄輸入快照版本；看到他人意見後形成的新判斷只能寫入圓桌討論，不能反改個人原始分。

### 個人表最低證據

每席必須提供：

- 一句話複述本批故事。
- 最強三點與最弱三點。
- 至少三條集號、場號和正文短語證據。
- 最想繼續看的位置、最可能棄劇的位置和原因。
- 十維分數、個人總分、繼續觀看意願。
- 可直接改寫的三項建議。

證據使用短語或動作概述，不長篇複製劇本：

```yaml
evidence:
  - episode_id: EP006
    scene_id: EP006-SC02
    quote_or_action: "角色把唯一證據交給對手"
    finding: "該動作支付了前兩集建立的信任成本"
```

批評與優點都必須定位；僅寫「總體流暢」「節奏偏慢」不計入有效意見。

### 獨立性檢查

出現以下情況應重做個人審讀：五份報告段落結構和結論完全同序；三名觀眾使用主編術語而沒有觀看體驗；所有人選擇同一最強點、最弱點，卻沒有各自證據；個人分數在圓桌後被統一修改；觀眾聲稱代表真實用戶群體或引用不存在的數據。

### 討論規則

圓桌主持只做四件事：1. 合併重複發現；2. 要求無證據判斷補證；3. 並列衝突意見並尋找適用條件；4. 根據固定公式計算結論。

主持人不能新增第六個評分席位，也不能用「綜合考慮」隨意改分。最終報告保留少數意見和未解決分歧。

## 1.5 每批八步評審

### 1. 凍結輸入快照

記錄劇本版本、批次、集數、文件哈希、上游版本、市場基準日期和評審輪次。返修後必須產生新快照和新輪次，不得覆蓋舊意見。

### 2. 獨立審讀

五席分別只讀乾淨劇本，再按需核對審稿層。任何席位在提交個人表前不得讀取其他席位的分數、結論或建議。

### 3. 硬門檢查

先檢查來源權威、故事完整、相鄰連續、單集理解、鉤子兌現、價值與合規六項硬門。任一失敗，綜合等級只能是 `NOT_READY`，不得靠高爽點分拉回。

### 4. 證據合併

把相同問題合併，把相反意見並列。每個結論必須回答「哪一集、哪一場、哪段動作或台詞導致這個判斷」。「節奏不夠」「不夠爽」「人物不討喜」沒有證據時無效。

### 5. 圓桌討論

依次討論：

1. 普通觀眾能否連續複述。
2. 每集是否先支付結果再落鉤子。
3. 爽點、笑點、情感或懸念是否有建立、對抗、見證和後果。
4. IP選擇和台詞是否可辨識。
5. 相鄰集與整批是否重複、疲勞或斷裂。
6. 相比當前同題材內容，差異化賣點是否來自故事與人物，而非噱頭堆砌。

保留少數意見，不強行偽造全票共識。

### 6. 計算綜合分與等級

使用固定十維權重和席位權重。綜合分只能由個人已凍結分數計算。先判硬門，再判分數和席位下限。輸出等級與推薦：

- `S`：強爆款劇本潛力，`PROCEED_RECOMMENDED`。
- `A`：具備平台競爭力，`PROCEED_RECOMMENDED`。
- `B`：基礎故事成立但未達到爆款目標，`REFINE_RECOMMENDED`。
- `NOT_READY`：存在阻斷問題，`REWRITE_RECOMMENDED`。

推薦不能替代用戶選擇。任何結果均輸出同一組可選動作和回覆案例。

### 7. 形成返修任務

按 `P0/P1/P2` 排序：`P0` 來源跑偏、因果斷裂、人物失真、時間衝突、鉤子失約、合規風險；`P1` 節奏、爽點、主角主動性、台詞、開場與集尾不足；`P2` 措辭、表演空間、局部趣味和製作成本優化。

每項寫明受影響集數、正文證據、修改目標、不可改變的上游事實和驗收方法。圓桌不直接改寫劇本。

### 8. 更新批次與全劇評審賬本

登記本輪等級、分數、推薦、主要優缺點、用戶決策狀態和下一次評審入口。審核完成後保持 `AWAITING_USER_DECISION`。只有用戶接受當前版本，該批才可鎖定；`B/NOT_READY` 還需登記風險接受。用戶選擇修改時，本輪保持只讀，等待新劇本版本開啟下一輪獨立評審。

## 1.6 評分、等級與返修門禁

### 十維統一評分

每席對十個維度打 `0—10` 分，使用同一權重，便於比較。維度權重合計 100：

| 維度 | 權重 | 核心問題 |
|---|---:|---|
| `source_fidelity` | 12 | 改編是否保留原作事實、動機、關係、規則與關鍵功能 |
| `story_clarity_completeness` | 13 | 本批與各集是否完整、流暢、能連續複述 |
| `conflict_strategy_progression` | 10 | 目標、反制、換策與代價是否真實推進 |
| `pacing_information_density` | 10 | 是否緊湊但不切碎，信息釋放是否恰當 |
| `payoff_satisfaction` | 10 | 爽點/情緒點是否有建立、見證、結果和後果 |
| `hook_next_click` | 12 | 集尾是否具體、可支付、令人必須點下一集 |
| `character_ip_appeal` | 10 | 角色是否鮮活、可愛、可辨識並持續做選擇 |
| `dialogue_performance` | 8 | 台詞是否像人物爭取結果、可演、有潛台詞 |
| `standalone_and_continuity` | 8 | 單集可懂與上下集承接是否同時成立 |
| `novelty_market_fit` | 7 | 同題材中是否有來自人物與機制的差異化 |

個人總分：`Σ(維度分 × 維度權重) ÷ 10`。不得先寫個人總分再倒推維度分。

### 席位權重與綜合分

| 席位 | 權重 |
|---|---:|
| EDITOR-01 | 25% |
| EDITOR-02 | 25% |
| VIEWER-01 | 17% |
| VIEWER-02 | 17% |
| VIEWER-03 | 16% |

綜合分：`Σ(個人總分 × 席位權重) ÷ 100`。主編合計 50%，觀眾合計 50%，避免只顧專業結構或只顧即時刺激。

### 六項硬門

必須分別為 `PASS`：

1. `source_authority`：沒有無授權核心改寫。
2. `narrative_completeness`：沒有碎片化、因果斷裂或無局部結果。
3. `adjacent_continuity`：上下集與跨批狀態連續。
4. `episode_comprehension`：首看觀眾能理解人物、困境、目標和結果。
5. `hook_payoff_integrity`：鉤子有來源、有支付位置且本批沒有失約。
6. `value_and_compliance`：價值表達與內容風險沒有阻斷性問題。

任一為 `FAIL`，等級直接為 `NOT_READY`。整改後重新開啟新一輪評審，不保留原分直接升檔。

### 等級定義

**S：強爆款劇本潛力**——同時滿足：綜合分 90—100；兩名主編均不低於 88；五席無人低於 80；至少兩名觀眾為 `MUST_CONTINUE`，第三名不低於 `WILL_CONTINUE`；六項硬門全過；本批沒有 P0 問題。推薦 `PROCEED_RECOMMENDED`，仍須等待用戶選擇。

**A：具備平台競爭力**——同時滿足：綜合分 80—89.99；兩名主編均不低於 78；五席無人低於 70；至少兩名觀眾為 `MUST_CONTINUE` 或 `WILL_CONTINUE`；六項硬門全過。推薦 `PROCEED_RECOMMENDED`。P1/P2 可以由用戶選擇繼續優化；不得自動進入下一批。

**B：基礎成立但未達到爆款目標**——綜合分 70—79.99，或雖高於 80 但不滿足 A 的席位下限/觀看意願；六項硬門全過。推薦 `REFINE_RECOMMENDED`。用戶可以選擇進行一次精修/重寫，也可以明確接受當前質量風險後進入下一步。

**NOT_READY：未達 B 級**——綜合分低於 70；或任一硬門失敗；或存在來源跑偏、核心因果斷裂、嚴重人物失真、時間不可能、鉤子失約或阻斷性合規風險。推薦 `REWRITE_RECOMMENDED`。用戶仍需明確選擇；若接受當前版本繼續，必須記錄硬傷和風險接受，不得改寫等級。

### 統一用戶決策門

每次審核無論等級都寫：

```yaml
decision: AWAITING_USER_DECISION
allowed_user_actions:
  - PROCEED_CURRENT
  - REFINE_OR_REWRITE
selected_action: NONE
```

固定提示：1. 接受當前版本，進入下一批或下一階段。回覆：`1`。2. 進行一次精修或重寫。回覆：`2`。

用戶未選擇前不得路由。`B/NOT_READY` 的 `risk_acceptance_required` 為 `true`，只有用戶明確選擇 1 並確認風險後才可登記 `USER_APPROVED`。

### 紅果同賽道劇本層潛力

只允許：`STRONG_SCRIPT_POTENTIAL`（通常對應 S）、`COMPETITIVE_SCRIPT_POTENTIAL`（通常對應 A）、`BORDERLINE_SCRIPT_POTENTIAL`（對應 B）、`NOT_READY_FOR_PLATFORM_COMPARISON`（對應 NOT_READY）。

必須同時寫：`SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION`。不得寫預計播放量、充值率、完播率、平台採購價或「必爆」。這些數據需要真實上線樣本或平台內部數據。

### 返修優先級條目

每個任務必須包含：

```yaml
priority: P0
episode_ids: ["EP011", "EP012"]
evidence: "EP011-SC03的證據失竊沒有觸發EP012第一動作"
problem: "相鄰集鉤子未支付"
revision_target: "讓EP012第一動作直接處理證據失竊，並建立新的行動目標"
protected_facts: "不得改變鎖定的失竊者和證據內容"
acceptance_test: "LAST_FRAME_FIRST_ACTION_TEST通過"
```

不得只寫「加強節奏」「增加爽點」「台詞更生動」。

## 1.7 市場基準

- `benchmark_id`：`HG-SCRIPT-2026-07-23`
- `as_of_date`：`2026-07-23`
- `basis_type`：`PUBLIC_SOURCE_SYNTHESIS`
- `official_internal_scorecard`：`false`
- `prediction_scope`：`SCRIPT_LEVEL_ONLY`

本基準用於評估「紅果同賽道劇本層競爭力」，不是紅果官方內部評分表。公開資料沒有披露統一的 S/A/B 算法、採購閾值、完播率門檻或爆款公式；不得自行編造。

**公開來源**：

1. 湖南省廣播電視局與紅果短劇真人微短劇項目通知（2026-06-08）：投稿劇本需完成不少於 40 集；真人項目限定豎屏，並按階段組織專家評估；鼓勵「畫風優良、創新探索、立意向上」，用短劇節奏講積極且有主題表達的故事。
2. 國家廣播電視總局《微短劇發展管理辦法（徵求意見稿）》（2026-06-24）：對微短劇的公開定義強調主題主線明確、故事情節連續完整、人物角色突出；強調原創、版權、價值導向和內容規範。
3. 國家廣播電視總局「微短劇精品創作傳播計劃」（2026-05-26）：強調內容為本、品質為魂、守正創新；追求思想與藝術交融、網感與美感兼備、通俗質樸、貼近現實；平台承擔創作者孵化、原創IP和系列化IP培育、精品審核與傳播責任。
4. 2026「星耀影都」全國微短劇創投季（紅果短劇參與承辦）：劇本與AI漫劇均設置專項賽道；評價方向包括多元題材創新、城市文化IP表達、主題鮮明、製作精良和創意突出。

**轉化為劇本評審維度**——公開基準只能支持以下判斷：主線是否明確，故事是否連續完整；角色是否突出且具備系列化IP潛力；是否具有短劇節奏、網感、情緒回報和持續追看機制；創意是否來自人物、題材機制或真實生活，而非低俗獵奇和套路堆砌；是否兼顧通俗表達、主題表達、正向價值與合規；40 集以上項目是否具備長線穩定性，而不是前幾集強、後續注水。

**不允許推斷**——沒有真實平台數據時，不判斷：一定會被紅果採購或簽約；一定成為爆款；具體播放量、完播率、付費率、拉新率和分賬；紅果內部編輯的真實分數或算法推薦結論。

最終措辭必須是：「基於截至2026-07-23的公開資料和本批劇本證據，該項目在劇本層呈現某等級潛力；這不是平台官方結論或實際上線表現預測。」

**更新規則**——以下任一發生時重新檢索並更新：距 `as_of_date` 超過 90 天；紅果、抖音集團或廣電主管部門發佈新徵集/審核/精品計劃；用戶要求比較某一具體年度、賽道或平台活動；項目從AI漫劇切換為真人豎屏、橫屏精品或其他發行形態。

## 1.8 雙層交付

每批寫入 `04_roundtable/BATCH-###/`：

```text
04_roundtable/
├── SERIES_REVIEW_LEDGER.json
└── BATCH-001/
    ├── PANEL_INPUT_SNAPSHOT.json
    ├── EDITOR_01_REVIEW.md
    ├── EDITOR_02_REVIEW.md
    ├── VIEWER_01_REVIEW.md
    ├── VIEWER_02_REVIEW.md
    ├── VIEWER_03_REVIEW.md
    ├── ROUND_TABLE_DISCUSSION.md
    ├── BATCH_REVIEW_REPORT.md
    ├── REVISION_BRIEF.md
    ├── BATCH_REVIEW_MANIFEST.json
    ├── USER_DECISION_PROMPT.md
    └── HANDOFF_CARD.md
```

全劇共用 `04_roundtable/SERIES_REVIEW_LEDGER.json`。個人審讀、圓桌過程與最終判定不能只存在聊天中。

### 個人評審條目

```yaml
PANEL_MEMBER_REVIEW:
  member_id: VIEWER-02
  panel_type: AI_ROLE_SIMULATION
  batch_id: BATCH-001
  input_snapshot_version: SNAPSHOT-B001-R1
  one_sentence_recall: "普通觀眾對本批故事的複述"
  strongest_points: []
  weakest_points: []
  evidence: []
  most_want_to_continue_at: "集號、場號、原因"
  likely_drop_point: "集號、場號、原因；沒有則寫NONE_WITH_REASON"
  continue_intent: MUST_CONTINUE
  scores: {}
  weighted_total: 88.4
  recommendations: []
  independent_submission: true
```

### 圓桌討論

`ROUND_TABLE_DISCUSSION.md` 至少包含：五席獨立結論摘要；已達成共識的優點；已達成共識的問題；分歧議題、雙方證據和主持結論；單集獨立觀看討論；相鄰集與整批連刷討論；爽點/看點建立—見證—兌現討論；紅果同賽道劇本層比較與邊界；少數意見。

不寫虛構的寒暄、鼓掌或人物表演。圓桌是專業評審記錄，不是綜藝對白。

### BATCH_REVIEW_MANIFEST 合同

清單至少記錄：輸入劇本版本、批次、連續集數和評審輪次；`panel_type: AI_ROLE_SIMULATION`；五個固定席位及各自權重、十維分數、個人總分、繼續觀看意願和證據；六項硬門結果；固定市場基準ID、基準日期、公開來源和劇本層預測邊界；綜合分、等級、推薦動作、統一用戶決策門和紅果同賽道劇本層潛力；分歧、阻斷問題、優先返修項、失敗標記和文件路徑。

```json
{
  "schema_version": "1.0",
  "version": "ROUND-TABLE-B001-R1",
  "review_stage": "04R_SCRIPT_ROUNDTABLE",
  "panel_type": "AI_ROLE_SIMULATION",
  "script_manifest_version": "SCRIPT-SET-V1",
  "batch_id": "BATCH-001",
  "review_round": 1,
  "episode_ids": ["EP001", "EP002", "EP003", "EP004", "EP005"],
  "input_snapshot_version": "SNAPSHOT-B001-R1",
  "panel_members": [],
  "dimension_weights": {
    "source_fidelity": 12,
    "story_clarity_completeness": 13,
    "conflict_strategy_progression": 10,
    "pacing_information_density": 10,
    "payoff_satisfaction": 10,
    "hook_next_click": 12,
    "character_ip_appeal": 10,
    "dialogue_performance": 8,
    "standalone_and_continuity": 8,
    "novelty_market_fit": 7
  },
  "hard_gate_results": {
    "source_authority": "PASS",
    "narrative_completeness": "PASS",
    "adjacent_continuity": "PASS",
    "episode_comprehension": "PASS",
    "hook_payoff_integrity": "PASS",
    "value_and_compliance": "PASS"
  },
  "market_benchmark": {
    "benchmark_id": "HG-SCRIPT-2026-07-23",
    "as_of_date": "2026-07-23",
    "basis_type": "PUBLIC_SOURCE_SYNTHESIS",
    "official_internal_scorecard": false,
    "prediction_scope": "SCRIPT_LEVEL_ONLY"
  },
  "composite_score": 0,
  "grade": "NOT_READY",
  "decision": "AWAITING_USER_DECISION",
  "recommended_action": "REWRITE_RECOMMENDED",
  "user_decision": {
    "status": "AWAITING_USER_DECISION",
    "allowed_actions": ["PROCEED_CURRENT", "REFINE_OR_REWRITE"],
    "selected_action": "NONE",
    "risk_acceptance_required": true,
    "risk_acceptance_recorded": false
  },
  "hongguo_script_potential": "NOT_READY_FOR_PLATFORM_COMPARISON",
  "claim_boundary": "SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION",
  "panel_disagreements": [],
  "blocking_findings": [],
  "priority_revisions": [],
  "failure_flags": [],
  "open_items": []
}
```

`panel_members` 條目記錄：`member_id`、`role_type`、`specialty`、`panel_weight_percent`、`review_path`、`independent_submission`、十維 `scores`、`weighted_total`、`continue_intent`（主編為 `NOT_APPLICABLE` 並另寫 `personal_verdict`）、`evidence`、`strengths`、`must_fix`。

### 最終報告與用戶決策提示

`BATCH_REVIEW_REPORT.md` 先寫結論：綜合分與等級；五席個人總分與繼續觀看意願；是否具備紅果同賽道劇本層潛力；三個最強證據；三個最危險問題；是否進入下一批。最後必須重複預測邊界，避免把劇本評審寫成平台承諾。

`USER_DECISION_PROMPT.md` 先展示等級、推薦動作、主要風險，再固定顯示：1. 接受當前版本，進入下一批或下一階段。2. 進行一次精修或重寫。回覆案例：`回覆：1`、`回覆：2`、`接受當前版本`、`進行修改`。

評審文件只保存待選擇狀態。用戶選擇另存 `USER_QUALITY_DECISION.json` 並更新項目狀態，不覆蓋原始評審。

### HANDOFF_CARD

交接卡記錄批次等級、綜合分、五席繼續觀看意願、已通過硬門、推薦動作、用戶可選動作和風險。用戶未選擇前，不寫允許進入的下一批，也不調用精修流程。

## 1.9 階段自檢

- 五席數量、角色、權重和個人文件完整。
- 每席獨立意見不是換名複述，且至少三條正文證據。
- 十維分數、個人總分和綜合分可重新計算。
- 六項硬門全部有證據；失敗時沒有被平均分覆蓋。
- `S/A/B/NOT_READY` 與分數、席位下限和觀看意願一致。
- 「紅果爆款」只寫為劇本層潛力，不聲稱實際播放結果。
- `B/NOT_READY` 有可執行返修任務，所有等級都有用戶決策提示。
- 評審完成後是 `AWAITING_USER_DECISION`，沒有自動路由字段。
- 返修後創建新評審輪次，保留舊記錄。

## 1.10 圓桌禁止越界

不假扮真實人類觀眾，不編造紅果內部指標、官方 S/A/B 標準、播放量或轉化率；不因題材熱門就判爆款；不以平均分掩蓋硬傷；不直接修改小說事實、分集承諾或劇本正文；不讀取或執行精修流程；不替用戶選擇繼續或修改；不創建資產、分鏡、燈光、剪輯或視頻提示詞。

## 1.11 防捧殺硬規則與「會診一致度過高」警報

> 融合自 script-writing-studio 02 模塊。**核心目的：防止 AI 會診變成集體說好話。**

### 1.11.1 六條硬規則

| # | 規則 |
|---|---|
| 1 | **真實反饋，不捧殺**：每位評委必須給出**至少 1 個真實弱點**；劇本真好時給**未來風險點**。 |
| 2 | **每條意見必須有證據**：必須引用**至少 1 段劇本原文、大綱條目或明確劇情事實**，不允許空泛判斷。 |
| 3 | **必須有優先級**：問題要區分**高/中/低**優先級，告訴用戶**先改什麼**。 |
| 4 | **必須有立場衝突**：如果所有評委意見都很溫和 → 主治醫生歸納前**觸發"會診一致度過高"警報**，檢查是否召集偏差。 |
| 5 | **禁止角色 OOC**：評委發言要符合該評委身份和關注點，**不要全部說同一種話**。 |
| 6 | **重要分歧立即追問**：碰到與項目檔案、大綱或用戶目標衝突的地方，**停下問**，不假裝理解後硬評。 |

### 1.11.2 禁用泛話清單

以下泛話**禁止出現在五席意見中**：

```
❌ 整體不錯
❌ 節奏可以
❌ 人物還可以
❌ 這個地方可以再加強一下
❌ 建議再豐富一點
❌ 立意很好
❌ 有潛力
```

**必須改寫成**：`【問題定位】+【具體證據（引用原文）】+【影響】+【優先改法】`

### 1.11.3 「會診一致度過高」警報機制

**觸發條件**：所有席位的意見**都很溫和**（無高優先級問題、無非議、無立場衝突）。

**觸發後動作**：

```
① 主治醫生在歸納前暫停，輸出警報：
   ⚠️ 會診一致度過高，可能存在召集偏差
② 檢查兩件事：
   · 是否召集偏差？（五席是否都偏向了同一立場）
   · 是否評價失真？（是否因題材偏好/作者濾鏡而普遍寬鬆）
③ 處理：
   · 若確認召集偏差 → 重新配置席位視角或補充對立視角
   · 若確認評價失真 → 強制要求每席補充"最壞情況推演"
④ 在 BATCH_REVIEW_REPORT 中顯式記錄本次警報及其處理
```

**反捧殺強度三檔**（隨用戶明確要求切換）：

| 檔位 | 措辭 | 適用 |
|---|---|---|
| 常規檔 | 保持，措辭溫和 | 默認 |
| 嚴苛檔 | 評委更辛辣，所有"對作者的善意"被抑制 | 用戶要求"往死裡批" |
| 經典檔 | 保持，但允許對經典作品有真誇獎（不強行挑刺） | 改編名作 |

### 1.11.4 階段自檢追加項

- 五席中每一席是否都給出了至少 1 個真實弱點？
- 每條意見是否都引用了具體證據（非空泛判斷）？
- 是否出現了"會診一致度過高"警報？若有，是否已記錄處理？

## 1.12 台詞七維診斷框架

> 融合自 script-writing-studio 03 模塊。**與 `short-drama-director/references/dialogue-doctor-7d.md`（總控）雙向互鏈**：那份管"台詞七宗罪的症狀清單"，本框架管"**逐句過七維**的量化診斷"。

### 1.12.1 七維定義（每條台詞都過）

| 維度 | 核心拷問 | 紅線 |
|---|---|---|
| **① 角色辨識度** | 遮住角色名，能不能認出誰在說？ | A 角色台詞換給 B 說也毫無違和 = 嚴重不及格 |
| **② 潛台詞層級** | 字面說的是不是真意？有幾層？ | 所有台詞都是 0 層（想什麼說什麼）= 像 AI 寫的而非戲 |
| **③ 衝突推進力** | 這一句讓張力前進了，還是原地踏步？ | 連續 3 句以上沒推進任何東西 = 該刪 |
| **④ 類型語感** | 這句話在這個類型裡成立嗎？ | 單句混入跨類型違和詞 = 立即標紅 |
| **⑤ 信息效率** | 用最少的字傳遞最多的東西嗎？ | 連續兩句設定灌輸 = 重寫 |
| **⑥ 節奏與音樂性** | 讀出來好聽嗎？長短句搭配嗎？ | 通篇齊整長句 / 通篇短促獨詞 = 單調 |
| **⑦ 金句潛力** | 能不能截圖發抖音 / 引用 / 複用？ | **加分項非底線**；一集 1-3 句即可，滿篇金句 = 沒有金句 |

### 1.12.2 各維檢查項速查

```
① 角色辨識度：詞彙庫 / 句長偏好 / 句式習慣 / 口頭禪語氣詞 / 文化層
② 潛台詞層級：字面意vs真實意圖（0層直白/1層反話/2層錯位/3層折射）/ 觀眾解碼難度 / 雙方不知情時的雙關
③ 衝突推進力：信息量/立場/關係/情緒溫度/下一步動作 至少一項變化 / 回合感 / 拒絕反駁加碼
④ 類型語感：古裝忌現代詞 / 都市忌文言密度 / 懸疑信息控制 / 喜劇反轉錯位 / 年代術語匹配
⑤ 信息效率：反exposition / 一句多用（≥2項=優秀）/ 刪字測試 / 替換測試
⑥ 節奏音樂性：長短交錯 / 停頓點 / 語氣詞顆粒度 / 壓韻排比（高級項）/ 可朗讀性
⑦ 金句潛力：可獨立成句 / 修辭鉤子 / 真理+反差 / 角色烙印
```

### 1.12.3 輸出硬契約（★ 關鍵）

**診斷台詞時，必須按「原台詞 → 改寫建議 → 為什麼這麼改」結構輸出，且"為什麼這麼改"必須給出 ≥3 條維度依據。**

```
【原台詞】"你根本不懂我！"
【改寫建議】"（把煙按滅）……你以為你懂了？"
【為什麼這麼改】
  ① 角色辨識度：加"把煙按滅"的動作綁定，區別於其他角色
  ② 潛台詞層級：從 0 層直白情緒 → 1 層反詰（表面質問，實則逃避）
  ③ 信息效率：刪掉"根本"這類無效加強詞，用動作替代形容詞
```

⚠️ **凡"改寫建議"未附 ≥3 條維度依據的，視為不合格產出，必須重做。**

### 1.12.4 與其他模塊的邊界

- **本框架不改台詞**：只做診斷 + 改寫建議；實際改寫由劇本階段執行。
- **不改劇本結構**：結構問題回 `six-stage-pipeline.md`。
- **不涉分鏡**：台詞分配節拍屬分鏡引擎職責。

# 第二部分 · 敘事連續性與反碎片化

本規則判斷劇本正文是否真的是完整、流暢的故事，而不是字段齊全的劇情片段。鎖稿前必須執行，不得用分鏡、音樂、剪輯或元數據掩蓋劇本問題。

## 2.1 完整故事單元

每集不要求解決全劇主線，但必須完成一個可複述的 `STORY_UNIT`：

```yaml
STORY_UNIT:
  entry_pressure: "開場已經作用於人物的壓力，不是背景介紹"
  active_goal: "主角本集要完成、阻止、取得或確認什麼"
  first_strategy: "主角首先採取的可見行動"
  counteraction: "對手、規則、環境或關係對象如何主動反制"
  strategy_change: "原辦法失效後，主角換了什麼做法"
  visible_cost: "本集畫面中實際支付或確認的代價"
  local_result: "本集完成、失敗或部分完成的明確結果"
  new_pressure_or_closure: "交給下一集的新行動壓力，或本弧閉合結論"
```

這些字段必須能在正文中指向具體動作、台詞和結果。不能把「承擔風險」「關係改變」只寫在審稿元數據中，正文卻沒有人失去、拒絕、暴露、負責或改變行動。

## 2.2 CONTINUOUS_SCENE_SPLIT 連續場景拆集

同一地點、同一時間、同一目標的一場戲，默認作為一個完整場次或一集處理。只有同時滿足以下條件才允許跨集：

1. 前一集已經完成一次局部兌現，不是把一句話或一個動作攔腰截斷。
2. 集尾發生不可逆狀態變化，例如證據出現、行動啟動、身份暴露、選擇落地或關係破裂。
3. 下一集開場立即支付鉤子，並建立新的行動目標或策略，不只是繼續上一輪解釋。
4. 兩集分別具有獨立的 `STORY_UNIT`，刪去集號後不是一場普通談判被機械切成兩半。

若不滿足，標記 `CONTINUOUS_SCENE_SPLIT` 並退回分集合並或重排。

## 2.3 單集獨立開場與相鄰集過橋

每集是獨立發佈的視頻，也是連續劇的一環。首場前 10 秒必須用正在發生的危險、衝突、證據、行動或反常狀態，同時建立行動主體、直接困境、本集目標和 `WHY_NOW`；不能要求觀眾先看上一集簡介才能理解。

相鄰集按「上一集最後變化 → 本集第一動作 → 本集新目標/新策略」連讀。允許用 1–3 秒動作、聲音或短句重疊幫助獨立觀看，但不能完整復播上一集，也不能先解釋幾十秒才兌現上集鉤子。

每集執行：`STANDALONE_EPISODE_TEST`、`LAST_FRAME_FIRST_ACTION_TEST`、`FLASHBACK_ANCHOR_TEST`（完整定義見第三部分）。

## 2.4 衝突、代價與關係轉變

**方案必須經歷抵抗**：人物提出方案後，至少出現一次針對該方案的質疑、阻止、失敗、條件交換或現實檢驗。僅在紙上列步驟、說清道理、對方立即同意，標記 `CHECKLIST_SOLUTION`。

**關係轉變必須有證據**：從敵對到合作、懷疑到信任、疏離到親近，都要有觸發行動：保護、拒絕利益、公開站隊、交出控制權、承擔責任或付出資源。只有一句漂亮台詞或一次眼神就達成共識，標記 `SUDDEN_CONSENSUS`。

**可見代價必須發生**：代價可以是失去時間、資源、機會、身份安全、關係信任或道德退路。必須在本集發生、被確認或觸發後果；只寫「可能被問責」「承擔風險」但無人採取導致風險的行動，標記 `UNPAID_COST`。

**賭注先建立再調用**：資格、生命、婚姻、項目、秘密或親人等賭注，在人物拿它施壓前必須被觀眾建立。突然說「你連資格也不要了」，而前文沒有資格線，標記 `UNESTABLISHED_STAKE`。

**情感必須改變行動**：創傷、親情和愛情不能只用摸道具、閃回或一句宣言代表。情感證據必須影響人物選擇、遲疑、隱瞞、犧牲或策略；否則標記 `EMOTION_BY_LABEL`。

## 2.5 反碎片化標記總表

出現任一未解決標記時，劇本不得 `LOCKED`：

- `CONTINUOUS_SCENE_SPLIT`：同一場戲因時長機械拆集。
- `CHECKLIST_SOLUTION`：方案靠列清單或解釋直接解決，沒有抵抗與檢驗。
- `SUDDEN_CONSENSUS`：關係轉變缺少觸發行為和代價。
- `UNPAID_COST`：宣稱有代價，正文沒有支付或後果。
- `UNESTABLISHED_STAKE`：重要賭注第一次出現就被拿來施壓。
- `EMOTION_BY_LABEL`：元數據說情緒重要，正文沒有改變行動。
- `PROP_ONLY_PROGRESS`：主要進展只靠連續摸、看、放置道具，沒有人物策略。
- `EXPOSITION_CHAIN`：連續對白只解釋信息，沒人改變對話目的或行動。
- `EXPECTED_HOOK_ONLY`：結尾只確認觀眾已經預料的結果，沒有改變下一步行動。
- `UNSOURCED_CORE_PAYOFF`：為讓本批顯得完整，新增來源未提供的身份、簽名、證據、機關、暗號、能力、勝負或謎底。
- `IMPOSSIBLE_TIME_BRIDGE`：相鄰集的日期、時段、倒計時或「連續」標記互相沖突，所需經過的時間沒有被建立。
- `ALTERED_SOURCE_STAKE`：把原作的期限、觸發條件、懲罰強度、資格狀態或風險可能性擅自改早、改重、改輕或寫成既成事實。
- `SEMANTICALLY_BROKEN_LINE`：台詞有氣勢但主語、對象、條件或並列關係不成立，觀眾無法準確複述意思。
- `UNESTABLISHED_ACTION_STATE`：用於轉折的重要界面、標題、文件、審批或道具狀態沒有被此前動作建立，突然作為既成事實出現。
- `KEY_LINE_OVERUSE`：來源金句或主題句在相鄰集被完整重複，卻沒有關係位置、行動功能或含義升級。
- `SUMMARY_NOT_SCRIPT`：正文仍是故事概述、場次說明或編劇意圖，沒有可表演的行動和對白。
- `BEAT_LIST_FRAGMENTATION`：靠節拍標題和短句拼貼代替連續故事。
- `SCENE_CAUSAL_GAP`：上一場結果沒有導致下一場，關鍵過程被場間跳過。
- `PASSIVE_PROTAGONIST`：主角只接收信息和反應，沒有主動目標、策略或選擇。
- `GENERIC_IP_PERFORMANCE`：角色動作、台詞和關係信號可任意換給其他人。
- `VOICE_HOMOGENIZATION`：主要人物句式、攻防方式和語氣趨同。
- `DIALOGUE_AS_EXPOSITION`：對白主要承擔資料說明，沒有爭取行動結果。
- `SOURCE_KEY_LINE_LOSS`：關鍵台詞缺失、錯置人物或丟失原有行動功能。
- `LOCAL_PAYOFF_MISSING`：只留下下一集鉤子，沒有支付本集承諾。
- `HOOK_DEBT_BROKEN`：主鉤子沒有按賬本兌現，或下一集沒有從承接動作開始支付。
- `MECHANICAL_FAST_PACING`：通過刪除動機、反制、反應和代價製造表面快節奏。
- `MAINLINE_DRIFT`：本集主要講述內容偏離鎖定主事件。
- `UNAUTHORIZED_PLOT_INVENTION`：新增來源和上游未授權的重要故事事實。
- `DELETION_CAUSAL_BREAK`：刪減導致因果、動機、伏筆或後續理解斷裂。
- `SOURCE_MOTIVATION_DRIFT`：人物行動理由偏離原作。
- `TROPE_REPLACEMENT`：用流行套路替換原作衝突機制或人物選擇。
- `CONNECTIVE_MATERIAL_OVERREACH`：連接材料實際改變了事實、責任、關係、規則或答案。
- `CROSS_BATCH_STATE_DRIFT`：上一批出口狀態與下一批入口狀態不一致。
- `BATCH_CONTEXT_GAP`：本批依賴的關鍵狀態未在上游、劇本或連續性賬本中建立。
- `STANDALONE_CONTEXT_GAP`：單獨觀看本集時，前 10 秒無法識別行動主體、直接困境、當前目標或 `WHY_NOW`。
- `EPISODE_OPENING_DEPENDENCY`：本集開場只有看過上一集或讀取簡介才能理解。
- `ADJACENT_EPISODE_BRIDGE_BREAK`：上一集最後變化沒有觸發本集第一動作，或人物狀態被重置。
- `FLASHBACK_TIME_ANCHOR_MISSING`：閃回、時間經過或返回主時間線缺少正文中的可見時間錨點。

標記必須通過改寫正文消除，不能在報告中把標記改為空數組而保留原問題。

## 2.6 SOURCE_BOUNDED_CLOSURE 來源受限的閉合

完整故事單元必須閉合行動問題，不必閉合全劇事實謎團。原文只給出「某物可能與失蹤親人有關」時，可以閉合「人物決定封存、公開驗證或與誰合作」，不能新增文件、簽名、機關或檢測結果證明關聯成立。

`INFERENCE 不是` 把新謎底寫入正式劇本的授權。允許推定的內容僅限不改變主線事實的表情、移動、職業流程和連接動作；一旦新增內容改變觀眾對身份、責任、世界規則、關鍵道具或結局的判斷，就屬於核心事實。未提供的謎底必須保留為 `OPEN_ITEM`，並用人物行動結果產生追看，而不是用編造答案製造閉合。

鎖稿時從每個 `local_result` 和鉤子反查來源。無法引用 `EVT` 或明確允許的連接推定時，標記 `UNSOURCED_CORE_PAYOFF` 並退回故事聖經或分集階段。

## 2.7 SOURCE_PRESSURE_CONTRACT 原作壓力保真

來源中的壓力不只是一句「有危險」，還包含生效時間、觸發條件、對象和後果強度。例如「**三天後的開放日必須展出，否則撤項**」不能改成「**今天停展就立即撤項**」；「資格可能受影響」不能寫成「已經取消資格」。為了製造強衝突而縮短期限、升級處分或把風險寫成事實，屬於篡改主線因果，不屬於連接推定。

每集在 `SCRIPT_SET_MANIFEST.json` 記錄：

```yaml
pressure_contract:
  source_pressure: "來源原意"
  script_pressure: "劇本實際使用的壓力"
  onset_and_condition: "何時、在什麼條件下觸發什麼後果"
  source_trace: "SRC-###:範圍"
  change_status: "UNCHANGED 或 USER_AUTHORIZED"
```

默認只能寫 `UNCHANGED`。只有用戶明確授權改變該壓力時才能寫 `USER_AUTHORIZED`，並在項目 `USER_OVERRIDE` 中留痕。發現劇本把「以後/可能/條件成立才發生」改成「現在/一定/已經發生」，標記 `ALTERED_SOURCE_STAKE`，`source_pressure_fidelity` 不得寫 `PASS`。

## 2.8 EPISODE_TRANSITION_CONTRACT 時間線與跨集過橋

相鄰兩集必須先核對絕對時間、相對時間和倒計時。上一集若明確「開放日在三天後」，下一集不得寫成「時間連續」並直接進入開放日；必須用場頭、屏顯、環境變化、人物狀態或一個有效動作建立「三天後」。相反，上一集若以正在下落的杯子作鉤子，下一集不得無說明跳到次日。

每集在 `SCRIPT_SET_MANIFEST.json` 記錄：

```yaml
timeline:
  entry_time: "本集開場所處的明確時間狀態"
  exit_time: "本集結束所處的時間狀態"
  elapsed_time: "本集正文實際經過多久"
  transition_from_previous: "承接動作，或明確的時間跳轉建立"
  transition_to_next: "連續承接，或下集必須建立的時間跳轉"
```

檢查所有屏顯時間、人物說出的期限、日夜、服裝傷勢和流程耗時。可以省略無戲劇價值的過程，不能省略會讓因果看似瞬移的時間證據。發現矛盾時標記 `IMPOSSIBLE_TIME_BRIDGE`；修復正文和跨集橋後，`timeline_continuity` 才能寫 `PASS`。

## 2.9 METADATA_STRIPPED_READ 去元數據通讀

鎖稿前臨時隱藏集頭字段、`BEAT` 標題、功能標籤、審稿結論和解釋性項目符號，只朗讀場頭、動作、台詞、聲音與場尾。逐集以及相鄰兩集連讀，回答：

1. 不看說明，能否知道人物此刻要什麼、為什麼現在必須做？
2. 每個動作是否由上一動作、信息或選擇觸發，而非作者把新材料擺上桌？
3. 對手是否根據主角行動改變策略？
4. 關係變化能否指出觸發行為，而非靠審稿表宣稱？
5. 本集結束時是否有實際結果，不只是「準備開始下一步」？
6. 同場跨集是否形成兩個完整單元，而不是一個場次的上下半段？
7. 台詞是否像人物在爭取結果，而非編劇總結主題？
8. 相鄰集連讀時，日期、倒計時和「連續/稍後/次日」等標記是否真的相容？
9. 劇本使用的期限、懲罰和資格風險，是否與來源的生效條件同樣準確？
10. 關鍵台詞能否用直白句準確複述；參與轉折的界面、文件和道具狀態是否有建立動作？
11. 單獨抽出本集時，首場前 10 秒能否識別行動主體、直接困境、本集目標和 `WHY_NOW`？
12. 上一集最後變化是否由本集第一動作直接承接；閃回和時間跳轉是否有正文錨點？

任一核心答案為否，`metadata_stripped_read` 不能寫 `PASS`。

## 2.10 跨批連續性

長劇分批輸出時，批次邊界不是敘事邊界。每一批都維護人物位置、身體與情緒狀態、目標、知識和秘密，關係位置，道具歸屬，時間與倒計時，伏筆狀態和鉤子債務。

新批次開始前必須讀取全劇策略、全部分集卡、上一批末集完整正文和 `CONTINUITY_LEDGER.json`。只讀上一批摘要會遺漏台詞承諾、動作位置和情緒餘波。逐項驗證：

1. 上一批出口人物狀態等於本批入口狀態。
2. 上一批集尾動作由本批第一動作直接支付，或明確建立合法時間跳轉。
3. 已公開與未公開信息沒有復位或越權洩露。
4. 傷勢、服裝、道具、地點和流程耗時連續。
5. 關係變化累積，不因換批恢復到早期位置。
6. 關鍵台詞 `PRIMARY_USE`、伏筆和鉤子賬本跨批唯一。

不一致時分別標記 `CROSS_BATCH_STATE_DRIFT` 或 `BATCH_CONTEXT_GAP`。每批完成後連讀「上一批末集 + 本批全部集 + 下一批分集卡首集」；全部批次完成後執行全劇去元數據通讀。

## 2.11 鎖稿質量合同

`SCRIPT_SET_MANIFEST.json` 中每個鎖定集必須記錄完整 `story_unit`、`pressure_contract`、`timeline`、空的 `fragmentation_flags`，以及以下 `quality_gates` 全部為 `PASS`：

```yaml
quality_gates:
  source_event_fidelity: PASS
  deletion_safety: PASS
  episode_plan_fidelity: PASS
  source_bounded_closure: PASS
  source_pressure_fidelity: PASS
  timeline_continuity: PASS
  narrative_continuity: PASS
  episode_completeness: PASS
  scene_causality: PASS
  active_opposition: PASS
  visible_cost_or_consequence: PASS
  relationship_turn_evidence: PASS
  key_dialogue_fidelity: PASS
  dialogue_naturalness: PASS
  ip_dramatization: PASS
  visual_story_progression: PASS
  audience_comprehension: PASS
  local_payoff_and_hook: PASS
  first_10_seconds_hook: PASS
  standalone_episode_comprehension: PASS
  adjacent_episode_bridge: PASS
  flashback_time_anchor: PASS
  metadata_stripped_read: PASS
  duration_table_read: PASS
  cross_batch_continuity: PASS
fragmentation_flags: []
failure_flags: []
```

若本集不包含關係轉變，`relationship_turn_evidence: PASS` 表示正文沒有偽造關係變化；不能使用 `N/A` 繞過檢查。若本集沒有閃回，`flashback_time_anchor: PASS` 表示沒有偽造或遺漏時間跳轉，同樣不使用 `N/A` 繞過檢查。

## 2.12 合成對照

弱版本：角色寫出三條方案，對方聽完立即同意，兩人宣佈共同承擔風險；為增強結尾，又從道具裡彈出一份原文不存在的身份證明。它同時觸發 `CHECKLIST_SOLUTION`、`SUDDEN_CONSENSUS`、`UNPAID_COST` 和 `UNSOURCED_CORE_PAYOFF`。

有效版本：角色先封存證據，對方因必須提交材料而準備發送舊方案；角色提出替代方案但被主管拒絕；對方主動刪除能保住自己的噱頭標題並簽名承擔延期責任，才換來一次限時驗證。關係變化由行動觸發，代價已經進入現實流程。

# 第三部分 · 單集獨立開場與相鄰集過橋契約

本規則解決兩個必須同時成立的觀看入口：

1. 連續觀看：上一集最後的狀態、鉤子或動作自然觸發下一集第一動作。
2. 單集觀看：觀眾沒有看上一集，也能在本集前 10 秒內知道誰正處在什麼困境、本集要解決什麼、為什麼必須現在行動。

不能用「上集回顧」替代戲劇開場，也不能為了單集可懂重複解釋整段前情。最小補課信息必須嵌在正在發生的衝突、選擇、證據或危險中。

## 3.1 前 10 秒雙入口

首場前 10 秒至少同時提供：

- 一個可見爆點：危險、行動、證據、反常、衝突、身份落差、不可逆選擇或關係突變。
- 最小人物處境：行動主體是誰，他正在承受什麼直接壓力。
- 本集行動問題：他現在要完成、阻止、確認或奪回什麼。
- `WHY_NOW`：為什麼不能晚一點再做。

爆點不是無來源閃回、喊口號、突然打人或單獨展示奇觀。它必須來自本集主事件、上集鉤子、已授權重排或來源允許的連接動作，並在本集得到推進或結算。

不要在開頭塞入世界觀、人物小傳和全劇前情。若刪除某條背景後，觀眾仍能理解本集行動，就不應放入前 10 秒。

## 3.2 STANDALONE_EPISODE_TEST

把本集乾淨劇本單獨交給一名不知道上集內容的觀眾，只閱讀首場前 10 秒和本集正文。觀眾必須能回答：

1. 誰是當前行動主體？
2. 他眼前遇到什麼具體麻煩？
3. 本集當前要解決或確認什麼？
4. 為什麼必須現在處理？
5. 本集結束時實際得到什麼？
6. 為什麼願意繼續看下一集？

前四題任一無法回答，標記 `STANDALONE_CONTEXT_GAP`；只能依賴集名、簡介、審稿字段或上一集才能回答，標記 `EPISODE_OPENING_DEPENDENCY`。

單集可懂不等於單集封閉。觀眾可以不知道全劇謎底，但不能不知道當前行動因果。

## 3.3 LAST_FRAME_FIRST_ACTION_TEST

逐對連讀相鄰兩集，先只看：上一集局部兌現；上一集最後不可逆變化或主鉤子；上游鎖定的 `next_episode_first_action`；下一集第一場的首個有效動作。

必須形成：

`上一集最後變化 → 下一集第一動作 → 下一集新目標或新策略`

下一集不能重置人物位置、身體、情緒、知識、關係、道具或危險，也不能先解釋幾十秒再支付上集鉤子。若第一動作不是由上一集產生，標記 `ADJACENT_EPISODE_BRIDGE_BREAK`。

允許用 1–3 秒動作、聲音或關鍵短句重疊幫助單集觀眾進入，但不得完整復播上一集結尾；重複內容必須同時承擔新一集的目標建立或策略變化。

## 3.4 時間跳轉與閃回

相鄰集或首場發生時間跳轉時，觀眾必須在正文看見或聽見時間證據，不能只在清單裡寫「閃回」：

- `CONTINUOUS`：連續動作、同一聲音、未完成動作或明確「連續」狀態。
- `FLASHBACK`：可見「數小時前/三日前」等進入錨點；回到主時間線時再給返回錨點。
- `ELAPSED`：用屏顯、環境、服裝、傷勢、流程結果或台詞建立經過時間。
- `PARALLEL`：用「與此同時」、共同聲源、同一事件反饋或同步時點建立為何此刻切入。
- `SERIES_OPENING`：第一集開篇，不消費上集狀態。

把「三日前」寫成「當日稍早」、把「數日後」寫成「連續」、閃回結束後直接切回現在而無提示，標記 `FLASHBACK_TIME_ANCHOR_MISSING` 或 `IMPOSSIBLE_TIME_BRIDGE`。

## 3.5 結構化合同

每集在 `SCRIPT_SET_MANIFEST.json` 寫入：

```yaml
opening_contract:
  hook_type: DANGER
  visual_or_conflict_hook: "花轎突然側傾，主角撞向轎壁"
  protagonist_and_situation: "蘇棠正在被迫送往陌生婚局"
  immediate_conflict: "轎伕故意加重顛簸"
  active_goal_or_question: "她必須先穩住身體並逼停顛轎"
  why_now: "繼續顛簸會令體弱身體失去行動能力"
  first_10_seconds_evidence_text: "轎身猛地向一側傾斜"
  standalone_test_summary: "盲看可識別主角、顛轎危險、即時目標與時限"
  status: PASS

transition_contract:
  previous_episode_id: EP003
  previous_local_payoff: "上集鎖定的局部兌現原文"
  previous_hook_id: HK-EP003
  planned_first_action: "上集鎖定的 next_episode_first_action 原文"
  first_action_evidence_text: "轎身再次猛地側傾"
  causal_bridge: "上一集第一次側傾未解決，下一集繼續升級並迫使蘇棠反制"
  opening_time_relation: CONTINUOUS
  source_time_basis: "SRC-001:L95，花轎駛出信王府所在長街後"
  time_consistency_summary: "與上集出口均為替嫁當日送嫁途中，沒有提前或重置"
  opening_time_anchor_evidence_text: "連續"
  return_to_main_timeline_evidence_text: NOT_APPLICABLE
  no_reset_proof: "人物仍在轎內，針囊在袖中，危險和身體狀態連續"
  status: PASS
```

第一集使用：

```yaml
previous_episode_id: SERIES_OPENING
previous_local_payoff: NOT_APPLICABLE
previous_hook_id: NOT_APPLICABLE
planned_first_action: NOT_APPLICABLE
opening_time_relation: SERIES_OPENING
source_time_basis: "來源開篇時間事實"
time_consistency_summary: "系列開篇，沒有上集時間狀態"
opening_time_anchor_evidence_text: NOT_APPLICABLE
return_to_main_timeline_evidence_text: NOT_APPLICABLE
```

非第一集的 `previous_local_payoff`、`previous_hook_id` 和 `planned_first_action` 必須逐字綁定上一集鎖定分集卡，禁止劇本層同義改寫。`source_time_basis` 必須引用小說或事件賬本的時間事實，`time_consistency_summary` 必須說明來源、分集與正文是否同日、連續、經過時間、閃回或平行；不能把「三日前」改成「當日稍早」。`first_10_seconds_evidence_text`、`first_action_evidence_text` 和適用的時間錨點必須能在乾淨劇本正文中找到。

## 3.6 鎖稿門

以下質量門全部為 `PASS` 才能鎖稿：`first_10_seconds_hook`、`standalone_episode_comprehension`、`adjacent_episode_bridge`、`flashback_time_anchor`。

# 第四部分 · 全上下文深讀與權威順序

> 本契約供授權後的精修/重寫執行（流程見 [six-stage-pipeline.md](six-stage-pipeline.md) 第八節）。

## 4.1 固定閱讀順序

1. 讀取 `SOURCE_MANIFEST` 和用戶提供的全部原小說範圍。
2. 讀取鎖定 IP 版本、角色小傳、行為錨點、聲音規則和關係簽名。
3. 讀取故事聖經、世界觀價值觀、事件賬本、人物弧、信息邊界和改編藍圖。
4. 讀取分集規劃、本批前後集卡、鉤子兌現賬本和批次入口出口。
5. 讀取當前乾淨劇本、來源改編地圖、關鍵台詞賬本和連續性賬本。
6. 最後讀取五席意見、圓桌報告和返修清單。

不得先看評分再帶著結論找證據。

`REFINEMENT_MANIFEST.verified_inputs.read_order` 必須按上述順序留下機器可檢驗記錄；輸入核驗還應核對來源文件哈希和五個版本綁定。任何輸入缺失或仍為測試/臨時未鎖定狀態，都必須先返回對應上游，不得進入正式精修。

## 4.2 理解簡報最低內容

`UPSTREAM_COMPREHENSION_BRIEF.md` 必須回答：

- 當前來源是完整小說還是節選，哪些結論仍是 `OPEN_ITEM`。
- 本批覆蓋哪些來源事件，哪些後續因果依賴本批。
- 主角、對手和關鍵關係各自想要什麼，為什麼現在行動。
- 鎖定 IP 的穩定內核、靈魂選擇、缺陷、行為錨點和聲音禁區。
- 本批在全劇弧線中的入口、變化、出口和下一批第一動作。
- 每集的命題、局部兌現、主鉤子與支付集。
- 人物、道具、傷勢、知識、關係和時間的進入與退出狀態。
- 不得刪除、改序或改義的來源事實與關鍵台詞。

只複述圓桌問題、不復述原作和上游，判定 `CONTEXT_NOT_UNDERSTOOD`。

## 4.3 評審意見的權威邊界

評審意見只有三種合法用途：

- 指出正文證據支持的觀看或結構問題。
- 提出不改變上游事實的修改目標。
- 暴露需要返回上游的真實衝突。

出現以下情況拒絕意見：

- 要求新增來源沒有的核心反轉、身份、證據或救援。
- 要求人物違反鎖定 IP 換取即時爽感。
- 要求取消分集已鎖定的局部兌現或鉤子。
- 把平台猜測、個人偏好或分數目標寫成故事事實。

拒絕時寫明衝突的上游版本、事實和替代處理，不得靜默忽略。

## 4.4 長篇來源

長篇可以分段讀取，但必須先建立全源索引，再完整讀取：本批直接來源段；本批前因；本批後果和未來支付段；角色身份、關係、能力和秘密的全局證據。

不得只讀當前三集對應段而誤改後續伏筆。

## ★ 全稿純口播連讀測試（初稿完稿及任何刪改移動後的強制終檢）

初稿寫完或任何相鄰場次挪動/刪改後，**臨時剝離章節標題、場景說明與 `△` 動作提示，僅將全部對白與旁白從頭到尾連續朗讀一遍**，專抓四類結構隱疾：
1. **主語懸空與指代不清**（“他/那個/下一批”在當前語境存在兩個以上指向）；
2. **信息重複與二次上課**（前面已講明的結果或數字，後文換人再複述一遍）；
3. **時間突跳與因果斷橋**（刪掉章節標題後上下兩場接不上）；
4. **高潮後結尾拖沓**（核心反轉已成立，結尾仍在複述前面細節而非收刀升維）。
