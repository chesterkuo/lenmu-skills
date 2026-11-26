# 閉源模型與 Canvas 工作流自動化對接引擎 (Cloud Models & Canvas Workflow Engine)

本引擎專門面向 Seedance 2.5 / 2.0 等閉源雲端視頻模型及 Canvas 協作畫布，提供提示詞解耦注入、資產圖映射與批量任務調度規範，實現“AI 自動完成參數裝配，導演僅在關鍵節點審核確認”。

---

## 一、 閉源雲端模型三層對接架構

```text
[分鏡動力學與解耦提示詞組]
       │
       ├──> 1. 資產圖/4 View 資產板綁定 (@asset_name -> 平台參考圖輸入)
       ├──> 2. 提示詞解耦投餵 (主體層 + 環境層 + 鏡頭動態層)
       └──> 3. 平台參數契約 (生成時長隨模型契約: Seedance 2.0 ≤15s, 運鏡強度, 提示詞相關性, 風格預設)
       │
       ▼
[Seedance 2.0 / Canvas 畫布 API]
```

---

## 二、 Canvas / 雲端 API 批量調度模版 (Python)

```python
import json
import requests

def inject_shot_payload(shot_data, api_endpoint="https://api.example.com/v1/video/generate", api_key="YOUR_API_KEY"):
    """
    將單組分鏡提示詞與資產參考圖組裝為閉源平台標準請求載荷
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": shot_data.get("model", "seedance-2.0"),
        "prompt": shot_data["positive_prompt"],
        "negative_prompt": shot_data.get("negative_prompt", "blurry, low quality, distorted anatomy, text artifacts"),
        "duration": shot_data.get("duration", 15),
        "aspect_ratio": shot_data.get("aspect_ratio") or shot_data.get("user_aspect", "9:16"),  # 畫幅以用戶指定為準，見 aspect-ratio-adaptation.md
        "ref_images": shot_data.get("ref_images", []),
        "camera_motion": shot_data.get("camera_motion", "dynamic_follow"),
        "motion_intensity": shot_data.get("motion_intensity", "high")
    }
    
    response = requests.post(api_endpoint, headers=headers, json=payload)
    return response.json()
```

---

## 三、 平台生成批次與資產前置預估規範

每組輸出提示詞與分鏡時，系統將自動彙總閉源平台任務資產清單：
- **視頻生成任務組數**：如標準 3 分鐘劇本輸出 14 組視頻單元（每組 12s~15s）；
- **前置參考圖需求**：角色資產 4 View 板（CHR-）+ 場景氛圍參考圖（SCN-）；
- **任務輪次預估**：按閉源平台標準生成批次統計，輔助團隊高效規劃生成批次與點數預算。
