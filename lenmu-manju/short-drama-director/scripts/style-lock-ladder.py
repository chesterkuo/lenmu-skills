# -*- coding: utf-8 -*-
"""
I 畫風鎖 · 遞進式選擇引擎
來源：審計工作區原型 f_lock_ladder.py，邏輯未改，僅改在案口徑。
Step1 影像基底(自動) → Step2 技法家族(給3族) → Step3 導演卡(≤4張) → Step4 可選輔助質感
設計要點：每步都在排除；排除鏈可追溯；同族 ≤2 張；打鬥★/特效★ 為硬門檻。
用法：python style-lock-ladder.py  （內置 5 個題材自測例）
"""
import re

# ============================================================
# 風格庫：(編號, 名稱, 技法族, 打鬥★, 特效★, 一句話特徵, 易跑偏, AI落地度, 題材)
# ============================================================
T1, T2, T3, T4, T5, T6, T7, T8 = "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"

STYLES = [
    # ---- T1 刃光派 ----
    (9,  "徐克",      T1, 3, 3, "高反差硬光·廣角低機位仰拍·體積霧·凌厲升格", "塑料三渲二 / 遊戲CG均勻打光", "B", "武俠玄幻"),
    (7,  "路陽",      T1, 3, 2, "冷青灰配燭火暖橙·低機位貼身跟拍·快刃三五合", "長鏡過難須拆跟拍切鏡 / 禁五彩仙俠光球", "B", "武俠動作"),
    (12, "袁和平",    T1, 3, 2, "硬橋硬馬真實發力鏈·兵器形制特寫·中全景交代", "招式堆砌 / 禁隔空對波", "B", "武俠動作"),
    (38, "塔倫蒂諾",  T1, 3, 1, "極低機位仰拍·復古類型色·章節感",           "時代錯位 / 特效單薄",       "A", "犯罪暴力"),
    (44, "昆汀",      T1, 3, 1, "低機位仰拍·章節字幕·九十年代質感",        "同上",                     "A", "犯罪暴力"),
    (39, "芬奇",      T1, 2, 2, "冷綠低照度·硬邊光·秩序構圖",             "過冷過暗 / 打鬥看不清",    "A", "懸疑犯罪"),
    (37, "維倫紐瓦",  T1, 2, 3, "單色主導·巨物壓迫·塵霧瀰漫",             "色調過灰 / 節奏拖沓",      "A", "科幻史詩"),
    (42, "庫布里克",  T1, 3, 2, "絕對對稱·冷暖極端分離·固定長鏡",         "AI難撐，須降級為固定對稱", "C", "哲學驚悚"),
    # ---- T2 冷峻秩序派 ----
    (10, "王家衛",    T2, 0, 0, "抽幀殘影·霓虹暖黃交錯·狹窄空間貼身手持", "禁粒子禁高幀率，打戲禁用", "B", "都市情感"),
    (33, "樸贊鬱",    T2, 3, 2, "中軸對稱·高對比·冷藍深紅",               "造作 / 儀式感過重",        "A", "驚悚暴力"),
    (52, "羅傑·狄金斯", T2, 2, 2, "陰影側取景·純實用光源·冷暖分離·10~15cm緩推", "禁無源夜戲藍光 / 禁正面平光", "A", "實拍光影"),
    (11, "杜琪峰",    T2, 0, 1, "長焦壓縮·冷靜機位·疏離構圖·灰藍調",     "節奏過平 / 缺情緒抓手",    "A", "都市寫實"),
    (40, "韋斯·安德森", T2, 0, 0, "正面中軸·粉彩低飽和·舞台式佈景",        "打鬥變擺拍",                "A", "喜劇美學"),
    (41, "大衛·林奇",  T2, 1, 1, "強色光源·廣角變形·夢境空間",           "非自然配色 / 觀眾出戲",    "B", "超現實"),
    # ---- T3 柔光寫實派 ----
    (17, "李安",      T3, 0, 1, "自然側光·中景為主·低飽和·留白",         "節奏過緩 / 缺視覺衝擊",    "A", "剋制寫實"),
    (25, "是枝裕和",  T3, 0, 0, "家庭實景·窗側自然光·中近景",             "無動作 / 情緒平",          "A", "家庭日常"),
    (31, "高畑勳",    T3, 2, 1, "淡雅寫實·溫和光·織物與器物細節",         "動作幅度小",                "A", "溫柔寫實"),
    (30, "鈴木敏郎",  T3, 0, 0, "水彩手繪·柔和日光·淡雅彩",               "無動作",                    "A", "生活質感"),
    (51, "呂貝·貝松", T3, 1, 1, "兒童視角低機位·暖自然光·靜謐",           "不適合打鬥",                "A", "童年視角"),
    # ---- T4 濃豔裝飾派 ----
    (1,  "張藝謀",    T4, 1, 2, "大色塊·對稱儀式感·民藝濃豔",             "配色過豔 / 人物失焦",      "A", "儀式敘事"),
    (21, "王童",      T4, 1, 1, "民間裝飾紋樣·濃飽和·圖畫性構圖",         "畫面擁擠 / 缺縱深",        "A", "視覺華麗"),
    (15, "李少紅",    T4, 0, 1, "柔焦·濃豔綢緞·對稱簾幕·燭光暖影",       "過甜 / 缺質感",             "A", "古典唯美"),
    (16, "劉鎮偉",    T4, 1, 2, "高飽和奇幻·柔光人像·藍紫幻光",         "廉價影樓感",                "A", "港式奇幻"),
    (35, "金炯柱",    T4, 0, 1, "高飽和撞色·裝飾性構成·時尚造型感",       "過時尚 / 脫離題材",         "A", "時尚視覺"),
    # ---- T5 紀實手持派 ----
    (18, "侯孝賢",    T5, 0, 0, "固定遠景長鏡·真實環境光",                "打鬥會被看淡",              "B", "文藝寫實"),
    (34, "李滄東",    T5, 0, 0, "粗糲手持·真實自然光·灰土調",             "非動作向",                  "A", "社會寫實"),
    (45, "索德伯格",  T5, 1, 0, "冷調自然光·輕手持·街拍感",               "動作鬆散",                  "A", "街拍犯罪"),
    (57, "荒木經惟",  T5, 0, 1, "高ISO噪點·侵入式近距·弱光冷綠",          "噪點過量 / 人物變形",      "B", "侵入視角"),
    (53, "霍伊特",    T5, 1, 0, "手持·自然光·自然運動模糊·抓拍構圖",      "畫面不穩 / 主體丟失",       "A", "紀錄感"),
    # ---- T6 極端寫意派 ----
    (49, "塔可夫斯基", T6, 0, 1, "自然光·水與霧·極長鏡",                  "AI亦難撐，須拆靜幀+慢鏡",   "C", "詩電影"),
    (61, "斯文·尼奎斯特", T6, 0, 0, "自然光·柔和低反差·中遠景·靜止長拍",       "無動作",                    "B", "極簡長鏡"),
    (23, "北野武",    T6, 1, 0, "極簡固定鏡·大段空鏡·驟停畫格",           "打鬥會被剪成靜止",           "C", "極簡暴力"),
    (8,  "畢贛",      T6, 0, 0, "潮溼霧氣·隧道霓虹·長焦壓縮",             "時間失速，無動作語法",       "C", "文藝詩電影"),
    (50, "帕索里尼",  T6, 1, 1, "極遠景平視·黃昏低角度光·油畫筆觸",       "人物過小 / 敘事斷裂",       "B", "古典油畫"),
    # ---- T7 神話史詩派 ----
    (66, "暗黑神話遊戲CG", T7, 3, 3, "虛幻5主機遊戲CG·高精PBR戰損甲冑·暗黑高光比·丁達爾體積霧", "禁2D卡通平塗 / 禁輕飄無重力", "A", "遊戲CG暗黑神話"),
    (72, "東方神話3D奇幻", T7, 3, 3, "東方神話3D電影感·織金玉石次表面散射·青綠赤金·巨物法相奇觀", "禁2D粗黑邊 / 禁陰暗廢土風", "A", "東方神話3D"),
    (6,  "烏爾善",    T7, 3, 3, "巖畫獸紋·巨大體量對比·土紅骨白·篝火暖光", "西方奇幻鎧甲 / 廉價土黃",   "A", "神話史詩(實拍)"),
    (47, "卡梅隆",    T7, 2, 3, "巨物·冷藍·高動態範圍·奇觀場面",         "重技術輕動作",              "A", "技術奇觀"),
    (29, "大友克洋",  T7, 2, 3, "冷金屬機械·微距·硬表面反射",             "機械過密 / 人物被吞",       "A", "機甲科幻"),
    (36, "諾蘭",      T7, 2, 2, "巨物尺度·冷藍高對比·中軸對稱",           "動作偏重 / 節奏慢",         "A", "科幻動作"),
    (46, "雷德利",    T7, 1, 2, "古典油畫感·厚實暗部·暖金燭光",           "打鬥偏陣仗",                "A", "古典史詩"),
    (22, "黑澤明",    T7, 3, 1, "自然硬光·實景搭景·多機位群像",          "無特效傳統 / 需另補",        "A", "時代劇"),
    # ---- T8 動畫與國漫3D/CG派 ----
    (65, "國漫3D仙俠",     T8, 3, 3, "次世代國漫3D半寫實·PBR絲綢金玉·丁達爾雲霧·流光劍氣", "禁2D粗黑描邊 / 禁廉價塑料反光", "A", "國漫3D修仙玄幻"),
    (71, "國漫3D進階水墨", T8, 3, 3, "國漫3D三渲二水墨·枯筆飛白描邊·狂草墨韻刀氣·硃砂留白對沖", "禁退化為2D剪紙 / 禁死灰濾鏡", "A", "3D進階水墨國風"),
    (64, "MAPPA",     T8, 3, 3, "厚塗質感·高對比陰影·動態變形幀",         "日式賽璐璐 / 表情崩壞",      "A", "2D都市動畫厚塗"),
    (62, "吉卜力",    T8, 2, 2, "手繪水彩背景·柔和日光·雲與風寫實",       "偏飛行自然 / 非硬核打鬥",   "A", "奇幻日常"),
    (63, "新海誠",    T8, 1, 2, "極致高飽和天空·強烈光斑·玻璃反射",       "過甜 / 人物失真",            "A", "都市青春"),
    (68, "押井守動畫向", T8, 2, 3, "冷調·玻璃幕牆·手繪人物+3D背景",       "混合質感不統一",             "B", "賽博動畫"),
]

FAMILY_NAME = {
    T1: "刃光派",   T2: "冷峻秩序派", T3: "柔光寫實派", T4: "濃豔裝飾派",
    T5: "紀實手持派", T6: "極端寫意派", T7: "神話史詩派", T8: "動畫與國漫3D/CG派",
}
FAMILY_FEATURE = {
    T1: "高反差硬光 · 強輪廓 · 廣角低機位仰拍 · 升格慢鏡",
    T2: "冷藍灰調 · 中軸對稱 · 幾何分割 · 低照度",
    T3: "窗側自然光 · 低對比 · 中近景 · 剋制表演",
    T4: "大色塊 · 高飽和 · 對稱儀式感 · 民藝紋樣",
    T5: "粗糲手持 · 自然光 · 灰土調 · 顆粒不修飾",
    T6: "大留白 · 極簡 · 非自然色 · 極長鏡",
    T7: "巨大體量對比 · 逆光塵霧 · 圖騰獸紋 · 硬表面機械",
    T8: "次世代國漫3D建模 · 遊戲CG · 3D三渲二進階水墨 · 2D厚塗賽璐璐",
}

# ★互斥族對：不可作為「主 + 輔」混用
EXCLUSIVE = [({T1}, {T3}), ({T1}, {T4}), ({T1}, {T5}),
             ({T7}, {T8}), ({T2}, {T4}), ({T6}, {T4})]

# ============================================================
# Step 1 · 影像基底
# ============================================================
BASE_ANIME   = "3D CG 動畫"
BASE_LIVE    = "真人實拍質感"
BASE_2D      = "2D 手繪動畫"
BASE_INK     = "水墨二維"

# 各族適配哪些基底（T8 動畫與國漫3D/CG派只配動畫基底，T1/T3/T5 等通用）
FAMILY_BASE = {
    T1: [BASE_ANIME, BASE_LIVE, BASE_2D],
    T2: [BASE_LIVE, BASE_ANIME],
    T3: [BASE_LIVE, BASE_2D],
    T4: [BASE_LIVE, BASE_2D, BASE_ANIME],
    T5: [BASE_LIVE],
    T6: [BASE_LIVE, BASE_2D, BASE_INK],
    T7: [BASE_ANIME, BASE_LIVE],
    T8: [BASE_ANIME, BASE_2D, BASE_INK],
}

# ============================================================
# 題材 → 技法族路由（每場只給 3 族）
# ============================================================
GENRE_FAMILY = [
    (["玄幻", "仙俠", "修真", "鬥法", "神魔", "法術"], [T1, T7, T8]),
    (["武俠", "武打", "械鬥", "江湖", "刀劍"],         [T7, T1, T3]),
    (["機甲", "賽博", "科幻戰鬥"],                    [T7, T8, T2]),
    (["異能", "超能力", "都市戰鬥"],                  [T8, T1, T2]),
    (["懸疑", "犯罪", "暗殺", "警匪", "追車"],        [T2, T5, T1]),
    (["戰爭", "史詩", "神話"],                        [T7, T1, T6]),
    (["恐怖", "驚悚", "靈異"],                        [T2, T5, T1]),
    (["都市情感", "情感", "都市", "職場", "甜寵", "愛情"], [T2, T3, T4]),
    (["懷舊", "年代", "復古", "回憶"],                [T2, T4, T3]),
    (["文藝", "靜思", "詩", "散文", "家庭", "日常"],  [T6, T3, T5]),
    (["青春", "校園", "成長"],                        [T8, T3, T6]),
    (["喜劇", "荒誕"],                                [T2, T4, T5]),
]

GENRE_COMBAT  = ["玄幻","仙俠","修真","武俠","武打","格鬥","動作","戰鬥","打鬥","打戲",
                 "械鬥","暗殺","槍戰","追車","戰爭","搏殺","廝殺"]
GENRE_NOCOMBAT = ["都市情感","情感","文藝","靜思","家庭","日常","青春","懷舊","年代",
                  "甜寵","職場","商戰","懸疑文戲","心理","生活流","散文",
                  "文戲","純對話","劇情向"]   # ★P8 補：文戲/純對話 是分鏡稿最常用的「無打鬥」自述詞
NEG_PREFIX = ["無", "不", "沒有", "沒", "非", "零", "免", "去"]
# ★P8 補：舊實現用 `(p + w) in t` 逐字拼接，只能識別**緊貼**的「無打鬥／沒有打鬥」；
#   「沒有**任何**打鬥」「不含一點打鬥」這類中間隔字的否定仍然判成**有打鬥**
#   （實測：題材串「都市甜寵辦公室，兩人對話，純文戲，沒有任何打鬥」→ 含打鬥=True，
#    依據「信號詞打鬥」→ 甜寵項目被塞一張仙俠打鬥卡）。
#   現改為**前置窗口否定判定**：關鍵詞前 8 字內出現否定詞即視為已被否定。
_NEG_WINDOW_RE = re.compile(
    r"(?:毫無|沒有任何|沒有|不含|無任何|全無|無|沒|不|非|零|免|去)[^，。；、！？\s]{0,4}$")


def _negated_at(t, start):
    return bool(_NEG_WINDOW_RE.search(t[max(0, start - 8):start]))


def _live_hits(t, words):
    """返回在**非否定語境**下真實出現的詞（每個詞只看首處出現即可）。"""
    out = []
    for w in words:
        for m in re.finditer(re.escape(w), t):
            if not _negated_at(t, m.start()):
                out.append(w)
                break
    return out
VFX_HIGH_SIG = ["法術","鬥法","玄幻","仙俠","修真","神通","法陣","大招","神魔","仙術","異能","風暴","領域"]
COMBAT_SIG = ["打鬥","打戲","戰鬥","對決","開打","武打","搏殺","廝殺","對招","交手","格鬥","鬥法","大戰"]


def detect_combat(t):
    live = _live_hits(t, COMBAT_SIG)          # 非否定語境的打鬥信號
    hc = _live_hits(t, GENRE_COMBAT)          # 非否定語境的題材詞
    hn = [w for w in GENRE_NOCOMBAT if w in t]
    if not live and not hc:
        _raw = [w for w in COMBAT_SIG if w in t]
        if _raw:
            return False, f"否定式（「{_raw[0]}」前有否定詞）"
    if hn and not hc:
        return False, f"題材詞「{hn[0]}」非動作向"
    if hc:
        return True, f"題材詞「{hc[0]}」"
    if live:
        return True, f"信號詞「{live[0]}」"
    return False, "無打鬥信號"


def detect_base(t):
    if any(w in t for w in ["禪意", "水墨", "古風意蘊"]):
        return BASE_INK
    if any(w in t for w in ["玄幻", "仙俠", "機甲", "神魔", "3D", "國漫", "高燃"]):
        return BASE_ANIME
    if any(w in t for w in ["手繪", "童話", "水彩", "賽璐璐"]):
        return BASE_2D
    return BASE_LIVE


# ★P8（2026-10-24 · 採納網友建議書 P-02）：影像基底是**必問項**，不是自動判定項。
#   病根：舊版第 193 行字面寫「（不問，自動帶出）」，而 style-lock-protocol.md:46 是
#   2026-10-13 用戶裁定原文「影像基底不得由執行者自動帶出……用戶未表態 = 停下詢問」。
#   腳本與協議直接衝突，且**執行者會照腳本走**——真人項目被自動判成 3D CG，畫質詞 /
#   骨相 / 候選池 / 打戲檔位全錯在源頭（用戶原話：「我這個是真人的哈」）。
#   故 detect_base() 降級為**傾向提示**（suggest），只有用戶顯式給了 --base 才出卡。
BASE_ALIASES = [
    (BASE_LIVE,  ("真人", "實拍", "liveaction", "live-action", "live")),
    (BASE_2D,    ("2d", "手繪", "賽璐璐", "動畫2d", "厚塗")),
    (BASE_ANIME, ("3d", "cg", "國漫", "三維", "動畫3d", "anime")),
    (BASE_INK,   ("水墨", "ink", "國風意蘊")),
]


def parse_base(raw):
    """把用戶回答規整到四種基底之一；認不出返回 None（不許猜）。"""
    if not raw:
        return None
    s = str(raw).strip().lower().replace(" ", "")
    for canon, keys in BASE_ALIASES:
        if s == canon.lower().replace(" ", ""):
            return canon
        for k in keys:
            if k in s:
                return canon
    return None


def route_family(t):
    best = None
    for keys, fams in GENRE_FAMILY:
        hit = [k for k in keys if k in t]
        if hit and (best is None or len(hit) > best[0]):
            best = (len(hit), fams, hit[0])
    if best:
        return best[1], best[2]
    return [T1, T2, T3], "未命中（默認綜合）"


# ============================================================
# 主流程
# ============================================================
def recommend(text, top=4, base=None):
    lines = []
    # ---- Step 1 ----
    suggest = detect_base(text)
    combat, why = detect_combat(text)
    vfx_high = any(w in text for w in VFX_HIGH_SIG)

    lines.append("=" * 84)
    lines.append(f"題材輸入：{text}")
    lines.append("=" * 84)
    lines.append("")
    if base is None:
        # ★P8：不問就不出卡。出卡 = 默認替用戶拍了形態，正是 2026-10-13 裁定要禁的事。
        lines.append("【Step 1 · 影像基底】⛔ 必問項 · 不得自動帶出")
        lines.append("   請先向用戶確認，四選一（用戶未表態 = 停下詢問，禁自行判定）：")
        lines.append("     ① 真人實拍質感    ② 2D 手繪（賽璐璐／厚塗）")
        lines.append("     ③ 3D CG（國漫3D／遊戲CG）    ④ 水墨二維")
        lines.append(f"   機器識別傾向：{suggest} —— **僅供提示，不得當結論**")
        lines.append("   （依據：style-lock-protocol.md §三 · 2026-10-13 用戶裁定「形態必問」）")
        lines.append("")
        lines.append("   → 用戶明確後重跑：python style-lock-ladder.py \"<題材>\" --base=真人|2D|3D|水墨")
        lines.append("   → 基底一旦判錯，畫質詞／形體骨相／候選池／打戲檔位全部跟著錯，且錯在源頭、下游無從糾正")
        return "\n".join(lines)
    lines.append(f"【Step 1 · 影像基底】用戶已確認：{base}")
    lines.append(f"   → 打鬥={combat}（依據：{why}）  高特效={vfx_high}")
    if suggest != base:
        lines.append(f"   ⚠ 機器傾向原為「{suggest}」，與用戶確認不一致 → **以用戶為準**，"
                     f"並按真人/形態口徑重寫 STYLE_PROFILE")

    # ---- Step 2 ----
    fams, gk = route_family(text)
    lines.append("")
    lines.append("【Step 2 · 技法家族】給你 3 族（其餘已排除）")
    excluded_fams = [f for f in FAMILY_NAME if f not in fams]
    for f in fams:
        lines.append(f"   ◆ {f} {FAMILY_NAME[f]:<7}  {FAMILY_FEATURE[f]}")
    lines.append(f"   命中題材族：{gk}")
    lines.append(f"   已排除 {len(excluded_fams)} 族："
                 + " · ".join(f"{FAMILY_NAME[f]}" for f in excluded_fams))
    if combat:
        lines.append("   原因：這些族的打鬥承載均 ≤★1，且部分與硬邊打光互斥")

    # ---- Step 3 ----
    # 排除鏈：① 基底衝突 ② 打鬥門檻 ③ 特效門檻
    pool, excl = [], []
    for s in STYLES:
        num, name, fam, fight, fx, look, warn, grade, genre = s
        if base not in FAMILY_BASE[fam]:
            excl.append((name, fam, f"與影像基底「{base}」衝突"))
            continue
        if fam not in fams:
            excl.append((name, fam, "不在本次技法家族內"))
            continue
        if combat:
            if fight <= 1:
                excl.append((name, fam, f"打鬥承載 ★{fight}，不適合打戲"))
                continue
            if vfx_high and fx < 2:
                excl.append((name, fam, f"特效承載 ★{fx}，撐不住高特效打鬥"))
                continue
        pool.append(s)

    # ★★排序規則（唯一一套，有無打鬥通用）：
    #   題材親和度優先 → 能力總分次之
    #   反面教材（已實測抓到）：無條件按 打鬥★+特效★ 排，
    #     會讓「都市懸疑格鬥」場景把武俠史詩的徐克頂到 A 卡 —— 純荒謬。
    AFFINITY = {
        # 打戲向
        "國漫3D仙俠": ["國漫", "3D", "玄幻", "仙俠", "修仙", "修真", "鬥法", "法術", "劍氣", "宗門", "高燃"],
        "暗黑神話遊戲CG": ["遊戲CG", "CG", "黑神話", "暗黑", "神話", "神魔", "虛幻5", "重工業", "妖魔", "古剎"],
        "國漫3D進階水墨": ["水墨", "三渲二", "國風", "國漫", "3D", "武俠", "仙俠", "劍道", "狂草", "寫意", "鬥法"],
        "東方神話3D奇幻": ["神話", "神魔", "法相", "奇幻", "國漫", "3D", "仙俠", "追光", "天庭"],
        "徐克":   ["實拍", "武俠", "江湖", "刀劍", "打鬥", "香港"],
        "烏爾善": ["實拍", "上古", "戰爭", "史詩", "封神"],
        "MAPPA":  ["2D", "厚塗", "都市異能", "異能", "超能力", "日漫"],
        "維倫紐瓦": ["科幻", "巨物", "神魔", "對轟", "機甲"],
        "卡梅隆": ["科幻", "巨物", "技術", "奇觀", "對轟"],
        "大友克洋": ["機甲", "機械", "賽博", "科幻"],
        "諾蘭":   ["科幻", "巨物", "懸疑", "結構"],
        "黑澤明": ["武俠", "時代", "史詩", "群像", "戰爭"],
        "雷德利": ["戰爭", "史詩", "古典"],
        "袁和平": ["武俠", "動作", "兵器"],
        "路陽":   ["武俠", "動作", "長鏡"],
        "昆汀":   ["犯罪", "追車", "槍戰", "暴力", "章節"],
        "塔倫蒂諾": ["犯罪", "暴力", "復古", "章節"],
        "樸贊鬱": ["暴力", "驚悚", "犯罪", "對稱", "儀式"],
        "芬奇":   ["懸疑", "犯罪", "暗殺", "驚悚", "秩序", "冷"],
        "溫子仁": ["恐怖", "驚悚", "幽閉", "靈異"],
        "大友":   ["機甲", "機械"],
        # 情感/文藝向
        "王家衛": ["情感", "都市", "懷舊", "年代", "夜", "曖昧", "回憶", "愛情"],
        "李安":   ["情感", "家庭", "剋制", "現實", "親情", "倫理"],
        "是枝裕和": ["日常", "家庭", "情感", "孩子", "溫情"],
        "高畑勳": ["日常", "溫柔", "手繪", "童話", "治癒"],
        "鈴木敏郎": ["日常", "手繪", "水彩", "治癒"],
        "李少紅": ["古典", "唯美", "柔焦", "綢緞", "愛情"],
        "張藝謀": ["儀式", "濃豔", "敘事", "民藝", "古裝"],
        "王童":   ["濃豔", "華麗", "裝飾", "民藝", "古裝"],
        "劉鎮偉": ["奇幻", "港式", "柔光", "愛情"],
        "金炯柱": ["時尚", "高飽和", "都市", "甜寵"],
        "杜琪峰": ["都市", "寫實", "疏離", "長焦", "警匪"],
        "韋斯·安德森": ["喜劇", "荒誕", "對稱", "舞台", "荒誕喜"],
        "大衛·林奇": ["夢境", "超現實", "非自然", "懸疑"],
        # 寫實/紀實向
        "侯孝賢": ["寫實", "遠景", "生活", "文藝", "年代"],
        "李滄東": ["社會", "寫實", "灰調", "粗糲", "現實"],
        "索德伯格": ["街拍", "自然", "冷調", "犯罪", "年代"],
        "荒木經惟": ["侵入", "弱光", "日常", "噪點", "紀實"],
        "霍伊特":   ["紀錄", "手持", "抓拍", "運動"],
        # 極端寫意向
        "塔可夫斯基": ["詩", "靜思", "長鏡", "水", "哲思"],
        "斯文·尼奎斯特":  ["極簡", "靜思", "靜止", "自然光", "長鏡", "哲思"],
        "北野武": ["極簡", "暴力", "驟停", "懸疑"],
        "畢贛":  ["詩", "文藝", "溼", "夢境"],
        "帕索里尼": ["古典", "油畫", "遠景", "神話題"],
        # 動畫向
        "吉卜力": ["奇幻", "日常", "手繪", "童話", "治癒"],
        "新海誠": ["青春", "都市", "校園", "高飽和"],
        "押井守動畫向": ["賽博", "科幻", "玻璃", "都市"],
        "押井守": ["賽博", "科幻", "孤獨", "都市"],
    }

    def aff(s):
        return sum(1 for w in AFFINITY.get(s[1], []) if w in text)
    #題材親和優先 → 能力總分次之
    pool.sort(key=lambda s: (aff(s), s[3] + s[4]), reverse=True)
    picked, per_fam = [], {}
    for s in pool:
        f = s[2]
        if per_fam.get(f, 0) >= 2:
            continue
        per_fam[f] = per_fam.get(f, 0) + 1
        picked.append(s)
        if len(picked) >= top:
            break

    lines.append("")
    lines.append(f"【Step 3 · 導演卡】候選池 {len(pool)} 組 · 已排除 {len(excl)} 組 · 出卡 {len(picked)} 張")
    lines.append("")
    for i, (num, name, fam, fight, fx, look, warn, grade, genre) in enumerate(picked):
        tag = "【默認推薦】" if i == 0 else ""
        label = "ABCD"[i] if i < 4 else str(i + 1)
        lines.append(f"  {label} {tag}{name}向· {fam} {FAMILY_NAME[fam]} · {genre}")
        lines.append(f"      看得見：{look}")
        lines.append(f"      易跑偏：{warn}")
        fs = "★" * fight if fight else "—"
        xs = "★" * fx if fx else "—"
        lines.append(f"      打鬥 {fs:<4} 特效 {xs:<4}    AI 落地度 {grade}")
        if grade == "B":
            lines.append(f"      系統將自動補寫法約束（B級）")
        if grade == "C":
            lines.append(f"      ★視頻模型難穩定呈現，須先確認降級方案")
    lines.append("")
    lines.append(f"  D 自定義 → 你直接描述，我按你的描述建 STYLE_BIBLE")

    # ---- Step 4 ----
    # ★修正：Step4 是「選定主族之後，問能不能配輔助族」，
    #   不是把所有候選族都標成可疊加。必須走互斥對查表。
    # ★2026-10-15 修復：候選池被排除鏈排空時，原代碼直接 `picked[0][1]` / `FAMILY_NAME[None]`
    #   → IndexError / KeyError 崩潰（實測「水墨 懸疑 犯罪」：INK 基底 + T2/T5/T1 均不支持 INK）。
    #   排除鏈本就允許排空（可追溯），排空必須優雅降級、保留排除明細，不得崩。
    main_fam = picked[0][2] if picked else None
    lines.append("")
    lines.append("【Step 4 · 可選輔助質感】（可選；不指定 = 不疊加，按主族執行）")
    if not picked:
        lines.append("   ⚠️ 排除鏈把候選池排空：沒有任何導演卡同時滿足"
                     "「影像基底 × 技法家族 × 打鬥/特效門檻」。")
        lines.append("   處理建議：① 換更寬的題材詞（去掉「水墨」這類強基底詞）；"
                     "② 直接走 D 自定義描述你要的質感；③ 核對題材與影像基底是否衝突。")
    else:
        lines.append(f"   假設你選了 A {picked[0][1]}向 · 主族 = {main_fam} {FAMILY_NAME[main_fam]}")
        lines.append("   可疊加的輔助族：")
        any_ok = False
        for f in FAMILY_NAME:
            if f == main_fam:
                continue
            conflict = any((main_fam == a and f == b) or (main_fam == b and f == a)
                           for a, b in EXCLUSIVE)
            if conflict:
                continue
            if f not in fams:
                continue          # 只在本次候選族內談疊加
            eff = {
                T1: "硬光打戲 + 厚塗質感（已實測成立）",
                T2: "硬邊輪廓 + 冷調秩序",
                T3: "強化自然光下的動勢",
                T4: "史詩體量 + 濃豔民藝",
                T5: "秩序構圖 + 粗糲手持",
                T6: "冷調 + 留白疏離",
                T7: "硬光 + 上古圖騰",
                T8: "硬光打戲 + 厚塗質感（已實測成立）",
            }.get(f, "視參數組兼容度而定")
            lines.append(f"     ✓ {f} {FAMILY_NAME[f]:<7} → {eff}")
            any_ok = True
        if not any_ok:
            lines.append("     （本次候選族內無族可疊加，直接按主族執行）")
        lines.append("   不可疊加（互斥，寫死，與是否在本場候選無關）：")
        any_bad = False
        for a, b in EXCLUSIVE:
            if main_fam in (a, b):
                other = (b if main_fam == a else a)
                lines.append(f"     ✗ {other} {FAMILY_NAME[other]:<7} → 互斥"
                             f"（{FAMILY_FEATURE[main_fam][:10]}… ↔ {FAMILY_FEATURE[other][:10]}…）")
                any_bad = True
        if not any_bad:
            lines.append("     （無）")

    # ---- 排除明細 ----
    lines.append("")
    lines.append("【排除明細】（讓你知道系統替你做了什麼）")
    from collections import defaultdict
    byreason = defaultdict(list)
    for nm, fam, rs in excl:
        byreason[rs].append(nm)
    for rs, names in byreason.items():
        lines.append(f"   · {rs}（{len(names)} 組）：" + " · ".join(names[:10])
                     + (" …" if len(names) > 10 else ""))

    return "\n".join(lines)


if __name__ == "__main__":
    # ★P8（2026-10-24 · 採納網友建議書 P-01）：舊版 __main__ 只循環硬編碼示例，**全程不讀
    #   sys.argv** → 任何輸入都輸出同一套「3D CG + 打鬥=True（依據：題材詞「玄幻」）」，
    #   SKILL 與協議宣稱的「題材→候選池路由引擎」實際是**演示腳本**。使用者拍甜寵會拿到
    #   仙俠打鬥卡。現改為：位置參數=題材，--base=用戶已確認的影像基底，--demo=原示例迴歸。
    import sys

    # 迴歸鎖案例（--demo / 無參數時跑；亦作 2026-10-15 INK 排空迴歸）
    demo_cases = [
        "玄幻仙俠打鬥，有法術特效",
        "都市情感夜戲，無打鬥",
        "現代都市懸疑，追車加近身格鬥",
        "神魔級對轟，特效很重",
        "年代懷舊文戲，兩個人回憶往事",
        # ★2026-10-15 迴歸鎖：INK 水墨基底 + 不支持水墨的題材族 → 候選池排空，
        #   舊代碼在此 IndexError/KeyError 崩潰；修復後應優雅降級（出卡 0 張 + 排空提示）。
        "水墨 懸疑 犯罪",
    ]

    args = [a for a in sys.argv[1:]]
    # ★P9：包內慣例是 `--self-test`，本腳本原先只有 `--demo` →「自檢三件套」在這裡
    #   按名字找不到入口（check_package ◑25 已把這條做成結構斷言）。別名等價。
    _selftest = "--self-test" in args
    if not args or "--demo" in args or _selftest:
        print("【演示模式】出卡基底按各示例各自的機器傾向（僅演示，禁當判定依據）")
        print("實質使用：python style-lock-ladder.py \"<題材>\" --base=真人|2D|3D|水墨\n")
        for c in demo_cases:
            print(recommend(c, base=detect_base(c)))
            print("\n\n")
        if _selftest:
            print(f"[+] style-lock-ladder self-test PASSED（{len(demo_cases)} 組內置示例全部出卡未崩）")
        sys.exit(0)

    base_raw, text_parts, top = None, [], 4
    for a in args:
        if a.startswith("--base="):
            base_raw = a.split("=", 1)[1]
        elif a == "--base":
            base_raw = "__MISSING__"      # 只寫 --base 不給值 → 視為未確認
        elif a.startswith("--top="):
            try:
                top = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        elif not a.startswith("--"):
            text_parts.append(a)
    text = " ".join(text_parts).strip()
    if not text:
        print("用法：python style-lock-ladder.py \"<題材串>\" --base=真人|2D|3D|水墨 [--top=4]")
        print("      python style-lock-ladder.py --demo        # 跑內置迴歸示例（--self-test 等價）")
        sys.exit(2)

    base = parse_base(base_raw) if base_raw and base_raw != "__MISSING__" else None
    if base_raw and base_raw != "__MISSING__" and base is None:
        print(f"⚠ 無法識別 --base=「{base_raw}」→ 按「未確認」處理，不出卡。")
        print("   可寫：真人 / 實拍 / 2D / 手繪 / 3D / CG / 水墨")
        base = None

    print(recommend(text, top=top, base=base))
    if base is None:
        # 退出碼 3 = 明確信號「等用戶回答，不是錯誤，也不是完成」
        sys.exit(3)