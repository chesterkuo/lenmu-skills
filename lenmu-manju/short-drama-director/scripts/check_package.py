#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package Integrity Check —— 包級完整性 / 迴歸自檢（打包與出廠時跑）

現行版本以本文件 `VERSION` 常量為準——**不在 docstring 裡寫死版本號**
（2026-10-14 代碼體檢修復：原寫死上一版版本號，升版後與正文漂移；且 `.py` 的 docstring
不在 `scan_rule_docs()` 的 `.md` 掃描域內，`[A]`/`◑8` 均未報警 → 逃逸三處版本殘留之一）

設計原則（本版重寫要點）
----------------------
① **掃描範圍 = 全包**（總控 + 10 個子技能）。原實現只 os.walk() 總控目錄，
   子技能目錄的 Markdown 完全不參與內容規則檢查 —— 這是「靜默假通過」的根因。
② **版本斷言是真斷言**（`frontmatter version == VERSION` 常量比較）。原實現的版本一致性檢查寫成
   "歷史文本里是否出現過某個舊串"，因歷史記錄必然含有舊串而恆真。
③ **輸出按域分項**，任何一項 FAIL 即以退出碼 1 結束。

檢查域
------
[A] 版本一致性   根 SKILL / README / 10 子技能 / CHANGELOG 均為 7.4.23；CURRENT 文檔無舊版本串
[B] 結構完整性   總控 references == 48；子技能 == 10；被引用的規則文件真實存在
[C] 內容規則門   可靈零出現 / 三視圖 / 格式別名 / 2.0 首尾幀 / 規則自洽門（全包範圍）
[D] 機檢腳本     全部腳本可編譯；validate_prompt.py self-test PASS；關鍵門在案
[E] 套裝路由     四層縱深 / 素材來源鎖 / 權威歸屬表 / 強制讀取清單 / 10 子技能掛線
               + 四項融合域完整性：㉒ 場面調度權威 / ㉓ 故事板圖標準 / ㉔ 場景空間事實五件事 / ㉕ 素材形態與接線單
               + 新增域完整性：㉗ 方言配音控制詞典外掛 / ㉘ 打鬥規程吸收
[E+++] 接線修復域：㉚ 三份出圖模板完整性（九宮格 / 立繪 / 道具——刪掉或字段刪空即 FAIL）
               + ㉛ 機檢 C 碼一致性：validate_prompt.py 實現的 C 系碼 ⊆ 機檢手冊登記的 C 系碼（防「腳本有、手冊無」）
[E++++] 打戲護欄域：㉜ 兩份打戲新庫完整性（激烈度硬護欄 / 特效手繪化）
               + C21 三處互鎖：三引擎聲明 ↔ validate_prompt.py 實現 ↔ 機檢手冊登記
[E++++] 節奏負載域：㉝ 節奏與渲染負載護欄庫完整性 + C22 四處互鎖
               + ★防迴歸：鐵律26「動作數上限」必須已接入自檢閘口
[E*5] 畫風鎖域：㉞ style-bible 8 份 + 成稿示例 2 份 + 引擎腳本 2 份完整性
               + C23 三處互鎖：validate_prompt.py 實現 ↔ 機檢手冊登記 ↔ 總控觸發門口徑
               + 接線防迴歸：feed 契約 9 / asset 鎖系統 I 鎖 / 編號裁定（F 鎖 = I 鎖）在案
[E*6] 禁項單點域：㉟ C24a/b 實現 ↔ 機檢手冊登記 ↔ C7 前置等價聯動 + 自測五組用例在案
[G] 素材形態       M0/M1/M2 權威完整性 / 門禁改判表 / 接線單 / 文字鎖 / 三不一要 / 閘門 6B 機檢
[F] 外部版本保全 V3.9.0 / V2.6.0 / V5.0.2 / v13.0 未被版本統一誤傷
[E*9] 字數口徑域：㊲ C4 篇級 6000「單文件」口徑 ↔ 閘門3 段級 2.0 2900/3000 · 2.5 3600/4000 粒度聲明（防單值漂移）
[E*10] 外部增量與病句修復域：㊳ 版本清洗殘句清零 / 照明兩節 / 高光 8 套 / OTS 拓撲 / C17b
[E*13] 融合規則補載體域（2026-10-10）：㊷ 六個新子碼五處互鎖
       （規則源文件 ↔ validate_prompt.py ↔ 機檢手冊 ↔ 子碼計數 ↔ 自檢用例）
[E*16] 圖形化產物與段縫景別承接域（2026-10-11 用戶實測反饋）：
       ㊺ 故事板圖版式/交付清單/四宮格消歧 ↔ ㊻ C18m 段縫景別落差八互鎖（含 C7c 元檢查）
[E*23] 前置鎖完整性域（2026-10-13 · D 鎖缺位修復）：
       ㊼ 「多段任務」判定式 + 判定時點（P0 立項期）+ 五道鎖同批鎖完 三處互鎖（防「自稱非多段任務」跳過 D 鎖）
       （治「四宮格故事板沒出」與「末鏡拉全景後下段切中景」兩條實跑反饋）
[E*24] 劇本引擎階段② 更名域（2026-10-13 用戶要求「不是動漫IP」）：
       ㊿ 階段②名「動漫IP開發」→「IP 與角色開發」生效位四處一致 + 舊名清零 + 形態無關聲明在案
       （治「真人項目被階段名誤判為動漫項目」）
[E*25] 前置鎖默認口子清零域（2026-10-13 用戶裁定「這個還是沒有給我選」）：
       ◆ C 鎖「未指定默認 ③」與 I 鎖「按默認推薦卡走」兩個口子清零 + 新口徑三處同源 + 形態基底改必確認
       （圈碼 ㉑~㊿ 已被前序 24 個域佔滿，本域改用 ◆1~◆4 編號，避免與既有域混淆）
       （治「鎖寫了默認值、執行者就不彈卡，用戶根本沒得選」）
[E*26] 道具資產錨點域（2026-10-13 用戶發現「提示詞裡沒有道具的 @ 位」）：
       ◇ 關鍵道具錨點 @PRP- 落位【場景資產】欄（與 @SCN- 並列 · 七段式不增段）+ 舊「@人名/@場景名」兩類寫法清零
         + 三族錨點同源（asset-spatial-ledger）+ 投餵引擎與故事板層同步
       （◆1~◆4 已被 [E*25] 佔用，本域改用 ◇1~◇3 編號，與 ◆ 組區分）
       （治「人物/場景/站位都有 @ 錨點，唯獨道具沒有，只能寫鏡行括號夾註「（圖9）」」）
[E*27] 特寫佔比與分鏡字段完整性域（2026-10-13 項目體檢修復）：
       ◈ 特寫佔比口徑寫死（人物特寫含人體局部肢體 / 物件特寫不計入 / 判定基準在案）
         + 補機檢 C18n（含 4 條自檢用例）+ 故事板引擎增設「逐鏡九字段完整性」硬自檢
       （◇1~◇3 已被 [E*26] 佔用，本域改用 ◈1~◈3 編號）
       （治「硬指標只寫不檢」與「分鏡稿漏欄無兜底」：72 鏡人物特寫 19.4% 低於下限而機檢零告警）
[E*28] 粉絲系統性意見全修域（2026-10-13 · 劇本 5 條 + 分鏡 3 條 · 全修裁定）：
       ◉ 外部劇本潤色層（P0-1 新增 references）+ R1 速查衝突修復（P0-2）
         + 公式去重升級全劇配額（P1-1）+ 分鏡形態適配與特寫×平視組合禁令（P1-2）
         + 反派能力基線與受挫配額（P2-1）+ 懸念存量配額（P2-2）
         + FACS 形態強制與「敘事/動作/表情」三要素（P3）
       （◈1~◈3 已被 [E*27] 佔用，本域改用 ◉1~◉4 編號）
       （治「包自己教出粉絲抱怨的結果」：R1 速查寫「不追求人物深度」架空整套成長地圖）
[E*29] 台詞擬人化域（2026-10-13 · 用戶實測「台詞對白機械化／不夠擬人／缺稱呼」）：
       ◐ 新建台詞擬人化引擎 dialogue-naturalization.md（含《台詞擬人化過站》）
         + 消聲音卡三口徑分裂（§1.8 YAML 補 address_system / avg_line_length / signature_particles）
         + 表演層壞表演圖鑑 8「台詞太乾淨」改指針 + 下游探測器 C28a~c（只報不改）
         + P1 必讀清單補台詞七維診斷（消「孤兒權威」）
       （◉1~◉4 已被 [E*28] 佔用，本域改用 ◐1~◐8 編號）
       （根因：規則在包裡卻全失效——唯一口語化規則被劃歸表演層、劇本層讀不到 / 七維只診斷不治病
         且要手動觸發 / 規則全是否定式、正向供給為零（「擬人」「機械化」「腔調」全包 0 命中）/
         聲音卡同概念三個版本互不覆蓋 / 下游鐵律「台詞逐字保留」致上游寫錯後全鏈路無人能救）
[E*30] 規則文件掛載一致性域（2026-10-13 · 元層面反思 · 治「★權威 ≠ 會被讀到」）：
       ◑ 包內三套重要性清單（唯一權威歸屬表 / 文件樹★ / **八階段必讀清單**）**互無斷言** →
         文件可寫進表、標上★、畫進文件樹，卻不在必讀清單裡 —— 照樣「是權威」，只是永遠沒人讀。
       修復：總控新增《按需規則文件 · 觸發條件台賬》（**39 份非必讀規則文件全部登記觸發條件**）
         + 表演層 `acting-direction.md` 接進 P3 必讀（修復前它自聲明「P1 寫《角色表演檔案》」卻無讀取路徑）
       ◑ 2026-10-16 追加：**掃描域收斂為本套裝 13 目錄**（`suite_roots()`）——原 `scan_md_files()`
         用 `os.walk(PKG)` 直掃「包根」，真實部署下把 ① GitHub 倉庫根**落地頁 `README.md`**（含上一版版本號）
         ② 用戶本機同級**其它技能**（`real-combat-director` / `xuanhuan-combat-director` / …）
         一併捲入內容規則門 → 升版後必報**與 13 目錄無關的假 FAIL**。本域以 **◑16** 鎖定掃描域；
         ◑8 原先的同級技能名白名單屬「補丁打補丁」，隨之退休。
[E*31] 資產狀態偏離域（2026-10-13 · 用戶實測「資產圖戴頭盔 + 提示詞夾頭盔 = 兩個頭盔」）：
       ◒ `CHAR_STATE` 人物持續狀態變體（與場景 `SET_STATE` 對稱）+ 立繪配飾口徑改「默認鎖定·可變需聲明」
         + 投餵層「資產偏離聲明」三件套（`model-adapters.md` §5.0.6）+ 機檢 `C29`
       （根因：`SET_STATE` 只管場景 / 換裝只解決跨造型 / 穿戴物被寫成「固定不可變更」
         → **無優先級聲明 → 模型【疊加】而非【替換】**）
[E*35] Agent 系統性修復域（2026-10-15 · 治「大模型修復留下的修A漏B」）：
       ◔ ① **小數秒口徑 `MM:SS.s`**：`build_board_lite.to_seconds` 的 `int(s)` 曾把 `00:10.5` 拋 ValueError
         並**靜默丟鏡**（實測《鹽梟劫》稿 17 鏡只出 10 鏡 = 丟 41%；看板與 SRT/CSV/JSON 三導出時間軸出現 7 秒空洞、
         CLI 零告警）；同一病因的 `fr / 100.0` 把 `.5` 算成 0.05s，腳本內共 **5 處副本**
         → 三腳本統一「按小數位數換算」+ 丟鏡安全網（對賬「原文帶時碼行數 vs 已解析鏡數」）+ 四處 self-test 迴歸鎖
       ◔ ② **C30c/C30d 觸發門**：原只認顯式 `--plugin real|xuanhuan|combat`，默認 `auto` 下整組靜默不跑，
         與總控 SKILL.md 把回執頭/聲線鎖寫成硬規形成空檔 → `auto` 判出 R1/R3 打戲檔時一併核驗
       ◔ ③ **子碼計數唯一口徑**：手冊新增 `SUBCODE-Registry` 機器可讀塊（現行 **99 條**）為唯一權威；
         ㊾ 由「查『自稱 68 條』字符串在不在」改為**真校驗**（條數自洽 + 腳本/註冊清單/手冊三方集合雙向相等）；
         ㉛ 新增「總控 SKILL 子碼清單完整覆蓋註冊塊（含 `C18a~n` 類範圍展開）」斷言，堵住「手冊有、總控無」
[E*36] 畫風鎖三方對賬域（2026-10-15 Agent 修復 · 治「加卡頂掉老卡 / 漏族 / 數字漂移」）：
       ◔ 病灶：`n` 版補 4 張國漫3D卡時**頂掉了原有 4 張卡**（皮克斯/迪士尼經典/皮埃爾·孔切·平面插畫/
         Nelagraphs·長條漫畫風），T8 家族縮編致 宮崎駿/京阿尼 掉隊，參數庫章節號重複、「其餘 N 組」算錯——
         **全程零斷言覆蓋**。本域把 12 項全部變成真斷言：
         選卡表卡數自洽（◔1）/ 編號唯一（◔2）/ 停用號位聲明（◔3）/ 補回卡在位（◔4）/ 移除卡不在選項卡內（◔5）/
         **引擎 STYLES ↔ 文檔 T 族表雙向一致（成員+家族+星級 · ◔6）** / 引擎已摘除移除卡（◔7）/
         參數庫章節號唯一（◔8）/ 補錄算式自洽（◔9）/ 全包無舊口徑殘留（◔10）/ 紅線 2 交叉引用在案（◔11）/
         題材矩陣兩表聲明數 == 實際行數（◔12）
"""
import os
import re
import sys
import json
import shutil
import tempfile
import py_compile
import subprocess
import warnings

VERSION = "8.2.0-SLIM"
EXPECTED_REFS = 53   # 遞歸計數（40 份頂層規則庫 + style-bible 8 份）。⚠️ 注意：SKILL.md 對外統一聲明「49 份規則庫」（遞歸口徑）。2026-10-22 新增 blooper-prevention-playbook.md（成片穿幫防治軍規）後由 50 升至 51；2026-10-24 新增 crowd-behavior-direction.md 升到 52；2026-11-03 P13 剝離 H3 支線（h3-adapter.md 獨立成包）回落至 51。
SUB_SKILLS = [
    "sd-decision-engine", "sd-recon-engine", "sd-script-engine",
    "sd-asset-engine", "sd-storyboard-engine", "sd-combat-engine", "sd-xuanhuan-engine",
    "sd-real-engine", "sd-feed-engine", "sd-qc-engine",
]
# 本包歷史版本串（僅允許出現在 CHANGELOG 與 LEGACY/沿革說明行）
# 注：**V7.3.9 起，正文不再保留任何歷史版本標註**——此前「V7.3.x 新增·續·修訂」類在案溯源標註已全部清除，
#     沿革統一收斂至 CHANGELOG.md。故 7.3 / 7.4 系列（除當前版 VERSION）納入 OLD_VER_RE 約束。
# ⚠️ 元規則四（斷言只鎖常量）：排除項由 VERSION 常量派生，**不得寫死字面版本號**。
#     實測事故 2026-10-14：升版 7.4.19 時排除項仍寫 (?!4\.18) → 新版號被當舊版號誤殺 6 處。
#     二次事故（同日）：把前瞻塞在 `7\.` 之後 → 前綴已消費 `7.`，前瞻比對 `4.19` 永久失敗。
#     ✅ 正確寫法：負向前瞻必須錨在**整個版本號之前**，即在 `V` 後立刻排除當前版全串。
_CUR_ESC = re.escape(VERSION)                    # e.g. 7\.4\.19
OLD_VER_RE = re.compile(
    r"V(?!%s(?!\d))(?:6\.[5-9]|7\.\d+(?:\.\d+)*|8\.\d)(?:\.\d+)*" % _CUR_ESC
)
# 沿革/域命名豁免詞：版本串可出現在 LEGACY/沿革/域命名說明行（`.md` 與 `scripts/*.py` 同一口徑）。
# ⚠️ 元規則：**豁免詞不得讓整行放過「規格區」**——表格行不適用（見 ◑9）。
#    「域命名沿革」類標識（如 `section("[E+] V7.3.0 三項融合域")`）是互鎖域的**結構性錨點**，
#    刪除會破壞引用與可讀性，故單列一類顯式標註（2026-10-14 補：此前 scripts/*.py 完全不在掃描域內）。
VER_ALLOW_RE = re.compile(r"LEGACY|歷史|沿革|代號|廢止|不再|不得|舊口徑|舊編號|CHANGELOG")
# 外部產品版本（不得被版本統一改寫）
EXTERNAL_VERS = ("V3.9.0", "V2.6.0", "V5.0.2", "v13.0")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 總控目錄
PKG = os.path.dirname(BASE)                                          # 包根（含總控與 sd-*）
CHANGELOG = os.path.join(BASE, "CHANGELOG.md")

FAILED = []
SECTION = {"cur": None}


def section(name):
    SECTION["cur"] = name
    print()
    print("=" * 62)
    print(name)
    print("=" * 62)


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(f"{SECTION['cur']} / {name}")


def read(path):
    """缺文件返回空串（有韌性）：讓"文件不存在"表現為該項 FAIL，而不是整腳本 traceback 崩掉。
    新文件的"存在性"由各自的 os.path.exists() 斷言獨立覆蓋，不會被空串掩蓋。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        return ""


def rel(p):
    return os.path.relpath(p, PKG)


def suite_roots():
    """本套裝掃描域 = 總控 + 10 子技能（**恰 13 個目錄**）。
    ⚠️ **不得用 `os.walk(PKG)` 直掃「包根」**（2026-10-16 根治）：PKG 在真實部署下未必是
    「只裝本套裝的空目錄」——
      ① GitHub 倉庫根另置**落地頁 `README.md`**（含「上一版版本號 + 多技能套裝版」之類版本/沿革表述），
         升版後被「CURRENT 文檔無舊版本串」判為**本套裝的規則文件**；
      ② 用戶本機 `.openclaw/workspace/skills/` 下**並列著其它技能**（`real-combat-director` /
         `xuanhuan-combat-director` / `short-drama-factory` / …），其版本串與文件名被一併捲入。
    兩者都產生**與「本套裝 13 目錄」無關的假 FAIL**。舊解法是給 ◑8 掛同級技能名**白名單**——
    屬「補丁打補丁」（新增同級即漏）。「全包」的唯一正解 = **本套裝 13 目錄**，與 ◑8 斷言口徑一致。"""
    roots = [BASE]
    for _n in SUB_SKILLS:
        _p = sub_skill_path(_n)
        if _p:
            roots.append(_p)
    return roots


def scan_md_files():
    """本套裝全包掃描（總控 + 10 子技能）—— 原實現只掃總控，是假通過根因。"""
    out = []
    for _root0 in suite_roots():
        for root, dirs, files in os.walk(_root0):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in files:
                if fn.endswith(".md"):
                    out.append(os.path.join(root, fn))
    return sorted(set(out))


def scan_rule_docs():
    """參與內容規則門的文檔：全包 Markdown，排除歷史沿革文件。"""
    return [p for p in scan_md_files() if os.path.abspath(p) != os.path.abspath(CHANGELOG)]


def sub_skill_path(name):
    for p in (os.path.join(PKG, name), os.path.join(BASE, "skills", name)):
        if os.path.isdir(p):
            return p
    return None


def frontmatter_version(text):
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None
    m2 = re.search(r'^version:\s*"?([^"\n]+?)"?\s*$', m.group(1), re.M)
    return m2.group(1).strip() if m2 else None


# ---------------------------------------------------------------- [A] 版本一致性
section(f"[A] 版本一致性（唯一現行版本 = {VERSION}）")

skill = read(os.path.join(BASE, "SKILL.md"))
readme = read(os.path.join(BASE, "README.md"))
changelog = read(CHANGELOG)

check(f"根 SKILL.md frontmatter version == {VERSION}",
      frontmatter_version(skill) == VERSION, f"實際 {frontmatter_version(skill)}")
check("根 SKILL.md 聲明「現行唯一版本口徑」", "現行唯一版本口徑" in skill)
check(f"README.md 版本行 = {VERSION}",
      re.search(r"\*\*版本\*\*：V" + re.escape(VERSION), readme) is not None)
check("README.md 聲明「現行唯一版本口徑」", "現行唯一版本口徑" in readme)
check(f"CHANGELOG.md 含 {VERSION} 條目",
      f"## V{VERSION} " in changelog or f"· V{VERSION}：" in changelog or f"V{VERSION} ·" in changelog)
check("CHANGELOG.md 聲明「版本編號說明」與當前口徑",
      "版本編號說明" in changelog and "不代表當前版本高低" in changelog)

_bad_sub_ver = []
for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    sp = os.path.join(p, "SKILL.md")
    if not os.path.exists(sp):
        _bad_sub_ver.append(f"{name}(缺 SKILL.md)")
        continue
    v = frontmatter_version(read(sp))
    if v != VERSION:
        _bad_sub_ver.append(f"{name}={v}")
check(f"10 子技能 frontmatter version 均為 {VERSION}", not _bad_sub_ver, "; ".join(_bad_sub_ver))

_bad_old = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if OLD_VER_RE.search(line) and not VER_ALLOW_RE.search(line):
            _bad_old.append(f"{rel(p)}:{i}")
check("CURRENT 文檔無舊版本串（僅 LEGACY/沿革/代號行可提及）",
      not _bad_old, "; ".join(_bad_old[:6]))

# ---------------------------------------------------------------- [B] 結構完整性
section("[B] 結構完整性")

refs_dir = os.path.join(BASE, "references")
# 遞歸計數（含 style-bible/ 子目錄知識庫），與 SKILL.md/README 的「49 份規則庫」口徑一致（P14：原 51 含 2 份已剔除的成稿示例）
refs = [os.path.relpath(os.path.join(dp, f), refs_dir).replace("\\", "/")
        for dp, _dn, fn in os.walk(refs_dir) for f in fn if f.endswith(".md")]
check(f"總控 references 規則庫 == {EXPECTED_REFS} 份（含 style-bible）",
      len(refs) == EXPECTED_REFS, f"實際 {len(refs)} 份")

_missing_skill = [n for n in SUB_SKILLS if sub_skill_path(n) is None]
check("10 子技能目錄全部存在", not _missing_skill, "缺: " + ", ".join(_missing_skill))

_thin_refs = []
for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    rd = os.path.join(p, "references")
    n = len([f for f in os.listdir(rd) if f.endswith(".md")]) if os.path.isdir(rd) else 0
    if n < 3:
        _thin_refs.append(f"{name}({n})")
check("每個子技能 references >= 3 份", not _thin_refs, "; ".join(_thin_refs))

# 被引用的規則文件真實存在（三檔解析：同目錄相對 → 總控相對 → 包根相對 → 全包同名兜底）
# 注：CHANGELOG 為歷史記錄，不參與本門（其中的舊路徑可能已遷移）
_bad_ref = []
REF_TOKEN = re.compile(r"`((?:references/|scripts/|sd-[a-z\-]+/)[^`<>…*]*?\.(?:md|py))`")
_all_basenames = set()
for _root0 in suite_roots():          # 2026-10-16：同名兜底同樣只在 13 目錄內找，防越界到同級技能 / 落地頁
    for _root, _dirs, _files in os.walk(_root0):
        for _fn in _files:
            _all_basenames.add(_fn)
for p in scan_rule_docs():
    here = os.path.dirname(p)
    for tok in REF_TOKEN.findall(read(p)):
        cands = [os.path.join(here, tok), os.path.join(BASE, tok), os.path.join(PKG, tok)]
        if any(os.path.exists(c) for c in cands):
            continue
        if os.path.basename(tok) in _all_basenames:   # 記法省略目錄，但文件確實存在
            continue
        _bad_ref.append(f"{rel(p)} → {tok}")
check("被引用的規則/腳本文件真實存在", not _bad_ref, "; ".join(sorted(set(_bad_ref))[:6]))

# ---------------------------------------------------------------- [C] 內容規則門
section("[C] 內容規則門（全包範圍，含 10 子技能）")

KLING_OK = re.compile(r"^$")
_bad_kling = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if "可靈" in line and not KLING_OK.search(line):
            _bad_kling.append(f"{rel(p)}:{i}")
check("① 包內零出現可靈（SLIM 版只留 Seedance 2.0/2.5 · 防回潮）", not _bad_kling,
      "; ".join(_bad_kling[:5]))
check("① model-adapters 零可靈殘留（LEGACY 聲明已隨 SLIM 版刪除）",
      "可靈" not in read(os.path.join(refs_dir, "model-adapters.md")) and "Kling" not in read(os.path.join(refs_dir, "model-adapters.md")))

VIEW_OK = re.compile(r"LEGACY|舊稱|舊「|歷史")
_bad_view = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if "三視圖" in line and not VIEW_OK.search(line):
            _bad_view.append(f"{rel(p)}:{i}")
check("② CURRENT 角色資產標準僅 4 View（三視圖僅存於 LEGACY 說明行）", not _bad_view,
      "; ".join(_bad_view[:5]))
asl = read(os.path.join(refs_dir, "asset-spatial-ledger.md"))
check("② asset-spatial-ledger 定義 4 View 資產參考圖", "4 View 資產參考圖" in asl)

_ban = [l for l in "\n".join(read(p) for p in scan_rule_docs()).splitlines()
        if re.search(r"八段式|六欄|九欄", l) and not re.search(r"禁|別名", l)]
check("③ 禁用「八段式/六欄/九欄」別名（禁令聲明行除外）", not _ban, "; ".join(_ban[:3]))
ma = read(os.path.join(refs_dir, "model-adapters.md"))
check("③ 七段式唯一命名 + 【接續狀態】廢止口徑（model-adapters §5）",
      "「七段式」為唯一命名" in ma and "【接續狀態】尾行已於 2026-10-09 廢止" in ma)

check("④ spatial-reference-system-V3 帶 LEGACY/備查標記",
      "LEGACY" in read(os.path.join(refs_dir, "spatial-reference-system-V3.md")))
check("④ CHANGELOG 帶 LEGACY/HISTORY 聲明", "LEGACY/HISTORY 聲明" in changelog)

NEG = re.compile(r"無首尾幀|禁用|不適用|禁止|不得|排除|2\.0 無|禁投|禁寫|殘留|出現首尾幀|FAIL")
# ⚠️ 版本號陷阱：包版本串若含 "2.0" 子串，會被本項誤判為「Seedance 2.0 語境」。
#    故用負向後顧排除 "7." 前綴，只認真正的模型版本號 2.0。
MODEL_20 = re.compile(r"(?<![\d.])2\.0")
_bad_fl = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if MODEL_20.search(line) and ("首幀" in line or "尾幀" in line) \
                and not NEG.search(line):
            _bad_fl.append(f"{rel(p)}:{i}")
check("⑦ 2.0 語境無首尾幀（僅否定/禁用表述可提及 · 排除包版本串的子串誤判）", not _bad_fl, "; ".join(_bad_fl[:5]))
check("⑦ SKILL 〇節含「首尾幀僅限 2.5」硬約束 + 參考模式二選一默認①",
      "首尾幀僅限 Seedance 2.5" in skill and "全能參考模式（默認推薦）" in skill)

chk_path = os.path.join(refs_dir, "prompt-feeding-checklist.md")
chk = read(chk_path)
check("⑥ 場景拼接圖產物已廢止（2026-10-11 用戶裁定 · 職能併入母版）",
      "拼接圖" not in asl)
check("⑥ 舊口徑「關鍵區域細節三聯」已清零", "細節三聯" not in asl)
check("⑥ 場景雙圖鐵律（母版 → 五宮格 · 按出圖順序）",
      "場景雙圖" in chk and "場景母版" in chk and "五宮格" in chk)

# ⑰ 規則自洽門：被廢止句式只允許出現在警示語境（規則文檔自己過自己的禁令）
DEAD_PATTERNS = (
    "首幀即這隻手", "指甲蓋大的一片暖黃光斑", "火光從側面照在玉面",
    "舉到油燈旁", "面無笑意", "漏雨成線", "映出油燈火苗",
)
WARN_MARKS = ("已廢止", "廢止", "禁寫", "禁入", "禁止", "不得", "一律刪", "⚠️", "❌",
              "替代", "規避", "裸禁令", "病根", "無視", "畫不出來", "翻車", "已修訂")
RULE_DOCS = [
    os.path.join(refs_dir, "model-adapters.md"),
    os.path.join(BASE, "SKILL.md"),
    chk_path,
    os.path.join(refs_dir, "seedance-render-engine.md"),
]
_v17 = []
for doc in RULE_DOCS:
    if not os.path.exists(doc):
        _v17.append(f"缺失 {rel(doc)}")
        continue
    for i, line in enumerate(read(doc).splitlines(), 1):
        for pat in DEAD_PATTERNS:
            if pat in line and not any(m in line for m in WARN_MARKS):
                _v17.append(f"{rel(doc)}:{i}『{pat}』")
check("⑰ 規則自洽門：被廢止句式僅存於警示語境（規則不產毒）", not _v17, "; ".join(_v17[:6]))
check("⑰ 示範句驗證紀律在案（model-adapters + SKILL 法則 24）",
      "示範句驗證紀律" in ma and "示範句驗證紀律" in skill and "先驗創作" in skill)

# ---------------------------------------------------------------- [D] 機檢腳本
section("[D] 機檢腳本（編譯 / self-test / 關鍵門在案）")

scripts_dir = os.path.join(BASE, "scripts")
py_files = sorted(f for f in os.listdir(scripts_dir) if f.endswith(".py"))
_compile_fail = []
for fn in py_files:
    try:
        py_compile.compile(os.path.join(scripts_dir, fn), doraise=True)
    except Exception as e:  # noqa: BLE001
        _compile_fail.append(f"{fn}: {e}")
check(f"scripts/ 全部 {len(py_files)} 個腳本可編譯", not _compile_fail, "; ".join(_compile_fail[:3]))

# ★ 語法告警門（2026-10-16 補 · 沿革見 CHANGELOG）
# 交付腳本每次運行都會把 SyntaxWarning（如非法轉義序列 "\["）打到**用戶終端**，
# 屬交付件噪聲；且未來 Python 版本將把非法轉義序列升為 SyntaxError → 直接崩。
# 歷史病灶：本文件內探測 build_board_lite.py 的字符類片段 `[\[【]?` 未加 raw 前綴，
# 每次跑必打 `SyntaxWarning: invalid escape sequence '\['`；已改為 r"..." 寫法。
_sw, _npy = [], 0
for _r_sw in suite_roots():
    for _dp_sw, _dn_sw, _fn_sw in os.walk(_r_sw):
        _dn_sw[:] = [d for d in _dn_sw if d != "__pycache__"]
        for _f_sw in _fn_sw:
            if not _f_sw.endswith(".py"):
                continue
            _p_sw = os.path.join(_dp_sw, _f_sw)
            try:
                _src_sw = open(_p_sw, encoding="utf-8", errors="replace").read()
            except Exception:  # noqa: BLE001
                continue
            _npy += 1
            with warnings.catch_warnings(record=True) as _ws_sw:
                warnings.simplefilter("always")
                try:
                    compile(_src_sw, _p_sw, "exec")
                except SyntaxError as _e_sw:
                    _sw.append(f"{_f_sw}: SyntaxError {_e_sw}")
                for _w_sw in _ws_sw:
                    if issubclass(_w_sw.category, SyntaxWarning):
                        _sw.append(f"{_f_sw}:{_w_sw.lineno} {_w_sw.message}")
check(f"◑17 全包 {_npy} 個 .py 零語法告警（非法轉義序列 / SyntaxWarning）", not _sw, "; ".join(_sw[:4]))

vp = os.path.join(scripts_dir, "validate_prompt.py")
check("validate_prompt.py 存在（稿件級出稿門禁）", os.path.exists(vp))
vp_src = read(vp) if os.path.exists(vp) else ""
if os.path.exists(vp):
    try:
        r = subprocess.run([sys.executable, vp, "--self-test"],
                           capture_output=True, text=True, timeout=60)
        check("validate_prompt.py --self-test 通過", r.returncode == 0,
              (r.stdout or r.stderr)[-200:])
    except Exception as e:  # noqa: BLE001
        check("validate_prompt.py --self-test 通過", False, str(e))

for label, needle in [
    ("C8 2.0 禁用首尾幀門", "C8 Seedance 2.0 全面禁用首尾幀"),
    ("C9 平台高危詞門", "C9 正文出現平台高危詞"),
    ("C13 鏡長雷同門", "C13 鏡長雷同"),
    ("C14 畫外聲門", "聲畫分離紅線"),
    ("C15 拉伸湊時門", "拉伸湊"),
    ("C16 對白語氣門", "語氣錯位"),
    ("C17 擺位必入畫門", "擺位必入畫"),
    ("C18 首鏡錨定門", "C18a"),
    ("C19 禁令失效門", "C19a"),
    ("C20 單主體錨定門", "C20a"),
]:
    check(f"validate_prompt 含 {label}", needle in vp_src)

check("SKILL 含法則 17 鏡長節奏鐵律", "鏡長節奏鐵律" in skill)
check("SKILL 架構樹 / 指令路由掛線 validate_prompt.py", "validate_prompt.py" in skill)
check("checklist 掛線 validate_prompt（出稿門禁）", "validate_prompt" in chk)

# ---------------------------------------------------------------- [E] 套裝路由
section("[E] 套裝路由與共享契約")

check("SKILL 含套裝路由章節與子技能路由表",
      "多技能套裝路由" in skill and "子技能路由表" in skill)
check("SKILL 含四層縱深架構說明（L0/L1/L2/L3）",
      all(k in skill for k in ("L0", "L1", "L2", "L3")) and "四層縱深" in skill)
_missing_route = [n for n in SUB_SKILLS if n not in skill]
check("SKILL 掛線全部 10 子技能", not _missing_route, "缺: " + ", ".join(_missing_route))
check("SKILL 含打戲三檔分流判定（通用 / R3 玄幻 / R1 寫實）",
      "打戲三檔分流" in skill and "sd-xuanhuan-engine" in skill and "sd-real-engine" in skill)
check("SKILL 已移除〇·0 賽道分流鎖（精簡版五道鎖）", "〇·0 · 賽道強制分流" not in skill and "五道前置鎖" in skill)
check("SKILL 含〇·1 素材來源鎖（與 A/B/C/D 並列）",
      "〇·1 · 素材來源鎖定" in skill and "素材來源鎖" in skill)
check("SKILL 含【強制讀取清單】（6 階段必讀表）", "強制讀取清單" in skill and "P0·1" in skill and "P0·0" not in skill)
check("SKILL 含 A 鎖二選一（2.5 / 2.0）",
      "模型版本二選一" in skill and "Seedance 2.5 / ② Seedance 2.0" in skill)
check("SKILL 已清除單模型舊句「Seedance 2.5 或 Seedance 2.0」二選一殘留",
      "Seedance 2.5** 或 **Seedance 2.0" not in skill)
check("SKILL 含兩檔運行模式表（嚴格模式 / 極速模式 · 極速僅軟推斷〇·1）",
      "嚴格模式" in skill and "極速模式" in skill and "不推斷、不默認" in skill)
check("SKILL 含《規則權威歸屬表》與衝突裁決順序",
      "唯一權威歸屬表" in skill and "衝突裁決順序" in skill)
check("SKILL 含機檢兩門制（結構門 C1~C15 / 語義風險門 C16~C20）與分級處置",
      "結構門" in skill and "語義風險門" in skill and "C1~C15" in skill
      and "C16~C20" in skill and "必須清零才交付" in skill
      and "必須由 AI/人工複核後放行" in skill)
check("SKILL 無字面重複段落（「只有一種例外」僅出現 1 次）",
      skill.count("只有一種例外：用戶**明確點名**某個子技能") == 1)
check("SKILL 聲明規則庫份數 == EXPECTED_REFS（元規則四：只鎖常量 · 2026-10-14 修 38/48 雙值懸掛）",
      f"{EXPECTED_REFS} 份規則庫" in skill and "38 份" not in skill and "49 份" not in skill)

for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    sp = os.path.join(p, "SKILL.md")
    s = read(sp)
    check(f"子技能 {name} frontmatter 合規（套裝前綴 / 版本 / 成員聲明）",
          f"V{VERSION} 套裝" in s and frontmatter_version(s) == VERSION
          and "short-drama-director" in s)

rce = sub_skill_path("sd-recon-engine")
if rce:
    rce_s = read(os.path.join(rce, "SKILL.md"))
    check("㉑ sd-recon-engine 含採風四步 / 信源三級分級 / 情報卡十三項字段 / 六條證據紀律",
          "採風四步" in rce_s and "T1 一手" in rce_s and "十三項字段" in rce_s
          and "不編造" in rce_s)
    check("㉑ sd-recon-engine 聲明輕量版邊界（不做打分/門檻/聚簇/台賬/定時）",
          "輕量版邊界" in rce_s and "不做" in rce_s)
# ------------------------------------------------- [E+] 三項融合域完整性
section("[E+] V7.3.0 三項融合域（場面調度 / 故事板圖 / 場景空間事實）")  # 域命名沿革：V7.3.0 引入，標識保留

# ㉒ 場面調度與站位決策層
bd = read(os.path.join(refs_dir, "blocking-direction.md"))
check("㉒ 場面調度權威文件存在（references/blocking-direction.md）",
      os.path.exists(os.path.join(refs_dir, "blocking-direction.md")))
check("㉒ blocking-direction 含文字平面圖 / 權力幾何 / 節拍閉環五段 / 對話調度鏈",
      "文字平面圖" in bd and "權力幾何" in bd
      and all(k in bd for k in ("起勢", "路徑", "落點", "接收者反應"))
      and "說話者" in bd and "反應者" in bd)
check("㉒ blocking-direction 含關鍵道具賬（持有 / 手位 / 落點 / 狀態）",
      "持有" in bd and "手位" in bd and "落點" in bd)
check("㉒ blocking-direction 聲明不重複定義鏡頭策略四模式（權威仍歸 editing-transition-gate）",
      "不重複定義" in bd and "editing-transition-gate" in bd)
check("㉒ 禁圖口徑已收窄：導演稿允許文字平面圖 + 投餵詞仍禁任何圖",
      "投餵詞" in bd and ("圖畫在導演稿裡" in bd or "圖在導演稿裡" in bd)
      and "投餵詞" in read(os.path.join(refs_dir, "model-adapters.md"))
      and "blocking-direction.md" in read(os.path.join(refs_dir, "model-adapters.md")))
check("㉒ SKILL 掛線場面調度（權威歸屬表 + 強制讀取清單 + 路由表）",
      "blocking-direction.md" in skill and "場面調度" in skill)

# ㉓ 故事板圖（面板鏈）
sbe = sub_skill_path("sd-storyboard-engine")
sbs = read(os.path.join(sbe, "references", "storyboard-sheet-template.md")) if sbe else ""
check("㉓ 故事板圖標準文件存在（sd-storyboard-engine/references/storyboard-sheet-template.md）",
      bool(sbe) and os.path.exists(os.path.join(sbe, "references", "storyboard-sheet-template.md")))
check("㉓ 故事板圖含七態動作相位（起始/過程/接觸/頂點/結果/反應/出口）",
      all(k in sbs for k in ("起始", "過程", "接觸", "頂點", "結果", "反應", "出口")))
check("㉓ 故事板圖聲明「每段一張」且「禁機械九宮格」",
      "每段一張" in sbs and "九宮格" in sbs and ("不機械九宮格" in sbs or "禁機械湊九宮格" in sbs or "禁止為了版式好看強行湊 9 格" in sbs))
check("㉓ 故事板圖含 CLEAN_GRID 乾淨版 + 出口幀=下段入口幀 + 面板邊界≠剪輯點",
      "CLEAN_GRID" in sbs and "TECHNICAL_ANNOTATED" in sbs
      and ("出口幀 = 下段入口幀" in sbs or "出口】面板 = 下段" in sbs or "出口幀" in sbs)
      and "面板邊界" in sbs)
check("㉓ 故事板圖聲明與五宮格場景圖/HTML 看板/15 格 PREVIS 四者互不替代",
      "五宮格場景圖" in sbs and "storyboard-board-lite" in sbs)
check("㉓ sd-storyboard-engine SKILL 掛線故事板圖（章節 + 規則庫索引 + 契約）",
      bool(sbe) and "storyboard-sheet-template.md" in read(os.path.join(sbe, "SKILL.md"))
      and "故事板圖" in read(os.path.join(sbe, "SKILL.md")))

# ㉔ 場景空間事實五件事
check("㉔ asset-spatial-ledger §四 含座標系 / SET_STATE / 空氣介質層 / 尺度參照",
      "場景空間座標系" in asl and "SET_STATE" in asl
      and "空氣介質" in asl and ("scale_evidence" in asl or "尺度參照" in asl))
check("㉔ asset-spatial-ledger §四·E 年代錨在案（2026-10-12 新增 · 劇本層《世界錨卡》同源）",
      "年代錨 ERA_ANCHOR" in asl and "禁用元素清單" in asl and "必現元素清單" in asl)
check("㉔ asset-spatial-ledger §一 人物錨在案（年齡錨/體型錨/身份外觀三件套 + 反漂移清單）",
      all(k in asl for k in ("年齡錨", "體型錨", "身份外觀三件套", "反漂移清單")) and "C26c" in asl)
check("㉔ SET_STATE 聲明生效區間與同源變體 + 空氣介質禁無源之霧",
      "生效區間" in asl and "同源" in asl and ("無源" in asl or "萬能光柱" in asl))
check("㉔ asset-spatial-ledger §三 已掛導演稿上游指針（先有導演稿再寫本欄）",
      "blocking-direction.md" in asl)

# ------------------------------------------------- [G] 素材形態與接線單域
section("[G] 素材形態與接線單域（圖片入庫降級為可選登記）")

_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
check("㉕ 素材形態權威文件存在（references/asset-delivery-modes.md）", bool(_ade.strip()))
check("㉕ 含 M0 / M1 / M2 三形態定義",
      "M0" in _ade and "M1" in _ade and "M2" in _ade
      and "純提示詞" in _ade and "編號佔位" in _ade and "已入庫" in _ade)
check("㉕ 明寫默認形態 = M1（不寫默認值執行者就會各寫各的）", "默認形態 = M1" in _ade or "默認 M1" in _ade)
check("㉕ 含門禁按形態改判表（覆蓋門禁 1~5，且門禁 6 不受影響）",
      "門禁分級生效" in _ade and "門禁 5" in _ade and "門禁 6" in _ade and "不受形態影響" in _ade)
check("㉕ 含文字鎖 Text-Lock（M0/M1 一致性替代路徑）",
      "Text-Lock" in _ade and "複述塊" in _ade and "同上" in _ade)
check("㉕ 含《素材接線單》模板與「你該掛哪張」列",
      "素材接線單" in _ade and "你該掛哪張" in _ade and "不控制什麼" in _ade)
check("㉕ 含三不一要（不索要 / 不阻塞 / 不假裝 / 要聲明）",
      "不索要" in _ade and "不阻塞" in _ade and "不假裝" in _ade and "要聲明" in _ade)
check("㉕ 含與 A0~A3 的正交說明（A 軸管複雜度 / M 軸管圖在不在手裡）",
      "正交" in _ade and "A0" in _ade and "A3" in _ade)
check("㉕ 含形態聲明紀律（每次交付首行必寫）", "素材形態：" in _ade and "首行" in _ade)

_afp = read(os.path.join(refs_dir, "asset-first-pipeline.md"))
check("㉕ asset-first-pipeline 已把「無圖不進分鏡」改為條件門並指向新權威",
      "改判為條件門" in _afp and "asset-delivery-modes.md" in _afp
      and "沒有圖\"本身永不構成阻斷理由" in _afp)
check("㉕ asset-first-pipeline 門禁表含「形態影響」列", "形態影響" in _afp)
check("㉕ SKILL 核心法則 0 已含素材形態初判 + 默認 M1",
      "素材形態初判" in skill and "默認 M1" in skill)
check("㉕ SKILL 法則 11 已改為「素材形態與唯一事實來源按形態定義」",
      "素材形態與「唯一事實來源」按形態定義" in skill and "僅適用於 M2" in skill)
check("㉕ SKILL §E 含 E.1「圖不在本包手裡」四鐵律",
      "E.1" in skill and "不索要" in skill and "要聲明" in skill)
check("㉕ SKILL 權威歸屬表含第 23 規則域（素材存在形態與接線單）",
      "素材存在形態與接線單" in skill
      and "references/asset-delivery-modes.md" in skill)
check("㉕ SKILL 指令路由含 /素材形態 與 /接線單", "/素材形態" in skill and "/接線單" in skill)
check("㉕ SKILL 共享契約含素材形態條（第 12 條）", "12. **素材形態**" in skill)

_sfe = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("㉕ sd-feed-engine 共享契約含素材形態契約 + 首行聲明必備",
      "素材形態契約" in _sfe and "素材形態：" in _sfe and "不得交付" in _sfe)
_gc = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
check("㉕ gate_check.py 已實現閘門 6B（--mode + 形態一致性）",
      "--mode" in _gc and "check_asset_mode" in _gc and "閘門6B" in _gc)
check("㉕ gate_check.py 含虛假核驗攔截（非 M2 不得聲稱已核驗）",
      "虛假核驗" in _gc and "已核驗" in _gc)
check("㉕ 素材形態機檢仍由投餵閘門層承載（未併入 C 系編號——C21 是打戲護欄杆，與素材形態無關）",
      "C21" not in _gc and "素材形態" in _gc)

_cfl = read(os.path.join(refs_dir, "prompt-feeding-checklist.md"))
check("㉕ prompt-feeding-checklist 錨點項已改按形態判定（舊絕對門條目已不存在）",
      "按素材形態判定" in _cfl
      and "- [ ] 錨點全部指向《資產圖冊》已鎖定資產圖（無圖=門禁 3/4 阻斷，回補 P2c）" not in _cfl)
_qgr = read(os.path.join(refs_dir, "quality-gate-review.md"))
check("㉕ quality-gate-review P0 含「虛假核驗」與「形態違約」",
      "虛假核驗" in _qgr and "形態違約" in _qgr)
_sae = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
check("㉕ sd-asset-engine 含 Step 3.8 素材形態判定 + 禁索要圖片",
      "Step 3.8" in _sae and "禁止索要圖片" in _sae)
_sqe = read(os.path.join(PKG, "sd-qc-engine", "SKILL.md"))
check("㉕ sd-qc-engine 一致性門按形態改判 + 明確「沒有圖片不屬於缺失」",
      "asset-delivery-modes.md" in _sqe and "沒有圖片" in _sqe)

# ------------------------------------------------- [E++] 三項新增域
section("[E++] 新增域（方言外掛 / 打鬥規程）")  # 域命名沿革：V7.3.1 引入，標識保留

# ㉗ 方言外掛參考
_dv = read(os.path.join(refs_dir, "dialect-voice-control-dictionary.md"))
check("㉗ 方言詞典外掛文件存在（references/dialect-voice-control-dictionary.md）", bool(_dv.strip()))
check("㉗ 方言詞典含 50 套 + 總控 12 條 + 外掛定位（非規則域）",
      "50 套" in _dv and "總控" in _dv and "外掛" in _dv and "非規則域" in _dv)
check("㉗ SKILL 聲明方言詞典為外掛（不進權威歸屬表）",
      "dialect-voice-control-dictionary.md" in skill and "外掛參考" in skill)
check("㉗ SKILL 指令路由含 /方言配音", "/方言配音" in skill)

# ㉘ 打鬥規程吸收
_ebp = read(os.path.join(PKG, "sd-xuanhuan-engine", "references", "epic-battlefield-protocols.md"))
check("㉘ 史詩戰場協議文件存在（sd-xuanhuan-engine/references/epic-battlefield-protocols.md）",
      bool(_ebp.strip()))
check("㉘ 史詩戰場協議含陣營色彩鎖 / Z 型移位 / 群戰遞增 / 武器單次變形 / 蓄力與定格",
      "陣營色彩鎖" in _ebp and "Z 型" in _ebp and "遞增" in _ebp
      and "武器形態單次變形" in _ebp and "尾幀定格" in _ebp)
_ifa = read(os.path.join(PKG, "sd-combat-engine", "references", "impact-frame-and-banlist.md"))
check("㉘ 衝擊幀與負面詞庫文件存在（sd-combat-engine/references/impact-frame-and-banlist.md）",
      bool(_ifa.strip()))
check("㉘ 衝擊幀分級含三級 + 3 幀白閃", "三級" in _ifa and "白閃" in _ifa)
check("㉘ 戰鬥段「只要音效、禁 BGM」已入聲音設計模板",
      "只要音效" in read(os.path.join(PKG, "sd-qc-engine", "references", "sound-design-template.md")))
check("㉘ 參考圖投餵順序已入素材映射",
      "參考圖投餵順序" in read(os.path.join(PKG, "sd-feed-engine", "references", "asset-mapping-and-rules.md")))
check("㉘ SKILL 掛線史詩戰場協議與衝擊幀詞庫",
      "epic-battlefield-protocols.md" in skill and "impact-frame-and-banlist.md" in skill)
check("㉘ SKILL 含法則 27 打鬥史詩規程", "打鬥史詩規程" in skill)

# ------------------------------------------------- [E+++] 接線修復域
# 動機：三份出圖模板（九宮格 / 立繪 / 道具）此前在 128 條斷言裡**各出現 0 次**——
# 把它們刪掉或字段刪空，包級校驗依然全綠（只保證"每個子技能 references ≥3 份"這個數量條件）。
# 本域把它們的關鍵字段變成真斷言；另加「腳本 C 碼 ⊆ 手冊 C 碼」鎖，防文檔再次滯後於腳本。
section("[E+++] V7.3.2 接線修復域（三份出圖模板完整性 / 機檢 C 碼一致性）")  # 域命名沿革：V7.3.2 引入，標識保留

# ㉚ 三份出圖模板完整性
_ass = sub_skill_path("sd-asset-engine")
_grid_p = os.path.join(_ass, "references", "scene-grid-template.md") if _ass else ""
_port_p = os.path.join(_ass, "references", "character-portrait-templates.md") if _ass else ""
_prop_p = os.path.join(_ass, "references", "prop-template.md") if _ass else ""
check("㉚ 三份出圖模板文件均存在（九宮格 / 立繪 / 道具）",
      bool(_ass) and all(os.path.exists(x) for x in (_grid_p, _port_p, _prop_p)))
_grid = read(_grid_p)
_port = read(_port_p)
_prop = read(_prop_p)

check("㉚ 五宮格模板含 8 個結構化字段（內容分配/鎖定模式/攝影機矩陣/攝影機參數/光照曝光/標註要求/畫面純淨/風格分支）",
      all(k in _grid for k in ("【五宮格內容分配】", "【參考場景鎖定模式】", "【五宮格攝影機矩陣】",
                               "【攝影機參數】", "【光照與曝光控制】", "【畫面標註要求】",
                               "【畫面純淨要求】", "【風格分支】")))
check("㉚ 五宮格模板聲明「按空間類型選表」+ 三張替代表 + 「禁止硬湊」",
      "空間類型" in _grid and "表 ①" in _grid and "表 ②" in _grid and "表 ③" in _grid
      and "禁止硬湊" in _grid)
check("㉚ 五宮格模板三張空間類型表齊備（室外獨立建築 / 室內半封閉 / 自然場地·街巷）",
      "室外獨立建築" in _grid and "室內 / 半封閉空間" in _grid and "自然場地 / 街巷" in _grid)
check("㉚ 五宮格模板含標註降級條款（降級 + 編號 + 對照表 + 禁裸格）",
      "降級" in _grid and "編號" in _grid and "對照表" in _grid and "裸格" in _grid)
check("㉚ 五宮格模板含槽位定位句（1 張圖 = 5 個核心視角 = 只佔 1 個素材槽）",
      "素材槽" in _grid and "5 個核心視角" in _grid)
check("㉚ 五宮格模板含模式B 鎖定檔拆分（允許切換子區域機位 與 僅允許攝影機移動 並存）",
      "允許按子區域切換機位" in _grid and "僅允許攝影機移動" in _grid)
check("㉚ 五宮格模板已與總控 asset-spatial-ledger §四 雙向接線（母版 / 站位版 / 出圖順序）",
      "asset-spatial-ledger.md" in _grid and "母版" in _grid and "站位版" in _grid and "出圖順序" in _grid)

check("㉚ 立繪模板含 4 View + 五官 + Voice Description 兩檔（完整版不進圖 / 速覽標籤入圖）",
      "4 View" in _port and "五官" in _port and "Voice Description" in _port
      and "不進圖" in _port)
check("㉚ 立繪模板含「禁止持道具 / 禁止 pose」硬條",
      "手持" in _port and "pose" in _port and "禁止" in _port)
check("㉚ 道具模板含「純道具 + 禁止出現手/人物剪影」硬條",
      "純道具" in _prop and "手持" in _prop and "剪影" in _prop and "禁止" in _prop)
check("㉚ 強制讀取清單 P2 行：三份出圖模板由「按需」改「必讀」+ 點名九宮格 8 字段硬產出",
      "必讀 `sd-asset-engine/references/scene-grid-template.md`" in skill
      and "五宮格提示詞須含 8 字段" in skill
      and "按需 `sd-asset-engine/references/scene-grid-template.md`" not in skill)

# ㉛ 機檢 C 碼一致性：validate_prompt.py 實現的 C 系碼 ⊆ 機檢手冊登記的 C 系碼
_C_PAT = re.compile(r"\bC(?:4[0-9]|3[0-9]|2[0-9]|1[0-9]|[1-9])[a-z]?\b")  # 2026-10-14：擴至 C1~C39 及全字母子碼（含 C27x/C30a~d），徹底鎖死「腳本 ⊆ 手冊」；2026-10-24 P7 擴至 C40；P8 擴至 C41
_vp = read(vp)
_vp_codes = set(_C_PAT.findall(_vp))
_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
_mcm_codes = set(_C_PAT.findall(_mcm))
_miss_mcm = sorted(_vp_codes - _mcm_codes,
                   key=lambda x: (int(re.search(r"\d+", x).group()), x))
check("㉛ 機檢手冊登記了腳本實現的全部 C 系碼（腳本 ⊆ 手冊 · 防「腳本有、手冊無」）",
      not _miss_mcm, "手冊缺登記: " + ", ".join(_miss_mcm))
check("㉛ 手冊含「子檢查碼登記」表（V7.3.2 補登入口）",  # 域命名沿革：V7.3.2 引入，入口保留
      "子檢查碼登記" in _mcm and "C19a" in _mcm and "C20c" in _mcm and "C16d" in _mcm)
check("㉛ SKILL 機檢維度分組同步列出子碼清單（C19a~e / C20a~d 全名點名）",
      "C19a" in skill and "C19b" in skill and "C19c" in skill and "C19e" in skill
      and "C20c" in skill and "C18b" in skill)

# ------------------------------------------------- [E*22] 子碼計數口徑一致性域
# 動機（2026-10-13 整包體檢）：上一輪加 C26/C27 時只改了機檢手冊的計數（當時另有一份微核副本），
# 漏改 README / checklist / 打戲庫三處「子檢查碼共 59 條」，造成同一指標
# 跨文件數值打架（59 vs 64），而 check_package.py **沒有任何斷言覆蓋它**——
# 這是互鎖盲區：計數漂移無人管，直到人工體檢才發現。本域補上該斷言。
section("[E*22] 子碼計數口徑一致性域（防 59/64 漂移 · 2026-10-13 體檢補）")
_readme = read(os.path.join(BASE, "README.md"))
_checklist = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
_combat_guard = read(os.path.join(PKG, "sd-combat-engine", "references",
                                 "combat-rhythm-and-load-guardrails.md"))

# ---------------------------------------------------------------- 子碼計數唯一口徑
# ★2026-10-15 Agent 修復：原實現只查「自稱 68 條」這個字符串在不在，**不校驗加總**——
#   故 2026-10-14 把 C26 由 a~d 擴到 a~g 時只改了枚舉、忘改總數，造成
#   「自稱 68 / 自身枚舉加總 71 / 腳本實為 94」三方打架而零告警（[E*22] 建域時想防的正是這類事故）。
# 現口徑：手冊內 `SUBCODE-Registry` 機器可讀塊 = 唯一權威清單，三項斷言：
#   ① 塊內條數 == 手冊聲稱的總數（自洽）
#   ② 塊內集合 == 腳本出現的全部子碼集合（雙向 · 防「腳本有、清單無」）
#   ③ 塊內集合 == 手冊全文出現的子碼集合（雙向 · 防「登記了卻沒進清單」與幽靈碼）
# 改名/加碼時只需同步這**一個塊**，其餘計數落點全部引用本常量。
SUBCODE_TOTAL = 104
_SUB_PAT = re.compile(r"\bC\d{1,2}[a-z]\d?\b")
_reg_blk = re.search(r"SUBCODE-Registry:START.*?-->(.*?)<!--\s*SUBCODE-Registry:END",
                     _mcm, re.S)
_registry = _reg_blk.group(1).split() if _reg_blk else []
_reg_set = set(_registry)
_mcm_subs = set(_SUB_PAT.findall(_mcm))
_vp_subs = set(_SUB_PAT.findall(read(vp)))


def _expand_c_ranges(txt):
    """把 `C18a~n` / `C30i~l` 這類範圍寫法展開成子碼集合。

    總控 SKILL.md 用**範圍記賬**（`C18g~l`），逐字面查會漏判——必須先展開再比對，
    否則會出現「SKILL 明明已覆蓋 C18h~l，斷言卻說缺失」的假 FAIL。
    """
    out = set(_SUB_PAT.findall(txt))
    for m in re.finditer(r"C(\d{1,2})([a-z])\s*~\s*(?:C)?(\d{1,2})?([a-z])", txt):
        fam, a, fam2, b = m.groups()
        if fam2 and fam2 != fam:
            continue
        for o in range(ord(a), ord(b) + 1):
            out.add(f"C{fam}{chr(o)}")
    return out


_skill_subs = _expand_c_ranges(skill)
check("㉛ 總控 SKILL 子碼清單完整覆蓋 SUBCODE-Registry（防「手冊有、總控無」· 含範圍展開）",
      not (_reg_set - _skill_subs) and f"全 {SUBCODE_TOTAL} 條" in skill,
      f"總控缺: {sorted(_reg_set - _skill_subs)}")
check("㊾ 子碼計數唯一口徑：手冊 SUBCODE-Registry 塊存在，且塊內條數 == 聲稱總數（防「自稱 N、實為 M」）",
      bool(_registry) and len(_registry) == SUBCODE_TOTAL
      and f"{SUBCODE_TOTAL} 個子碼" in _mcm,
      f"註冊清單 {len(_registry)} 條 / 常量 {SUBCODE_TOTAL} 條"
      + ("（未找到 SUBCODE-Registry 塊）" if not _registry else ""))
check("㊾ 子碼註冊清單雙向完備：腳本集合 == 清單 == 手冊全文集合（防漏登與幽靈碼）",
      _vp_subs == _reg_set and _mcm_subs == _reg_set,
      f"腳本有清單無: {sorted(_vp_subs - _reg_set)} ｜ 清單有腳本無: {sorted(_reg_set - _vp_subs)} "
      f"｜ 手冊有清單無: {sorted(_mcm_subs - _reg_set)}")
check("㊾ 計數口徑單一來源：本文件內所有計數落點均引用 SUBCODE_TOTAL 常量（無寫死數字殘留）",
      ("68" + " 個子碼") not in read(__file__)
      and ("子檢查碼共 " + "68" + " 條") not in read(__file__))
check("㊾ 子碼計數無過時殘留：全包不得再出現「子檢查碼共 59 條」",
      "子檢查碼共 59 條" not in _readme
      and "子檢查碼共 59 條" not in _checklist
      and "子檢查碼共 59 條" not in _combat_guard
      and "子檢查碼共 59 條" not in _mcm)
check(f"㊾ 三處姊妹落點均聲明 {SUBCODE_TOTAL} 條（README / checklist / 打戲庫）",
      f"子檢查碼共 {SUBCODE_TOTAL} 條" in _readme
      and f"子檢查碼共 {SUBCODE_TOTAL} 條" in _checklist
      and f"子檢查碼共 {SUBCODE_TOTAL} 條" in _combat_guard)
# ★P7 新增：C40 病根檔案斷言（治「把病根寫錯，沿革錨點變偽證」）。
#   手冊裡已寫明「嚴禁寫錯 · check_package 有檔案校驗」——那就必須真的有這條校驗，
#   否則這句話本身又是一條永不生效的死規則（與 C40 治的病同構）。
_c40_doc_ok = (
    "原則層不缺" in _mcm
    and "blocking-direction.md` §4.2" in _mcm
    and "禁止一群人「齊動」（C25b）≠ 允許一群人「齊不動」" in _mcm
    and "不得把 C40 寫成全局默認" in _mcm
    and "條件觸發" in _mcm)
check("㊿ C40 病根檔案四要素在案（原則層不缺 / §4.2 已有背景行為 / 齊動≠齊不動 / 條件觸發）",
      _c40_doc_ok,
      "手冊 C40 條目的病根表述被改寫或刪除——群像行為層的病根檔案必須保持原樣，"
      "它是 P7 的沿革錨點；確需修改請同步 CHANGELOG 並更新本斷言")
check("㊾ 主碼口徑穩定：全包對外仍報 C1~C26（編號不重排）",
      "編號不重排" in skill and "C1~C26" in skill
      and "編號不重排" in _mcm)
check("㊾ 增量主碼 C26/C27 均在手冊 §二 門禁清單登記主碼行",
      re.search(r"^\| C26 \|", _mcm, re.M) is not None
      and re.search(r"^\| C27 \|", _mcm, re.M) is not None)
check("㊾ 手冊 §二 子碼登記表不含 C27a~d 重複行（C27 只以主碼行登記）",
      "| **C27a~d** |" not in _mcm)

# ------------------------------------------------- [E++++] 打戲護欄域
# 動機：外部包 huhe-combat-director V2.1 的「拉片實證層」有四項實測校正規則——
# 對抗激烈度硬護欄 / 特效手繪化鐵律 / 減速器配額 / 三層分層寫法。全包關鍵詞普查證實
# 本包此前**四項命中全為 0**；且 C1~C20 裡**沒有任何一項管「打戲到底打沒打起來」**。
# 本域把吸收結果變成真斷言，並把 C21 做成「引擎聲明 ↔ 腳本實現 ↔ 手冊登記」三處互鎖。
section("[E++++] V7.3.3 打戲護欄域（兩份新庫完整性 / C21 三處互鎖）")  # 域命名沿革：V7.3.3 引入，標識保留

_cb = sub_skill_path("sd-combat-engine")
_cib_p = os.path.join(_cb, "references", "combat-intensity-guardrails.md") if _cb else ""
_vrm_p = os.path.join(_cb, "references", "vfx-rendering-mandate.md") if _cb else ""
check("㉜ 兩份打戲新庫文件均存在（激烈度硬護欄 / 特效手繪化）",
      bool(_cb) and all(os.path.exists(x) for x in (_cib_p, _vrm_p)))
_cib = read(_cib_p)
_vrm = read(_vrm_p)

check("㉜ 護欄庫含六條硬護欄（位移接觸 / 構圖不許重複 / 貼身時長下限 / 禁擺拍 / 抽特效自檢 / 隔空對波定位）",
      all(k in _cib for k in ("每段必含", "相鄰兩段不許同構圖", "貼身對招佔比下限",
                              "禁止擺拍動詞", "抽掉特效", "隔空對波")))
check("㉜ 護欄庫含分層管理（自由組合區 / 硬護欄區）+【快】拍 ≥40% 下限",
      "自由組合區" in _cib and "硬護欄區" in _cib and "≥ 片長 40%" in _cib)
check("㉜ 護欄庫含減速器配額（黑白閃 / 定格幀 / 慢鏡 三檔片長上限）",
      "減速器配額" in _cib and "黑白閃" in _cib and "定格幀" in _cib and "慢鏡" in _cib)
check("㉜ 護欄庫含節奏零件六件 + 術語避撞聲明（勿與文戲「情緒節拍」混用）",
      all(k in _cib for k in ("蓄", "快", "停", "慢", "靜", "爆"))
      and "情緒節拍" in _cib and "勿與" in _cib)
check("㉜ 護欄庫聲明機檢載體 C21a~d（三處互鎖的「規則側」）",
      all(k in _cib for k in ("C21a", "C21b", "C21c", "C21d")))

check("㉜ 手繪化庫含五手法表 + 禁用孤立概念詞硬約束",
      all(k in _vrm for k in ("潑墨", "漫畫式平塗色塊", "手繪速度線", "墨線勾勒", "筆觸狀殘影"))
      and "禁用" in _vrm and "粒子" in _vrm)
check("㉜ 手繪化庫含三層分層寫法（外層 / 中層 / 內層 / 邊緣附著）",
      all(k in _vrm for k in ("外層", "中層", "內層", "邊緣附著")))
check("㉜ 手繪化庫含黑白閃三個必須詞 + 8K 口徑爭議備案（登記但不落地）",
      "三個必須詞" in _vrm and "8K" in _vrm and "爭議備案" in _vrm)

# C21 三處互鎖：三引擎聲明 ↔ validate_prompt.py 實現 ↔ 機檢手冊登記
check("㉜ 三處互鎖①：三份打戲引擎 SKILL 均聲明 C21（引擎側）",
      all("C21" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉜ 三處互鎖①：玄幻 / 真人兩引擎回指兩份新庫（跨引擎共用接線）",
      "combat-intensity-guardrails.md" in read(os.path.join(sub_skill_path("sd-xuanhuan-engine"), "SKILL.md"))
      and "vfx-rendering-mandate.md" in read(os.path.join(sub_skill_path("sd-xuanhuan-engine"), "SKILL.md"))
      and "combat-intensity-guardrails.md" in read(os.path.join(sub_skill_path("sd-real-engine"), "SKILL.md")))
check("㉜ 三處互鎖②：validate_prompt.py 實現 C21a~d + --combat 觸發門（腳本側）",
      all(k in _vp for k in ("C21a", "C21b", "C21c", "C21d"))
      and '"--combat"' in _vp and "COMBAT_SIGNAL_RE" in _vp
      and "_combat_on" in _vp and "_combat_ranges" in _vp)
check("㉜ 三處互鎖③：機檢手冊已登記 C21a~d（手冊側）",
      all(k in _mcm for k in ("C21a", "C21b", "C21c", "C21d")))
check("㉜ 總控 SKILL 聲明「激烈度門」與 --combat 參數",
      "C21" in skill and "--combat" in skill and "激烈度門" in skill)

# ------------------------------------------- [E++++] 節奏負載域（C22 四處互鎖 + 防迴歸）
section("[E++++] V7.3.4 節奏與渲染負載護欄域（新庫完整性 / C22 四處互鎖 / 接線防迴歸）")  # 域命名沿革：V7.3.4 引入，標識保留

_rlg_p = os.path.join(_cb, "references", "combat-rhythm-and-load-guardrails.md") if _cb else ""
check("㉝ 節奏負載護欄庫存在", bool(_cb) and os.path.exists(_rlg_p))
_rlg = read(_rlg_p)

check("㉝ 庫含獨立動作單元 IAU 定義 + 上限表（★上限型，補 C21 方向性缺口）",
      "獨立動作單元" in _rlg and "IAU" in _rlg and "上限" in _rlg)
check("㉝ 庫含 IAU 上限表分檔（≤2s/3s/4s/5s/≥6s）",
      all(k in _rlg for k in ("≤ 2s", "3s", "4s", "5s", "≥6s")))
check("㉝ 庫含鏡內速度四拍（起·爆·頓·收）+ 頓拍為最關鍵一拍",
      all(k in _rlg for k in ("起（慢）", "爆（快）", "頓（停）", "收（慢）"))
      and "最關鍵" in _rlg)
check("㉝ 庫含逐鏡判定口徑 + 禁用『全片總數≥鏡數』的反面教材",
      "逐鏡" in _rlg and "全片總數" in _rlg and "矇混過關" in _rlg)
check("㉝ 庫含結構標註剝離規則（只剝純標籤·不得連坐正文）",
      "純結構標註" in _rlg and "連坐" in _rlg)
check("㉝ 庫含全身景別下限 + 貼臉檔連續上限",
      "全身景別" in _rlg and "中全景" in _rlg and "貼臉檔" in _rlg)
check("㉝ 庫含四條病根檔案（V7.3.3 呆滯出片實證，勿刪 · 沿革錨點）",
      all(k in _rlg for k in ("病根①", "病根②", "病根③", "病根④")))
check("㉝ 庫聲明機檢載體 C22a~d（規則側）",
      all(k in _rlg for k in ("C22a", "C22b", "C22c", "C22d")))
check("㉝ 庫含『機檢 PASSED ≠ 出片好看』紀律 + 出片復盤義務",
      "PASSED" in _rlg and "出片復盤" in _rlg and "抽幀" in _rlg)

# ★防迴歸：病根①是「鐵律26 動作數上限沒進自檢閘口」，故斷言其必須已接線
_cil = read(os.path.join(_cb, "references", "combat-iron-laws.md"))
check("㉝ ★防迴歸：鐵律26 已補『V7.3.4 接線補閘』說明（病根① 的修復錨點 · 沿革錨點）",
      "接線補閘" in _cil and "A 引擎的硬約束在 B 鏈上整體失效" in _cil)
check("㉝ ★防迴歸：鐵律26 已聲明量化口徑改用 IAU 表 + 判罰以 C22 為準",
      "combat-rhythm-and-load-guardrails.md" in _cil and "判罰以 C22 為準" in _cil)

# C22 四處互鎖
check("㉝ 四處互鎖①：三份打戲引擎 SKILL 均聲明 C 碼口徑（引擎側 · V7.3.7 起為 C1~C26 · 沿革錨點）",
      all("C1~C26" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四處互鎖①：三引擎規則庫索引表均收錄新庫（路由入口，缺則庫白建）",
      all("combat-rhythm-and-load-guardrails.md" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四處互鎖①：三引擎第5步自檢閘口均含『六問』（寫作期接線）",
      all("六問" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四處互鎖②：validate_prompt.py 實現 C22a~d + 三個輔助函數（腳本側）",
      all(k in _vp for k in ("C22a", "C22b", "C22c", "C22d"))
      and all(k in _vp for k in ("COMBAT_IAU_RE", "_combat_iau", "_iau_limit",
                                 "_strip_struct_annot", "COMBAT_BEAT_RE")))
check("㉝ 四處互鎖②：IAU 計數含『抓住』人名容錯（構建期踩坑③的修復鎖）",
      "抓住" in _vp and "0,6" in _vp)
check("㉝ 四處互鎖②：C22 與 C21 共用 --combat 觸發門（未新增獨立參數）",
      "C21/C22" in _vp or "C22 打戲節奏" in _vp)
check("㉝ 四處互鎖③：機檢手冊已登記 C22a~d（手冊側）",
      all(k in _mcm for k in ("C22a", "C22b", "C22c", "C22d")))
check("㉝ 四處互鎖④：總控 SKILL 聲明節奏負載門 + C22",
      "C22" in skill and "combat-rhythm-and-load-guardrails.md" in skill)

# 方向性斷言：C21 與 C22 必須同時存在且分工寫明（防把上限型判據刪掉只剩下限型）
check("㉝ 方向性：C21 與 C22 分工寫明（C21 管激烈度下限 / C22 管負載上限）",
      "C21" in _rlg and "C22" in _rlg and "上限型" in _rlg and "不許過載" in _rlg)

# ---------------------------------------------------------------- [F] 外部版本保全
section("[F] 外部版本保全（版本統一不得誤傷外來來源）")

_all_text = "\n".join(read(p) for p in scan_md_files())
for v in EXTERNAL_VERS:
    check(f"外部產品版本 {v} 仍存在（未被統一誤改）", v in _all_text)

# ---- ㉝ 域加固：結構化定位斷言（對抗測試定位到 4 處『關鍵詞判讀過鬆』後新增）----
# 教訓：`關鍵詞 in 文件全文` 這種判讀無法定位到具體結構——同一關鍵詞在庫中多處出現，
# 或與正文引用共用，拆掉一處斷言照樣通過。對抗測試實測 4/8 漏網，全部由此造成。
# 正法：按結構定位（表格行 / 標題行 / 函數調用），拆一處即倒。
def _row_has(text, key, must):
    """存在同時含 key 與 must 的表格行（以 '|' 開頭）。"""
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln.startswith("|") and key in ln and must in ln:
            return True
    return False


def _head_has(text, key, must):
    """存在同時含 key 與 must 的標題行（# / ## / ###）。"""
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln.startswith("#") and key in ln and must in ln:
            return True
    return False


def _in_warns_append(text, code):
    """code 是否真的出現在 warns.append(...) 的調用參數裡（而非註釋/文檔頭）。"""
    for m in re.finditer(r"warns\.append\((?:[^()]|\([^()]*\))*\)", text, re.S):
        if code in m.group(0):
            return True
    return False


def _warns_text(text, code):
    """取出該 code 所在的 warns.append(...) 調用全文。"""
    for m in re.finditer(r"warns\.append\((?:[^()]|\([^()]*\))*\)", text, re.S):
        if code in m.group(0):
            return m.group(0)
    return ""


check("㉝ 加固②：C22 機檢表逐行標註方向性（C22a/C22b 須為『上限型』）",
      _row_has(_rlg, "**C22a**", "上限型") and _row_has(_rlg, "**C22b**", "上限型"))
check("㉝ 加固③：§2.2 節標題須為『逐鏡判定』且顯式禁『全片總數』口徑",
      _head_has(_rlg, "2.2", "逐鏡") and "全片總數" in _rlg)
check("㉝ 加固⑥：三引擎規則庫索引表均含新庫表格行（區別於正文引用）",
      all(_row_has(read(os.path.join(sub_skill_path(n), "SKILL.md")),
                   "combat-rhythm-and-load-guardrails.md", "|")
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 加固⑦：C22a~d 均真實落在 warns.append 調用中（不是隻寫在註釋裡）",
      all(_in_warns_append(_vp, c) for c in ("C22a", "C22b", "C22c", "C22d")))
# 方向性落到告警措辭：上限型判據必須在文案裡對作者明說「上限」與超了什麼
check("㉝ 加固⑦：C22a/C22b 告警文案須含『上限』語義（方向性落到措辭）",
      "上限" in _warns_text(_vp, "C22a") and "上限" not in _warns_text(_vp, "C22c"))

# ------------------------------------------------- [E*5] 畫風鎖域
# 動機：期間徐克版 10 秒實拍復盤證明畫風參數組有效（5/5 項量化通過），
# 把「選導演風格」收編為三件套：I 鎖 + style-bible 知識庫 + C23 機檢。
# 本域做真斷言：知識庫完整性 / 引擎在位 / C23 三處互鎖 / 接線防迴歸。
section("[E*5] V7.3.5 畫風鎖域（style-bible 完整性 / C23 三處互鎖 / 接線防迴歸）")  # 域命名沿革：標識保留

_sb_dir = os.path.join(BASE, "references", "style-bible")
_sb_files = ("style-lock-protocol.md", "style-archetype-taxonomy.md",
             "director-style-catalog-74.md", "style-fit-and-combat-matrix.md",
             "director-to-prompt-protocol.md", "director-param-library.md",
             "style-prefix-blocks.md", "style-bible-spec.md")
_missing_sb = [f for f in _sb_files if not os.path.isfile(os.path.join(_sb_dir, f))]
check("㉞ style-bible 知識庫 8 份齊備（鎖規程/六原型/74組/適配矩陣/植入規程/參數源/成品塊/交付規範）",
      not _missing_sb, "缺: " + ", ".join(_missing_sb))

_ex_dir = os.path.join(_sb_dir, "examples")
# P14：案例示例整體剔除 —— 反向斷言，示例目錄不得再出現（防「刪了又悄悄加回來」）
check("㉞ 案例示例已剔除：style-bible/examples 目錄不得存在",
      not os.path.exists(_ex_dir),
      "示例目錄仍在：" + _ex_dir)

_missing_sl = [f for f in ("style-lock-ladder.py", "style-lock-recommend.py")
               if not os.path.isfile(os.path.join(BASE, "scripts", f))]
check("㉞ 畫風鎖引擎腳本 2 份在位（ladder / recommend）", not _missing_sl, "缺: " + ", ".join(_missing_sl))

check("㉞ 編號裁定在案：style-lock-protocol.md 註明「方案通稱 F 鎖 = 包內 I 鎖」口徑",
      os.path.isfile(os.path.join(_sb_dir, "style-lock-protocol.md"))
      and "F 鎖" in read(os.path.join(_sb_dir, "style-lock-protocol.md")))

# C23 三處互鎖：腳本實現 ↔ 手冊登記 ↔ 總控觸發門口徑
check("㉞ C23 實現：validate_prompt.py 含 C23a/b/d1/d2/e/f 判據",
      all(c in _vp for c in ("C23a", "C23b", "C23d1", "C23d2", "C23e", "C23f")))
check("㉞ C23 登記：機檢手冊含 C23a~f 全套子碼（C23 七子碼逐條登記）",
      all(c in _mcm for c in ("C23a", "C23b", "C23c", "C23d1", "C23d2", "C23e", "C23f")))
check("㉞ C23 口徑：總控 SKILL.md 含 I 鎖節與 --c23 觸發門",
      "畫風鎖" in skill and "--c23" in skill and "I · 畫風鎖" in skill)
check("㉞ C23 接線：sd-feed-engine 含畫風鎖契約、sd-asset-engine 鎖系統含 I 鎖",
      "畫風鎖契約" in read(os.path.join(sub_skill_path("sd-feed-engine"), "SKILL.md"))
      and "I·畫風鎖" in read(os.path.join(sub_skill_path("sd-asset-engine"), "SKILL.md")))
check("㉞ C23 真實落在機檢輸出中（issues.extend(_c23_iss)，不是隻寫在註釋裡）",
      "issues.extend(_c23_iss)" in _vp)

# [E*6] 禁項單點紀律域：C24 實現 ↔ 手冊登記 ↔ C7 前置等價
section("[E*6] V7.3.6 禁項單點紀律域（C24a/b 實現 / 登記 / C7 聯動 / 自測在案）")  # 域命名沿革：標識保留
check("㉟ C24 實現：validate_prompt.py 含 C24a/C24b 判據與前置變體正則（逐段化 · 2026-10-10）",
      all(c in _vp for c in ("C24a", "C24b", "BAN_FRONT_TAG", "_ban_count", "_pre_n", "_seg_ban"))
      and "_dups" in _vp)
check("㉟ C24 登記：機檢手冊含 C24a/b（子碼計數口徑 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C24a", "C24b")) and f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㉟ C24 聯動：C7 段7 可由前置變體等價滿足（腳本與手冊雙側在案）",
      "BAN_FRONT_TAG.search(text)" in _vp and "等價滿足" in _mcm)
check("㉟ C24 自測：validate_prompt.py 含 C24 五組用例（合規段7/前置等價/雙寫/補充變體/缺失）",
      all(c in _vp for c in ("前置禁項塊應等價滿足", "禁項雙寫應報 C24a",
                             "禁項補充塊應報 C24a", "無禁項塊應報 C24b")))


# [E*7] 域（打戲/武學規則域遷出總控 + 零斷鏈）
section("[E*7] V7.3.7 去遺留域（9 份遺留件已刪 / 入鏈點已改 / 新引擎專檔在案）")  # 域命名沿革：標識保留
_LEGACY_GONE = [
    "action-cinematography-breakdown.md", "action-previs-15grid.md", "action-ultimate-finisher.md",
    "authentic-martial-taxonomy.md", "combat-direction-engine.md", "combat-rhythm-defense3state.md",
    "martial-arts-arsenal.md", "martial-arts-combat-library.md", "xuanhuan-magic-combat.md",
]
_still = [f for f in _LEGACY_GONE if os.path.exists(os.path.join(refs_dir, f))]
check("㊱ 9 份歷史遺留打鬥/武學文件已從總控 references 刪除", not _still,
      "仍存在: " + ", ".join(_still))
check("㊱ 遷出內容新專檔存在（sd-combat-engine/references/tier-and-finisher-system.md）",
      os.path.exists(os.path.join(PKG, "sd-combat-engine", "references", "tier-and-finisher-system.md")))
_tfs = read(os.path.join(PKG, "sd-combat-engine", "references", "tier-and-finisher-system.md"))
check("㊱ 新專檔承載三檔定檔表 + 大招終結技體系（遷入內容完整）",
      all(k in _tfs for k in ("R1 寫實剋制", "R2 商業高燃", "R3 玄幻大招",
                              "視覺巔峰", "終結技三幕", "模式 A ~ K", "特效生長三段論", "急停彈射")))
_dangling = []
for _p in (os.path.join(BASE, "SKILL.md"), os.path.join(BASE, "README.md"),
           os.path.join(refs_dir, "aspect-ratio-adaptation.md"),
           os.path.join(refs_dir, "blocking-direction.md"),
           os.path.join(refs_dir, "camera-specs-15rules.md"),
           os.path.join(refs_dir, "seedance-render-engine.md"),
           os.path.join(refs_dir, "asset-first-pipeline.md"),
           os.path.join(refs_dir, "prompt-feeding-checklist.md"),
           os.path.join(PKG, "sd-xuanhuan-engine", "SKILL.md"),
           os.path.join(PKG, "sd-real-engine", "SKILL.md"),
           os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md")):
    _s = read(_p)
    for _f in _LEGACY_GONE:
        if _f[:-3] in _s:
            _dangling.append(f"{os.path.basename(_p)}→{_f}")
check("㊱ 去遺留後零斷鏈（總控/子技能兩側入鏈點均已改指）", not _dangling,
      "殘留: " + "; ".join(_dangling))
check("㊱ 計數口徑同步（SKILL 聲明 == EXPECTED_REFS · 元規則四）",
      "45 份" not in skill and "36 份" not in skill and "37 份" not in skill
      and "38 份" not in skill and f"{EXPECTED_REFS} 份規則庫" in skill and EXPECTED_REFS == 53)
check("㊲ M1 出圖提示詞配套紀律（asset-delivery-modes §4.4 · 2026-10-09 用戶實測退回）",
      "出圖提示詞配套紀律" in _ade and "全套 P2.5 出圖提示詞" in _ade
      and "character-portrait-templates.md" in _ade and "scene-grid-template.md" in _ade
      and "prop-template.md" in _ade)
_pdg = read(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
check("㊲ 劇情分鏡格（推演宮格）條件必出（plot-deduction-grid §四 · V4.0 迴歸）",
      "條件必出" in _pdg and "人物一致性試金石" in _pdg
      and "豁免" in _pdg and "禁止靜默跳過" in _pdg
      and "條件必出" in skill)
check("㊱ 新引擎索引已掛專檔（sd-combat-engine SKILL 索引表含 tier-and-finisher-system）",
      "tier-and-finisher-system.md" in read(os.path.join(PKG, "sd-combat-engine", "SKILL.md")))

# ------------------------------------------------- [E*9] V7.3.9 字數口徑統一域（域命名沿革）
# 動機（外部審計 P0「規則與腳本口徑統一」）：舊註釋曾把篇級兜底寫成「單段 ≤N 字符」、實現按整份文件判；
#   且與 gate_check.py 的段級口徑關係從未寫明。本域鎖住「粒度 + 權威腳本」的聲明，防單邊漂移。
#   2026-11-03 P13：段級整檔上移 1000（2.0 → 2900/3000 · 2.5 → 3600/4000），篇級兜底按「段級最高硬上限 × 1.5」同步到 6000。
section("[E*9] V7.3.9 字數口徑統一域（C4 篇級 6000 與閘門3 段級 2900/3000 · 3600/4000 的粒度聲明）")  # 域命名沿革：標識保留
_vp_txt = read(vp)
_mcm_c4 = [l for l in _mcm.splitlines() if l.startswith("| C4 |")]
check("㊲ 機檢手冊 C4 行標明「單文件」篇級口徑 + 指向 gate_check 段級判定",
      bool(_mcm_c4) and "單文件" in _mcm_c4[0] and "6000" in _mcm_c4[0] and "gate_check" in _mcm_c4[0])
check("㊲ validate_prompt 的 C4 註釋與常量同步指向 gate_check 段級判定（口徑雙寫）",
      "MAX_CHARS = 6000" in _vp_txt and "gate_check" in _vp_txt)

# ------------------------------------------------- [E*10] V7.4.8 外部增量與版本清洗病句修復域（域命名沿革）
# 動機：① 版本註記清洗中「動態詞表內的動詞」會與版本號被一併吃掉，留下「已於進 / 已於 按」類殘句
#       ——此前的截斷掃描只按「格式」寫模式，漏了「刪除動作的語義後果」這一類。
#       ② 本版吸收外部包的照明（色溫對沖 / 氣氛介質）與運鏡（8 套單技法）增量，須鎖住防回退。
section("[E*10] V7.4.8 外部增量與版本清洗病句修復域")  # 域命名沿革：標識保留
_e10_seglink = read(os.path.join(PKG, "sd-storyboard-engine", "references", "segment-linkage.md"))
_e10_segcont = read(os.path.join(PKG, "sd-feed-engine", "references", "segment-continuity-strategy.md"))
_e10_light = read(os.path.join(PKG, "short-drama-director", "references", "lighting-and-antifake.md"))
_e10_camsys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_e10_madapt = read(os.path.join(PKG, "short-drama-director", "references", "model-adapters.md"))
check("㊳ 版本清洗殘句已清零（「已於進」/「已於 按此法」類不存在）", not ("已於進" in _e10_seglink or "已於進" in _e10_segcont or "已於 按此法" in _e10_seglink))
check("㊳ 照明體系含「雙色溫冷暖對沖」與「空間物理介質」兩節（外部增量已吸收）", "雙色溫冷暖對沖" in _e10_light and "空間物理介質" in _e10_light)
check("㊳ 高光運鏡含 8 套單技法鏡行參考寫法", "單技法鏡行參考寫法" in _e10_camsys and "Dolly Zoom" in _e10_camsys and "Speed Ramping" in _e10_camsys)
check("㊳ 長對白 OTS 拓撲已併入 model-adapters §5.0.1（與 C17b 同缺口的兩面）", "長對白過肩（OTS）雙人在場拓撲" in _e10_madapt)
check("㊳ 機檢 C17b 已實現（長對白段關係鏡缺失告警）", "C17b" in _vp_txt)

# ------------------------------------------------- [E*11] 表演指導層域（C25 三處互鎖）
# 動機：2026-10-09 接入粉絲投稿的 ACTING SKILL —— 它補的是本包此前的空白「行為與動機層」
#       （包裡原有 FACS 微表情層 + 神態紀律層，但無人管目標/障礙/戰術/節拍/潛台詞/聽與反應）。
#       接入紀律：規則文件必須真實存在、SKILL/README 必須掛路由、C25 必須三處互鎖（腳本 ↔ 手冊 ↔ 規則域）。
section("[E*11] 表演指導層域（acting-direction 新建 · C25 三處互鎖 · 與 C11 反轉同批）")
_e11_acting = os.path.join(refs_dir, "acting-direction.md")
check("㊴ 表演指導層文件存在（references/acting-direction.md）", os.path.isfile(_e11_acting))
_e11_at = read(_e11_acting) if os.path.isfile(_e11_acting) else ""
check("㊴ 表演指導層含五支柱（目標 / 障礙與代價 / 戰術 / 節拍 / 潛台詞）",
      all(w in _e11_at for w in ("目標", "障礙與代價", "戰術", "節拍", "潛台詞")))
check("㊴ 表演指導層含核心公理與兩條招牌律（壓力下的行為 / 兩個真相律 / 然而當 X）",
      "壓力下的行為" in _e11_at and "兩個真相" in _e11_at and "然而，當" in _e11_at)
check("㊴ 表演指導層含四層分工表與三環節落點表（與 FACS / 神態紀律正交聲明）",
      "神態紀律層" in _e11_at and "行為與動機層" in _e11_at and "落點表" in _e11_at)
check("㊴ 表演指導層標註未實拍驗證紀律（【待驗證·未實拍】）", "待驗證" in _e11_at)
check("㊴ SKILL.md 索引樹已掛 acting-direction（★表演指導層）",
      "★ acting-direction.md" in skill)
check("㊴ SKILL.md 唯一權威歸屬表含「表演（行為與動機層）」域行",
      "行為與動機層" in skill and "acting-direction.md`**" in skill)
check("㊴ README 規則域表已掛錶演·行為行",
      "表演·行為" in readme and "acting-direction" in readme)
check("㊴ C25 互鎖①：validate_prompt.py 實現 C25a/C25b",
      all(c in _vp_txt for c in ("C25a", "C25b", "C25_BLAND_FACE", "C25_SYNC_CROWD")))
check("㊴ C25 互鎖②：機檢手冊已登記 C25a/C25b（子碼計數口徑 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C25a", "C25b")) and f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㊴ C25 互鎖③：機檢手冊 C1~C26 門禁清單含「表演層」小節並指向 acting-direction.md",
      "### 表演層" in _mcm and "acting-direction.md" in _mcm)
check("㊴ C25 真實落在機檢輸出中（warns.append(f\"C25a…\")）",
      'warns.append(f"C25a' in _vp_txt and 'warns.append(f"C25b' in _vp_txt)

# ------------------------------------------------- [E*14] 錨點繼承域（C26 · 2026-10-12 新增）
# 動機：粉絲群實測反饋「劇本大綱明確了 2035 年南京…出來的是 80 年代的破街爛車，人物也搞得像協警」
#       「人物年齡、人物身材比例都卡不到」——世界錨與人物錨此前只寫在散文裡，沒落紙也沒有會響的檢查。
#       本域鎖死「劇本層規則源 ↔ 資產層規則源 ↔ 腳本實現 ↔ 手冊登記 ↔ 自檢用例 ↔ 總控分組」六處一致。
section("[E*14] 錨點繼承域（C26a~d 六處互鎖 · 世界錨/人物錨/因果表）")
_sbip = read(os.path.join(PKG, "sd-script-engine", "references", "story-bible-and-ip.md"))
_epp = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_ssp = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
check("㊼ 互鎖①：validate_prompt.py 實現 C26a~d + 四個錨點常量表",
      all(c in _vp_txt for c in ("C26a", "C26b", "C26c", "C26d",
                                 "C26_ERA_ANCHOR", "C26_AGE_ANCHOR", "C26_LOOK_ANCHOR",
                                 "C26_OLD_ELEMS", "C26_MODERN_ELEMS")))
check("㊼ 互鎖②：機檢手冊已登記 C26a~d（子碼計數口徑 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C26a", "C26b", "C26c", "C26d")) and f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㊼ 互鎖③：總控 SKILL 機檢維度分組含「錨點繼承門」行且範圍口徑已同步 C26a~g",
      "錨點繼承門" in skill and "C26a~g" in skill)
check("㊼ 互鎖④：劇本層規則源在案（《世界錨卡》+《人物錨卡》+ 七/四鐵律 + HANDOFF 交接）",
      "世界錨卡" in _sbip and "人物錨卡" in _sbip and "七條鐵律" in _sbip
      and "WORLD_ANCHOR_CARD" in _sbip and "HANDOFF_CARD" in _sbip)
check("㊼ 互鎖⑤：劇本層《因果與關係表》+ 情節點密度下限在案（治「沒有人情世故」「劇情跳太快」）",
      all(k in _epp for k in ("因果與關係表", "CAUSALITY_AND_RELATION_TABLE", "人情世故",
                              "情節點密度", "理所當然禁令")))
check("㊼ 互鎖⑥：階段③④ 強制產出已接線（缺任一張 = 階段未完成）",
      "世界錨卡" in _ssp and "人物錨卡" in _ssp and "因果與關係表" in _ssp)
check("㊼ 互鎖⑦：資產層落紙（場景年代錨 §四·E + 立繪身份外觀三件套 + 資產板人物錨）",
      "年代錨 ERA_ANCHOR" in asl and "身份外觀三件套" in asl and "身份外觀三件套" in _cpt
      and "反漂移清單" in _cpt)
check("㊼ 互鎖⑧：自檢含 C26 四組迴歸用例 + 結構定位（真實落在 warns.append）",
      all(c in _vp_txt for c in ("缺世界錨應報 C26a", "年代錨與正文物證衝突應報 C26b",
                                 "缺年齡錨應報 C26c", "缺身份可渲染外觀應報 C26d"))
      and all(_in_warns_append(_vp, c) for c in ("C26a", "C26c", "C26d")))

# ------------------------------------------------- [E*13] 融合規則補載體域（2026-10-10）
# 動機：本包 2026-10-10 從外部包融合 11 條規則，其中可機檢的 6 項此前**零執行載體**——
#       "規則寫在散文細則裡、生成時根本不生效"，只能靠事後人眼發現（正是"越加越不滿意"的病根）。
#       本域鎖死「規則源文件 ↔ 腳本實現 ↔ 手冊登記 ↔ 子碼計數 ↔ 自檢用例」五處一致，
#       防再次出現"寫了規則、卻沒有會響的檢查"。
section("[E*13] 融合規則補載體域（C11b/C12b/C17c/C18f/C20e/C25c 五處互鎖）")
_cam_sys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_shot_act = read(os.path.join(PKG, "sd-storyboard-engine", "references", "shot-economy-and-acting.md"))
_seg_spl = read(os.path.join(BASE, "references", "segment-splicing.md"))
_qgr = read(os.path.join(BASE, "references", "quality-gate-review.md"))
check("㊷ 互鎖①：validate_prompt.py 實現六個新子碼",
      all(c in _vp_txt for c in ("C11b", "C12b", "C17c", "C18f", "C20e", "C25c")))
check("㊷ 互鎖②：機檢手冊已登記六個新子碼",
      all(c in _mcm for c in ("C11b", "C12b", "C17c", "C18f", "C20e", "C25c")))
check("㊷ 互鎖③：子碼計數與手冊登記一致（防登記表與計數漂移）",
      f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㊷ 互鎖④：自檢含六個新子碼的迴歸用例",
      all(c in _vp_txt for c in ('startswith("C11b")', 'startswith("C12b")', 'startswith("C17c")',
                                 'startswith("C18f")', 'startswith("C20e")', 'startswith("C25c")')))
check("㊷ 互鎖⑤：規則源文件在案（景別幅度/過肩幾何/假表演/背景錨點/跨項目汙染）",
      "景別與表演幅度綁定" in _cam_sys and "過肩鏡頭幾何" in _cam_sys
      and "假表演規避" in _shot_act
      and "背景錨點鎖" in _seg_spl
      and "跨項目汙染" in _qgr)

# ------------------------------------------------- [E*14] 六維審計補載體域（2026-10-10）
# 動機：用戶六維審計（① 前置強制鎖 A/B/D ② 段落銜接形式 ③ 出圖執行到位 ④ 運鏡技法
#       ⑤ 人物遺漏 ⑥ 站位接續）暴露兩類根因——
#   ① **機檢的「單段假設」**：C1/C2/C3/C4/C17/C24 此前只讀文件第一段，而真實交付稿是
#      「提示詞組 × N 組」（3 分鐘劇 ≈14 段，每段從 00:00 起、≤15s）。後果是合規多段稿
#      **全線誤報**（C2 鏡頭數/ C4 字符/ C24 禁項），且**第 2 段起的人物遺漏抓不到**——
#      正是用戶反覆反饋的「A 和 B 說話，B 在下一個鏡頭就不見了」的結構性盲區。
#   ② **「有規則、零機檢」**：運鏡技法（camera-system §四）、畫幅一致性、跨段站位漂移
#      此前只有散文規則、沒有會響的檢查。
# 紀律：**逐段化 + 新門 = 腳本實現 ↔ 手冊登記 ↔ 子碼計數 ↔ 自檢用例** 四處必須一致。
section("[E*14] 六維審計補載體域（C6b/C17d/C18g~l 逐段化 + 運鏡門 · 八處互鎖）")
check("㊸ 互鎖①：validate_prompt.py 實現八處新子碼（C6b / C17d / C18g~l）",
      all(c in _vp_txt for c in ("C6b", "C17d", "C18g", "C18h", "C18i", "C18j", "C18k", "C18l")))
check("㊸ 互鎖②：機檢手冊已登記八處新子碼",
      all(c in _mcm for c in ("C6b", "C17d", "C18g", "C18h", "C18i", "C18j", "C18k", "C18l")))
check("㊸ 互鎖③：逐段化已落到 C1/C2/C3/C4/C17/C24（防「單段假設」回退）",
      "_split_segments" in _vp_txt and "_segments_time" in _vp_txt and "seg_zw" in _vp_txt
      and "_feed_body" in _vp_txt)
check("㊸ 互鎖④：自檢含八處新子碼的迴歸用例（含多段稿逐段自查用例）",
      all(c in _vp_txt for c in ('startswith("C6b")', 'startswith("C17d")', 'startswith("C18g")',
                                 'startswith("C18h")', 'startswith("C18i")'))
      and "_t_multi" in _vp_txt)
check("㊸ 互鎖⑤：運鏡門規則權威在案（§四 逐鏡必標運鏡 / 固定鏡 10% 上限 / 重技法頻率上限）",
      "每個鏡頭必須標註運鏡方式" in _cam_sys and "重技法頻率上限" in _cam_sys
      and "滑動變焦" in _cam_sys)
check("㊸ 互鎖⑥：手冊 C6/C17/C18 正文行同步掛上 b/d/g~l 子碼（防「表裡有、正文無」）",
      "**b** 畫幅自相矛盾" in _mcm and "**d** 跨段站位漂移" in _mcm
      and "**g** 鏡行未標註運鏡" in _mcm and "**l** 重技法名額超限" in _mcm)

# ------------------------------------------------- [E*17] 出稿口徑實測修訂域（2026-10-12 用戶實測 · 三改五互鎖）
# 動機：段1《遺囑頭七對峙》+ 段2《頭七堂屋爭房產》兩段實拍復盤，用戶三條實測裁定：
#   ① 運鏡：原「對話段落不得全程固定」→ 四鏡全微運鏡，模型把控不住，人物站位/朝向在鏡內持續漂移
#      （用戶原話「一段有兩個這種就夠了，剩下的應該是要固定在那聊天」）→ 文戲改「固定為主 · 運鏡 ≤2 個/段」
#   ② 視線：站位聲明只寫身體朝向、不寫視線落點 → 三人同鏡眼神全部跑偏
#      （用戶原話「三個人以上基本上就是亂了」）→ 站位聲明必寫「視線落點」
#   ③ 段8/段9：約 290 字符固定稅、實測沒大用 → 未選導演卡時默認不寫，美學 ≤15 字併入【畫幅風格】
section("[E*17] 出稿口徑實測修訂域（2026-10-12 用戶實測 · 三改五互鎖）")

_main_skill = skill
_feed_skill = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("㊽ 互鎖①：運鏡規則已分文戲/打戲檔（2026-10-14 廢除15s運鏡≤2死名額 · 動靜隨劇情自然發生）",
      "★ 運鏡分檔（2026-10-12 用戶實測修訂 · 文戲 / 打戲分治" in _cam_sys
      and "動靜隨劇情自然發生" in _cam_sys and "打戲 / 動作段" in _cam_sys)
check("㊽ 互鎖②：舊口徑「對話段落不得全程固定」已降級為廢止說明（不得仍處生效位）",
      "已隨本次修訂廢止" in _cam_sys and "文戲 / 對話段不適用本條" in _cam_sys)
check("㊽ 互鎖③：總控法則21④ 視線指派已擴寫為「單鏡 ≥2 人必寫視線落點」",
      "視線指派（★ 2026-10-12 擴寫 · 多人同鏡硬項）" in _main_skill
      and "視線落點：看向 @某人" in _main_skill)
check("㊽ 互鎖④：投餵引擎畫風鎖契約已改「常規稿不寫段8/段9 · 美學 ≤15/30 字併入畫幅風格」",
      "常規稿不寫段8/段9" in _feed_skill
      and any(x in _feed_skill for x in ("美學短語（≤30 字", "美學短語（≤15 字"))
      and "併入【畫幅風格】" in _feed_skill)
check("㊽ 互鎖⑤：總控 I 鎖段同步登記該路徑變更（且保留選卡時仍寫段8/9）",
      "2026-10-12 用戶實測修訂（路徑變更）" in _main_skill
      and "僅當用戶明確選定導演卡時才落段8/段9" in _main_skill)
# ★ 2026-10-13 措辭同步：C/I 鎖升格為強制鎖（域 [E*25]）時，段8/段9 觸發條件由
#   「未選導演卡」精確化為「用戶回『按你的推薦走』/ 未指定具體導演卡」，且「默認路徑」改稱「路徑」。
#   本節互鎖④⑤ 的檢查串已隨之同步，語義未變。

# ------------------------------------------------- [E*18] 粉絲實測修復域（2026-10-13 · 四改八互鎖）
# 動機：V7.4 粉絲實測反饋四條（沿革記錄）——
#   ① 結尾強行定格與台詞衝突（人在說話畫面凍住）→ 末鏡台詞預算 = 鏡長 − 1s、末 1 秒禁台詞
#   ② 2.5 模型出視頻但字數仍限 2000 → 閘門3 按模型分檔（2026-11-03 起 2.0: 2900/3000 · 2.5: 3600/4000）
#   ③ 強制禁止項太多 → 段7 極簡化為四項（禁字幕/水印/Logo/背景音樂/旁白），長清單按 C19 理論本就有害
#   ④ 資產提示詞混入編號/自檢/延續備註 + 局部特寫帶表格文字 + 缺頭身比 → 提示詞正文純淨四條
section("[E*18] 粉絲實測修復域（2026-10-13 · 四改八互鎖）")

_splic = read(os.path.join(BASE, "references", "segment-splicing.md"))
_fmg = read(os.path.join(PKG, "sd-feed-engine", "references", "feed-mode-and-gates.md"))
_gck = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
_mads = read(os.path.join(BASE, "references", "model-adapters.md"))
_e18_asa = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
check("㊾ 互鎖①：末鏡台詞靜默預算在案（預算 = 鏡長 − 1s · 末 1 秒禁台詞 · 三個解法）",
      "末鏡台詞靜默預算" in _splic and "末 1 秒（硬定格區）禁台詞" in _splic
      and "末鏡台詞字數預算 = (鏡長 − 1 − 標點停頓) × 語速檔" in _splic)
check("㊾ 互鎖②：閘門3 已按模型分檔（文檔 + gate_check.py 實現兩側）",
      "2.5 → **3600/4000**" in _fmg and "w_soft, w_hard = (3600, 4000) if a.model == '2.5'" in _gck)
# 用行為迴歸替代已廢止的局部變量源碼指紋，不降低定格扣時與累計對白要求。
# ★2026-10-23 體檢修：舊版只跑 test_budget_and_freeze 單個方法，test_scopes / test_render_parity
#   自 P2 改 feed-only 契約後長期紅燈（夾具沒帶「資產另冊」聲明）卻無人知曉——包檢只按方法名跑，
#   等於給迴歸測試開了後門。現改為**跑整個測試文件**，並補另兩份測試套件。
def _run_tests(rel_path, *methods):
    _p = os.path.join(BASE, "scripts", rel_path)
    if not os.path.isfile(_p):
        return None
    _args = [sys.executable, '-m', 'unittest', 'discover', '-s', os.path.dirname(_p), '-p', os.path.basename(_p)]
    return subprocess.run(_args, cwd=os.path.dirname(_p), capture_output=True, text=True,
                          encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})


_stability = _run_tests("test_validator_stability.py")
check("㊾ 互鎖③：累計對白預算、顯式定格扣時與否定定格行為迴歸（整份測試文件 · 不再只跑單方法）",
      _stability is not None and _stability.returncode == 0,
      (_stability.stdout + _stability.stderr) if _stability else "測試文件缺失")
_slice_stab = _run_tests("test_slice_stability.py")
check("㊾ 互鎖③b：切片上下文穩定性迴歸（整份測試文件）",
      _slice_stab is not None and _slice_stab.returncode == 0,
      (_slice_stab.stdout + _slice_stab.stderr) if _slice_stab else "測試文件缺失")
_bundle_stab = _run_tests("test_project_bundle.py")
check("㊾ 互鎖③c：項目包校驗/導出行為迴歸（整份測試文件）",
      _bundle_stab is not None and _bundle_stab.returncode == 0,
      (_bundle_stab.stdout + _bundle_stab.stderr) if _bundle_stab else "測試文件缺失")
check("㊾ 互鎖④：段7 禁項極簡四項（權威模板 + 長清單禁加理由）",
      "【強制禁止項】畫面：禁字幕、禁水印（含 Logo）；音頻：禁背景音樂、禁旁白。" in _mads
      and "禁項極簡（2026-10-13 粉絲實測修訂 · 默認只寫四項）" in _mads)
check("㊾ 互鎖⑤：資產提示詞正文純淨四條（編號/自檢延續備註/表格排版/頭身比）",
      "提示詞正文純淨（2026-10-13 粉絲實測修訂）" in _e18_asa
      and "人物提示詞主動寫頭身比" in _e18_asa)

# 三條同源推廣斷言（2026-10-13 收口）：粉絲反饋不只在權威文件落地，示範稿/模板/姊妹落點須同步
# P14：案例示例（storyboard-example.md）已整體剔除，本條收窄為「權威 + 姊妹規範」兩處，不再查示例稿
_e18_ra = read(os.path.join(PKG, "sd-real-engine", "references", "render-adapters.md"))
_e18_sre = read(os.path.join(refs_dir, "seedance-render-engine.md"))
check("㊾ 互鎖⑥：兩處規範段7 同步極簡（舊長清單「禁止角色變形」類串已清零）",
      "禁止角色變形" not in _e18_ra
      and "禁止角色變形" not in _e18_sre
      and "畫面：禁字幕、禁水印（含 Logo）；" in _e18_ra
      and "畫面：禁字幕、禁水印（含 Logo）；" in _e18_sre)
_e18_fsk = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
_e18_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
_e18_sat = read(os.path.join(PKG, "sd-qc-engine", "references", "stage-acceptance-table.md"))
_e18_act = read(os.path.join(refs_dir, "acting-direction.md"))
check("㊾ 互鎖⑦：字數分檔四處姊妹落點同步（feed SKILL / 機檢手冊 C4 / 驗收表 / 表演文檔）",
      all("2.5 ≤3600" in x for x in (_e18_fsk, _e18_mcm, _e18_sat, _e18_act)))
_e18_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
check("㊾ 互鎖⑧：正文純淨推廣到模板骨架（人物骨架主動寫頭身比 · 2026-10-13 粉絲反饋）",
      "主動寫頭身比是防「頭大身小」的第一道鎖" in _e18_cpt)

# ------------------------------------------------- [E*19] 段縫人物進出場域（2026-10-13 · 用戶實測反饋）
# 動機：用戶實測指出段1（兩人對峙）→ 段2（四人圍桌）之間「沒有任何邏輯的過渡」——
#   包內 C17/C17b/C17c/C17d 全是「同一個人的位置/景別接不接得上」，
#   **沒有一條規則管「人數變化」**；C17e 是本缺口的機器載體。
# 紀律：規則（segment-splicing.md §四·補二）+ 總控法則 20·②b + 台賬/手冊登記 + 機檢 C17e，
#   四處缺一即本節 FAIL（防「文檔寫了、執行時不生效」）。
section("[E*19] 段縫人物進出場域（新增 C17e · 2026-10-13 用戶實測）")
_e19_ss = read(os.path.join(PKG, "short-drama-director", "references", "segment-splicing.md"))
_e19_ms = skill
_e19_vp = read(os.path.join(PKG, "short-drama-director", "scripts", "validate_prompt.py"))
_e19_cl = read(os.path.join(PKG, "sd-qc-engine", "references", "continuity-ledger.md"))
_e19_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))

check("㊿ 互鎖①：segment-splicing.md 立「§四·補二 段縫人物進出場律」專節 + 四種過渡寫法齊備",
      "### 四·補二、段縫人物進出場律" in _e19_ss
      and "畫內入畫" in _e19_ss and "畫外先聲" in _e19_ss
      and "空鏡轉場" in _e19_ss and "末鏡行句尾" in _e19_ss)
check("㊿ 互鎖②：總控 SKILL.md 法則 20 已擴為 ≥五條鐵律，②b「新面孔首現要交代」在案並帶 C17e 碼",
      "②b **新面孔首現要交代" in _e19_ms
      and "六條鐵律" in _e19_ms
      and "`C17e`** 人數變化未交代" in _e19_ms)
check("㊿ 互鎖③：validate_prompt.py 實現 C17e（過渡詞表 + 名單比對 + 豁免 + 報碼文案）",
      "C17E_ENTRANCE_WORDS" in _e19_vp and "C17e 人數變化未交代" in _e19_vp
      and "def _core_people" in _e19_vp and "**`C17e`**" not in _e19_vp)
check("㊿ 互鎖④：台賬 continuity-ledger.md 登記「新面孔首現要交代」（2b 條）+ 機檢手冊登記 C17e 行",
      "2b. **新面孔首現要交代**" in _e19_cl
      and "| **C17e** | **人數變化未交代**" in _e19_mcm
      and f"{SUBCODE_TOTAL} 個子碼" in _e19_mcm)

# ------------------------------------------------- [E*20] 對話戲節奏與台詞密度域（2026-10-13 · 用戶實測反饋）
# 動機：用戶實測指出三件事——①「台詞量太少，這是非常多人反饋的一個問題」；
#   ②「我們現在出的台詞更像站樁式對話，一個人說完另一個人說，缺乏快速的正反打」；
#   ③「分鏡也很呆板，15 秒切成三四段、每段裡就幾個詞兒，非常呆傻地去執行台詞量控制」。
# 根因：包內此前**只有上限、沒有下限**（語速檔 / 密度表 / 閘門2 / 閘門3 全在防超載）→
#   描述是"必須寫"、台詞是"可以少寫" → 被犧牲的必然是台詞；且切鏡按"內容塊"切而非"回合"切。
# 紀律：規則（shot-economy §五·七 + dialogue-speed-check §一·補三）+ 總控法則 20·②c/⑤ +
#   劇本層過渡（episode-planning §TRANSITION_AS_BEAT）+ 必查清單 + 機檢 C27b/c/d，
#   五處缺一即本節 FAIL（防「文檔寫了、執行時不生效」）。
section("[E*20] 對話戲節奏與台詞密度域（新增 C27b/c/d · 2026-10-13 用戶實測）")
_e20_sea = read(os.path.join(PKG, "sd-storyboard-engine", "references", "shot-economy-and-acting.md"))
_e20_dsc = read(os.path.join(PKG, "short-drama-director", "references", "dialogue-speed-check.md"))
_e20_ep = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_e20_chk = read(os.path.join(PKG, "short-drama-director", "references", "prompt-feeding-checklist.md"))

check("㋅ 互鎖①：shot-economy-and-acting.md 立「§五·七 對話戲節奏律」"
      "（回合制切鏡 + 開口密度下限 + OS/短句化 + 病灶實證表）",
      "## 五·七、對話戲節奏律" in _e20_sea
      and "回合制切鏡" in _e20_sea
      and "同一說話人連續佔據 ≥2 個完整鏡行" in _e20_sea
      and "15 秒 ≥6 次" in _e20_sea
      and "OS（內心獨白）是零口型成本" in _e20_sea)
check("㋅ 互鎖②：dialogue-speed-check.md 立「§一·補三 台詞密度下限」（對話段 ≥2.0 字·秒⁻¹，"
      "空鏡/打鬥段不設下限）",
      "## 一·補三、 台詞密度**下限**" in _e20_dsc
      and "2.0 字·秒⁻¹" in _e20_dsc
      and "空鏡段 / 轉場段" in _e20_dsc
      and "⛔ 不是\"為加而加\"" in _e20_dsc)
check("㋅ 互鎖③：episode-planning.md 立「§ TRANSITION_AS_BEAT 過渡即戲點」"
      "（劇本層造過渡 · 四種類型 · 分鏡層只做落地）",
      "TRANSITION_AS_BEAT" in _e20_ep
      and "過渡即戲點" in _e20_ep
      and "動作橋" in _e20_ep and "空鏡敘事" in _e20_ep and "聲音橋" in _e20_ep
      and "劇本層 = 造過渡" in _e20_ep)
check("㋅ 互鎖④：總控 SKILL.md 法則 20 擴為六條鐵律 + ②c 過渡歸屬 + ⑤ 對話節奏在案 + 子碼清單登記 C27",
      "六條鐵律" in _e19_ms
      and "②c **過渡是劇本層的戲點" in _e19_ms
      and "⑤ **對話戲節奏與台詞密度" in _e19_ms
      and "`C27b`** 對話段台詞密度" in _e19_ms)
check("㋅ 互鎖⑤：必查清單登記 C27 兩項（第 29 項對話戲節奏 + 第 30 項台詞密度下限 + 第 31 項場次過渡）",
      "| 29 | **對話戲節奏**" in _e20_chk
      and "| 30 | **台詞密度下限**" in _e20_chk
      and "| 31 | **場次過渡即戲點**" in _e20_chk)
check("㋅ 互鎖⑥：validate_prompt.py 實現 C27b/c/d（段落類型識別 + 密度 + 開口數 + 站樁判據 + 豁免）",
      "C27_DIALOGUE_MARK" in _e19_vp
      and "C27b 對話段台詞密度不足" in _e19_vp
      and "C27c 對話段開口次數不足" in _e19_vp
      and "C27d 站樁式對話" in _e19_vp
      and "def _c27_seg_type" in _e19_vp)
check("㋅ 互鎖⑦：機檢手冊登記 C27 主碼行（§二 門禁清單）+ C27a~d 進 SUBCODE-Registry 清單",
      re.search(r"^\| C27 \| \*\*對話戲節奏與台詞密度下限\*\*", _e19_mcm, re.M) is not None
      and all(c in _e19_mcm for c in ("C27a", "C27b", "C27c", "C27d"))
      and f"{SUBCODE_TOTAL} 個子碼" in _e19_mcm
      and "| **C27a~d** |" not in _e19_mcm)
# ── 對話段全面豁免（2026-10-13 用戶裁定）──
#   動機：C2/C13/C18j/C18k 是「鏡必須少、必須動」這一組判據——正反打的標準形態恰恰相反
#   （固定機位 + 高頻切鏡換嘴）。文檔早有「文戲不受固定上限約束」，但機檢未實現，
#   段2 改回合制正反打時被連報 6 條即實證。此處斷言「文檔口徑 ↔ 機檢實現」雙向對齊。
_e20_cam = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
check("㋅ 互鎖⑧：對話段全面豁免已文檔化（shot-economy 豁免表 + camera-system 機檢對齊段 + checklist 第 25 項）",
      "對話段全面豁免（2026-10-13 用戶裁定" in _e20_sea
      and "機檢對齊（2026-10-13 用戶裁定）" in _e20_cam
      and "對話段全面豁免（2026-10-13 用戶裁定）" in _e20_chk)
check("㋅ 互鎖⑨：validate_prompt.py 實現對話段豁免（C2 ÷2s + C13/C18j/C18k 走 _in_dlg）",
      "_dlg_line_ranges" in _e19_vp
      and "def _in_dlg" in _e19_vp
      and "對話段按 ÷2s 放寬以支持正反打" in _e19_vp
      and "_tr_nd = [(s, e, ln) for s, e, ln in tr if not _in_dlg(ln)]" in _e19_vp
      and "_fix_lns_nd = [ln for ln in _fix_lns if not _in_dlg(ln)]" in _e19_vp)

# ── ★ 節奏靈活化（2026-10-13 用戶第二輪申明）──
#   動機：用戶糾正「**你靈活一點，不要說我說啥就把它完全定死了，這個東西它本身是服務著劇情走的**」；
#   「我**也不知道你為了切而切**，像有一些劇情就**不適合這種來回的切**，**靈活懂嗎？是服務劇情的**」。
#   病根：上一輪把規則寫成硬指標 —— ①「空鏡段不設下限」被讀成「空鏡禁寫台詞」，擋掉了
#   「空鏡 + 聲音先入畫」的合法聲橋手法；②「同一人不得連續 ≥2 鏡獨佔開口」等三條沒有給
#   「該慢的戲」（靜場/宣判/留白）留出口；③「全片禁用長鏡頭」一刀切。
#   紀律：**靈活化必須雙向可鎖** —— 既要有「默認為主」的硬項，也要有「劇情有理由時走例外 +
#   必須顯式標註段落意圖」的出口；且總則須上升到總控法則層（否則子技能文檔各說各話）。
check("㋅ 互鎖⑩：shot-economy 立「★★ 總則：節奏服務劇情，規則不是模板」+ 三條硬指標改為"
      "「適用前提：本段是該有來回的對話戲」+ 總則含劇情性質對照表",
      "★★ 總則：節奏服務劇情，規則不是模板" in _e20_sea
      and "適用前提：本段是\"該有來回\"的對話戲" in _e20_sea
      and "靜場對峙 / 宣判 / 留白 / 獨白 / 長鏡壓迫" in _e20_sea
      and "靠沉默和靜止更有力" in _e20_sea)
check("㋅ 互鎖⑪：shot-economy §五 廢除「全片禁用長鏡頭」一刀切 → 改為四類允許保留 + 寫作要求",
      "已廢止**" in _e20_sea
      and "允許保留長鏡/一鏡到底" in _e20_sea)
check("㋅ 互鎖⑫：dialogue-speed-check 立「空鏡帶聲是合法且常用的手法」+「總原則」引用塊 + "
      "空鏡行改為「不設下限，但也不禁言」",
      "空鏡帶聲是合法且常用的手法" in _e20_dsc
      and "但也不禁言" in _e20_dsc
      and "既不強制、也不禁止" in _e20_dsc)
check("㋅ 互鎖⑬：總控 SKILL.md 立「法則 20·★ 一切節奏類規則服務劇情，不是模板」（五條要求 · "
      "含禁止把靈活讀成可以拍呆）",
      "20·★ **一切節奏類規則服務劇情，不是模板" in _e19_ms
      and "禁止把本條的\"靈活\"讀成\"可以拍呆\"" in _e19_ms
      and "空鏡帶先聲是合法且常用的手法" in _e19_ms)
check("㋅ 互鎖⑭：必查清單第 32 項「節奏服務劇情」在案（第 29/30 項的前提）",
      "| 32 | **節奏服務劇情**" in _e20_chk)
check("㋅ 互鎖⑮：validate_prompt.py 的 C27_NO_DIALOGUE_MARK 詞表擴展（靜場/留白/氛圍段/長鏡段/"
      "情緒積累 → 該慢的戲三條全跳過）",
      "靜態場" not in _e19_vp
      and "\"靜場\"" in _e19_vp
      and "\"留白\"" in _e19_vp
      and "\"氛圍段\"" in _e19_vp
      and "\"長鏡段\"" in _e19_vp
      and "\"情緒積累\"" in _e19_vp)

# ------------------------------------------------- [E*21] 創意轉場手法庫域（D 鎖 ④ · 2026-10-13 用戶追問）
# 動機：用戶追問「相似動作 / 前景遮擋 / 形狀匹配 / 甩鏡 / 閃白 / 畫中畫 這類轉場，
#   我們有沒有進行設定？」——實測發現：**結構型銜接（D 鎖 ①②③）齊全，但「技巧型轉場」這一層缺失**——
#   手法詞彙散落在打戲域與 camera-transitions-6types.md，文戲段縫無統一手法庫、無大師技巧、無寫法示例。
# 紀律：**新能力進包 = 文件存在 + 總控有路由（文件樹 + 歸屬表 + D 鎖 ④）+ 文檔間互相指認 +
#   計數口徑同步（38/48）+ 「按劇情選用非必用」口徑在案**，缺一即本節 FAIL。
section("[E*21] 創意轉場手法庫域（D 鎖 ④ · 2026-10-13 用戶追問）")
_e21_ctl = read(os.path.join(refs_dir, "creative-transition-library.md"))
_e21_seg = read(os.path.join(refs_dir, "segment-splicing.md"))
_e21_c6 = read(os.path.join(refs_dir, "camera-transitions-6types.md"))
check("ㆂ 互鎖①：creative-transition-library.md 在案（文戲六式 + 打戲索引 + 大師技巧輯錄）",
      "創意轉場手法庫" in _e21_ctl
      and "相似動作轉場" in _e21_ctl and "形狀/圖形匹配轉場" in _e21_ctl
      and "前景遮擋轉場" in _e21_ctl and "甩鏡轉場" in _e21_ctl
      and "閃白/閃黑轉場" in _e21_ctl and "畫中畫/畫框內的畫框轉場" in _e21_ctl)
check("ㆂ 互鎖②：本庫「按劇情選用非必用」口徑在案（法則 20·★ · 單集 ≤3 處 · 禁為轉而轉）",
      "轉場服務劇情，不是模板" in _e21_ctl
      and "需要時手邊有的工具箱" in _e21_ctl
      and "單集 ≤3 處" in _e21_ctl
      and "為轉而轉" in _e21_ctl
      and "我不是每一段都要用這種比較偏特效一點的轉場" in _e21_ctl)
check("ㆂ 互鎖③：大師技巧輯錄在案（J-cut/L-cut 聲先導 + 視線引導 + 時間省略 + 反差錯位 + 空間軸線 + 定格抽幀）",
      "J-cut（聲先畫後）" in _e21_ctl and "L-cut（畫先聲後）" in _e21_ctl
      and "視線匹配切" in _e21_ctl and "時間省略族" in _e21_ctl
      and "反差與錯位族" in _e21_ctl and "空間與軸線族" in _e21_ctl)
check("ㆂ 互鎖④：總控 SKILL.md 唯一權威歸屬表登記「7b 技巧型轉場（D 鎖 ④）」（★ 新增）",
      "| 7b | **技巧型轉場（D 鎖 ④）** |" in skill
      and "`references/creative-transition-library.md`（★ 2026-10-13 新增）" in skill)
check("ㆂ 互鎖⑤：總控 SKILL.md 文件樹掛載 creative-transition-library.md + D 鎖由三選一擴為四選一",
      "├── ★ creative-transition-library.md" in skill
      and "### D · 段縫銜接方式四選一" in skill
      and "**④ 技巧型轉場（★ 2026-10-13 新增 · 用戶追問）**" in skill)
check("ㆂ 互鎖⑥：segment-splicing.md（結構化權威）指認 ④ 技巧型在案（分工不替代）",
      "creative-transition-library.md" in _e21_seg)
check("ㆂ 互鎖⑦：camera-transitions-6types.md 指認本庫為「擴寫 + 新增未覆蓋手法」",
      "creative-transition-library.md" in _e21_c6)
check("ㆂ 互鎖⑧：README 文件清單登記 creative-transition-library 行 + D 鎖口徑四選一",
      "| 銜接 | `creative-transition-library` |" in read(os.path.join(BASE, "README.md")))
check("ㆂ 互鎖⑨：計數口徑同步（SKILL 聲明 == EXPECTED_REFS · 元規則四）——本庫入包後 SKILL 聲明須同步",
      f"{EXPECTED_REFS} 份規則庫" in skill and EXPECTED_REFS == 53
      and "45 份" not in skill and "37 份" not in skill and "38 份" not in skill)
check("ㆂ 互鎖⑩：必查清單登記第 33 項「技巧型轉場（D 鎖 ④）」（按需 · 非每段必用）",
      "| 33 | **技巧型轉場（D 鎖 ④）**" in read(os.path.join(refs_dir, "prompt-feeding-checklist.md")))

# ------------------------------------------------- [E*12] 新增能力的「規則化」四互鎖域（2026-10-09 用戶追問）
# 動機：用戶實測指出 —— SHOT_TEXT 卡與出圖提示詞配套紀律「只有文檔、沒有規則」：
#   ① SHOT_TEXT 卡在 check_package 零斷言、sd-storyboard-engine/SKILL.md 里根本沒提（子技能自己不知道有這能力）；
#   ② 出圖提示詞配套紀律 §4.4 掛總控 references，執行資產的實際入口 sd-asset-engine/SKILL.md 一字未提（不加載）；
#   ③ 劇情分鏡格有內容斷言但總控歸屬表無獨立歸屬說明。
# 紀律：**能力進包 = 文件存在 + 子技能入口有規則 + 總控有路由 + 機檢有互鎖**，四者缺一即本節 FAIL。
section("[E*12] 新增能力「規則化」四互鎖域（SHOT_TEXT / 劇情分鏡格 / M1 出圖三件套）")
_e12_sb = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
_e12_sa = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
_e12_sst = read(os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md"))
_e12_pdg = read(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
_e12_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
check("㊵ SHOT_TEXT 互鎖①：總控 SKILL 提及（路由 + 歸屬表）", "SHOT_TEXT" in skill)
check("㊵ SHOT_TEXT 互鎖②：sd-storyboard-engine/SKILL.md 有規則條 + 專節",
      "SHOT_TEXT 分鏡線稿卡歸屬" in _e12_sb and "## 七·二、SHOT_TEXT 分鏡線稿卡" in _e12_sb)
check("㊵ SHOT_TEXT 互鎖③：模板 §十一 含俯視走位圖 + 逐鏡卡版式",
      "§十一" in _e12_sst and "俯視" in _e12_sst and "SHOT_TEXT" in _e12_sst)
check("㊵ SHOT_TEXT 互鎖④：README 路由提及", "SHOT_TEXT" in readme)
check("㊵ 劇情分鏡格 互鎖①：文件存在且含「條件必出」",
      os.path.isfile(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
      and "條件必出" in _e12_pdg)
check("㊵ 劇情分鏡格 互鎖②：子技能 SKILL 規則條點名（含條件必出口徑）",
      "plot-deduction-grid.md" in _e12_sb and "條件必出" in _e12_sb)
check("㊵ 劇情分鏡格 互鎖③：總控歸屬表點名 plot-deduction-grid.md", "plot-deduction-grid.md" in skill)
check("㊵ M1 出圖三件套 互鎖①：sd-asset-engine/SKILL.md 有交付清單硬紀律",
      "M1 交付三件套" in _e12_sa and "交付不全" in _e12_sa)
check("㊵ M1 出圖三件套 互鎖②：子技能形態自檢含出圖提示詞齊全性核對",
      "出圖提示詞齊全性" in _e12_sa)
check("㊵ M1 出圖三件套 互鎖③：紀律源文件 §4.4 存在且子技能引用",
      "出圖提示詞配套紀律" in _e12_ade and "asset-delivery-modes.md" in _e12_sa)

# --- ㊶ 單一面部錨點 + 全身完整性（2026-10-09 粉絲反饋 · 四互鎖）
#     2026-10-10 口徑修正：舊「無頭」廢棄（砍頭致頭身比失真）→ 現行「無臉全身」 ---
# 病灶：總控早已定「無臉全身三聯 + 唯一 Face Close-up」，但子技能執行模板寫的是
#       「正面/側面/背面」未標去臉、舊版主圖只到膝蓋以上 → 出的圖裡有 4~5 張清晰臉 + 主圖沒鞋。
_e12_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_e12_asl = read(os.path.join(refs_dir, "asset-spatial-ledger.md"))
check("㊶ 面部錨點 互鎖①：立繪模板含 §七 專節（無臉定義 + 保頭去五官 + 禁字面馬賽克 / 廢無頭）",
      "## 七、角色資產板圖面規則" in _e12_cpt and "Face-Anchor Uniqueness" in _e12_cpt
      and "無臉" in _e12_cpt and "mosaic" in _e12_cpt and "頭身比" in _e12_cpt)
check("㊶ 面部錨點 互鎖②：子技能 SKILL.md 有規則條 + 自檢鉤子（入口可見）",
      "單一面部錨點" in _e12_sa and "character-portrait-templates.md` §七" in _e12_sa
      and "形態自檢⑥" in _e12_sa and "無臉" in _e12_sa)
check("㊶ 面部錨點 互鎖③：總控權威 §二 4View 塊含面部錨點紀律 + 全身完整性 + 無臉口徑",
      "面部錨點紀律" in _e12_asl and "全身完整性" in _e12_asl
      and "全圖唯一允許渲染清晰五官" in _e12_asl and "無臉" in _e12_asl)
check("㊶ 面部錨點 互鎖④：交付配套紀律 §4.4 人物行點名錨點 + 含鞋含頭",
      "單一面部錨點" in _e12_ade and "完整全身頭頂至鞋" in _e12_ade and "無臉" in _e12_ade)
check("㊶ 全身完整性防迴歸：全身格口徑已是「完整全身頭頂至鞋」（舊「65%-75%」中景口徑須清零）",
      "85%-95%" in _e12_cpt and "65%-75%" not in _e12_cpt and "頭頂至鞋" in _e12_cpt)
check("㊶ 無臉口徑防迴歸：現行寫法須為「無臉全身」，舊「無頭全身三聯」寫法須清零",
      "無臉全身" in _e12_cpt and "四格純圖設定板" in _e12_asl
      and "無頭全身三聯" not in _e12_cpt and "無頭全身三聯" not in _e12_asl)
# 2026-10-10 第二輪：除圖底音色外零文字 + 只出四格（粉絲反饋：圖上字太多且亂碼 / 三個特寫不需要）
# 2026-10-10 第四輪修正：音色口徑翻轉 —— 音色英文「必須入圖（渲染於圖底部）」，其餘文字仍禁止
# 2026-10-12 第五輪修正（B 方案）：圖底改為「聲紋錨（波形·非文字）+ ≤8 詞速覽標籤（唯一入圖文字）」，
#            完整版 Voice Description 轉純文本「不進圖」——治長英文崩字 / 被模糊 / 被判成字幕水印
check("㊶ 零文字 互鎖①：立繪模板有「除音色外零文字」專條 + 負向詞含 text/watermark",
      "除音色外零文字" in _e12_cpt and "watermark" in _e12_cpt
      and "不得出現任何文字" in _e12_cpt)
check("㊶ 零文字 互鎖②：子技能 SKILL.md 有「除圖底音色外零文字」硬性紀律條",
      "除圖底音色外零文字" in _e12_sa and "圖上文字只有一處" in _e12_sa)
check("㊶ 零文字 互鎖③：總控 §二 四格純圖條含「除圖底聲紋錨」+「圖面紀律」",
      "四格純圖" in _e12_asl and "除圖底聲紋錨" in _e12_asl)
check("㊶ 音色入圖 互鎖①：模板音色為「必須入圖 · 渲染於圖底部」、舊「禁止入圖」須清零",
      "必須入圖" in _e12_cpt and "渲染於圖底部" in _e12_cpt
      and "純文本交付 · 禁止入圖" not in _e12_cpt
      and "Voice Description 禁止入圖" not in _e12_cpt
      and "Voice Description 禁止入圖" not in _e12_sa)
check("㊶ 音色入圖 互鎖②：模板 §七 明確「圖底音色速覽標籤 = 唯一入圖文字」且 7.10 保留該指令句",
      "唯一入圖文字" in _e12_cpt and "圖底部必須標註以下英文音色速覽標籤" in _e12_cpt
      and "Voice Description Label 速覽標籤（進圖" in _e12_cpt)
_e12_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
check("㊶ 音色入圖 互鎖③：總控 §二 ★條含「圖底音色速覽標籤必須入圖」+「第四輪修正」",
      "圖底音色速覽標籤必須入圖" in _e12_asl and "第四輪修正" in _e12_asl
      and "渲染於圖底部" in _e12_ade)
# 2026-10-12 第五輪新增：聲紋錨（波形·非文字）四處互鎖
#   動機：用戶實測證據 —— 豆包等平台走圖生視頻時，資產圖底部聲紋波形條可作視覺一致性錨；
#   且完整長英文易崩字/被模糊。故底部 = 波形（兜一致性）+ ≤8 詞標籤（兜可讀性）。
#   ⚠️ 只宣稱「視覺錨 + 工作流標記」，不宣稱「能鎖聲線」（未獲證據，不符圖生視頻 conditioning 方式）。
check("㊶ 聲紋錨 互鎖①：立繪模板圖底細節條 = 聲紋波形（非文字·不佔入圖文字名額）+ ≤8 詞速覽標籤",
      "聲紋波形" in _e12_cpt and "不佔「唯一入圖文字」名額" in _e12_cpt
      and "第五輪修正" in _e12_cpt)
check("㊶ 聲紋錨 互鎖②：子技能 SKILL.md 形態自檢⑥ 含 (h) 聲紋錨條 + 術語正名",
      "聲紋錨" in _e12_sa and "不宣稱能鎖聲線" in _e12_sa and "術語正名" in _e12_sa)
check("㊶ 聲紋錨 互鎖③：總控 §二 圖面紀律條含「聲紋波形」+「不佔入圖文字名額」",
      "聲紋波形" in _e12_asl and "不佔入圖文字名額" in _e12_asl)
check("㊶ 聲紋錨 互鎖④：交付配套紀律 §4.4 人物行含「聲紋波形錨」且完整版標「不進圖」",
      "聲紋波形錨" in _e12_ade and "不進圖" in _e12_ade)
check("㊶ 只出四格 互鎖①：模板落位表已收斂為四格、三類特寫取消且明確寫出",
      "只出四格" in _e12_cpt and "三類特寫已全部取消" in _e12_cpt)
check("㊶ 只出四格 互鎖②：舊「膝蓋以下至鞋」**圖格**口徑須清零（只允許出現在「已取消」說明裡，閾值 ≤8）",
      _e12_cpt.count("膝蓋以下至鞋") <= 8
      and "三類特寫已全部取消" in _e12_cpt)
# 2026-10-12 第六輪修正：廢「主圖 + 四格板」並列寫法
#   病灶（用戶實測）：骨架同時含「主圖」與「四格純圖板」→ 模型按 1 主圖 + 4 格 = 5 格輸出（正面被畫兩次）
#   現行寫法 = 顯式總數聲明「全圖共 4 格」，且負向詞須含防重複正面項
check("㊶ 四格總數 互鎖①：立繪模板骨架含「全圖共 4 格」總數聲明 + 禁重複正面負向詞",
      "全圖共 4 格" in _e12_cpt and "不設獨立大主圖" in _e12_cpt
      and "duplicate front view panel" in _e12_cpt)
check("㊶ 四格總數 互鎖②：子技能 SKILL.md 亦含「全圖共 4 格」+ 點明「主圖 + 四格板」病灶",
      "全圖共 4 格" in _e12_sa and "主圖 + 四格板" in _e12_sa)
check("㊶ 四格總數 互鎖③：總控 §二 含「全圖共 4 格」+「不設獨立大主圖」+「任一視角不得重複」",
      "全圖共 4 格" in _e12_asl and "不設獨立大主圖" in _e12_asl
      and "任一視角不得重複" in _e12_asl)
# 2026-10-10 第三輪補：防過度外推——「零文字 + 只出四格」只管角色資產板，不得蔓延到道具/場景
_e12_prop = read(os.path.join(PKG, "sd-asset-engine", "references", "prop-template.md"))
check("㊶ 防過度外推 互鎖①：模板 §7.11 邊界表已登記「道具設定圖」行 + 顯式免責段",
      "道具設定圖" in _e12_cpt and "不要過度外推" in _e12_cpt
      and "只適用於角色四格純圖板" in _e12_cpt)
check("㊶ 防過度外推 互鎖②：道具模板仍保留「左上角標註」法定寫法（未被零文字誤刪）",
      "左上角標註" in _e12_prop and "關鍵細節特寫" in _e12_prop)
# 2026-10-12 第七輪修正：道具模板補總數聲明（與「主圖 + 四格板」**同源病灶**）
#   病灶：§二 只寫「道具三視角圖 + 關鍵細節特寫」→ **無總數聲明**，模型可出成 3 格 / 4 格 / 散圖 / 5 格
#   現行寫法 = 顯式總數聲明「全圖共 4 格」+「不設獨立大主圖 / 不得出現第 5 格」+ 防重複負向詞
#   ⚠️ 與本文件上方「防過度外推」兩條並存：道具雖同為 4 格，但**允許格內標註、含細節特寫格**，
#      不得據此把角色板的「零文字 + 不出特寫格」紀律套到道具圖上（§7.11 邊界表已登記區分句）
check("㊶ 道具四格 互鎖①：道具模板含「全圖共 4 格」+「不設獨立大主圖」+「不得出現第 5 格」+ 防重複負向詞",
      "全圖共 4 格" in _e12_prop and "不設獨立大主圖" in _e12_prop
      and "不得出現第 5 格" in _e12_prop and "duplicate view angle panel" in _e12_prop)
check("㊶ 道具四格 互鎖②：子技能 SKILL.md 道具行含「全圖共 4 格」+ 新增「形態自檢⑦ 道具圖版式」",
      "全圖共 4 格" in _e12_sa and "形態自檢⑦ 道具圖版式" in _e12_sa)
check("㊶ 道具四格 互鎖③：總控 §五 道具執行規範給出四格骨架 + 舊「手持基準」須清零（改「尺寸基準」）",
      "單圖四格：正面 / 45°側視 / 頂部俯視 / 關鍵細節特寫" in _e12_asl
      and "尺寸基準" in _e12_asl and "手持基準" not in _e12_asl)
check("㊶ 道具四格 互鎖④：立繪模板 §7.11 邊界表登記「道具圖同為 4 格」區分句（防與角色板紀律混為一談）",
      "道具圖同為 4 格" in _e12_cpt)
check("㊶ 道具四格 互鎖⑤：交付配套紀律 §4.4 道具行含「全圖共 4 格」+ 四格枚舉（舊「三視角」歧義已清）",
      "全圖共 4 格" in _e12_ade and "頂部俯視圖 / ④ 關鍵細節特寫" in _e12_ade
      and "不出第 5 格" in _e12_ade)
# 2026-10-12 第七輪（同批）：場景九宮格補**顯式**格數聲明 —— 與角色板 / 道具同源收口
#   原有「3×3 九宮格」是名稱隱含 9 格，非顯式總數聲明；實測同源風險（模型按加法出第 10 格 / 拆散圖）
_e12_sg = read(os.path.join(PKG, "sd-asset-engine", "references", "scene-grid-template.md"))
check("㊶ 五宮格格數 互鎖：場景模板含「全圖共 5 格，不多不少」顯式聲明 +「不得出現第 6 格」紀律條",
      "全圖共 5 格，不多不少" in _e12_sg and "不得出現第 6 格" in _e12_sg)

# ------------------------------------------------- [E*15] 運行態微核域 → 【2026-10-13 整環移除】
# 用戶裁定「徹底刪掉微核」。原六互鎖（㊹①②③④⑤⑥b）隨之下線，改為「移除固化域」。
#
# 移除理由（詳見 CHANGELOG `2026-10-13 · 微核整環移除`）：
#   微核的 4 個 `literal` 塊（§1 怎麼用 / §2 鎖速查表 / §5 投餵格式 / §17 生成報告）是
#   `build_core.py` 內的**手寫編排文字**，不隨全庫自動同步。2026-10-13 把 C/I 鎖升格為
#   強制鎖後，§2《鎖速查表》**仍輸出已廢止口徑**（C「不阻塞·按 ③ 走」/ I「可默認」/
#   總括「四鎖齊備」），而 §2 又排在**自動抽取的 §3 原文之前**、且被 SKILL.md 指定為
#   「開工先讀」→ 執行者讀到的第一口徑就是過期的，**直接導致鎖被跳過**。
#   舊校驗（`LITERAL_CHECKS`）只查「名詞是否在源中存在」、不查「處置口徑是否過期」，攔不住。
#
# 結論：**當「摘要」的位置比原文更靠前時，它的漂移危害 > 沒有摘要。** 故取消摘要層，一律讀原文。
# 連帶移除物：`agent-system-core.md` + `scripts/build_core.py` + 全部引用位點。
# （保留 `subprocess` import——本文件仍用它跑 `validate_prompt.py --self-test`。）
section("[E*15·m] 微核移除固化域（2026-10-13 用戶裁定 · 防「摘要層」復活）")

check("㊹m 微核整環移除：包內不得再出現 agent-system-core.md / build_core.py",
      not os.path.exists(os.path.join(BASE, "agent-system-core.md"))
      and not os.path.exists(os.path.join(BASE, "scripts", "build_core.py")))
check("㊹m 總控與 README 均聲明「不設摘要層」（約束寫進文檔，防換人後改回）",
      "不設摘要層" in skill
      and "不設摘要層" in read(os.path.join(BASE, "README.md")))

# ------------------------------------------------- [E*16] 圖形化產物與段縫景別承接域（2026-10-11 用戶實測反饋）
# 動機（兩條實跑反饋）：
#   ① **圖形化產物靜默跳過**：用戶拿修表鋪實稿反饋「四宮格的故事板沒出」——核查其
#      `修表鋪段1/段2` 與官方示範稿後發現：**故事板圖與劇情分鏡格在實跑中整環未產出**，
#      而全包此前對這兩件產物**零斷言**。根因不是"忘了寫規則"，而是
#      「只有『文戲最小 4 格』這句散文——沒有版式名、沒有交付清單、也沒有會響的檢查」：
#      規則不可見，即可被靜默跳過。
#   ② **跨段景別落差**：用戶問「末幀留一秒拉個全景，下一段切中景會不會很奇怪」——
#      §四 只要求「至少換視角或換景別其一」，於是「全景 → 中景」這類 2 級**反向跳**
#      可合法通過，實測讀作跳切。
# 紀律：**新增兩條規則 = 規則源 ↔ 腳本實現 ↔ 手冊登記 ↔ 自檢用例 ↔ 交付清單** 全部在案。
section("[E*16] 圖形化產物與段縫景別承接域（2026-10-11 用戶實測反饋 · 兩域互鎖）")

_pfc = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))

# ㊺ 圖形化產物交付域（故事板圖四宮格版式 + 劇情分鏡格 · 禁靜默跳過）
check("㊺ 互鎖①：故事板權威文件給出「版式與格數下限」表（文戲 2×2 四宮格 / 打戲 2×3 六宮格）",
      "2×2 四宮格" in _e12_sst and "2×3 六宮格" in _e12_sst and "版式與格數下限" in _e12_sst)
check("㊺ 互鎖②：故事板權威文件 §一 已擴為六條硬規則（含版式下限 + 交付清單必列）",
      "六條硬規則" in _e12_sst and "交付清單必列（禁靜默跳過）" in _e12_sst)
check("㊺ 互鎖③：子技能 SKILL 有專節（版式表 + 四宮格消歧 + 交付清單格式）並在高頻鐵律掛線",
      "### 七·一、版式與格數下限" in _e12_sb and "### 七·二、交付清單必列" in _e12_sb
      and "圖形化產物必列清單" in _e12_sb)
check("㊺ 互鎖④：總控 P3 硬產出與極速直出均寫入「圖形化交付清單」（不列即禁進 P4）",
      "P3 圖形化交付清單" in skill and "禁靜默跳過" in skill)
check("㊺ 互鎖⑤：「四宮格」兩處同名產物已雙向消歧（故事板圖 vs 劇情分鏡格）",
      "四宮格故事板" in _e12_sst and "四宮格故事板" in _e12_pdg and "同名不同物" in _e12_pdg)
check("㊺ 互鎖⑥：劇情分鏡格文件寫入交付清單格式（逐場列 · 不列即未完成）",
      "劇情分鏡格：場1 ✅ 四宮格" in _e12_pdg)
check("㊺ 互鎖⑦：故事板模板給出文戲 4 格 2×2 四宮格出圖範例（含 §6.2b）",
      "### 6.2b 文戲範例" in _e12_sst and "2×2 四宮格" in _e12_sst)

# ㊻ 段縫景別承接域（C18m 八互鎖）
check("㊻ 互鎖①：規則源在案（segment-splicing §四·補 段縫景別承接律 · 五規則 + 參考必入組）",
      "### 四·補、段縫景別承接律" in _seg_spl and "段落差 = 0 級（同檔 · 硬綁定）" in _seg_spl
      and "尾幀參考必進參考組" in _seg_spl)
check("㊻ 互鎖②：validate_prompt.py 實現 C18m（9 級階梯 + 終點/起點景別 + 過渡豁免）",
      all(k in _vp_txt for k in ("C18m", "C18M_LADDER", "_c18m_tail_size",
                                 "_c18m_open_size", "_c18m_bridge")))
check("㊻ 互鎖③：機檢手冊已登記 C18m（C18 行內子碼 + 子檢查碼登記行 + 計數一致）",
      "C18m" in _mcm and "段縫景別落差" in _mcm and f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㊻ 互鎖④：自檢含 C18m 四組迴歸用例（收束後反向收緊報 / 收束後同檔不報 / 未收束落差 1 級不報 / 過渡豁免不報）",
      all(k in _vp_txt for k in ("段縫 全景→中景", "末鏡收束後同檔起手不應報 C18m",
                                 "未收束段縫落差 1 級不應報 C18m",
                                 "寫出過渡手段不應報 C18m")))
check("㊻ 互鎖⑤：相鄰段邊界推薦表已加「段縫景別」列 + 規則 7 · 景別階梯掛跨段指針",
      "段縫景別（末鏡終點 → 首鏡起點）" in _seg_spl
      and "任意段（景別承接 · 硬性）" in _seg_spl and "跨段承接口徑" in _cam_sys)
check("㊻ 互鎖⑥：P4 動筆前必查表已掛第 28 項（段縫景別承接 · C18m）",
      "段縫景別承接" in _pfc and "C18m" in _pfc)
check("㊻ 互鎖⑧：C7c 站位人物賬解析元檢查三處互鎖（腳本實現 + 手冊登記 + 自檢用例）",
      "_zw_people_loose" in _vp_txt and "C7c" in _vp_txt and "C7c" in _mcm
      and "站位聲明漏 @ 應報 C7c" in _vp_txt and f"{SUBCODE_TOTAL} 個子碼" in _mcm)
check("㊻ 互鎖⑦：末幀「末 1 秒整秒硬定格 + 前置 0.5 秒收束窗」已標註用戶確認（2026-10-12 裁定）",
      "2026-10-12 用戶裁定" in _seg_spl and "末 1 秒整秒硬定格" in _seg_spl
      and "尾幀穩定區（= 段縫景別收束窗）" not in _seg_spl
      and "尾幀截圖即下段首幀參考圖" in _seg_spl)

# ------------------------------------------------- [E*23] 前置鎖完整性域
section("[E*23] 前置鎖完整性域（D 鎖缺位修復 · 2026-10-13）")
# 病灶：全包無「多段任務」判定式 → 執行者可自稱「當前非多段任務」合法跳過 D 鎖。
# 本域鎖死判定式 + 判定時點 + 同批鎖完三條，防復發。
check("㊼ 互鎖①：總控 §〇 首段寫明「多段任務」判定式（目標成片時長 ÷ A 鎖單段上限 > 1）",
      "目標成片時長 ÷ A 鎖單段上限 > 1" in skill and "多段任務，D 鎖必鎖" in skill)
check("㊼ 互鎖②：判定時點鎖死在 P0 立項期（禁以「劇本階段 / 分鏡層」為由推遲）",
      "判定時點 = P0 立項鎖定期" in skill and "階段論 = 漏鎖事故的直接成因" in skill)
check("㊼ 互鎖③：五道鎖同批鎖完鐵律在案（可分批彈出，但任一批未鎖完禁進 P1）",
      "五道鎖（〇·1 / A / B / C / D）須在同一鎖定期內一次性鎖完" in skill
      and "任一批未鎖完禁止進入 P1" in skill)
check("㊼ 互鎖④：判定式三處同源（§〇 首段 + 〇節摘要句 + D 鎖節，防單點漂移）",
      skill.count("目標成片時長 ÷ A 鎖單段上限 > 1") >= 3)

# ------------------------------------------------- [E*24] 劇本引擎階段② 更名域
section("[E*24] 劇本引擎階段② 更名域（動漫IP開發 → IP 與角色開發 · 2026-10-13）")
# 病灶：階段②舊名「動漫IP開發」會讓真人項目被誤判為動漫項目（用戶原話：「這不是動漫 IP 啊」）。
# 本域鎖死「新名生效位一致 + 舊名清零 + 形態無關聲明在案」，防舊名迴流。
_sse_skill = read(os.path.join(PKG, "sd-script-engine", "SKILL.md"))
_sse_ssp = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
_sse_epp = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
check("㊿ 互鎖①：劇本引擎生效位已更名（SKILL 描述/鏈/路由表/規則表 + 六階段鏈 + 分集邊界表）",
      "IP 與角色開發" in _sse_skill and _sse_skill.count("IP 與角色開發") >= 4
      and "IP 與角色開發" in _sse_ssp and "IP 與角色開發" in _sse_epp)
check("㊿ 互鎖②：舊名已從生效位清零（劇本引擎 SKILL 與六階段流程不得再出現舊名）",
      "動漫IP開發" not in _sse_skill and "動漫IP開發" not in _sse_ssp
      and "動漫IP開發" not in _sse_epp)
check("㊿ 互鎖③：階段②「形態無關聲明」在案（真人/2D/3D/水墨同走一套角色 IP 化流程）",
      "形態無關聲明" in _sbip and "動漫化程度 = 0" in _sbip and "真人實拍質感" in _sbip)
check("㊿ 互鎖④：STYLE_PROFILE 的「動漫化程度」字段已標註形態鎖取值",
      "動漫化程度（形態鎖：真人實拍項目填" in _sbip)

# ------------------------------------------------- [E*25] 前置鎖默認口子清零域
section("[E*25] 前置鎖默認口子清零域（C/I 鎖升格為強制鎖 · 2026-10-13 用戶裁定）")
# 病灶：C 交付形態「未指定默認 ③，不阻塞創作」+ I 畫風鎖「可默認值鎖 · 未指定 = 按默認推薦卡執行」
# 兩個口子讓執行者"合法"跳過彈卡（寫了默認值就不問了），用戶全程沒有選擇權。
# 用戶原話：「這個還是沒有給我選。」
# 本域鎖死「舊口子清零 + 新口徑三處同源 + 形態基底改必確認」，防迴流。
_mdl_adp = read(os.path.join(BASE, "references", "model-adapters.md"))
_slp = read(os.path.join(BASE, "references", "style-bible", "style-lock-protocol.md"))
_readme_top = read(os.path.join(BASE, "README.md"))
_sae_skill = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
_sfe_skill = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("◆1：C 鎖舊口子已清零（§〇 摘要句 / C 鎖節標題 / 嚴格·極速模式對照表 C 列 · 含 model-adapters）",
      "C·交付形態未指定時默認" not in skill
      and "未指定默認 ③" not in skill
      and "未指定默認 ③" not in _mdl_adp)
check("◆2：C 鎖新口徑三處同源（總控 SKILL + model-adapters + README 均標「強制鎖 · 未指定 = 停下詢問」）",
      "強制鎖 · 與 A/B 同規格；未指定 = 停下詢問" in skill
      and "強制鎖 · 與 A/B 同規格 · 未指定 = 停下詢問" in _mdl_adp
      and "未指定 = 停下詢問" in _readme_top)
check("◆3：I 鎖舊口子已清零（禁「可默認值鎖」），新性質「必彈卡鎖」兩處同源",
      "可默認值鎖" not in skill and "可默認值鎖" not in _slp
      and "必彈卡鎖" in skill and "必彈卡鎖" in _slp
      and "禁止在用戶未表態時自行按默認推薦卡執行" in skill)
check("◆4：形態基底改必確認 + 舊引導話術清零 + 下游兩引擎同步",
      "不問用戶 · 自動帶出" not in _slp
      and "Step 1 · 影像基底（★ 2026-10-13 用戶裁定：**必須確認**" in _slp
      and "畫風想要哪一種？不指定我就按默認卡走」" not in _slp
      and "必彈卡鎖" in _sae_skill
      and "未選卡且用戶未表態 = 停下詢問" in _sfe_skill)

# ------------------------------------------------- [E*26] 道具資產錨點域
section("[E*26] 道具資產錨點域（2026-10-13 用戶發現「提示詞裡沒有道具的 @ 位」）")
# 病灶：七段式原只有三類行內錨點——@SCN-（場景）/ @CHR-（人物）/ @角色（站位聲明），**關鍵道具無位可放**。
#      全包 @PRP- 僅 1 處命中（production-ledger-handbook.md 台賬手冊），投餵層字段定義/示例/機檢均未採納；
#      而 validate_prompt.py 的 H8 正則與 ZW_PERSON_RE 早已認 PRP|ITM|PROP 前綴——
#      屬「下游已預留、上游無規定」的反向斷鏈；實跑稿裡道具只能寫鏡行括號夾註「（圖9）」。
# 裁定：併入既有【場景資產】欄（七段式不增段）——本域鎖死「舊兩類寫法清零 + 三族錨點同源 + 下游兩層同步」。
# 用戶原話：「場景資產可供艾特、核心人物可供艾特、站位聲明也還有艾特，但是道具呢？」
_dlv26 = read(os.path.join(BASE, "references", "asset-delivery-modes.md"))
_spa26 = read(os.path.join(BASE, "references", "asset-spatial-ledger.md"))
_amr26 = read(os.path.join(PKG, "sd-feed-engine", "references", "asset-mapping-and-rules.md"))
_sst26 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md"))
check("◇1：asset-delivery-modes 的「新稿一律寫」清單已含道具（舊「@人名 / @場景名」兩類寫法不再裸現）",
      "@人名` / `@場景名` / `@道具名`" in _dlv26
      and "新稿一律寫 `@人名` / `@場景名`**" not in _dlv26)
check("◇2：三族錨點同源（asset-spatial-ledger 聲明 @CHR/@SCN/@PRP）",
      "@CHR/@SCN/@PRP 屬性" in _spa26)
check("◇3：七段式權威 + 投餵引擎 + 故事板層三處同步（骨架含 @PRP- · 錨定紀律章節在案 · 道具錨定句式落地）",
      "【場景資產】@SCN-xxx（參考圖N）" in _mdl_adp and ";@PRP-xxx" in _mdl_adp.replace("；", ";")
      and "道具錨定紀律（2026-10-13 新增 · 治「道具無 @ 位」）" in _mdl_adp
      and "@PRP-道具名（外觀以道具參考圖鎖定；狀態" in _sfe_skill
      and "@PRP-道具名（外觀以道具參考圖鎖定；狀態" in _amr26
      and "@PRP-" in _sst26)

# ------------------------------------------------- [E*27] 特寫佔比與分鏡字段完整性域
section("[E*27] 特寫佔比與分鏡字段完整性域（2026-10-13 項目體檢修復）")
# 病灶（項目體檢實測）：
#   ① 「特寫比例區間 25%~40%」是硬指標，但 validate_prompt.py 全腳本**零佔比斷言**——
#      實測某項目 72 鏡人物特寫僅 19.4%（低於 25% 下限）而機檢 PASSED 零告警。
#      與道具 @PRP 同屬「上游有規定、下游無斷言」。
#   ② 口徑歧義：規則只寫「物件特寫不計入」，**人體局部肢體（手/拳/肩背）是否計入未定義**。
#   ③ 分鏡稿九字段**無任何機檢**（validate_prompt 只檢投餵稿七段式）→ 某項目 1 鏡漏寫
#      `光影/色調` 兩欄，靜默影響下行投餵封裝。
# 裁定：① 口徑寫死（局部肢體計入 / 純物件不計入 / 判定基準在案）；② 補機檢 C18n + 自檢用例；
#      ③ 故事板引擎增設「逐鏡九字段完整性」硬自檢。
_camsys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_vprompt = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_sbstory = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
check("◈1：特寫佔比口徑已寫死（「人物特寫」定義含人體局部肢體 + 「物件特寫」定義 + 判定基準 + 機檢指向）",
      "「人物特寫」定義（2026-10-13 補齊 · 治口徑歧義）" in _camsys
      and "或人的身體局部（手、拳、肩背等肢體）" in _camsys
      and "「物件特寫」定義" in _camsys
      and "判定基準（機檢同此口徑）" in _camsys
      and "機檢 C18n 兜底" in _camsys)
check("◈2：validate_prompt.py 已補 C18n（常量 + 實現 + docstring 聲明 + 自檢用例）",
      "CU_RATIO_MIN, CU_RATIO_MAX = 0.25, 0.40" in _vprompt
      and "C18n 人物特寫佔比" in _vprompt
      and "WARN  C18n 人物特寫佔比" in _vprompt
      and "# 70f) C18n" in _vprompt
      and "# 70i) C18n" in _vprompt)
check("◈3：故事板引擎已設「逐鏡字段完整性」硬自檢（九字段齊全 + 不刪行 + 說明機檢為何抓不到）",
      "交付前硬自檢：逐鏡字段完整性" in _sbstory
      and "不得整行刪掉" in _sbstory
      and "該缺陷**機檢抓不到**" in _sbstory)

# ------------------------------------------------- [E*28] 粉絲系統性意見全修域
section("[E*28] 粉絲系統性意見全修域（2026-10-13 · 劇本 5 條 + 分鏡 3 條）")
# 病灶（粉絲針對 6.9 版的系統性實測意見，逐條對照 V7.4.18 · 沿革記錄）：
#   劇本① 懸念基本歸零 / ② 反派零智商·衝突一起當場被反殺 / ③ 結構注水
#        / ④ 主角滿級零認知轉變·配角工具人 / ⑤ 爽點公式重複→疲勞
#   分鏡⑥ 3D 橫屏禁平視臉部特寫 / ⑦ 微表情要深入補充 / ⑧ 外部標準劇本無潤色層
# 診斷結論：8 條裡 4 條真缺口 + 1 條「規則層自汙染」（R1 速查「不追求人物深度」架空成長地圖）。
# 裁定：全修（P0~P3 七條）。
_polish = read(os.path.join(PKG, "sd-script-engine", "references", "external-script-polish.md"))
_sep = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_six = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
_sbip = read(os.path.join(PKG, "sd-script-engine", "references", "story-bible-and-ip.md"))
_scriptskill = read(os.path.join(PKG, "sd-script-engine", "SKILL.md"))
_camsys2 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_sbstory2 = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
_master = skill
check("◉1：外部劇本潤色層已落地（權威文件 + 邊界三禁 + 六件產出 + 回籤流程 + 入口三處）",
      "EXTERNAL_SCRIPT_POLISH" in _polish
      and "潤色只補「表演層 + 調度層」，嚴禁觸碰「台詞層 / 事件層 / 人物層」" in _polish
      and "潤色產出物（六件 · 逐件交付）" in _polish
      and "回籤流程（強制 · 不得跳過）" in _polish
      and "外來劇本檢測與潤色層" in _scriptskill
      and "external-script-polish.md" in _master)
check("◉2：R1 速查衝突已修（限定語 + 刪「誤會」+ 鉤子擴 8 類）+ 能力/認知起點約束",
      "不追求「慢熱式」人物深度，但人物弧光狀態必須逐集可測" in _sep
      and "禁用「誤會」" in _sep
      and "鉤子類型**用全 8 類**" in _sep
      and "ability_start" in _sbip
      and "cognition_start" in _sbip
      and "MAX_LEVEL_START" in _sbip)
check("◉3：公式去重升全劇配額 + 階段升級義務 + 基線差異 + 反派能力基線 + 懸念存量配額",
      "全劇同一公式族出現不得超過 3 次" in _sep
      and "階段升級義務（★ 新增）" in _sep
      and "新鮮度衰減檢查（★ 新增）" in _sep
      and "懸念存量配額（★ 2026-10-13 新增" in _sep
      and "反派能力基線（★ 2026-10-13 新增" in _six
      and "首次交手須佔上風或全身而退" in _six)
check("◉4：分鏡形態適配 + 特寫×平視組合禁令 + FACS 形態強制 + 表演三要素自檢",
      "形態 → 機位適配（ESTHETIC-BASE-TO-CAMERA" in _camsys2
      and "「人物臉部特寫 × 平視正面」是一個" in _camsys2
      and "影像基底感知契約（★ 2026-10-13 新增" in _sbstory2
      and "表演三要素自查（★ 2026-10-13 新增" in _sbstory2
      and "形態強制項（2026-10-13 新增 · 粉絲實測）" in _master)

# ------------------------------------------------- [E*29] 台詞擬人化域
section("[E*29] 台詞擬人化域（2026-10-13 · 用戶實測「台詞機械化」全修）")
# 病灶（用戶原話：「台詞對白還是過於機械化」「可以增加點擬人的稱呼，更加口語化」）：
#   根因審計確認——**規則在包裡，但全部失效**：
#     R1 唯一的口語化操作規則（acting-direction 壞表演圖鑑 8「台詞太乾淨 → 撒碎屑」）
#        被劃歸「表演層」，劇本階段必讀清單讀不到 → 寫劇本的人看不到；
#     R2 台詞七維診斷是「事後體檢工具」（roundtable-review §1.12.4 明文「本框架不改台詞」）
#        + 手動命令觸發 + 不在 P1 必讀清單 → 孤兒權威（與「微核漂移」同構）；
#     R3 規則**全是否定式**，正向供給為零（全包「擬人」「機械化」「腔調」命中 0；
#        「稱呼系統」僅 1 處且是未定義字段名）→ 執行者知道"不要機械"卻不知"怎麼改"；
#     R4 「人物聲音卡」有要求、無載體、無校驗，且同概念三個版本互不覆蓋
#        （§1.8 YAML 偏偏沒有稱呼字段 → 階段③建的卡傳不到階段⑤）；
#     R5 下游鐵律「台詞逐字保留、不得刪改」→ 上游寫機械了，P3→P4→成片全鏈路無人能救，
#        且此前**沒有任何機檢會報警**（無反饋迴路）。
# 修復（方案 A · 治本）：新建台詞語感唯一權威 + 接入階段⑤ 過站 + 消三口徑分裂 + 補下游探測器 C28。
_nat = read(os.path.join(PKG, "sd-script-engine", "references", "dialogue-naturalization.md"))
_acting2 = read(os.path.join(PKG, "short-drama-director", "references", "acting-direction.md"))
_mcm2 = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
_readme2 = read(os.path.join(BASE, "README.md"))
_vp2 = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_checklist2 = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
_combat2 = read(os.path.join(PKG, "sd-combat-engine", "references", "combat-rhythm-and-load-guardrails.md"))
check("◐1：台詞擬人化引擎已建（權威文件七要件齊全）",
      "台詞擬人化引擎（Dialogue Naturalization · ★權威）" in _nat
      and "稱呼系統（★ 本包空白 · 最高優先）" in _nat
      and "ADDRESS_LEDGER" in _nat
      and "「撒碎屑」四法" in _nat
      and "機械化認症表" in _nat
      and "台詞擬人化過站（執行流程 · 階段⑤硬產出）" in _nat
      and "【待驗證·未實拍】" in _nat
      and "唯一權威" in _nat)
check("◐2：接入劇本引擎（references 表 + 流程鏈 + description 觸發詞）",
      "| [references/dialogue-naturalization.md]" in _scriptskill
      and "台詞擬人化過站" in _scriptskill
      and "台詞口語化、台詞擬人化、台詞太機械" in _scriptskill)
check("◐3：階段⑤ 工序與 §6.8 已掛過站指針",
      "★ 本道工序開工前必須先過《台詞擬人化過站》" in _six
      and "它給的是「怎麼寫」" in _six
      and "以 `dialogue-naturalization.md` 為唯一權威" in _six)
check("◐4：聲音卡三口徑分裂已消（§1.8 YAML 補三字段 + 唯一模板聲明）",
      "address_system" in _sbip
      and "avg_line_length" in _sbip
      and "signature_particles" in _sbip
      and "本 YAML 是唯一卡模板" in _sbip)
check("◐5：表演層壞表演圖鑑 8 已改指針（消同規則兩處口徑）",
      "處方已移至 `sd-script-engine/references/dialogue-naturalization.md` §三" in _acting2
      and "避免同一規則兩處口徑" in _acting2)
check("◐6：下游探測器 C28 已落地（腳本實現 + 手冊登記 + 總控分組 + 三處口徑）",
      "C28_BOOKISH" in _vp2
      and "C28b 對話段零語氣詞" in _vp2
      and "**台詞機械化探測**（2026-10-13 新增" in _mcm2
      and "台詞語感門" in _master
      and "C28a~c 台詞機械化" in _readme2
      and "台詞機械化自檢" in _checklist2)
check(f"◐7：子碼計數 {SUBCODE_TOTAL} 全鏈同步（手冊 / README / checklist / 打戲庫 四處一致）",
      f"{SUBCODE_TOTAL} 個子碼" in _mcm2
      and f"子檢查碼共 {SUBCODE_TOTAL} 條" in _readme2
      and f"子檢查碼共 {SUBCODE_TOTAL} 條" in _checklist2
      and f"子檢查碼共 {SUBCODE_TOTAL} 條" in _combat2)
check("◐8：P1 必讀清單已補七維診斷與擬人化引擎（消「孤兒權威」）",
      "dialogue-doctor-7d.md`（台詞七維診斷 · 定稿前體檢）" in _master
      and "dialogue-naturalization.md`（台詞擬人化引擎" in _master)

# ------------------------------------------------- [E*30] 規則文件掛載一致性域
section("[E*30] 規則文件掛載一致性域（2026-10-13 · 治「★權威 ≠ 會被讀到」）")
# 元缺陷（2026-10-13 元層面反思確立）：
#   包內有三套**各自手工維護、互無斷言**的「文件重要性清單」——
#     ① 唯一權威歸屬表（SKILL.md §一 · 27 行）
#     ② 文件樹 ★ 標記（SKILL.md 文件樹區）
#     ③ **八階段強制讀取清單（唯一決定實際讀不讀的）**
#   ①②③ 之間零一致性斷言 → **文件可寫進①、標上★、畫進②，卻不在③裡，
#   照樣「是權威」，只是永遠沒人讀**（靜默失效）。實證：台詞七維 `dialogue-doctor-7d`
#   與表演層 `acting-direction`（後者自聲明「P1 寫《角色表演檔案》」卻無任何讀取路徑）。
# 修復：SKILL.md 新增《按需規則文件 · 觸發條件台賬》，把**不在必讀清單**的規則文件
#   全部登記觸發條件；本域斷言「台賬 ∪ 必讀清單」== 文件系統裡的全部 references，
#   防日後新增規則文件漏登記（這是把「靜默失效」變成「打包即報警」的關鍵一環）。
def _refs_abs():
    _out = []
    for _dp, _dn, _fn in os.walk(os.path.join(BASE, "references")):
        for _f in _fn:
            if _f.endswith(".md"):
                _out.append(os.path.relpath(os.path.join(_dp, _f),
                                            os.path.join(BASE, "references")).replace(os.sep, "/"))
    return sorted(_out)

_sm = _master
# 定位串必須帶標題標記（"### ★"）——否則會被正文裡的同名引用搶先命中
# （2026-10-13 實測：元規則二引用了台賬名，導致 find 命中元規則而非台賬標題 → 三條斷言集體 FAIL）
_lg = _sm.find("### ★ 按需規則文件 · 觸發條件台賬")
_ledger = _sm[_lg:_sm.find("\n###", _lg)] if _lg > 0 else ""
_rd = _sm[_sm.find("★ 強制讀取清單"):_sm.find("自檢動作（AI 助手在每階段開始時執行）")]
_unregistered = [f for f in _refs_abs()
                 if os.path.basename(f) not in _ledger and os.path.basename(f) not in _rd]
check("◑1 台賬已建：不在八階段必讀清單的規則文件已全部登記觸發條件（漏一個即 FAIL）",
      bool(_ledger) and not _unregistered)
check("◑2 表演層已接進 P3 必讀路徑（修復前 acting-direction 無任何讀取路徑）",
      "★表演環：總控 `references/acting-direction.md`" in _rd
      and "《角色表演檔案》（每主要角色一份" in _sm
      and "acting-direction.md" in _ledger)
check("◑3 台賬含三條鐵律（按需≠可讀可不讀 / 表外不得再有隻標★無觸發條件 / 判定權在觸發條件）",
      "**「按需」≠「可讀可不讀」**" in _ledger
      and "本表之外不得再存在" in _ledger
      and "判定權在觸發條件" in _ledger)
check("◑4 四條元規則已立（一 同概念單一權威 / 二 掛載即生效 / 三 禁令必須配供給 / 四 斷言只鎖常量）",
      "元規則一（同概念單一權威" in _sm
      and "元規則二（掛載即生效" in _sm
      and "元規則三（禁令必須配供給" in _sm
      and "把這條禁令整句刪掉——執行者還知道該怎麼做嗎" in _sm
      and "元規則四（斷言只能鎖" in _sm
      and "這個斷言裡的數字，改了會不會導致別的提交失敗" in _sm)
check("◑5 元規則四已落地：份數斷言引用 EXPECTED_REFS 常量 + SKILL 無「38 份」殘留",
      "38 份" not in skill
      and f"{EXPECTED_REFS} 份規則庫" in skill
      and "EXPECTED_REFS" in open(__file__, encoding="utf-8").read()
      and "f\"{EXPECTED_REFS} 份規則庫\"" in open(__file__, encoding="utf-8").read())
# ⚠️ 元規則四自洽：本斷言的判據串不得以字面形式出現在本文件（否則自我命中）。
#    故用 chr() 拼接構造禁項，避免斷言文本本身觸發匹配。
_selfsz = open(__file__, encoding="utf-8").read()
_n60 = "6" + "0"
check("◑6 元規則四已落地：斷言文案無過時子碼數（52 / 59 / 6" + "0 / 64 / 65）",
      all((n + " 子碼口徑") not in _selfsz for n in ("52", "59", "64", "65"))
      and ("計數 " + _n60) not in _selfsz
      and ("同步為 " + _n60) not in _selfsz
      and (" " + _n60 + "（防") not in _selfsz)
# ◑7 元規則四 · 版本類斷言只鎖常量（2026-10-14 實測事故：升版 7.4.19 時
#     OLD_VER_RE 排除項仍寫死 (?!4\.18) → 新版號被當舊版號誤殺套裝 6 處文件，
#     且因命中列表截斷顯示而被「4 條恆紅」掩蓋）。
#     判據：OLD_VER_RE 的構造必須以 VERSION 為來源，不得出現任何字面版本號。
_oldver_src = "\n".join(l for l in _selfsz.splitlines()
                        if not l.strip().startswith("#")
                        and ("OLD_VER_RE" in l or "_CUR_ESC" in l))
check("◑7 元規則四已落地：OLD_VER_RE 排除項由 VERSION 常量派生（不得寫死字面版本號）",
      "%s" in _oldver_src and "_CUR_ESC" in _oldver_src
      and re.search(r"OLD_VER_RE\s*=\s*re\.compile", _oldver_src) is not None)
# ◑8 防迴歸 · 本套裝自身不得命中「舊版本串」斷言（歷史事故：命中被前 6 條截斷掩蓋）
# 2026-10-16：掃描域已收斂為本套裝 13 目錄（見 ◑16），同級技能名白名單隨之退休——
#   原先靠 `pingshu- / short-drama-factory / huhe- / xuanhuan- / skill-package- / real-combat-`
#   前綴過濾，屬「補丁打補丁」：新增一個同級技能或倉庫根落地頁即漏。現由 ◑16 從源頭鎖定。
_self_hits = _bad_old
check("◑8 本套裝 13 目錄零命中「舊版本串」（防命中被截斷顯示掩蓋）",
      not _self_hits, "; ".join(_self_hits[:6]) or "零命中")

# ◑16 掃描域鎖定（2026-10-16 根治 · 治「os.walk(PKG) 越界」）：
#   本套裝的規則文件掃描域**恰為 11 個目錄**（總控 + 10 子技能）。
#   事故：`scan_md_files()` 直掃包根 → ① GitHub 倉庫根落地頁 `README.md`（寫著上一版版本號）
#   ② 用戶本機同級其它技能 → 被併入內容規則門，從倉庫根跑必報假 FAIL（升版後實測發現）。
_scan_outsiders = []
for _p in scan_md_files():
    _top = os.path.relpath(_p, PKG).replace("\\", "/").split("/")[0]
    if _top not in SUB_SKILLS and _top != os.path.basename(BASE):
        _scan_outsiders.append(os.path.relpath(_p, PKG))
check("◑16 掃描域鎖定：本套裝規則文件掃描恰為 13 目錄（防 os.walk 越界至倉庫根落地頁 / 同級技能）",
      not _scan_outsiders, "; ".join(_scan_outsiders[:6]) or "零越界")
_root_readme = os.path.join(PKG, "README.md")
check("◑16 倉庫根落地頁 README.md 不參與本套裝內容規則門（若存在）",
      (not os.path.exists(_root_readme))
      or os.path.abspath(_root_readme) not in {os.path.abspath(x) for x in scan_md_files()})
# ◑9 防迴歸 · 豁免詞不得「整行放過」版本串（2026-10-14 實測事故：
#     SKILL.md 權威歸屬表 #19 行寫死 `V7.4.18`，因該行同時出現 `CHANGELOG.md`
#     → 被行級豁免詞 `CHANGELOG` 放過，斷言與 ◑8 均未報警，逃過整個 V7.4.19 升版）。
#     判據：**表格行（以 | 開頭）不適用豁免詞**——表格是規格區，不是沿革區。
_bad_tbl = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if line.lstrip().startswith("|") and OLD_VER_RE.search(line):
            _bad_tbl.append(f"{rel(p)}:{i}")
check("◑9 表格行內無舊版本串（豁免詞只對沿革行生效，不適用表格 · 修 #19 逃逸）",
      not _bad_tbl, "; ".join(_bad_tbl[:6]) or "零命中")
# ◑12 腳本 docstring 無寫死舊版本串（2026-10-14 代碼體檢修復）：
#   `scan_rule_docs()` 只掃 .md —— scripts/*.py 的 docstring **不在版本斷言覆蓋範圍內**。
#   實測：check_package.py 自己的 docstring 曾寫死上一版版本號（升版後漂移），
#   `[A]`/`◑8` 均未報警。→ 補一條「腳本域」斷言，把 .py 也納入。
_SCRIPT_DIR = os.path.join(BASE, "scripts")
_bad_py = []
for _f in sorted(os.listdir(_SCRIPT_DIR)):
    if not _f.endswith(".py"):
        continue
    for i, line in enumerate(read(os.path.join(_SCRIPT_DIR, _f)).splitlines(), 1):
        # 沿革行豁免口徑與 .md 域完全一致（VER_ALLOW_RE）——域命名如
        # `[E+] V7.3.0 三項融合域`、`V7.3.9 起正文不再保留歷史版本標註` 屬合法沿革。
        if OLD_VER_RE.search(line) and not VER_ALLOW_RE.search(line):
            _bad_py.append(f"{rel(os.path.join(_SCRIPT_DIR, _f))}:{i}")
check("◑12 scripts/*.py 無舊版本串（.py 的 docstring 不在 .md 掃描域 · 補逃逸）",
      not _bad_py, "; ".join(_bad_py[:6]) or "零命中")
# ◑13 單一權威 · IDLE_PROP_RE 只定義一次（2026-10-14 代碼體檢修復）：
#   實測 L761（C16d 段）與 L807（C18c 段）各定義一次，L807 覆蓋 L761 →
#   靜默丟掉 `撥弄|翻弄|轉著` 三詞。屬元規則一「同概念單一權威」違規。
_vp_lines = read(vp).splitlines()
_idle_defs = [i for i, l in enumerate(_vp_lines, 1)
              if re.match(r"^IDLE_PROP_RE\s*=", l)]
check("◑13 IDLE_PROP_RE 在 validate_prompt.py 中只定義一次（防二次定義覆蓋丟詞）",
      len(_idle_defs) == 1, f"定義 {len(_idle_defs)} 處：行 {_idle_defs}")
check("◑13 IDLE_PROP_RE 詞表覆蓋六詞（把玩/摩挲/撥弄/把弄/翻弄/轉著）",
      len(_idle_defs) == 1 and all(w in _vp_lines[_idle_defs[0] - 1]
                                   for w in ("把玩", "摩挲", "撥弄", "把弄", "翻弄", "轉著")),
      _vp_lines[_idle_defs[0] - 1] if _idle_defs else "未找到定義")
# ◑14 單一權威 · C11b/C17c/C19c/C19e 均按段遍歷（2026-10-14 代碼體檢修復靜默失明四條）：
#   病灶：① C11b 取 `_tlines[-1]` 只查全文末鏡 → 段1~N-1 全漏；
#        ② C17c 用 `re.search` 只取第一個【站位聲明】→ 段2+ 全漏；
#        ③ C19c 硬匹配半角 `[鏡頭1]` → 全角稿整條靜默跳過；
#        ④ C19e 用 `[\s\S]*` 貪婪吞到文末 → 鏡行正描寫被誤判為禁止項錯位。
check("◑14 C11b 逐段檢查末鏡（遍歷 seg_zw，不得取全文最後一行）",
      "_c11b_miss" in read(vp) and "for (_n, _b, _l, _blk, _ppl, _shots, _dlgs) in seg_zw:" in read(vp),
      "C11b 仍為全文級實現")
check("◑14 C17c 逐段檢查站位聲明（遍歷 seg_zw，不得只取第一個）",
      "_c17c_miss" in read(vp), "C17c 仍為全文首個匹配")
check("◑14 C19c 鏡號判定兼容全角（用 SHOT_TAG_RE，不得硬匹配半角）",
      "_shot_no(l) == 1" in read(vp) or "_shot_no(_l) == 1" in read(vp),
      "C19c 仍硬匹配 [鏡頭1]")
check("◑14 C19e 禁止項有段界（非貪婪 + 截止下一個【欄位標記）",
      "【強制禁止項】([\\s\\S]*?)(?=\\n【|\\Z|```)" in read(vp),
      "C19e 仍貪婪吞到文末")
# ◑15 TIME_RE 第三形態 `N-N秒`（2026-10-14 用戶裁定「更寬容」納入）：
#   打戲/玄幻稿慣用 `0-3秒` 整數秒時碼，舊 TIME_RE 只認 MM:SS 與 Xs-Ys → 整篇被當
#   「無時間軸」，C1~C3/C10/C11b/C17~C25 整套鏡級判據靜默失效（實測 storyboard-board-lite.md
#   只報一句"C1-C3 未識別到時間軸"）。但裸 `N~N秒` 散文極常見 → 必須帶守衛 + 緊寫判別。
_vp_txt = read(vp)
# 取 TIME_RE 定義塊（從 `TIME_RE = re.compile` 到本塊結束 `re.I)`）做局部斷言，防全文誤命中
_time_def = ""
_m = re.search(r"TIME_RE = re\.compile\([\s\S]*?re\.I\)", _vp_txt)
if _m:
    _time_def = _m.group(0)
check("◑15 TIME_RE 含 N-N秒 第三形態（守衛版 · 散文不誤判）",
      bool(_time_def) and "(?<=[\\s\\[【\\]】])" in _time_def and "秒" in _time_def,
      "TIME_RE 未含 N-N秒 第三形態或守衛缺失")
check("◑15 parse_time_ranges 已同步三形態解算（防 float(None) 崩）",
      "m.group(9)" in _vp_txt and "m.group(10)" in _vp_txt,
      "parse_time_ranges 缺第三形態分支——N-N秒 會落到 float(None) 崩潰")
check("◑15 緊寫判別在案（秒 前不得有 \\s* · 散文判別特徵）",
      "緊寫判別" in _vp_txt or "緊寫" in _vp_txt,
      "缺緊寫判別註釋——裸 `1~2 秒` 散文會被誤當時碼")
check("◑15 self-test 含 N-N秒 雙向用例（70l 正例 7 組 / 反例散文判別）",
      "TIME_RE 第三形態判別錯誤" in _vp_txt and "N-N秒 稿應識別到時間軸" in _vp_txt,
      "self-test 缺 70l/70n 用例")
# ◑10 單一權威 · 單段時長口徑收口（2026-10-14 外部評審獨立指出「四口徑並存」）：
#   曾經：SKILL.md §〇.D.⑦=25~30s ／ SKILL.md §二=每組≤15s ／ seedance-render-engine=嚴格4~15秒
#        ／ 鐵律2=每鏡10秒 —— 四處並存互不引用，執行時無法判斷聽誰。
#   裁定：唯一權威 = model-adapters.md（模型契約表 + §5）；其餘一律改指針。
_DUR_ALLOW = ("machine-check-manual.md",  # 機檢手冊複述 C1b 口徑（登記用途）
              "model-adapters.md")        # 權威本體
# ⚠️ 元規則四：判據只抓「肯定式寫死」，放過「否定式引用」。
#    實測踩坑：首版斷言把「⚠️ 本節不再寫『每組 ≤15s』」這類**否定句**也判紅了。
#    修法 = 否定詞先行負向匹配（同句內出現「不再/不適用/僅適用/僅）→ 視為引用，放過。
_NEG_NEAR = re.compile(r"不再|不適用|僅適用|不再另寫|廢止|禁|❌|⚠️")
_bad_dur = []
for _p in scan_rule_docs():
    _r = rel(_p)
    # ⚠️ 只掃本套裝（其餘技能有獨立治理權，不屬本包管轄）
    if not _r.startswith(("short-drama-director/", "sd-")):
        continue
    if os.path.basename(_r) in _DUR_ALLOW:
        continue
    for _i, _line in enumerate(read(_p).splitlines(), 1):
        _hard = (re.search(r"每組\s*[≤<]\s*15\s*[s秒]", _line)
                 or "嚴格控制在 **4 ~ 15 秒**" in _line)
        if not _hard:
            continue
        # 若同句含否定語（該值被明確否定/限定），不算違反
        _seg = re.split(r"[；;。]", _line)
        if any(_hard and _NEG_NEAR.search(_s) for _s in _seg):
            continue
        # 逐段判定：只在「含該值的那個分句」裡找否定詞
        for _s in _seg:
            if (re.search(r"每組\s*[≤<]\s*15\s*[s秒]", _s)
                    or "嚴格控制在 **4 ~ 15 秒**" in _s):
                if not _NEG_NEAR.search(_s):
                    _bad_dur.append(f"{_r}:{_i}")
                break
check("◑10 單段時長口徑已收口：除權威與機檢手冊外，無文件再「肯定式寫死」每組≤15s / 嚴格4~15秒",
      not _bad_dur, "; ".join(_bad_dur[:6]) or "零命中")
# ◑11 單一權威聲明在位（model-adapters.md 必須顯式聲明自己是時長/時間碼唯一權威）
_mad = read(os.path.join(BASE, "references", "model-adapters.md"))
check("◑11 model-adapters.md 聲明「單段時長/組數/鏡行時間碼」唯一權威",
      "唯一權威聲明" in _mad and "全包任何其他文件不得再自行寫死時長數字" in _mad)

# ------------------------------------------------- [E*31] 資產狀態偏離域
section("[E*31] 資產狀態偏離域（2026-10-13 · 用戶實測「資產圖戴頭盔 + 提示詞夾頭盔 = 兩個頭盔」）")
# 病根（三條規則疊加）：
#   ① 立繪模板把穿戴物寫成「配飾（固定不可變更·保留入圖）」；
#   ② SET_STATE 只服務「場景」，**人物無狀態變體機制**；
#   ③ 換裝機制是「跨造型」（A裝/B裝各出一圖），解決不了「同一場戲內摘下來」。
#   → 資產圖鎖「戴著頭盔」、提示詞要「夾著頭盔」，**無優先級聲明** → 模型【疊加】而非【替換】。
_asl2 = read(os.path.join(BASE, "references", "asset-spatial-ledger.md"))
_ma2 = read(os.path.join(BASE, "references", "model-adapters.md"))
_cpt2 = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_vp3 = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_ckl2 = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
check("◒1：CHAR_STATE 人物持續狀態變體已建（四類型 + 三條硬規則 + 「鎖的是它長什麼樣、不是它必須在身上」）",
      "CHAR_STATE · 人物持續狀態變體" in _asl2
      and "鎖定的是「這個東西長什麼樣」，不是「它必須在身上」" in _asl2
      and "穿戴增減類" in _asl2
      and "半途矛盾" in _asl2)
check("◒2：立繪模板配飾口徑已改（舊「固定不可變更」須清零）",
      "配飾（默認鎖定 · 可變需聲明）" in _cpt2
      and "鎖定的是「它長什麼樣」，不是「它必須在身上」" in _cpt2
      and "配飾（固定不可變更·保留入圖）" not in _cpt2)
check("◒3：投餵層「資產偏離聲明」三件套已建（§5.0.6）",
      "資產狀態偏離聲明" in _ma2
      and "以本段提示詞為準，覆蓋角色參考圖" in _ma2
      and "禁項只作兜底，不能替代替換語" in _ma2)
check("◒4：C29 探測器已落地（腳本實現 + 手冊登記 + 總控分組 + checklist 四處一致）",
      "C29_DETACH" in _vp3
      and "C29 疑似資產狀態偏離未聲明" in _vp3
      and "資產狀態偏離探測" in _mcm2
      and "資產狀態門" in _master
      and "資產狀態偏離" in _ckl2)

# ------------------------------------------------- [E*32] 外掛激活回執·子技能零孤兒·跨腳本全鏈路一致性域
section("[E*32] 外掛激活回執·12子技能零孤兒·C30指紋探針·跨腳本一致性域（2026-10-14 全鏈路閉環）")

# ◓1 第一招落地：總控 SKILL.md 含【外掛激活回執頭】三行規範（激活外掛 / 已讀子庫 / 本段調用外掛指紋）
check("◓1 總控 SKILL.md 已立【外掛激活回執頭】（激活外掛 / 已讀子庫 / 本段調用外掛指紋）",
      "外掛激活回執頭" in _master
      and "激活外掛：" in _master
      and "已讀子庫：" in _master
      and "本段調用外掛指紋：" in _master)

# ◓2 第二招落地：P0B 必讀含 forbidden-zone-whitelist.md；P3 必讀廢除「只讀 SKILL.md + 招式庫」截胡話術，掛載 R1/R3 核心靈魂庫
check("◓2 P0B 必讀已補 forbidden-zone-whitelist.md，P3 必讀已掛載真武動力鏈與玄幻尺度/三層元素庫",
      "forbidden-zone-whitelist.md" in _rd
      and "kinetic-chain-11.md" in _rd
      and "defense-evasion-rules.md" in _rd
      and "impact-physics.md" in _rd
      and "core-combat-laws.md" in _rd
      and "xuanhuan-elements-vfx.md" in _rd
      and "grand-scale-domains.md" in _rd
      and "shot-economy-and-acting.md" in _rd
      and "plot-deduction-grid.md" in _rd
      and "SKILL.md + 招式庫" not in _rd)

# ◓3 第二招擴展：10 個子技能全部 77 份 references/*.md 零孤兒斷言（既在各自子技能 SKILL.md 掛載，也在總控必讀或觸發台賬掛載）
_sub_orphans_own = []
_sub_orphans_main = []
for _sname in SUB_SKILLS:
    _sp = sub_skill_path(_sname)
    if not _sp:
        continue
    _sskill = read(os.path.join(_sp, "SKILL.md"))
    _sref_dir = os.path.join(_sp, "references")
    if not os.path.isdir(_sref_dir):
        continue
    for _rfn in sorted(os.listdir(_sref_dir)):
        if not _rfn.endswith(".md"):
            continue
        if _rfn not in _sskill:
            _sub_orphans_own.append(f"{_sname}/{_rfn}")
        if _rfn not in _rd and _rfn not in _ledger:
            _sub_orphans_main.append(f"{_sname}/{_rfn}")
check("◓3 10 子技能全部 references 均在各自 SKILL.md 掛載（零子包內孤兒）",
      not _sub_orphans_own, "; ".join(_sub_orphans_own[:6]) or "零孤兒")
check("◓3 10 子技能全部 references 均在總控【強制讀取清單 ∪ 觸發條件台賬】掛載（零跨包孤兒）",
      not _sub_orphans_main, "; ".join(_sub_orphans_main[:6]) or "零孤兒")

# ◓4 第三招落地：validate_prompt.py 實現 C30a/b/c/d 外掛指紋與交接探針，且在手冊、總控、checklist 同步登記
check("◓4 C30 外掛指紋與交接探針四處互鎖（validate_prompt / 機檢手冊 / 總控分組 / checklist）",
      all(k in _vp3 for k in ("C30a", "C30b", "C30c", "C30d", "C30_SCALE_4", "C30_KINETIC_11"))
      and all(k in _mcm2 for k in ("C30a", "C30b", "C30c", "C30d"))
      and "外掛指紋與交接門" in _master
      and "外掛激活回執與指紋" in _ckl2)

# ◓5 第四招與多段逐段化全鏈路閉環（防「修A漏B」）：
#    - _c27_shot_span 複用 parse_time_ranges（不硬編碼 MM:SS）
#    - gate_check.py 與 build_board_lite.py 均兼容 N-N秒 與全角【鏡頭N】
#    - machine-check-manual.md §八 不再寫「TIME_RE ❌ 不識別 0-3秒」
#    - validate_seedance_segment_map.py 兼容 SEEDANCE_2_5 (30s)
_gc_txt = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
_bbl_txt = read(os.path.join(BASE, "scripts", "build_board_lite.py"))
_vssm_txt = read(os.path.join(PKG, "sd-qc-engine", "scripts", "validate_seedance_segment_map.py"))
check("◓5 跨腳本時間軸與逐段化閉環（_c27_shot_span / gate_check / build_board_lite / 手冊§八 / 2.5分段門）",
      "parse_time_ranges(line)" in _vp3
      and "GC_TIME_RE" in _gc_txt and "GC_SHOT_NO_RE" in _gc_txt
      and r"[\[【]?" in _bbl_txt
      and "❌ **不識別**" not in _mcm2
      and "SEEDANCE_2_5" in _vssm_txt)

# ------------------------------------------------- [E*33] 四大進階進化能力互鎖域（2026-10-14 架構升級）
section("[E*33] 四大進階進化能力互鎖域（sd_core / slice_context / compile_feed / 拉片診改與看板三導出）")

# ◓6 進化一：sd_core.py 公共解析與狀態台賬內核存在且自測通過，validate_prompt 支持 --state 對賬
_sd_core_p = os.path.join(BASE, "scripts", "sd_core.py")
_r_sdc = subprocess.run([sys.executable, _sd_core_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_sd_core_p) else None
check("◓6 sd_core.py 公共解析與 project_state.json 狀態台賬內核在位且 --self-test 通過",
      _r_sdc is not None and _r_sdc.returncode == 0 and "PASSED" in (_r_sdc.stdout or ""),
      (_r_sdc.stdout or _r_sdc.stderr) if _r_sdc else "缺失 sd_core.py")
check("◓6 validate_prompt.py 已接入 --state 跨階段狀態台賬對賬模式（verify_feed_against_state）",
      "verify_feed_against_state" in _vp3 and "--state" in _vp3)

# ◓7 進化二：slice_context.py 動態原文切片器存在且 P0~P5 全階段自測通過
_slice_p = os.path.join(BASE, "scripts", "slice_context.py")
_r_slc = subprocess.run([sys.executable, _slice_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_slice_p) else None
check("◓7 slice_context.py 動態原文切片器在位且 P0~P5 全階段 --self-test 通過",
      _r_slc is not None and _r_slc.returncode == 0 and "PASSED" in (_r_slc.stdout or ""),
      (_r_slc.stdout or _r_slc.stderr) if _r_slc else "缺失 slice_context.py")

# ◓8 進化三：compile_feed.py P4 自動裝配編譯器存在且編譯產物 100% 過 validate_prompt 與 gate_check
_comp_p = os.path.join(BASE, "scripts", "compile_feed.py")
_r_cmp = subprocess.run([sys.executable, _comp_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_comp_p) else None
check("◓8 compile_feed.py P4 投餵自動裝配編譯器在位且 --self-test 雙門全過",
      _r_cmp is not None and _r_cmp.returncode == 0 and "PASSED" in (_r_cmp.stdout or ""),
      (_r_cmp.stdout or _r_cmp.stderr) if _r_cmp else "缺失 compile_feed.py")

# ◓9 進化四（上）：多模態拉片診改協議（quality-gate-review.md §四 12 類實拍廢片矩陣 + SKILL /拉片診改 指令）
_qgr_txt = read(os.path.join(BASE, "references", "quality-gate-review.md"))
check("◓9 多模態拉片診改協議在案（quality-gate-review.md §四 12 類症狀矩陣 + SKILL /拉片診改 路由）",
      "多模態拉片診改協議" in _qgr_txt
      and "十二類實拍高頻廢片症狀" in _qgr_txt
      and "/拉片診改" in _master
      and "單組時長突破 15 秒" not in _qgr_txt)

# ◓10 進化四（下）：build_board_lite.py 支持一鍵導出 SRT 字幕 / 剪輯時間線 CSV / API 載荷 JSON 且 --self-test 通過
_bbl_p = os.path.join(BASE, "scripts", "build_board_lite.py")
_r_bbl = subprocess.run([sys.executable, _bbl_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_bbl_p) else None
check("◓10 build_board_lite.py 支持一鍵導出 SRT/CSV/JSON 且 --self-test 通過",
      _r_bbl is not None and _r_bbl.returncode == 0 and "PASSED" in (_r_bbl.stdout or "")
      and all(k in _bbl_txt for k in ("exportSRT()", "exportTimelineCSV()", "exportPayloadJSON()", "--export-srt", "--export-csv")),
      (_r_bbl.stdout or _r_bbl.stderr) if _r_bbl else "build_board_lite 自測失敗")

# ------------------------------------------------- [E*34] Lubezki×Deakins 物理運鏡·光學鎖焦·解剖微表·陰面取景融合域（2026-10-14 粉絲 shotlist-builder 吸收）
section("[E*34] Lubezki×Deakins 物理運鏡·光學鎖焦·解剖微表·陰面取景融合域（shotlist-builder 四大絕活吸收）")

_cam_sys_34 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_act_dir_34 = read(os.path.join(BASE, "references", "acting-direction.md"))
_lgt_af_34 = read(os.path.join(BASE, "references", "lighting-and-antifake.md"))
_eng_cl_34 = read(os.path.join(PKG, "sd-feed-engine", "references", "engineering-language-cleanup.md"))
_cmp_fd_34 = read(os.path.join(BASE, "scripts", "compile_feed.py"))

check("◓11 物理運鏡與光學鎖焦規程在案（10~15釐米物理限位 / 呼吸微動隨動構圖 / 單鏡分階段情緒運鏡 / 85mm F1.4 鎖焦 / 0.3~0.5秒閃切）",
      all(k in _cam_sys_34 for k in (
          "Lubezki × Deakins 物理運鏡與光學鎖焦規程",
          "10~15 釐米",
          "主動跟隨角色臉部運動",
          "單鏡內分階段情緒運鏡",
          "85mm",
          "F1.4",
          "0.3~0.5 秒"
      )))

check("◓12 解剖級微表情目錄·台詞三拍呼吸·焦外聽者 0.3~0.5 秒錯峰反應在案",
      all(k in _act_dir_34 for k in (
          "解剖級微表情目錄",
          "咬肌（masseter）",
          "台詞前 / 中 / 後三拍呼吸律",
          "焦外聽者非靜止與 0.3~0.5 秒錯峰反應律"
      )))

check("◓13 陰影側取景（shadow side）與純實用光防藍光色溢（blue spill）及 60:30:10 色彩配比在案",
      all(k in _lgt_af_34 for k in (
          "陰影側取景（Shadow-Side Shooting）",
          "shadow side",
          "practicals",
          "blue spill",
          "60:30:10"
      )))

check("◓15 D鎖首項獨立彈出「① 末幀定格承接」且清零舊「①+② 默認組合」捆綁殘留",
      "① 末幀定格承接" in skill and "①+② 為連續劇情多段的默認組合" not in skill and "禁止合併為①+②" in skill)
_dpl = read(os.path.join(_sb_dir, "director-param-library.md"))
_spb = read(os.path.join(_sb_dir, "style-prefix-blocks.md"))
check("◓16 畫風鎖參數庫與成品塊已補齊路陽+國漫3D仙俠/遊戲CG/3D進階水墨/東方神話3D等 14 張主力卡完整 11 槽位",
      all(k in _dpl and k in _spb for k in ("徐克", "王家衛", "路陽", "袁和平", "烏爾善", "張藝謀", "樸贊鬱", "大衛·芬奇", "羅傑·狄金斯", "MAPPA", "國漫3D仙俠", "暗黑神話遊戲CG", "國漫3D進階水墨", "東方神話3D奇幻")))
_sbl_txt = read(os.path.join(BASE, "references", "storyboard-board-lite.md"))
check("◓17 看板契約與 model-adapters 已清除「不另寫文字描述/P2.5空殼佔位」誤導並強制掛接 sd-asset-engine 三模板",
      "character-portrait-templates.md" in _sbl_txt and "scene-grid-template.md" in _sbl_txt and "prop-template.md" in _sbl_txt
      and "不另寫文字描述" not in _mdl_adp)
check("◓18 運鏡動靜隨劇情自然發生鎖：廢除「其餘鏡頭一律寫固定」死名額 + C18j非打戲放寬至0.85防誤殺",
      "其餘鏡頭一律寫固定" not in _cam_sys
      and "_c18j_ratio_cap = CAM_FIXED_RATIO_MAX if _combat_on(text, combat) else 0.85" in _vp3)
_ac_p = os.path.join(BASE, "scripts", "audit_contract.py")
_r_ac = subprocess.run([sys.executable, _ac_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_ac_p) else None
check("◓19 全流程交付契約與權威源核銷器 audit_contract.py 在位且 --self-test 通過（聯動 validate_prompt C31 與 SKILL 三防鐵律）",
      _r_ac is not None and _r_ac.returncode == 0 and "PASSED" in (_r_ac.stdout or "")
      and "C31" in _vp3 and "audit_contract.py" in _master,
      (_r_ac.stdout or _r_ac.stderr) if _r_ac else "缺失 audit_contract.py")
check("◓20 全能參考極簡 @ 鐵律（禁二次介紹外觀 C26e）+ 隨身道具全程 @ 跟隨鐵律（C26f）在案且互鎖",
      "C26e" in _vp3 and "C26f" in _vp3 and "嚴禁在後面二次介紹" in _mdl_adp and "隨身道具全程 @ 跟隨鐵律" in _mdl_adp)
check("◓21 實測拉片六條死律（禁比喻 C20c / 單人鏡禁點名他角 C20f / 禁多重視線 C20g / 群像朝向 C20h / 跨窗遞傘穿模與開合態鎖 C20i / 懸空局部詞 C20j）在案且互鎖",
      all(k in _vp3 for k in ("C20f", "C20g", "C20h", "C20i", "C20j", "如鐘", "傘尖懸在")) and "5.0.4b 實測拉片" in _mdl_adp and "文戲道具物理因果鏈與 AIGC 反穿模劇本設計鐵律" in _epp)
check("◓22 xuanhuan-combat-director V2.6.0 Ultimate 全量繼承與機檢閉環（C2支持打戲2~3s細切 / C30a四件套4維全齊AND三層元素 / C30b法武合一11環動力鏈 / C30e禁相持架招 / C30f禁假攻擊 / C30g四收束協議A~D / C30i中全景禁90°正側拍）",
      all(k in _vp3 for k in ("C30_SCALE_FRAME", "C30_SCALE_MACRO", "C30_SCALE_REF", "C30_SCALE_TINY", "C30e", "C30f", "C30g", "C30i", "_is_cmb_seg"))
      and "xuanhuan-combat-director V2.6.0 Ultimate 全量 9 份庫強制必讀" in skill)
check("◓14 投餵轉譯表與 compile_feed.py 遵循 C20m 零默認攝影機理論廢話注入互鎖",
      "Lubezki × Deakins 物理運鏡與光學鎖焦轉譯表" in _eng_cl_34
      and "optics_and_camera_lock" in _cmp_fd_34 and "C20m" in _cmp_fd_34)

_cil_23 = read(os.path.join(PKG, "sd-combat-engine", "references", "combat-iron-laws.md"))
_r1c_23 = read(os.path.join(PKG, "sd-real-engine", "references", "r1-combat-core.md"))
# P14：案例示例整體剔除 → 原「示例稿二次複述清零」升級為「示例文件不得再現」
_ex_gone_23 = [p for p in (
    os.path.join(_sb_dir, "examples", "demo-feed-wkw-15s.md"),
    os.path.join(_sb_dir, "examples", "demo-feed-xuke-15s.md"),
    os.path.join(PKG, "sd-real-engine", "references", "storyboard-example.md"),
    os.path.join(BASE, "examples", "stability-project.json"),
) if os.path.exists(p)]
check("◓23 全包消除「補丁打補丁/左右互搏」與「獨立包沒通電」閉環（鐵律24禁比喻 / R1定格與C11b打通 / 案例示例零殘留 / gate_check兼容###段N / C25d-e與C30j-l通電 / CLI高危硬阻斷）",
      "嚴禁文學比喻" in _cil_23 and "如活物" not in _cil_23
      and "定鏡收束" in _vp3 and "「定格」與「定鏡收束」分工鐵律" in _r1c_23
      and not _ex_gone_23
      and "unit_hdr_re" in _gc_txt
      and all(k in _vp3 for k in ("C25d", "C25e", "C30j", "C30k", "C30l", "FATAL_WARN_PREFIXES", "_is_combat_plugin")),
      "示例殘留：" + ", ".join(_ex_gone_23) if _ex_gone_23 else "")

check("◓24 火山方舟官方（Seedance 2.0/2.5）與 GitHub 五大深水區破局規程在案（四格板裁單圖與≥4人Group-First合圖 / 每鏡句尾環境微鎖 / 前刪6幀後刪1幀與白模中轉 / 全模態參考槽與同音字注音 / 原生語速與後期倍速解耦）",
      "5.0.4c 火山方舟官方" in _mdl_adp
      and "Group-First I2V" in _mdl_adp
      and "Shot-Level Lock Tail" in _mdl_adp
      and "前刪 6 幀 + 後刪 1 幀" in read(os.path.join(BASE, "references", "segment-splicing.md")))

# ================================================================
# [E*36] 畫風鎖「選卡表 / 引擎 / 參數庫」三方對賬域（2026-10-15 Agent 修復）
# ================================================================
# 動機：2026-10-14 的 n 版用「加 4 張國漫3D 卡」的方式補卡，卻**頂掉了原有 4 張卡**
#       （皮克斯 / 迪士尼經典 / 皮埃爾·孔切·平面插畫 / Nelagraphs·長條漫畫風），
#       並把 T8 家族縮編（宮崎駿 / 京阿尼 掉出家族）、參數庫重複編號 + 「其餘 N 組」算錯。
#       **全程無任何斷言覆蓋** —— 換卡 / 漏族 / 數字漂移全靠人工體檢才發現。
# 本域把「卡數 / 編號 / 家族歸屬 / 章節號 / 算式」全部變成真斷言。
section("[E*36] 畫風鎖三方對賬域（選卡表 / 推薦引擎 / 參數庫 · 2026-10-15 補）")

_sb = os.path.join(BASE, "references", "style-bible")
_cat = read(os.path.join(_sb, "director-style-catalog-74.md"))
_lad = read(os.path.join(BASE, "scripts", "style-lock-ladder.py"))
_pro = read(os.path.join(_sb, "style-lock-protocol.md"))
_par = read(os.path.join(_sb, "director-param-library.md"))
_mtx = read(os.path.join(_sb, "style-fit-and-combat-matrix.md"))

# ---- ① 選卡表：卡數自洽 + 編號唯一 + 停用號位聲明 ----
# ⚠️ 卡名單元格可能形如 `**國漫3D仙俠**（玄機/凡人/仙逆系）`，故只強約束「行首是編號 + 至少有第 2 列」，
#    不把卡名內部結構寫進正則（寫死了會漏掉帶括號/斜槓的卡，誤報「表頭 N 實際 M-7」）。
_cat_rows = re.findall(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|", _cat, re.M)
_cat_nos = [int(n) for n, _ in _cat_rows]
_cat_names = [re.sub(r"[\s*]", "", nm) for _, nm in _cat_rows]
_cat_total = re.search(r"導演風格候選庫（(\d+) 組）", _cat)
_cat_total = int(_cat_total.group(1)) if _cat_total else -1
check("◔1 選卡表卡數自洽：實際行數 == 標題聲稱組數（防「表頭寫 N、實際 M」）",
      len(_cat_nos) == _cat_total and _cat_total > 0,
      f"標題稱 {_cat_total} 組 · 實際 {len(_cat_nos)} 行")
check("◔2 選卡表編號唯一無重複（防頂號 / 重號）",
      len(set(_cat_nos)) == len(_cat_nos),
      "重號: " + ", ".join(str(x) for x in sorted({n for n in _cat_nos if _cat_nos.count(n) > 1})))
check("◔3 已停用號位 67 / 70 不得再出現在表內，且停用說明在案",
      67 not in _cat_nos and 70 not in _cat_nos
      and "67 / 70 兩個號位已停用" in _cat)
check("◔4 四張補回卡（皮克斯 / 迪士尼經典 / 皮埃爾·孔切·平面插畫 / Nelagraphs·長條漫畫風）"
      "以新號位 73~76 在位",
      all(k in _cat for k in ("皮克斯", "迪士尼經典", "皮埃爾·孔切 / 平面插畫", "Nelagraphs / 長條漫畫風"))
      and all(str(n) in [str(x) for x in _cat_nos] for n in (73, 74, 75, 76)))
check("◔5 宮崎駿 / 京阿尼 不再作為可選項（錶行內已無這兩張卡）",
      not any(("宮崎駿" in nm or "京阿尼" in nm) for nm in _cat_names)
      and "宮崎駿" in _cat)   # 卡名只允許出現在「停用說明」裡，作為沿革錨點

# ---- ② 引擎與文檔 T 族表雙向一致（成員 + 星級）----
_eng = {}
for _m in re.finditer(r'\((\d+),\s*"([^"]+)",\s*T(\d),\s*(\d),\s*(\d),', _lad):
    _no, _nm, _f, _a, _b = _m.groups()
    _eng[_nm] = (f"T{_f}", int(_a), int(_b))
_doc = {}
for _line in _pro.splitlines():
    _mm = re.match(r"^\|\s*\*\*(T\d)\*\*\s*\|[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$", _line)
    if _mm:
        # ⚠️ 分隔符是「空格·空格」，而卡名內部的 · 兩側無空格（羅傑·狄金斯 / 韋斯·安德森 / 呂貝·貝松）
        #    —— 若只按 `·` 切會把這類卡名腰斬，誤報「文檔獨有 安德森 / 林奇 / 狄金斯」。
        for _chunk in re.split(r"\s+·\s+", _mm.group(2)):
            _chunk = _chunk.strip()
            if not _chunk:
                continue
            _parts = _chunk.rsplit(" ", 1)
            if len(_parts) == 2 and re.fullmatch(r"\d/\d", _parts[1]):
                _doc[_parts[0].strip()] = (_mm.group(1), int(_parts[1][0]), int(_parts[1][2]))
check("◔6 引擎 STYLES 與文檔 T 族表雙向一致（成員集合 + 家族 + 打鬥★/特效★）",
      _eng == _doc,
      f"引擎獨有: {sorted(set(_eng) - set(_doc))} ｜ 文檔獨有: {sorted(set(_doc) - set(_eng))} ｜ "
      f"不一致: {[(k, _eng[k], _doc[k]) for k in sorted(set(_eng) & set(_doc)) if _eng[k] != _doc[k]]}")
check("◔7 宮崎駿 / 京阿尼 已從推薦引擎 STYLES 與 AFFINITY 摘除（防「表裡沒有、引擎還能推」）",
      "宮崎駿" not in _lad and "京阿尼" not in _lad)

# ---- ③ 參數庫：章節號唯一 + 補錄算式自洽 ----
_par_heads = re.findall(r"^##\s*([一二三四五六七八九十]+)\s*、", _par, re.M)
check("◔8 參數庫章節號唯一（防「十二/十三/十四 各出現兩次」造成引用歧義）",
      len(set(_par_heads)) == len(_par_heads),
      "重複編號: " + ", ".join(sorted({h for h in _par_heads if _par_heads.count(h) > 1})))
_rest = re.search(r"其餘\s*(\d+)\s*組的擴展補錄模板", _par)
_rest = int(_rest.group(1)) if _rest else -1
_main_cards = len(re.findall(r"^\|\s*\*\*\d+ [^|]+\|\s*T\d\s", _par, re.M))
check("◔9 參數庫補錄算式自洽：其餘 N == 選卡表卡數 − 已參數化主力卡數",
      _rest == _cat_total - _main_cards and _main_cards > 0,
      f"其餘 {_rest} 組 vs 實算 {_cat_total} − {_main_cards} = {_cat_total - _main_cards}")

# ---- ④ 跨文件數字唯一 + 紅線 2 交叉引用 ----
check("◔10 全包不得殘留「72 組」舊口徑（選卡表已 74 組）",
      "72 組" not in _pro + _mtx + _par + skill
      and "72組" not in read(os.path.join(_sb, "director-style-catalog-74.md")),
      "仍有文件寫 72 組")
check("◔11 model-adapters 保留《素材接線單》紅線 2「圖號雙向一致」的就地交叉引用",
      "紅線 2" in _mdl_adp and "雙向一致" in _mdl_adp)
check("◔12 題材矩陣兩表聲明數 == 實際行數（防「稱 24 組實 26 行」）",
      "篩出的 26 組" in _mtx and "不適合打戲的風格（16 組" in _mtx)

# ---- ⑤ recommend 引擎（題材→候選池）與目錄對賬（2026-10-15 補 · 防路由靜默漏推/幽靈卡）----
#   背景：recommend 是獨立原型，check_package 此前只校驗 ladder，致它相對目錄悄悄漂移而無人發現：
#   #30 掛成押井守（目錄 #30=鈴木敏郎，押井守實為 #28）、#55 人名錯、路由引用 15/17/21/35 卻查無此卡。
#   本組把 recommend 的「編號唯一 / 路由引用可達 / 編號不超目錄」變成真斷言。
#   ✅ #61 歧義已於 2026-10-15 裁定：目錄 #61=斯文·尼奎斯特（#52~#61 為攝影大師區塊，錫蘭不在目錄），
#      引擎三處（ladder/protocol/recommend）+ 矩陣 + validate_prompt C23 全部由「錫蘭」改「斯文·尼奎斯特」；
#      並新增 ◔16（ladder 卡名↔目錄同號位一致）堵住這類「引擎↔目錄卡名」漂移。
_rec = read(os.path.join(BASE, "scripts", "style-lock-recommend.py"))
_rec_nums = [int(n) for n in re.findall(r'^\s*\((\d+),\s*"[^"]+",\s*\d,\s*\d,', _rec, re.M)]
check("◔13 recommend 引擎 STYLES 編號唯一無重複",
      len(set(_rec_nums)) == len(_rec_nums),
      "重號: " + ", ".join(str(x) for x in sorted({n for n in _rec_nums if _rec_nums.count(n) > 1})))
_route_ref = set()
# ⚠️ 必須含逗號（≥2 個編號）才算路由列表——否則會把代碼裡的數組索引 best[0]/s[2] 誤當路由。
for _mm in re.finditer(r'\[(\d+(?:\s*,\s*\d+)+)\]', _rec):
    for _x in _mm.group(1).split(","):
        _x = _x.strip()
        if _x.isdigit():
            _route_ref.add(int(_x))
_miss_route = [n for n in sorted(_route_ref) if n not in _rec_nums]
check("◔14 recommend 引擎 GENRE_ROUTES 引用的編號都存在於 STYLES（防「路由查無此卡」靜默漏推）",
      not _miss_route, "路由引用但 STYLES 缺失: " + ", ".join(map(str, _miss_route)))
_oob_rec = [n for n in _rec_nums if n not in set(_cat_nos)]
check("◔15 recommend 引擎 STYLES 編號都在選卡表目錄內（防引用目錄外幽靈卡）",
      not _oob_rec, "目錄外編號: " + ", ".join(map(str, _oob_rec)))

# ---- ⑥ ladder STYLES 卡名 ↔ 選卡表目錄同號位一致（2026-10-15 補 · 堵 #61 類漂移）----
#   病根：◔6 只校驗 ladder↔protocol，從沒校驗「ladder 卡名 ↔ 目錄卡名」→ #61 引擎長期寫「錫蘭」
#   （目錄實為「斯文·尼奎斯特」，且錫蘭根本不在 74 卡目錄內）而無人發現。本斷言把「引擎每個號位的
#   卡名必須能在目錄同號位對上」變成真斷言。寬鬆匹配容納簡稱：芬奇=大衛·芬奇 / 押井守動畫向⊃押井守。
_cat_map = {int(n): re.sub(r"[\s*]", "", nm) for n, nm in _cat_rows}
_lad_pairs = {int(_m.group(1)): _m.group(2)
              for _m in re.finditer(r'\((\d+),\s*"([^"]+)",\s*T\d,\s*\d,\s*\d,', _lad)}
def _name_ok(a, b):
    a = re.sub(r"[\s·]", "", a or ""); b = re.sub(r"[\s·]", "", b or "")
    return (not a or not b) or a == b or a in b or b in a or a[:2] == b[:2]
_name_drift = [(n, nm, _cat_map[n]) for n, nm in _lad_pairs.items()
               if n in _cat_map and not _name_ok(nm, _cat_map[n])]
check("◔16 ladder STYLES 卡名與選卡表目錄同號位一致（堵 #61「引擎錫蘭 vs 目錄斯文·尼奎斯特」類漂移）",
      not _name_drift,
      "卡名漂移: " + "; ".join(f"#{n} {nm}≠{c}" for n, nm, c in _name_drift))

# ---- ⑰ 閘門5 模型分檔 + 分組門檻 + 2.0 圖數口徑（2026-10-17 補）----
#   病根：閘門5 原寫死 `if len(figs) > 9`，**不讀 --model**，與文檔閘門5（2.0≤9 / 2.5≤30）
#   脫節 → 一個常數造成雙向誤判（2.5 掛 10~30 被誤殺、2.0 掛 2~9 被漏放）。
#   本輪同時把粉絲「森林」反饋中站得住的兩條（資產隔離 / ② 接口餘量）落成規則，
#   故一併上鎖：**改回舊寫法或刪掉規則段，本節立刻轉紅**。
section("[E*37] 閘門5 模型分檔 · 分組三門檻 · 2.0 圖數口徑域（2026-10-17 補）")

_gc_feed = read(os.path.join(sub_skill_path("sd-feed-engine") or "", "scripts", "gate_check.py"))
_gates_doc = read(os.path.join(sub_skill_path("sd-feed-engine") or "", "references", "feed-mode-and-gates.md"))
_asset_doc = read(os.path.join(sub_skill_path("sd-feed-engine") or "", "references", "asset-mapping-and-rules.md"))
_seg_doc = read(os.path.join(BASE, "references", "segment-splicing.md"))
_skill_doc = skill

check("◑18 閘門5 已按模型分檔：IMG_LIMIT_BY_MODEL + img_gate_check 純函數在案，且無寫死 `if len(figs) > 9:`",
      ("IMG_LIMIT_BY_MODEL" in _gc_feed)
      and ("img_gate_check" in _gc_feed)
      and ("'2.5': 30" in _gc_feed)
      and not re.search(r'if\s+len\(figs\)\s*>\s*9\s*:', _gc_feed),
      "閘門5 仍是寫死 9 或分檔表被刪（2.5 會被誤殺 / 2.0 會被漏放）")

check("◑19 閘門5·補「分組三重門檻」在案（時長 / 資產數 / 資產隔離）且含邊界說明",
      all(k in _gates_doc for k in ("分組三重門檻", "資產隔離", "同一角色的不同形態",
                                     "別讀成「同角色不能跨組」")),
      "分組三門檻缺失或邊界說明丟失（會被誤讀成「同角色不能跨組」）")

check("◑20 資產隔離升為第五條鐵律，且與「相鄰編號」分層並存寫明",
      ("五條鐵律" in _asset_doc) and ("同角色多形態分組建" in _asset_doc) \
      and ("分層生效" in _asset_doc or "分層並存" in _asset_doc),
      "asset-mapping-and-rules 鐵律未升到五條，或未寫明與第 4 條的分層關係")

check("◑21 D 鎖② 接口餘量 + 段縫 ①/② 分流表在案（總控 SKILL 與 segment-splicing 雙落點）",
      ("接口餘量" in _seg_doc) and ("分流表" in _seg_doc) \
      and ("段縫 ①/② 分流口徑" in _skill_doc) and ("默認值" in _skill_doc),
      "② 接口餘量或 ①/② 分流口徑缺失")

_old20 = [rel(p) for p in scan_rule_docs()
          if re.search(r'Seedance 2\.0\s*單圖 1 張', read(p))
          or re.search(r'2\.0\s*單圖綁定（1 張', read(p))
          or re.search(r'\*\*Seedance 2\.0\*\*\s*單圖綁定', read(p))]
check("◑22 Seedance 2.0 圖數口徑已統一（全包不得殘留「單圖 1 張」舊口徑）",
      not _old20, "仍寫單圖 1 張: " + ", ".join(_old20))

# ★2026-10-17 達爾文檢測補：本輪給 gate_check.py 新增 --img-limit，若只改腳本不改用法索引，
#   等於又製造一處「腳本改了文檔沒改」（本包早前那輪「修A漏B」同型病）。
_feed_skill = read(os.path.join(sub_skill_path("sd-feed-engine") or "", "SKILL.md"))
check("◑23 gate_check 新參數 --img-limit 已同步到子技能快速索引（防「腳本改了文檔沒改」）",
      ("--img-limit" in _gc_feed) and ("--img-limit" in _feed_skill),
      "gate_check 有 --img-limit 但 sd-feed-engine/SKILL.md 用法行未同步")

check("◑24 sd-feed-engine 機檢碼清單已覆蓋 C31 / C32 / C18p（防子技能碼錶停在 C30）",
      all(k in _feed_skill for k in ("C31", "C32", "C18p")),
      "子技能機檢碼清單仍停在 C30a~d（與總控 §三 碼錶脫節）")

# ★P11 重寫 ◑25（2026-10-24 · 從「查字面」改為「真跑程序」）：
#   舊實現 `"--self-test" not in read(p)` 只驗證**源碼裡出現過這個字符串**，三條硬傷：
#     ① check_package.py 自己源碼裡有一堆 "--self-test"（它在調別人），於是它把自己
#        也塞進了名單還順利通過——**字符串存在 ≠ 參數可用 ≠ 自測能跑通**；
#     ② 名單裡 5 個腳本（check_asset_blocks / check_p45 / style-lock-ladder /
#        style-lock-recommend / gate_check）從未被真正執行過 --self-test，
#        它們能不能跑通，包級自檢根本不知道；
#     ③ 另有 4 個腳本完全游離在自測體系外（script_feed_diff / validate_seedance_segment_map /
#        generate_emotion_curve / project_bundle），連字符串檢查都沒進。
#   修法：① 名單剔除 check_package.py（檢查者不能遞歸調自己，它的證據是「跑一遍全綠」）；
#        ② 其餘腳本**真起子進程**跑 --self-test 看返回碼；
#        ③ 把游離的 4 個補進自測體系（它們各自實現了 --self-test）。
_gate_scripts = [
    "short-drama-director/scripts/validate_prompt.py",
    "short-drama-director/scripts/check_asset_blocks.py",
    "short-drama-director/scripts/audit_contract.py",
    "short-drama-director/scripts/compile_feed.py",
    "short-drama-director/scripts/sd_core.py",
    "short-drama-director/scripts/build_board_lite.py",
    "short-drama-director/scripts/slice_context.py",
    "short-drama-director/scripts/style-lock-ladder.py",
    "short-drama-director/scripts/style-lock-recommend.py",
    "sd-feed-engine/scripts/gate_check.py",
    "sd-storyboard-engine/scripts/check_p45.py",
    # ★P11 補入：此前完全游離於自測體系之外
    "sd-feed-engine/scripts/script_feed_diff.py",
    "sd-qc-engine/scripts/validate_seedance_segment_map.py",
    "short-drama-director/scripts/generate_emotion_curve.py",
    "short-drama-director/scripts/project_bundle.py",
]
_selftest_bad = []
for _rel in _gate_scripts:
    _abs = os.path.join(PKG, _rel)
    if not os.path.exists(_abs):
        _selftest_bad.append(os.path.basename(_rel) + "(文件不存在)")
        continue
    try:
        _r = subprocess.run([sys.executable, _abs, "--self-test"],
                            cwd=PKG, capture_output=True, text=True, timeout=300)
    except Exception as _exc:
        _selftest_bad.append(os.path.basename(_rel) + f"({type(_exc).__name__})")
        continue
    _pass = bool(re.search(r"\bPASS(?:ED)?\b", _r.stdout))
    _failed = bool(re.search(r"(?m)^(?:\[-\]\s*)?FAIL(?:ED)?\b", _r.stdout))
    if "[SKIP]" in _r.stdout:
        print(f"[SKIP] {_rel}：可選繪圖路徑未驗證")
    if _r.returncode != 0 or not _pass or _failed:
        _tail = (_r.stdout or _r.stderr or "").strip().splitlines()[-1:] or [""]
        _selftest_bad.append(os.path.basename(_rel) + f"(exit {_r.returncode}: {_tail[0][:60]})")
check("◑25 全部門禁腳本 --self-test 實跑通過（防「查字面假綠」）",
      not _selftest_bad,
      "以下腳本 --self-test 實跑失敗：" + "、".join(_selftest_bad))

# ★P11 新增 ◑26：README 徽章必須與實際包體對得上。
#   病根（2026-10-24 核驗）：README 頂部徽章寫「規則庫-50 份 / 文件-164」，
#   而實際是 52 份 / 185 文件；腳本里寫「(177 文件)」「(176 files)」兩處也各說各的。
#   徽章是全包對外唯一的第一眼信息，卻沒有任何斷言管它——它比 SKILL.md 正文更容易漂。
#   口徑：**規則庫份數精確相等**（它是結構性數字）；**文件數只卡不虛報**（徽章寫 185+，
#   包變大不必改 README，但寫成比實際還大就是騙人）。
def _count_pkg_files(root):
    n = 0
    for _dp, _dns, _fns in os.walk(root):
        _dns[:] = [d for d in _dns if d != "__pycache__"]
        n += sum(1 for _f in _fns if not _f.endswith(".pyc"))
    return n


_readme_txt = read(os.path.join(PKG, "README.md"))
_actual_files = _count_pkg_files(PKG)
_m_refs = re.search(r"規則庫-(\d+)%20份", _readme_txt)
_m_files = re.search(r"文件-(\d+)-", _readme_txt)
_m_qc = re.search(r"機檢-C1~C(\d+)", _readme_txt)
check("◑26 README 徽章與實際包體一致（規則庫份數精確 · 文件數不虛報）",
      bool(_m_refs) and int(_m_refs.group(1)) == EXPECTED_REFS
      and bool(_m_files) and int(_m_files.group(1)) <= _actual_files  # Lenmu fork：按上方註釋本意改為「只卡不虛報」（原為 ==）
      and bool(_m_qc) and int(_m_qc.group(1)) == 41,
      "README 徽章：規則庫=%s（應 %d）、文件=%s（實際 %d）、機檢上限 C%s（應 C41）" % (
          _m_refs.group(1) if _m_refs else "缺失", EXPECTED_REFS,
          _m_files.group(1) if _m_files else "缺失", _actual_files,
          _m_qc.group(1) if _m_qc else "缺失"))

# ★P11 新增 ◑27：多段稿端到端迴歸（全包最重要的一條斷言）。
#   病根（2026-10-24）：整套自測都在**單段 10~15 秒的玩具樣本**上直調 `validate()`，
#   而真實生產跑的是 `python validate_prompt.py <多段稿>`。正是這個測試盲區，
#   讓「逐段模式給告警加 `[段N]` 前綴 → 24 個高危碼 startswith 失配 → 全部降級放行」
#   這個 P0 在 462 項包檢全綠的情況下活了整整一個版本：
#   **同一個病句，單段稿 exit=1 阻斷，兩段稿 exit=0 PASSED。**
#   因此這條斷言的形態必須是「端到端 CLI + 真實多段稿 + 已知病句 + 數阻斷條數」，
#   任何一環退回單元測試形態，它就又會漏。樣本由 compile_feed 現場生成，
#   保證測的是**編譯器真實產物**，而不是手寫的理想稿。
_mp_dir = tempfile.mkdtemp(prefix="p11_multiseg_")
try:
    if os.path.join(BASE, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(BASE, "scripts"))
    import sd_core as _sdc
    import copy as _copy
    _st = _sdc.default_project_state()
    _s0 = _st["segments"][0]
    _s1 = _copy.deepcopy(_s0)
    _s1["seg_id"] = "段2"
    _s1["bridge"] = "承接上段末鏡；同場示例，尾幀待生成後核驗。"
    _s1["shots"][0]["spec"] = "全景 · 35mm · 略仰 · 緩拉"   # 與段1 末鏡同景別，排除 C18m
    _st["segments"] = [_s0, _s1]
    _state_p = os.path.join(_mp_dir, "state.json")
    with open(_state_p, "w", encoding="utf-8") as _f:
        json.dump(_st, _f, ensure_ascii=False)
    _feed_p = os.path.join(_mp_dir, "feed.md")
    _rc = subprocess.run([sys.executable, os.path.join(BASE, "scripts", "compile_feed.py"),
                          "--state", _state_p, "--out", _feed_p],
                         capture_output=True, text=True, timeout=180)
    _feed_txt = read(_feed_p)
    # 每段首鏡各注入一處 C20c（手冊明寫的實測事故句「端坐如鐘」）
    _bad_md = _feed_txt.replace("畫面主體：", "畫面主體：端坐如鐘，", 2)
    _bad_p = os.path.join(_mp_dir, "bad.md")
    with open(_bad_p, "w", encoding="utf-8") as _f:
        _f.write(_bad_md)
    _rv = subprocess.run([sys.executable, os.path.join(BASE, "scripts", "validate_prompt.py"),
                          _bad_p, "--model", "2.5"],
                         capture_output=True, text=True, timeout=180)
    _n_block = _rv.stdout.count("[高危實拍必崩阻斷]")
    check("◑27 多段稿迴歸：兩段各一處 C20c → 必須 2 條硬阻斷 + exit=1",
          _rc.returncode == 0 and _n_block == 2 and _rv.returncode == 1,
          "編譯器 rc=%s（應 0）/ 硬阻斷=%d 條（應 2）/ validate rc=%s（應 1）"
          % (_rc.returncode, _n_block, _rv.returncode))
finally:
    shutil.rmtree(_mp_dir, ignore_errors=True)

_p12 = subprocess.run([sys.executable, os.path.join(BASE, 'scripts', 'test_p12_regression.py'), '-v'],
                      cwd=PKG, capture_output=True, text=True, timeout=300)
check('◑28 P12 標籤/狀態/C40/顯式橋接/五碼與多格式真實CLI迴歸',
      _p12.returncode == 0 and re.search(r'(?m)^OK$', _p12.stderr) is not None,
      (_p12.stdout + _p12.stderr)[-2000:])

# ---------------------------------------------------------------- 彙總
print()
print("-" * 62)
if FAILED:
    print(f"[-] {len(FAILED)} 項未通過：")
    for f in FAILED:
        print(f"      · {f}")
    sys.exit(1)
print(f"[+] 全部檢查通過（現行版本 V{VERSION} · references {len(refs)} 份 · "
      f"{len(SUB_SKILLS)} 子技能 · 本套裝掃描 {len(scan_md_files())} 個 Markdown）")
