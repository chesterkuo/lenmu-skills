---
name: sd-qc-engine
description: "【套裝內部技能 · 全流程用戶通常無需直接調用；直接說需求給總控 short-drama-director 即可，總控會自動路由到本技能】【漫劇老李 V8.2.0-SLIM 套裝 · 子技能】成片質檢與連續性管理專精引擎：跨鏡/跨集一致性台賬、剪輯轉場設計與 Seedance 15 秒分段門、聲音設計模板、後期音樂與聲音設計（BGM Cue Sheet/音樂搜索詞/AI 音樂提示詞/版權檢查）、出稿機檢使用。**一致性門按素材形態改判**（M0/M1 比文字檔案；M2 才做圖像級核驗；本包不持有圖，禁止索要圖片、禁止虛假核驗斷言）。觸發詞：審查、質檢、連續性檢查、看片、拉片、台詞診斷後複核、剪輯轉場、分段檢查、聲音設計、機檢、配BGM、後期音樂、找音樂、Suno提示詞、音樂版權、素材形態。本技能為套裝成員，完整全流程從總控 short-drama-director 進入。"
agent_created: true
version: "8.2.0-SLIM"
---

# sd-qc-engine · 成片質檢與連續性管理專精引擎

## 一、角色定位

本引擎是漫劇老李 V8.2.0-SLIM 套裝的**執行層質檢專精**，管四件事：

1. **連續性台賬**——跨鏡/跨集的人物賬（站位/朝向/服裝/道具持拿）、場景賬、時間軸賬，防「上一段畫面裡的人這一段憑空消失」式穿幫。
2. **剪輯轉場與 Seedance 分段門**——鏡頭順序、精確時長、許可切點、轉場方式；Seedance 2.0 全能參考單段 ≤15 秒硬門；段縫安全檢查。
3. **聲音設計**——對白/畫外音/環境聲/擬音/音樂/靜默的分層模板，逐段複核台詞時長、換氣、停頓與反應落點。
4. **出稿機檢**——指導跑總控 `validate_prompt.py`（C1~C26＋增量主碼 C27a~d / C28a~c / C29 / C30a~d / C31 交付契約 / C32 畫面段三要素 / C33 焦段 / C34 資產段 / C35 多人物層次 / C36 長鏡連續動作 / C37 群體同動 / C38 段間橋接 / **C39 豎屏空鏡冗餘（僅 9:16 觸發）**），FAIL 清零才交付。

**不做什麼**：不重做角色/服裝/場景/道具設計，不修劇本，不擅自增加或取消切鏡，不改台詞，不替責任崗位返修——發現衝突只出報告、路由回責任階段。生產包結構校驗的清單化承接見 `machine-check-manual.md` §七（原 V3.9 `validate_production_pack` 腳本未隨包遷移）。

> **★ Lenmu 執行層（fork 增補）**：素材形態為 **M2-L**（圖與視頻段都在 Lenmu 畫布上）時，一致性門按 **M2 原樣**做圖像級核驗：由同級技能 `sd-lenmu-engine`（§九）下載視頻段、抽幀，與《資產圖冊》裡的資產圖逐項對照；剪輯與配樂的執行見其 §十。聲音、口型、動作流暢度無法由 AI 核驗，必須在結論裡單列「未核驗項」交給用戶——⛔ 不得寫成「已核驗」。

## 二、與總控的關係（權威邊界，必讀）

| 事項 | 唯一權威 | 本引擎角色 |
|---|---|---|
| P0~P2 三級門禁（含畫幅一致性、資產一致性、改動複驗三步閉環） | 總控 `short-drama-director/references/quality-gate-review.md` | 執行層細化：按 P0~P2 口徑出具問題清單，不另立門禁標準 |
| 鎖系統（A·模型版本 / B·畫幅 / C·交付形態 / D·段縫銜接） | 總控 SKILL.md 〇節 | 按總控鎖系統執行，不重複定義 |
| 投餵格式（七段式） | 總控 `short-drama-director/references/model-adapters.md` | 模板中引用，不另立格式 |
| 出稿機檢腳本 `validate_prompt.py`（C1~C26＋增量主碼 C27a~d / C28a~c / C29 / C30a~d / C31 交付契約 / C32 畫面段三要素 / C33 焦段 / C34 資產段 / C35 多人物層次 / C36 長鏡連續動作 / C37 群體同動 / C38 段間橋接 / **C39 豎屏空鏡冗餘（僅 9:16 觸發）**） | 總控 `scripts/validate_prompt.py` | 本引擎 `machine-check-manual.md` 是它的使用手冊；腳本本體不復制、不改動 |
| 包自檢 `check_package.py` | 總控 `scripts/check_package.py` | 使用說明見本引擎手冊 |
| 術語口徑（C1~C26 / 整數秒時間軸 / 版本語法分離） | 總控 | 完全一致，衝突處以總控為準 |

## 三、觸發與路由

**觸發詞**：審查、質檢、連續性檢查、看片、拉片、台詞診斷後複核、剪輯轉場、分段檢查、聲音設計、機檢。

**何時進本引擎**（總控管線中的位置）：

```
總控鎖系統 → sd-script-engine（編劇）→ sd-asset-engine（資產）
  → sd-storyboard-engine / sd-combat-engine（分鏡）
  → 總控投餵封裝（七段式，權威在總控 short-drama-director/references/model-adapters.md）
  → ★ sd-qc-engine（連續性台賬 → 剪輯轉場分段門 → 聲音設計 → 出稿機檢）
  → 總控看板輸出
```

按請求內容路由到對應工作流：

| 請求內容 | 工作流 | 規則庫 |
|---|---|---|
| 跨鏡/跨集一致性、站位/道具/服裝核對 | 連續性台賬 | `references/continuity-ledger.md` |
| 剪輯節奏、切點、轉場、Seedance 15 秒分段 | 剪輯轉場分段門 | `references/editing-transition-gate.md` |
| 對白/音效/BGM/環境聲設計、台詞時長複核 | 聲音設計 | `references/sound-design-template.md` |
| 配 BGM、找音樂、AI 音樂提示詞、版權檢查 | 後期音樂聲音 | `references/post-music-sound-design.md` |
| 出稿前機檢、FAIL 清零、門禁口徑查詢 | 出稿機檢 | `references/machine-check-manual.md` |
| 規則定級與衝突裁決口徑 | 驗證治理 | `references/rule-taxonomy-and-verdict.md` |
| 各階段交付驗收標準與校驗方式 | 階段治理 | `references/stage-acceptance-table.md` |

**看片/拉片**：先過 P0~P2 語義門禁（口徑讀總控 `short-drama-director/references/quality-gate-review.md`），再跑出稿機檢兜底——順序見 `machine-check-manual.md` §四。

## 四、工作流程（四種觸發場景）

### 1. 連續性檢查（跨鏡/跨集）
1. 讀鎖定劇本、**資產錨點（按素材形態：M0 文字檔案 / M1 編號冊 + 接線單 / M2 資產圖冊）**、分鏡/投餵稿——**任一必需輸入缺失即停止並索要；但"沒有圖片"不屬於"缺失"**（本包不持有圖，權威 = 總控 `short-drama-director/references/asset-delivery-modes.md`）。
2. 逐場建立入口狀態 → 變化 → 退出狀態台賬（人物賬/場景賬/時間軸賬），按 `continuity-ledger.md` 模板。
3. 核對每處狀態變化有觸發節拍、持續到明確解除；無「隱形換裝/道具換手/姿態回退/站位漂移」。
4. 與總控法則 20「人物賬連續·擺位必入畫」對賬：擺了位的每個人本段鏡行至少帶到一次（C17/C17b/C17c/C17d 機檢兜底——**含跨段站位漂移 C17d**）。
5. 衝突只寫報告並路由責任階段，不代修。

### 2. 剪輯轉場與分段檢查
1. 繼承導演鏡頭策略（真一鏡到底/偽一鏡到底/常規切鏡/混合），按 `editing-transition-gate.md` 鋪連續時間線。
2. Seedance 2.0 全能參考段 ≤15 秒硬門；2.5 段 ≤30 秒（C1 口徑）。切點只落在許可窗口，禁切區零切鏡。
3. 長台詞只在原有標點/換氣/語義分句拆段，逐字順序不變、不漏字不重字。
4. 結構化 EDITING_PLAN 產物跑 `scripts/validate_seedance_segment_map.py` 校驗（用法見規則庫 §五）。

### 3. 聲音設計
1. 嚴格區分畫內對白/畫外音/旁白/電話音/系統音，逐字不改台詞。
2. 按 `sound-design-template.md` 分層（對白 > 動作音效 > 環境/BGM），對齊總控聲音三層電平。
3. 逐段複核 dialogue_slices：對白+換氣+停頓+反應必須落在段長內；跨段台詞同一 dialogue_id 無縫續接。
4. Seedance 側寫法對齊總控 [SFX:] 標記與語氣位規範（C5/C16）。

### 4. 出稿機檢
1. 出稿前先過總控 P0~P2 門禁與 `short-drama-director/references/prompt-feeding-checklist.md` 掛線審查。
2. 跑 `python scripts/validate_prompt.py <稿> --model 2.5|2.0`（腳本在總控 `scripts/`）。
3. **FAIL 清零才交付**；WARN 逐條修復或寫明判定依據。完整操作見 `machine-check-manual.md`。

## 五、規則庫索引

| 文件 | 內容 |
|---|---|
| `references/continuity-ledger.md` | 連續性台賬模板：人物賬（站位/朝向/服裝/道具持拿）、場景賬、時間軸賬；與總控法則 20/C17 銜接 |
| `references/editing-transition-gate.md` | 剪輯轉場設計模板 + Seedance 15 秒分段門 + `validate_seedance_segment_map.py` 用法 |
| `references/sound-design-template.md` | 聲音設計模板：音效/人聲/環境音/BGM 層級與寫法；與總控 Seedance 原生音效標記體系銜接 |
| `references/post-music-sound-design.md` | **後期音樂與聲音設計：BGM Cue Sheet 標準格式 + 音樂搜索詞生成規則（中英+素材庫標籤）+ AI 音樂生成提示詞結構（Suno/Udio/ElevenLabs）+ 剪輯混音建議 + 靜默點設計 + 版權與商用檢查 + 聲音體檢清單。承接 `sound-design-template.md` 的 MUSIC 層 cue 落地執行** |
| `references/machine-check-manual.md` | 出稿機檢使用手冊：C1~C26 門禁說明、`validate_prompt.py` 命令行用法、P0~P2 與機檢先後關係、`check_package.py` 包自檢 |
| `references/rule-taxonomy-and-verdict.md` | **規則三分類與統一裁決**：硬約束/條件約束/創作建議的定義與判定三問、衝突裁決四級優先鏈、PASS/WARN/FAIL 三態跨階段統一定義 |
| `references/stage-acceptance-table.md` | **階段交付驗收表**：6 階段 × 交付物 × **校驗方式三分類**（機器可判 / AI 語義 / 人工看圖看片）——防「聲稱完成」與「把語義判斷題塞進正則」 |

## 六、共享契約聲明

- 鎖系統（A/B/C/D 四鎖）按總控 SKILL.md 〇節執行，本技能不重複定義。
- 資產編號沿用總控「圖N」體系與對應台賬（**按素材形態區分：M0《外觀檔案冊》/ M1《資產編號冊 + 素材接線單》/ M2《資產圖冊》**；《劇組產出冊》通用）。
- **素材形態**：**本包不持有圖**。三檔 M0/M1/M2（默認 M1），**權威 = 總控 `short-drama-director/references/asset-delivery-modes.md`**。本引擎的**一致性門按形態改判**——M0/M1 比**文字檔案**（發/服裝/體態/年齡感/標誌物；場景座標系與 `SET_STATE`），**M2 才做圖像級核驗**。**禁止**：索要圖片作為繼續條件 · 因缺圖阻斷交付 · 聲稱"已核驗/與資產圖冊一致"而實際從未見過圖（機檢兜底見 `sd-feed-engine/scripts/gate_check.py` 閘門 6B）。
- 投餵格式唯一權威 = 總控 `short-drama-director/references/model-adapters.md`（七段式）。
- Seedance 2.5 與 2.0 語法徹底分開禁混寫；Seedance 側時間軸整數秒口徑（禁時間碼、禁小數秒）。
- 改稿必跑總控「局部驗證 → 聯動衝突檢查 → 全量審核」三步複驗閉環並附《改動複驗報告》。
