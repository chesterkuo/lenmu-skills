# -*- coding: utf-8 -*-
"""
I 畫風鎖 · 推薦引擎（題材 → 候選池）
來源：審計工作區原型 f_lock_recommend.py，邏輯未改，僅改在案口徑。
核心：含打鬥時硬排除「不適合打戲」的風格，並把能力標籤寫進候選卡。
知識庫：references/style-bible/（74 組候選源 / 適配矩陣 / 鎖規程）。
用法：python style-lock-recommend.py "<題材串>" [--top=4]（--demo 跑內置示例）
"""
import re

# 風格庫：(編號, 名稱, 打鬥★, 特效★, 原生題材, 一句話特徵, 易跑偏)
STYLES = [
    (65, "國漫3D仙俠",  3, 3, "國漫3D修仙玄幻", "次世代國漫3D半寫實·PBR絲綢金玉·丁達爾雲霧·流光劍氣", "禁2D粗黑描邊/禁廉價塑料反光"),
    (66, "暗黑神話遊戲CG",3, 3, "主機遊戲CG神話", "虛幻5主機遊戲CG·高精PBR戰損甲冑·暗黑高光比·丁達爾體積霧", "禁2D卡通平塗/禁輕飄無重力"),
    (71, "國漫3D進階水墨",3, 3, "3D三渲二水墨",   "國漫3D三渲二水墨·枯筆飛白描邊·狂草墨韻刀氣·硃砂留白對沖", "禁退化為2D平面剪紙/禁死灰濾鏡"),
    (72, "東方神話3D奇幻",3, 3, "東方神話3D電影", "東方神話3D電影感·織金玉石次表面散射·青綠赤金·巨物法相奇觀", "禁2D粗黑邊/禁陰暗廢土風"),
    (9,  "徐克",      3, 3, "武俠/玄幻(實拍)", "高反差硬光·廣角低機位仰拍·體積霧·凌厲升格", "塑料三渲二/遊戲CG打光"),
    (6,  "烏爾善",    3, 3, "神話史詩(實拍)",   "巖畫獸紋·巨大體量對比·土紅骨白·篝火暖光", "西方奇幻鎧甲/廉價土黃"),
    (64, "MAPPA",    3, 3, "2D都市動畫厚塗",   "厚塗質感·高對比陰影·動態變形幀", "日式賽璐璐/表情崩壞"),
    (37, "維倫紐瓦",  2, 3, "科幻史詩",   "單色主導·巨物壓迫·塵霧瀰漫", "色調過灰/節奏拖沓"),
    (47, "卡梅隆",    2, 3, "技術奇觀",   "巨物·冷藍·高動態範圍", "重技術輕動作"),
    (28, "押井守",    2, 3, "賽博科幻",   "冷青·玻璃幕牆反射·長焦靜止構圖", "過於靜止/不像打鬥"),
    (68, "押井守動畫向",2,3, "賽博動畫",   "冷調·玻璃幕牆·手繪人物+3D背景", "混合質感不統一"),
    (29, "大友克洋",  2, 3, "機甲科幻",   "冷金屬機械·微距·硬表面反射", "機械過密/人物被吞"),
    (12, "袁和平",    3, 2, "武俠動作",   "兵器形制特寫·皮甲質感·真實重心發力", "招式堆砌/無鏡頭語言"),
    (7,  "路陽",      3, 2, "武俠動作",   "長鏡頭連貫動勢·冷調·快刃", "長鏡過難/節奏拖"),
    (33, "樸贊鬱",    3, 2, "驚悚暴力",   "中軸對稱·高對比·冷藍深紅", "造作/儀式感過重"),
    (38, "塔倫蒂諾",  3, 1, "犯罪暴力",   "極低機位仰拍·復古類型色·章節感", "時代錯位/特效單薄"),
    (44, "昆汀",      3, 1, "犯罪暴力",   "低機位仰拍·章節字幕·九十年代質感", "同上"),
    (22, "黑澤明",    3, 1, "時代劇",     "自然硬光·實景搭景·多機位群像", "無特效傳統/需另補"),
    (39, "大衛·芬奇", 2, 2, "懸疑犯罪",   "冷綠低照度·硬邊光·秩序構圖", "過冷過暗/打鬥看不清"),
    (48, "溫子仁",    2, 2, "恐怖驚悚",   "極低照度·幽閉·冷綠·局部強光", "太暗/動作丟失"),
    (36, "諾蘭",      2, 2, "科幻動作",   "巨物尺度·冷藍高對比·中軸對稱", "動作偏重/節奏慢"),
    (62, "吉卜力",    2, 2, "奇幻日常",   "手繪水彩背景·柔和日光·雲與風寫實", "偏飛行自然/非硬核打鬥"),
    (42, "庫布里克 ⚠️C",3,2, "哲學驚悚",   "絕對對稱·冷暖極端分離·固定長鏡", "**AI 難撐，須降級為固定對稱**"),
    # ---- 不適合打戲（打鬥 ★0~★1）----
    (10, "王家衛",    0, 0, "都市情感",   "抽幀殘影·霓虹暖黃交錯·狹窄空間貼身手持", "**參數組禁粒子禁高幀率，打戲禁用**"),
    (8,  "畢贛",      0, 0, "文藝詩電影", "潮溼霧氣·隧道霓虹·長焦壓縮", "**時間失速，無動作語法**"),
    (18, "侯孝賢",    0, 0, "文藝寫實",   "固定遠景長鏡·真實環境光", "**打鬥會被看淡**"),
    (20, "蔡明亮",    0, 0, "文藝寫實",   "極低機位手持·潮溼暗調·慢節奏", "**與打鬥節奏對立**"),
    (43, "馬利克",    0, 1, "抒情",       "自然光·極低機位·慢鏡長焦靜觀", "**無動作**"),
    # ★2026-10-15 補：路由表引用但 STYLES 缺失的 4 張（原「路由引用卻查無此卡」→ 靜默漏推）。
    #   星級以 scripts/style-lock-ladder.py（唯一權威）為準，描述取 director-style-catalog-74.md。
    (15, "李少紅",    0, 1, "古典唯美",   "柔焦·濃豔綢緞·對稱簾幕·燭光暖影", "過甜/缺質感"),
    (17, "李安",      0, 1, "剋制寫實",   "自然側光·中景為主·低飽和·留白", "節奏過緩/缺視覺衝擊"),
    (21, "王童",      1, 1, "視覺華麗",   "民間裝飾紋樣·濃飽和·圖畫性構圖", "畫面擁擠/缺縱深"),
    (35, "金炯柱",    0, 1, "時尚視覺",   "高飽和撞色·裝飾性構成·時尚造型感", "過時尚/脫離題材"),
    (49, "塔可夫斯基 ⚠️C",0,1,"詩電影",   "自然光·水與霧·極長鏡", "**AI 亦難撐**"),
    (23, "北野武 ⚠️C", 1, 0, "極簡暴力",  "極簡固定鏡·大段空鏡·驟停畫格", "**打鬥會被剪成靜止**"),
    (25, "是枝裕和",  0, 0, "家庭日常",   "家庭實景·窗側自然光·中近景", "**無動作**"),
    (26, "河瀨直美",  0, 0, "抒情",       "逆光柔焦·淡曝光·淺景深", "**無動作**"),
    (27, "巖井俊二",  0, 0, "青春回憶",   "逆光光暈·柔焦·膠片青綠", "**無動作**"),
    (34, "李滄東",    0, 0, "社會寫實",   "粗糲手持·真實自然光·灰土調", "**非動作向**"),
    (40, "韋斯·安德森",0,0, "喜劇美學",   "正面中軸·粉彩低飽和·舞台式佈景", "**打鬥變擺拍**"),
    (45, "索德伯格",  1, 0, "街拍犯罪",   "冷調自然光·輕手持·街拍感", "動作鬆散"),
    (46, "雷德利",    1, 2, "古典史詩",   "古典油畫感·暖金燭光·數字繪景", "打鬥偏陣仗"),
    (51, "呂貝·貝松", 1, 1, "童年視角",   "兒童低機位·暖自然光·靜謐", "不適合打鬥"),
    (55, "維托里奧·斯托拉羅",1,2, "象徵用光",   "象徵性用光·色彩敘事·強反差光影·明暗塊面", "構圖優先於動作"),
    (61, "斯文·尼奎斯特", 0, 0, "極簡長鏡",   "自然光·柔和低反差·中遠景·靜止長拍", "**無動作**"),
]

# 打鬥信號詞
COMBAT_SIG = ["打鬥","打戲","戰鬥","對決","開打","武打","搏殺","廝殺","對招","交手","格鬥","鬥法","大戰"]
# 高特效信號
VFX_HIGH_SIG = ["法術","鬥法","玄幻","仙俠","修真","神通","法陣","大招","神魔","仙術","異能","風暴","領域"]
# 無特效題材
VFX_LOW_SIG = ["寫實","格鬥","軍警","警匪","追車","暗殺","械鬥","都市現實"]

# ★否定語境：命中即把該詞從打鬥信號裡剔除（"無打鬥""不打鬥""沒有打鬥""非打鬥"…）
NEG_PREFIX = ["無", "不", "沒有", "沒", "非", "零", "免", "去"]
_NEG_WINDOW_RE = re.compile(
    r"(?:毫無|沒有任何|沒有|不含|無任何|全無|無|沒|不|非|零|免|去)[^，。；、！？\s]{0,4}$")
# 題材關鍵詞（優先於信號詞判定"有沒有打鬥"）
GENRE_COMBAT  = ["玄幻", "仙俠", "修真", "武俠", "武打", "格鬥", "動作", "戰鬥", "打鬥", "打戲",
                 "械鬥", "暗殺", "槍戰", "追車", "戰爭", "搏殺", "廝殺"]
GENRE_NOCOMBAT = ["都市情感", "情感", "文藝", "靜思", "家庭", "日常", "青春", "懷舊", "年代",
                  "甜寵", "職場", "商戰", "懸疑文戲", "心理", "生活流", "散文",
                  "文戲", "純對話", "劇情向"]   # ★P8 補：分鏡稿最常用的「無打鬥」自述詞

# ★題材路由表：題材族 → (首選編號, 次選編號, ...)  順序即推薦優先級
GENRE_ROUTES = [
    (["國漫3D", "3D國漫", "修仙", "仙俠", "玄幻", "修真", "鬥法", "法術"], [65, 71, 66, 72, 9, 6]),
    (["遊戲CG", "主機CG", "黑神話", "暗黑神話", "神魔"],         [66, 72, 65, 6]),
    (["水墨", "三渲二", "國風武俠", "進階水墨"],                 [71, 65, 72, 7]),
    (["武俠", "武打", "械鬥", "江湖", "刀劍", "劍客"],           [12, 7, 71, 9, 22]),
    (["機甲", "賽博", "科幻戰鬥"],                              [29, 68, 28, 47]),
    (["異能", "超能力", "都市戰鬥"],                            [64, 28, 39, 36]),
    (["懸疑", "犯罪", "暗殺", "警匪", "追車"],                  [39, 48, 33, 45]),
    (["戰爭", "史詩", "戰爭場面"],                              [46, 36, 6, 22]),
    (["恐怖", "驚悚", "靈異"],                                  [48, 33, 39, 36]),
    (["都市情感", "情感", "都市", "職場", "甜寵", "愛情"],       [10, 25, 35, 26]),
    (["懷舊", "年代", "復古", "回憶"],                          [10, 15, 21, 17]),
    (["文藝", "靜思", "詩", "散文", "家庭", "日常"],            [49, 18, 8, 25]),
    (["青春", "校園", "成長"],                                  [27, 25, 26, 18]),
    (["喜劇", "荒誕"],                                          [40, 44, 34, 61]),
]


def route_genre(genre_text):
    """按題材關鍵詞命中路由表；返回 (首選編號列表, 命中的題材族名) 或 (None, None)"""
    best = None
    for keys, order in GENRE_ROUTES:
        hit = [k for k in keys if k in genre_text]
        if hit and (best is None or len(hit) > best[0]):
            best = (len(hit), order, hit)
    if best:
        return best[1], best[2][0]
    return None, None


def _negated_at(t, start):
    """★P8：前置窗口否定判定。舊版只認緊貼的「無打鬥/沒有打鬥」，
    「沒有**任何**打鬥」「不含一點打鬥」這類隔字否定仍被判成**有打鬥**
    ——實測甜寵文戲稿被塞了一張仙俠打鬥卡。"""
    return bool(_NEG_WINDOW_RE.search(t[max(0, start - 8):start]))


def _live_hits(t, words):
    out = []
    for w in words:
        for m in re.finditer(re.escape(w), t):
            if not _negated_at(t, m.start()):
                out.append(w)
                break
    return out


def detect_combat(genre_text):
    """
    判定是否含打鬥 —— 三步，順序不可換：
      ① 否定式命中（"無打鬥/不打鬥/沒有打鬥/沒有任何打鬥/非打鬥"）→ 直接 False，最高優先級
      ② 題材關鍵詞：命中 GENRE_NOCOMBAT 且未命中 GENRE_COMBAT → False
      ③ 打鬥信號詞：剔除否定語境後再判
    返回 (combat:bool, 判定依據:str)
    """
    # ① 否定式（關鍵詞前 8 字內出現否定詞即視為已否定）
    live = _live_hits(genre_text, COMBAT_SIG)
    hit_c = _live_hits(genre_text, GENRE_COMBAT)
    if not live and not hit_c:
        _raw = [w for w in COMBAT_SIG if w in genre_text]
        if _raw:
            return False, f"否定式（「{_raw[0]}」前有否定詞）"

    # ② 題材關鍵詞
    hit_n = [w for w in GENRE_NOCOMBAT if w in genre_text]
    if hit_n and not hit_c:
        return False, f"題材詞「{hit_n[0]}」非動作向"

    # ③ 信號詞
    if hit_c:
        return True, f"題材詞「{hit_c[0]}」"
    if live:
        return True, f"信號詞「{live[0]}」"
    return False, "無打鬥信號"


def recommend(genre_text):
    combat, why = detect_combat(genre_text)
    vfx_high = any(w in genre_text for w in VFX_HIGH_SIG)
    vfx_low = any(w in genre_text for w in VFX_LOW_SIG)

    excluded = []
    pool = []
    for s in STYLES:
        num, name, fight, fx, native, look, warn = s
        if combat:
            if fight <= 1:
                excluded.append((num, name, "打鬥適配 ★%d，不適合打戲" % fight))
                continue
            if vfx_high and fx < 2:
                excluded.append((num, name, "特效承載 ★%d，撐不住高特效打鬥" % fx))
                continue
        pool.append(s)

    pool.sort(key=lambda s: (s[2] + s[3]), reverse=True)

    # ★按題材路由重排候選池（題材匹配優先，能力總分只做同族內的次序）
    order, route_key = route_genre(genre_text)
    if order:
        num2s = {s[0]: s for s in pool}
        routed = [num2s[n] for n in order if n in num2s]
        routed_ids = {s[0] for s in routed}
        pool = routed + [s for s in pool if s[0] not in routed_ids]
    return combat, why, vfx_high, pool, excluded, route_key


def render(genre_text, top=4):
    combat, why, vfx_high, pool, excluded, route_key = recommend(genre_text)
    print("=" * 76)
    print(f"題材輸入：{genre_text}")
    print(f"含打鬥={combat}（依據：{why}）  高特效={vfx_high}   "
          f"題材族={route_key or '未命中'}   候選池 {len(pool)} 組 · 已排除 {len(excluded)} 組")
    print("=" * 76)
    print("\n【候選卡】")
    for i, (num, name, fight, fx, native, look, warn) in enumerate(pool[:top]):
        tag = "【默認推薦】" if i == 0 else ""
        fs = "★" * fight if fight else "—"
        xs = "★" * fx if fx else "—"
        print(f"\n{'ABCD'[i] if i < 4 else i+1} {tag}{name}向 · {native}        打鬥 {fs} 特效 {xs}")
        print(f"   看：{look}")
        print(f"   易跑偏：{warn}")
    print(f"\nD 自定義 → 你直接描述，我按你的描述建 STYLE_BIBLE")
    if excluded:
        names = " · ".join(f"{n}" for _, n, _ in excluded[:20])
        print(f"\n[本次已自動排除 {len(excluded)} 組不適合該題材的風格：{names}]")
        print(" [如需其中某個風格拍打戲，請明示——系統會給出降級方案與風險提示]")


if __name__ == "__main__":
    # ★P8（2026-10-24 · 採納網友建議書 P-01）：舊版 __main__ 只循環 5 組硬編碼示例，
    #   **全程不讀 sys.argv** → 「題材→候選池路由引擎」實際是演示腳本：任何輸入都得到
    #   同一套輸出（拍甜寵也會拿到仙俠打鬥卡）。現改為位置參數接題材，--demo 跑原示例。
    import sys

    demo_cases = ["15秒玄幻仙俠打鬥對決，有法術特效",
                  "都市情感夜戲，無打鬥",
                  "年代懷舊文戲，兩個人回憶往事",
                  "現代都市懸疑，追車加近身格鬥",
                  "都市異能戰鬥，賽博科幻城市場景"]

    argv = sys.argv[1:]
    # ★P9：`--self-test` 作為 `--demo` 的正式別名（包內慣例統一，見 check_package ◑25）
    _selftest = "--self-test" in argv
    if not argv or "--demo" in argv or _selftest:
        print("【演示模式】以下為內置示例，非本機輸入\n")
        for g in demo_cases:
            render(g)
            print("\n")
        if _selftest:
            print(f"[+] style-lock-recommend self-test PASSED（{len(demo_cases)} 組內置示例全部出卡未崩）")
        sys.exit(0)

    text_parts, top = [], 4
    for a in argv:
        if a.startswith("--top="):
            try:
                top = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        elif not a.startswith("--"):
            text_parts.append(a)
    text = " ".join(text_parts).strip()
    if not text:
        print('用法：python style-lock-recommend.py "<題材串>" [--top=4]')
        print("      python style-lock-recommend.py --demo        # 跑內置示例（--self-test 等價）")
        sys.exit(2)
    render(text, top=top)
    print("\n※ 本卡是「題材→候選池」建議；**影像基底須先由用戶確認**（形態必問，"
          "見 style-lock-protocol.md §三 · 2026-10-13 裁定），"
          "基底未定時請勿據此出卡。")