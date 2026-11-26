# 剪輯轉場設計與 Seedance 15 秒分段門

> 精編自《靈境AI漫劇製作流 V3.9.0》manju-editing-transition-designer

## 〇、定位與邊界

- **目的**：繼承導演鏡頭策略（真一鏡到底 / 偽一鏡到底 / 常規切鏡 / 混合），為每鏡鎖定時長、進入/退出幀與承接方式；為 Seedance 全能參考把場景拆成不超過 15 秒且自然接力的完整段，優先讓導演切鏡落在段間。
- **邊界**：不為節奏擅刪因果、台詞、反應或小閉環；不增加或取消導演決定的切鏡；不拆散真一鏡到底；不用特效轉場遮蓋生成錯誤。
- **輸入**：鎖定劇本、導演切點/禁切區、台詞節奏與動作時間線、連續性台賬（`continuity-ledger.md`）。

## 一、導演鏡頭策略（每場唯一，四選一，不得並存）

| 模式 | 判據（互斥，違者返工） |
|---|---|
| `TRUE_ONE_TAKE` 真一鏡到底 | 禁切區非空；**不得**含任何切鏡指令；必須關閉剪輯切點與隱藏縫；跨段必須保持同一鏡頭身份、攝影機軌跡、動作、空間、焦點與光線連續；每段恰好 1 個 shot_id 且必填 `continuous_take_unit_id` |
| `SIMULATED_ONE_TAKE` 偽一鏡到底 | 禁用可見剪輯切點；**僅**在導演批准的隱藏縫銜接；必須給出 `seam_conditions`；`HIDDEN_SEAM` 必須帶 `hidden_seam_id` |
| `CUT_COVERAGE` 常規切鏡 | 必須允許剪輯切點且至少含 1 個已批准切點；所有可見切鏡引用 `director_cut_directive_id` 並落在許可窗口 |
| `HYBRID` 混合 | 必須允許已批准剪輯切點、至少含 1 個已批准切點，且 `no_cut_zones` 非空 |

每場必須留檔：**選擇依據 + 被否決方案 + 運鏡指令 + 禁切區 + 強制切點/許可窗口 + 生成分段政策**。攝影、分鏡、剪輯**不得新增或取消**導演決定；`VISIBLE_CUT` 只在導演許可下出現。段落邊界與故事板面板邊界**均不得自動解釋為剪輯點**。

## 二、轉場設計

1. 先按完整場景建立情緒與信息節奏，再落切點；精確切幀只能落在導演的強制切點或許可窗口。
2. 轉場方式優先級：**硬切 > 動作匹配 > 視線匹配 > 道具匹配 > 聲音橋**（`HARD_CUT / ACTION_MATCH / GAZE_MATCH / PROP_MATCH / SOUND_BRIDGE`）。
   > 🔗 **手法庫指針**：段縫層面的**具體技巧手法**（相似動作 / 形狀匹配 / 前景遮擋 / 甩鏡 / 閃白 / 畫中畫 + 大師技巧輯錄）權威在總控 `short-drama-director/references/creative-transition-library.md`（**D 鎖 ④ 技巧型轉場** · 2026-10-13 新立）。本節管**剪輯門的判據與優先級**（何時允許切、切在哪個窗口），手法庫管**具體怎麼接**；兩者分工不替代——**需要時手邊有的工具箱，不是每段必用**（單集 ≤3 處，為轉而轉 = 違規）。
3. 疊化、黑白場、甩鏡、壓縮蒙太奇只在劇本有時間/空間/意識或衝擊斷裂依據時使用，必須寫敘事依據。
4. 不切斷台詞、動作受力、接收者反應或信息落點。
5. 所有可見切鏡須有導演指令依據；禁切區內零切鏡（對齊總控 P0 嚴重跳軸攔截與 qc 門前置）。

## 三、Seedance 15 秒分段門（硬約束）

> ⚠️ **本門分版本執行，禁混寫**（對齊總控「2.5/2.0 語法徹底分開」鐵律）：
> - **Seedance 2.0 + OMNI_REFERENCE**：**15 秒硬上限**，走本門 §三~§五 全流程（含六級段尾優先級表與隨包腳本）。
> - **Seedance 2.5**：段上限 **30 秒**，其分段與出稿走**總控 C1 口徑**，**不復用本門 §三 六級段尾優先級表**。
> - 🚫 **工具適用範圍（重要）**：§五 的 `validate_seedance_segment_map.py` **硬編碼 15 秒**，**只適用於 2.0 分段圖**——**禁止**用它校驗 2.5 的 30 秒分段圖（必然批量 ERROR）。2.5 分段圖出稿門禁走總控 `validate_prompt.py <稿> --model 2.5`。

- 每段 `duration <= 15` 秒（**Seedance 2.0 全能參考硬上限**），不以四捨五入、15.01 秒或"生成後再裁掉"規避。
- 先服從導演鏡頭策略，再優化生成段；模型限制不能創造新切鏡。
- 保留鎖定台詞原文、行動因果、接收者反應和關鍵聲畫落點。
- 每段有獨立故事任務、完整入口、明確出口和下一段第一動作。

### 分段步驟

1. 把場景展開為連續時間線：劇情節拍、台詞及停頓、動作階段、反應、攝影機運動、聲音橋、導演切點和禁切區。
2. 從當前段起點向後掃描 15 秒內全部安全候選。
3. 按以下優先級選擇段尾，**不機械取滿 15 秒，不機械等長切分**：
   1. 導演批准的可見切鏡；
   2. 場景結束或完整鏡頭結束；
   3. 台詞句/語義分句結束，且聽者反應已經落地；
   4. 動作結果、道具落點、視線落點或聲音橋；
   5. 攝影機停穩、人物穩定姿態或導演批准的隱藏縫；
   6. 僅因模型限制形成的連續續段錨點。
4. 15 秒內已有導演批准切鏡時，默認放在段間；只有台詞、動作、反應或禁切規則阻止時才能不用，並記錄原因。
5. 為相鄰段建立入口/出口幀、狀態繼承與參考接力。

### 禁止段界（段縫檢查點）

段縫落在以下位置一律返工：

- 單詞、短語或不可分語義中間；
- 台詞已說出但接收者反應尚未出現；
- 動作起勢與受力結果之間；
- 道具離手但尚未落點；
- 攝影機快速加速、甩動或焦點尚未落穩；
- 導演禁切區內的可見切鏡；
- 只為湊到 15 秒而增加的空鏡、重複動作或停頓。

### 長台詞跨段

優先保留整句。單條台詞及必要表演超過可用時長時，只能在劇本已有標點、角色自然換氣、明確語義分句或導演批准的反應切點拆分，且必須：

- 保持逐字順序，不重複、不漏字；
- 標記 `CLAUSE_HEAD / CLAUSE_MIDDLE / CLAUSE_TAIL`；
- 寫明 `split_anchor`、前段結束字詞和後段起始字詞；
- 保持同一 `dialogue_id`、說話者與情緒連續；
- 前後段之間不得插入無來源台詞。

找不到安全語義分點時標 `BLOCKED`，返回編劇/導演處理，不擅改台詞。

### 參考接力（尾幀用途）

每段為參考素材聲明"只繼承什麼、不得繼承什麼"。相鄰段至少傳遞：角色身份/造型/表情動作階段、左右位置/朝向/視線、道具持有者與手位、場景損毀/天氣/時間/主光方向/空氣狀態、鏡頭身份/焦點/運動階段。

- 連續鏡頭：前段**已驗收實際尾幀**作為下一段 `EXACT_CONTINUATION`；
- 可見切鏡：尾幀只作 `STATE_REFERENCE_ONLY`，並以新鏡頭首幀規格控制構圖。
- 首段：`NOT_APPLICABLE`。

### 段尾類型

| 類型 | 含義 |
|---|---|
| `VISIBLE_CUT` | 正式剪輯切點：段尾停在切前最後穩定幀，下一段從導演批准的新鏡頭開始（必須帶導演切點 ID） |
| `CONTINUOUS_TAKE` | 同一鏡頭自然續接 |
| `HIDDEN_SEAM` | 只用於導演批准的偽一鏡到底接縫（必須帶隱藏縫 ID） |
| `GENERATION_ONLY_BOUNDARY` | 只因 15 秒限制續段，**不是成片切鏡** |
| `SCENE_END` | 場景結束 |

段縫銜接的投餵側落地（**段縫畫面鎖** / 換機位 / 帶任務空鏡三選一）按總控 D 鎖與 `short-drama-director/references/segment-splicing.md` 執行；**段末不寫接續尾行**（【接續狀態】2026-10-09 廢止，C11 反轉為殘留攔截；C12 規則詞混入照常兜底）。

## 四、EDITING_PLAN 模板

結構化分段產物使用以下 JSON 模板（保留原字段結構，裁定：不再強制 V3 公共信封根字段，純分段校驗時保留 `payload` 結構即可；若使用隨包腳本校驗，腳本要求 `schema_version:"3.0" / artifact_type:"EDITING_PLAN" / stage_id:"16"` 根字段，按腳本要求補齊）：

```json
{
  "scene_id": "",
  "target_profile": {
    "name": "SEEDANCE_2",
    "reference_mode": "OMNI_REFERENCE",
    "max_segment_seconds": 15
  },
  "director_strategy_ref": {
    "strategy_id": "",
    "directive_version": 1,
    "mode": "CUT_COVERAGE"
  },
  "editorial_continuity_mode": "CUT_COVERAGE",
  "rhythm_curve": [],
  "shot_order": [{
    "shot_id": "",
    "duration": 0,
    "in_frame": {},
    "out_frame": {},
    "cut_reason": "",
    "transition": "HARD_CUT",
    "cut_authority": {
      "director_cut_directive_id": null,
      "allowed_window_id": null,
      "mandatory_cut_point_id": null,
      "exact_frame_or_time": "",
      "inside_no_cut_zone": false
    },
    "sound_bridge": ""
  }],
  "segments": [{
    "segment_id": "SEG-0001",
    "duration": 0,
    "shot_ids": [],
    "story_units": [],
    "dialogue_slices": [{
      "dialogue_id": "",
      "speaker_id": "",
      "voice_id": "",
      "exact_text": "",
      "start": 0,
      "end": 0,
      "integrity": "WHOLE",
      "split_anchor": null,
      "continues_to_segment_id": null
    }],
    "visual_action_units": [],
    "boundary_from_previous": "SCENE_ENTRY",
    "boundary_to_next": {
      "type": "VISIBLE_CUT",
      "director_cut_directive_id": "CUT-001",
      "hidden_seam_id": null,
      "reason": "",
      "safety_checks": {
        "dialogue_safe": true,
        "action_safe": true,
        "reaction_safe": true,
        "camera_safe": true
      }
    },
    "boundary_selection": {
      "selected_time": 0,
      "candidate_type": "DIRECTOR_VISIBLE_CUT",
      "why_selected": "",
      "approved_cut_candidates_before_deadline": [],
      "cut_alignment": "ALIGNED_AT_SEGMENT_END",
      "cut_alignment_override_reason": null
    },
    "entry_state": {},
    "exit_state": {},
    "continuity_handoff": {
      "anchor_description": "",
      "must_match": [],
      "previous_approved_tail_ref_required": false,
      "tail_usage": "NOT_APPLICABLE"
    },
    "next_first_action": ""
  }]
}
```

口徑說明：

- `boundary_from_previous` 取值：`SCENE_ENTRY / VISIBLE_CUT / CONTINUOUS_TAKE / HIDDEN_SEAM / GENERATION_ONLY_BOUNDARY`；`boundary_to_next.type` 另可取 `SCENE_END`。只有 `VISIBLE_CUT` 是正式剪輯切點。
- `dialogue_slices.integrity` 取值：`WHOLE / CLAUSE_HEAD / CLAUSE_MIDDLE / CLAUSE_TAIL`；非完整台詞必須寫 `split_anchor`，並以同一 `dialogue_id` 在後段無縫續接。
- 四項 `safety_checks`（dialogue/action/reaction/camera）必須全部為 true。
- `previous_approved_tail_ref_required` 除首段外必須為 true；`tail_usage` 按參考接力規則取值。

## 五、與總控機檢的銜接

| 分段門規則 | 對應總控機檢項 |
|---|---|
| 段長 ≤ 模型上限（2.0=15s / 2.5=30s） | C1 |
| 切鏡上限（鏡頭數 ≤ ceil(段長/3s)）、單鏡 <3s 告警 | C2 |
| 時間軸無斷檔/重疊、無倒掛 | C3 |
| 段末無接續尾行（殘留即 FAIL） | C11（2026-10-09 反轉） |
| 鏡長按劇情倒推、禁機械等分 | C13（同值鏡長佔比 ≥70% 告警） |
| 禁拉伸湊時（無台詞鏡 >5s、純氛圍段 >10s 告警） | C15 |
| 台詞語氣位與段內落點 | C16 |

## 六、validate_seedance_segment_map.py 用法（本技能 scripts/ 附帶）

隨包腳本為通用純 Python 校驗器（零第三方依賴，僅校驗 EDITING_PLAN JSON 自身結構），已複製到本技能 `scripts/validate_seedance_segment_map.py`。

```bash
python scripts/validate_seedance_segment_map.py "<EDITING_PLAN.json>"
```

- **輸入**：按 §三模板填寫、且帶根字段 `schema_version:"3.0"`、`artifact_type:"EDITING_PLAN"`、`stage_id:"16"` 的 JSON 文件。
- **輸出**：全部通過打印 `PASS`；否則逐條打印 `ERROR: ...` 並以退出碼 1 結束。**分段鎖定前必須 PASS。**
- **校驗內容**：根字段齊全；每段 0 < duration ≤ 15；`max_segment_seconds ≤ 15`；`shot_ids/story_units` 非空；相鄰段入口類型 = 前段出口類型（首段必須 `SCENE_ENTRY`，末段必須 `SCENE_END`）；`VISIBLE_CUT` 必須帶導演切點 ID、非切鏡邊界禁止攜帶；`HIDDEN_SEAM` 必須帶隱藏縫 ID；四項 safety_checks 全 true；`selected_time = duration`；跳過已批准切鏡必須寫 `cut_alignment_override_reason`；除首段外尾幀接力必須登記且 `tail_usage` 與入口類型匹配；台詞切片落點在段內、非完整切片必須帶 `split_anchor`、`CLAUSE_HEAD/MIDDLE` 必須能在目標段找到同一 `dialogue_id/speaker_id/voice_id` 的續接切片。
- **適用範圍**：僅當採用結構化 EDITING_PLAN JSON 工作流時使用；七段式文本投餵稿的出稿門禁走總控 `validate_prompt.py`（見 `machine-check-manual.md`），兩者不互相替代。
