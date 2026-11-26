#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 單集劇本機檢（分檔）

用法:
    python validate_episode.py <單集劇本.md> [--format auto|standard|long|manju] [--prev 前集.md ...]
    python validate_episode.py --self-test
    （Windows 用 python；macOS / Linux 用 python3）

檔位 profile (--format; 默認 auto = 按正文自檢: 含"長檔"→long, 含"漫劇"→manju, 否則 standard):
    standard  標準檔 90~120 秒   正文體量 實拍 480~850 / 漫劇 330~620   場景 <=2   對白行 >=4
    long      長檔   150~195 秒  正文體量 實拍 820~1400 / 漫劇 660~1150  場景 <=3   對白行 >=8   必設【本集中段小鉤】
    manju     漫劇檔 60~90 秒    正文體量 330~620                       場景 <=2   對白行 >=4

檢查項 (FAIL=攔截必須修復, WARN=告警複核, NOTE=保護性反例提示, 明確不是缺陷):
    E1  正文體量【參考帶】= 對白+動作行+斷章畫面（不計【】字段行/[場景][人物]）
          參考帶按【本集時長】動態推導（≈5.0~7.6 字/秒·含動作）；無時長則用檔位典型
          WARN(超參考帶，不攔) / FAIL(低於參考帶 0.5 倍 = 極端空稿)
    E2  單句台詞(常規 12~18 字 / 爆發金句 8~16) 上限 25 字(超長告警,非攔截)   WARN(逐句 >25)
          注: 獨白/旁白不按此判(改按 E12 的 os_len/vo_len)
    E3  場景數 <=2 ([場景] 標記計數)                FAIL(>2)
    E4  黃金前3秒: 首個內容行含衝突信號詞（②行動型可用「反常動作」詞）      FAIL(無)
    E5  開篇禁詞(起床/拉窗簾/太陽昇起/走在路上等)     WARN
    E6  斷章卡點: 存在【本集斷章卡點】且含黑屏/懸念   FAIL(缺)
    E7  情緒流變詞: 存在【情緒流變】鏈條(-> 或 ➔)    WARN(缺)
    E8  復讀檢測: 主角台詞與前集傳入(--prev)重複     WARN(重複句)
    E9  對白行數: >= 本檔位下限(標準/漫劇 4 行, 長檔 8 行)  WARN(不足)
          注: 獨白/旁白行不計入對白行數(防用獨白充數繞過攻防結構檢查)
    E10 合規紅線詞(斷肢/開膛/下蠱等一票否決直觀描寫)  FAIL
    E11 長檔中段小鉤: 存在【本集中段小鉤】(long 檔)      FAIL(長檔缺)
    E12 獨白/旁白配額: 內心獨白 標準1/長檔2/漫劇1 處(單處 25/30/20 字); 旁白 ≤1 處·≤12 字  FAIL(超配額)
    E13 獨白/旁白連排: 兩條相鄰, 或緊貼斷章收尾            FAIL
    E14 獨白裡寫交代設定 / 抽象情緒                       WARN
    E15 前 3 秒出現獨白/旁白(應為場內衝突)                FAIL
    E16 時長虛標(v4.9.1·全檔; 凡標註【本集時長】即校驗, 帶不帶「秒」字均可): 標註>可拆時長×1.20  FAIL
          可拆時長 = 純台詞字數÷4.5(參考語速) + 動作行數×動作拍權重 + 5s 留白；動作行字數不參與時長換算
    E17 長檔降級(v3.4.2·long 檔): 【本集時長】< 150 秒(長檔下限)          FAIL
    E18 對白語氣供給(v3.4.3/v5.0·對接導演端 V6.9.3 C16 / model-adapters §5.2):
        E18a 神態短語含空泛情緒結果詞(開心/憤怒等)                       WARN
        E18b 全篇對白行無一處語氣詞(極端態: 嗓音/發聲方式信息整集缺失)    WARN
        E18c 神態短語含網文常態套話(眼神微冷/淡淡開口/嘴角勾起等 · v5.0)  WARN
    E19 15秒窗口台詞密度(v4.0·WARN 生產端建議): 連續對白塊 >95 字       WARN
    E20 動作單段≤40字(v4.2·WARN 軟約束): 單條 △ 鏡頭淨字數 >40 字      WARN
    E21 對白/動作字數黃金比 25%~70%(v4.2·WARN): 對白/(對白+△動作)        WARN
    E22 台詞用語/錯別字(常用誤用對照，如 競然/迫不急待/掉過錢…)          WARN(只提示，不攔)
    E23 衝突形態適配: ②行動堅持型必須設【質疑者配角】                    FAIL
    E24 乾聊斷層檢測(v4.9·WARN 強畫面支撐): 連續純對白 >6 行無 △ 動作行  WARN
          解決"沒有畫面支撐、站樁廣播劇"痛點；建議每 2~4 句對白穿插一條強視覺 △
    E25 謎語黑話檢測(v4.9·WARN 大白話直給): 對白含未翻譯晦澀黑話/謎語詞  WARN
          解決"說的話想半天才能明白什麼意思"痛點；專名與黑話當句須翻譯為錢/命/地位等大白話後果
    E26 無效微動作檢測(v4.9·WARN 強視覺錨點): △ 僅含拍不出的微動作/心理詞 WARN
          封殺"△ 眼神微動 / 微微一怔 / 推了半寸"等假動作充數，要求落到三大視覺錨點
    E27 機械鏡頭標籤堆砌檢測(v5.0·WARN 反機械模板): 單集刷屏【慢鏡頭】/【特寫】 WARN
          防止每集機械貼【慢鏡頭】(>=2處)或高頻刷屏【特寫】(>=6處)充當高潮

保護性反例 (NOTE 級 —— 提示"你可能過度修正了", 不要求修改; 詳見 references/protective-counterexamples.md):
    N12 碎句化: 連續 >=5 行對白且每行淨字數 <=4      NOTE(疑為繞開 E2 而剁碎完整句)
    N13 堆動作: 動作行 >=12 且均淨字數 <=14 且對白行 <= 本檔下限  NOTE(疑為湊 E1 體量堆動作)
    N14 貼下限: 體量 <= 下限+15 且斷章段淨字數 <20    NOTE(疑為達標而壓掉必要過程/斷章過乾)
退出碼: 0=通過(可含WARN/NOTE), 1=FAIL, 2=用法錯誤
"""
import re
import sys

# 劇本文本體量閾值(僅計正文: 對白行 + △動作行 + 斷章卡點畫面描述)
NET_MIN, NET_MAX = 480, 850          # 實拍短劇（寬參考帶：只抓極端過薄/過厚，中間不卡）
NET_MIN_ANIME, NET_MAX_ANIME = 330, 620  # 漫劇/豎屏動畫
NET_LONG_MIN, NET_LONG_MAX = 820, 1400        # 長檔(150~195秒彈性) 實拍
NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX = 660, 1150  # 長檔 漫劇/豎屏動畫
SENT_MAX = 25                        # 單句台詞上限(WARN 級告警,非攔截; 常規 12~18)

# ---- 長檔時長守恆錨點（v4.3：按實測語速重校——15秒≈95字上限，寫作目標 5.5 字/s）----
LONG_MIN_SEC = 150                   # 長檔【本集時長】下限(秒)：低於此即"掛長檔名頭、交標準檔體量"
DLG_PER_SEC = 4.5                    # 台詞→時長換算參考語速(字/s)，用於 E16（容差 ±20%）
DLG_TARGET = {90: 400, 120: 540, 150: 670, 180: 800, 195: 870}   # 各目標時長的純台詞量【參考中值】(字)，非硬門檻
WIN15_MAX_CHARS = 105                 # E19: 任何連續對白塊淨字數上限(字)，≈15秒×7.0字/s觸頂
DRY_DLG_RUN_MAX = 6                  # E24 (v4.9): 連續純對白無 △ 動作行的最大行數上限（>6 行即告警乾聊斷層）

# ---- 對白語氣供給（v3.4.3 / v5.0 · 對接導演端 V6.9.3 C16 / model-adapters §5.2 對白三要素）----
TONE_WORDS = ("嘶啞", "沙啞", "氣音", "顫聲", "發顫", "哭腔", "哽咽", "破音", "氣若游絲",
              "有氣無力", "低語", "輕聲", "柔聲", "厲聲", "厲喝", "嘶吼", "低吼", "怒喝",
              "咆哮", "一字一頓", "一字一句", "拖長音", "陰陽怪氣", "譏誚", "嗤笑", "冷笑",
              "咬牙切齒", "壓低聲音", "壓著嗓", "急促", "咬著牙", "冷冷", "淡淡", "沉聲",
              "低聲", "高聲", "尖聲", "聲音極低", "聲音發", "嗓音", "語氣", "顫", "啞",
              "低聲道", "冷聲道", "字字")
E18_VAGUE_WORDS = ("開心", "難過", "生氣", "憤怒", "悲傷", "傷心", "高興", "邪魅", "傷感", "激動")
E18C_CANNED_PAREN_WORDS = (
    "眼神微冷", "眸光微冷", "目光微冷", "眼神微眯", "淡淡開口", "緩緩開口",
    "薄唇輕啟", "朱唇輕啟", "嘴角勾起", "勾起一抹", "眼中閃過", "眸中閃過",
    "神色淡漠", "面無表情"
)

# ---- E22 台詞用語/錯別字（常用誤用對照，WARN 級：只提示、不攔）----
TYPO_LITERALS = (
    ("競然", "竟然"), ("既使", "即使"), ("即然", "既然"),
    ("迫不急待", "迫不及待"), ("按耐", "按捺"), ("穿流不息", "川流不息"),
    ("走頭無路", "走投無路"), ("挺而走險", "鋌而走險"), ("一如繼往", "一如既往"),
    ("按步就班", "按部就班"), ("甘敗下風", "甘拜下風"), ("相形見拙", "相形見絀"),
    ("不加思索", "不假思索"), ("有持無恐", "有恃無恐"), ("天翻地復", "天翻地覆"),
    ("人情事故", "人情世故"), ("鬼鬼崇崇", "鬼鬼祟祟"), ("聲名雀起", "聲名鵲起"),
    ("一愁莫展", "一籌莫展"), ("不徑而走", "不脛而走"), ("張慌", "張皇"),
    ("倍受", "備受"), ("做為", "作為"), ("帳號", "賬號"), ("通霄", "通宵"),
    ("瞪目結舌", "瞠目結舌"), ("蜂湧", "蜂擁"), ("各行其事", "各行其是"),
    ("斷章取意", "斷章取義"), ("來不急", "來不及"), ("楞", "愣"),
    ("攢緊", "攥緊"), ("趔列", "趔趄"), ("踉倉", "踉蹌"),
    ("嘀估", "嘀咕"), ("囑付", "囑咐"), ("多嗦", "哆嗦"), ("硬嚥", "哽咽"),
)
TYPO_REGEX = (
    (r"掉(?:過|了)[^。！？\n]{0,4}(?:錢|銀子)", "「掉」用於錢物不通，口語應為「掏」/「出」"),
)

# ---- E25 謎語黑話與未翻譯設定詞（v4.9 新增 · WARN 級：防觀眾想半天聽不懂）----
OBSCURE_JARGON_WORDS = (
    "法則縫隙", "氣運錨點", "因果閉環", "維度坍縮", "高維投影",
    "底層邏輯閉環", "賦能矩陣", "火漏", "啞青", "第七份", "第八份", "把油燈往"
)

# ---- E26 無效微動作（v4.9 新增 · WARN 級：防鏡頭拍不出來的假動作充數）----
WEAK_MICRO_ACTIONS = (
    "眼神微動", "眼神微閃", "目光微閃", "目光微動", "微微一怔",
    "若有所思", "陷入沉思", "嘴角微揚", "嘴角微勾", "推了半寸", "移了半寸"
)

# 強動作標記（v4.9.1 修復回植）：△ 行內命中即視為有可見物理結果/物證對抗，E26 放行。
# 修復"弱微動作被湊長氛圍描寫包住即繞過檢測"的盲區：命中弱詞但行內無任一強標記時，
# 無論 △ 行長短都告警；組合 △（微微一怔 + 茶杯砸碎）不誤報。
STRONG_ACT_MARKERS = (
    "砸", "摔", "甩", "拍在", "拍桌", "拍案", "重拍", "踹", "踢", "扇",
    "掀", "撞", "掐", "抓住", "拽", "扯", "潑", "燒", "點燃", "撕",
    "跪", "癱", "倒地", "跌", "扔", "拋", "奪", "搶", "掏出", "抽出",
    "拔出", "按住", "擋", "躲", "衝上", "撲", "抱住", "拖", "綁", "堵住",
    "捂", "翻過", "推翻", "推開", "推倒", "舉", "亮出", "亮明", "逼近",
    "踉蹌", "後退", "轉身", "起身", "站起", "碎", "裂", "滾落", "滑落",
    "濺", "冒出", "漲紅", "攥", "捏", "摁", "特寫", "推給", "滑到"
)


# ---- v5.1 視聽可拍性四門禁（E37~E40）----
UNSHOOTABLE_NEG_ACTIONS = ("非但沒跪", "非但沒退", "看都沒看一眼", "連眼角都沒掃", "連眼皮都沒抬一下")
E39_IGNORE_WORDS = ("意思", "東西", "時候", "事情", "地方", "情況", "理由", "辦法", "玩意")
SCENE_TRANSITION_VERBS = ("走進", "推門", "推開", "來到", "趕到", "衝進", "轉身", "片刻後", "次日", "當晚", "隨後", "離開")

# ---- 獨白 / 旁白（非說話的敘述通道）----
VO_OS_TAGS = ("內心獨白", "獨白", "心聲")            # 只有觀眾聽見的說話人心聲
VO_VO_TAGS = ("旁白", "畫外音", "畫面字幕", "字幕")   # 第三人稱點題 / 時間錨
VO_EXPO_WORDS = ["事情要從", "這一切都要從", "這一切都因為", "之所以", "眾所周知",
                 "前情", "話說當年", "回顧一下", "背景是", "原來是這樣的"]
VO_ABSTRACT_WORDS = ["五味雜陳", "百感交集", "思緒萬千", "心如刀割", "難以言表", "感慨萬千"]

PROFILES = {
    "auto":     {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 25, "vo": 1, "vo_len": 12, "label": "自動分檔"},
    "standard": {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 25, "vo": 1, "vo_len": 12, "label": "標準檔 90~120 秒"},
    "long":     {"scenes": 3, "lines": 8, "midhook": True,  "os": 2, "os_len": 30, "vo": 1, "vo_len": 12, "label": "長檔 150~195秒彈性"},
    "manju":    {"scenes": 2, "lines": 4, "midhook": False, "os": 1, "os_len": 20, "vo": 1, "vo_len": 12, "label": "漫劇檔 60~90 秒"},
}

OPEN_BAN_WORDS = ["早晨起床", "起床", "拉窗簾", "太陽昇起", "醒過來", "走在路上",
                  "整理衣服", "開車上班", "喝咖啡閒聊", "悠閒的清晨", "陽光明媚的早晨"]

CONFLICT_SIGNALS = ["！?", "！", "槍", "刀", "巴掌", "扔", "砸", "吼",
                    "逼", "跪", "撕", "拍在", "頂在", "推", "踹", "罵", "羞辱", "退婚",
                    "病危", "簽字", "死", "滾", "住手", "救", "斷裂", "炸", "燒", "血", "休書"]
ACTION_SIGNALS = ["囤", "搬", "扛", "抬", "焊", "封", "鎖", "插銷", "裝箱", "碼",
                  "發電機", "鋼板", "密封", "加固", "搶購", "屯", "備貨", "儲", "水桶",
                  "斷電", "停水", "挖", "砌", "鑽", "擰", "釘", "背", "貼", "算"]

BREAK_WORDS = ["斷章", "卡點", "黑屏", "懸念"]

REDLINE_WORDS = ["斷肢", "開膛", "破肚", "身首異處", "凌遲", "活埋", "注射死刑", "吸毒",
                 "製毒", "自殺方法", "下蠱害人", "蠱毒害人", "真實的國家機關"]


_VO_LINE_RE = re.compile(r"^(內心獨白|獨白|心聲|旁白|畫外音|畫面字幕|字幕)(（[^）]*）|\([^)]*\))?\s*[:：]\s*(.+)$")


def _vo_line(line):
    """獨白/旁白行 → (kind, 內容)；kind ∈ {'os' 內心獨白, 'vo' 旁白/字幕}；非獨白行返回 None"""
    s = line.strip()
    if not s or s.startswith(("[", "△", "【", "#", ">")):
        return None
    m = _VO_LINE_RE.match(s)
    if not m:
        return None
    return ("os" if m.group(1) in VO_OS_TAGS else "vo", m.group(3))


def _is_dialogue(line):
    """對白行: 角色名(可選括號提示): 台詞  —— 不以[ △ 【開頭，且不是獨白/旁白行"""
    s = line.strip()
    if not s or s.startswith(("[", "△", "【", "#", ">")):
        return None
    if _vo_line(s):
        return None
    m = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9]{1,8})(（[^）]*）|\([^)]*\))?\s*[:：]\s*(.+)$", s)
    return m.group(3) if m else None


def _paren_of(line):
    """對白行的神態短語（括號內容）→ str；無括號或非對白行返回 ''"""
    s = line.strip()
    if not s or _vo_line(s) is not None:
        return ""
    m = re.match(r"^[\u4e00-\u9fa5A-Za-z0-9]{1,8}(?:（([^）]*)）|\(([^)]*)\))?\s*[:：]", s)
    if not m:
        return ""
    return (m.group(1) or m.group(2) or "").strip()


def net_chars(text):
    """劇本文本體量: 僅計對白行台詞 + 獨白/旁白行內容 + △動作指示行內容 + 【本集斷章卡點】畫面描述"""
    total = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        d = _is_dialogue(s)
        v = _vo_line(s)
        if v is not None:
            body = v[1]
        elif d is not None:
            body = d
        elif s.startswith("△"):
            body = re.sub(r"^△\s*", "", s)
        elif s.startswith("【本集斷章卡點】"):
            body = re.sub(r"^【本集斷章卡點】\s*[:：]?\s*", "", s)
        else:
            continue
        body = re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body)
        total += len(body)
    return total


def _header_text(text):
    """只取劇本頭部（前 3 行：集標題/檔位標註區）"""
    return "\n".join(text.splitlines()[:3])


def is_anime(text):
    """漫劇/豎屏動畫項目: 頭部含 '漫劇' 即按漫劇體量檔判 E1"""
    return "漫劇" in _header_text(text)


def is_long(text):
    """長檔項目: 頭部含 '長檔' 即按長檔體量判 E1/E3/E9/E11"""
    return "長檔" in _header_text(text)


def resolve_profile(text, profile="auto"):
    """auto 檔按正文自檢: 含"長檔"→long, 含"漫劇"→manju, 否則 standard"""
    if profile != "auto":
        return profile if profile in PROFILES else "standard"
    if is_long(text):
        return "long"
    if is_anime(text):
        return "manju"
    return "standard"


def net_band(text, profile):
    """正文體量【參考帶】。優先按劇本自報的【本集時長】動態推導，並按衝突形態微調係數"""
    m = re.search(r"【本集時長】[：:]?\s*(\d+)", text)
    if m:
        t = int(m.group(1))
        if t > 0:
            _mode = conflict_mode(text)
            _lo, _hi = (3.5, 5.5) if _mode == "行動型" else ((4.2, 6.5) if _mode == "混合" else (5.0, 7.6))
            return (round(t * _lo), round(t * _hi))
    if profile == "long":
        return (NET_LONG_ANIME_MIN, NET_LONG_ANIME_MAX) if is_anime(text) else (NET_LONG_MIN, NET_LONG_MAX)
    if profile == "manju":
        return NET_MIN_ANIME, NET_MAX_ANIME
    return (NET_MIN_ANIME, NET_MAX_ANIME) if is_anime(text) else (NET_MIN, NET_MAX)


def scene_count(text):
    return len(re.findall(r"^\[場景\]|^【場景】|^##?\s*場景", text, re.M))


def first_content_lines(text, n=3):
    out = []
    for line in text.splitlines():
        s = line.strip().lstrip("\ufeff").strip()  # v4.9.1 修復回植: 剝離 BOM，防其擠佔前3秒檢測窗口
        if not s or s.startswith(("#", ">", "第", "【", "[")):
            continue
        out.append(s)
        if len(out) >= n:
            break
    return out


def conflict_mode(text):
    """衝突形態：對話型（嘴仗）/ 行動型（準備×質疑）/ 混合；缺省=對話型。"""
    m = re.search(r"【衝突形態】[：:]\s*([^\n【]{1,30})", text)
    if m:
        s = re.split(r"[／/\s、,，]", m.group(1).strip())[0]
        if "行動" in s:
            return "行動型"
        if "混合" in s:
            return "混合"
    return "對話型"


def validate(text, prev_texts=(), profile="auto"):
    profile = resolve_profile(text, profile)
    prof = PROFILES[profile]
    mode = conflict_mode(text)
    if mode == "行動型":
        lines_min = max(3, prof["lines"] // 2)
    elif mode == "混合":
        lines_min = max(4, prof["lines"] - 2)
    else:
        lines_min = prof["lines"]
    act_credit = 4.0 if mode == "行動型" else (2.5 if mode == "混合" else 1.5)
    fails, warns = [], []
    nc = net_chars(text)
    lo, hi = net_band(text, profile)
    if nc < lo * 0.5:
        fails.append(f"E1 [{profile}] 正文體量 {nc} 過薄（參考帶 {lo}~{hi}；僅攔極端空稿）")
    elif not (lo <= nc <= hi):
        warns.append(f"E1 正文體量 {nc} 超出參考帶 {lo}~{hi}（體量為參考值：按【本集時長】或內容判斷，不攔）")

    # E2 單氣口≤25字：僅限對白行，按標點拆 clause（一行內可有多個氣口），逐 clause 淨字數 >25 → WARN
    for line in text.splitlines():
        d = _is_dialogue(line)
        if not d:
            continue
        for clause in re.split(r"[，。！？；、…—!?;]", d):
            c = re.sub(r"[\s“”\"‘’（）()《》：:，。！？；、…—]", "", clause)
            if len(c) > SENT_MAX:
                warns.append(f"E2 單句台詞 {len(c)} 字(>{SENT_MAX}): {c[:18]}…")

    sc = scene_count(text)
    _cap = prof["scenes"]
    _md = re.search(r"【本集時長】[：:]\s*(\d+)", text)
    if _md:
        _t = int(_md.group(1))
        if _t > 0:
            _cap = max(_cap, int(round(_t / 75.0)))
    if sc > _cap:
        fails.append(f"E3 [{profile}] 場景數 {sc} >{_cap}")
    if sc == 0:
        warns.append("E3 未檢出 [場景] 標記，無法核對場景數")

    head = "".join(first_content_lines(text))
    banned_hit = any(w in head for w in OPEN_BAN_WORDS)
    _sig = CONFLICT_SIGNALS + (ACTION_SIGNALS if mode == "行動型" else [])
    if banned_hit or not any(w in head for w in _sig):
        fails.append("E4 前3秒無衝突/命中開篇廢鏡頭詞(須直接切入衝突頂點，禁鋪墊；②行動型可用反常動作)")
    for w in OPEN_BAN_WORDS:
        if w in head:
            warns.append(f"E5 開篇疑似廢鏡頭禁詞「{w}」")

    if not re.search(r"【本集斷章卡點】|\[本集斷章", text):
        fails.append("E6 缺【本集斷章卡點】段")
    else:
        seg = re.search(r"【本集斷章卡點】(.{0,200})", text, re.S)
        if seg and not any(w in seg.group(1) for w in ["黑屏", "懸念", "下滑", "解鎖"]):
            warns.append("E6 斷章卡點缺黑屏/下滑解鎖落點詞")

    if not re.search(r"【情緒流變】.*(->|➔|➔|→)", text):
        warns.append("E7 缺【情緒流變】鏈條(應標: 遭受刁難 ➔ … ➔ 絕命斷章)")

    rounds = 0
    my_lines = [d for d in (_is_dialogue(l) for l in text.splitlines()) if d]
    rounds = len(my_lines)
    if prof["midhook"] and not re.search(r"【本集中段小鉤】|\[本集中段小鉤", text):
        fails.append("E11 長檔缺【本集中段小鉤】(≈90 秒處必設新信息/新威脅，防滑走)")
    if rounds < lines_min:
        warns.append(f"E9 [{profile}] 對白行僅 {rounds} 行(<{lines_min})，攻防結構不足" + ("（行動型已減半）" if mode == "行動型" else ""))
    # E23 行動型必須有【質疑者配角】（準備×質疑 的對手位）
    if mode == "行動型":
        _q = re.search(r"【質疑者配角】[：:]\s*([^\n]*)", text)
        if _q and _q.group(1).strip() in ("", "無", "無。", "—", "-"):
            fails.append("E23 行動型缺【質疑者配角】（對手位缺失：準備×質疑 必須有質疑者；無對手位＝行動流水賬）")

    # ---- 對白語氣供給（E18a/b/c · v3.4.3 / v5.0）----
    if my_lines:
        for l in text.splitlines():
            p = _paren_of(l)
            if not p:
                continue
            v = [w for w in E18_VAGUE_WORDS if w in p]
            if v:
                warns.append(f"E18a 神態短語含空泛情緒詞「{'/'.join(v)}」：{p}——"
                             "改為可執行的語氣/畫面詞（如 壓著怒·低語 ／ 指節捏白），"
                             "規格見 templates/episode-format.md §四")
                break
        for l in text.splitlines():
            p = _paren_of(l)
            if not p:
                continue
            canned = [w for w in E18C_CANNED_PAREN_WORDS if w in p]
            if canned:
                warns.append(f"E18c 神態短語含網文常態套話「{'/'.join(canned)}」：{p}——"
                             "請改為『具體手部/身體小動作｜發聲方式』（如 撣袖口｜冷聲 / 拍桌｜厲聲），"
                             "見 references/dialogue-doctor-anti-ai.md §三")
                break
        tone_lines = sum(1 for l in text.splitlines()
                         if _is_dialogue(l) and any(w in _paren_of(l) for w in TONE_WORDS))
        if tone_lines == 0:
            warns.append(f"E18b 全篇 {rounds} 行對白無一處語氣詞（嗓音/發聲方式信息整集缺失）——"
                         "官方對白三要素之三 HOW THEY SOUND 上游缺供：給關鍵對白補語氣詞"
                         "（如（氣音·發顫）／（俯身逼近｜甜笑·柔聲）），規格見 templates/episode-format.md §四")

    # ---- 獨白 / 旁白通道（E12~E15）----
    seq = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", ">", "[場景", "[人物", "第【")):
            continue
        if s.startswith("【本集斷章卡點】") or s.startswith("[本集斷章"):
            seq.append(("break", s)); continue
        if s.startswith("【"):
            continue
        v = _vo_line(s)
        if v is not None:
            seq.append((v[0], v[1])); continue
        if _is_dialogue(s) is not None:
            seq.append(("dia", s)); continue
        if s.startswith("△"):
            seq.append(("act", s)); continue

    os_cnt = sum(1 for c, _ in seq if c == "os")
    vo_cnt = sum(1 for c, _ in seq if c == "vo")
    if os_cnt > prof["os"]:
        fails.append(f"E12 [{profile}] 內心獨白 {os_cnt} 處 > {prof['os']}：獨白是配額制工具，超量即注水")
    if vo_cnt > prof["vo"]:
        fails.append(f"E12 [{profile}] 旁白/字幕 {vo_cnt} 處 > {prof['vo']}：旁白只服務點題轉折")
    for cls, body in seq:
        if cls in ("os", "vo"):
            cap = prof["os_len"] if cls == "os" else prof["vo_len"]
            n = len(re.sub(r"[\s，。！？；：、…—\-·“”\"'‘’（）()《》!?.]", "", body))
            if n > cap:
                fails.append(f"E12 {'內心獨白' if cls == 'os' else '旁白/字幕'}單處 {n} 字 >{cap}（{body[:14]}…）")

    for i in range(len(seq) - 1):
        if seq[i][0] in ("os", "vo") and seq[i + 1][0] in ("os", "vo"):
            fails.append("E13 連續兩條獨白/旁白（禁連排）：獨白之間必須隔動作或台詞")
            break
    bi = next((i for i, (c, _) in enumerate(seq) if c == "break"), None)
    if bi is not None and bi > 0 and seq[bi - 1][0] in ("os", "vo"):
        fails.append("E13 獨白/旁白緊貼斷章收尾：斷章必須落在畫面/事件上（獨白收尾＝軟收尾）")

    for cls, body in seq:
        if cls not in ("os", "vo"):
            continue
        for w in VO_EXPO_WORDS:
            if w in body:
                warns.append(f"E14 獨白含交代設定/前情信號「{w}」：獨白不承擔交代設定（紅線 2）")
                break
        for w in VO_ABSTRACT_WORDS:
            if w in body:
                warns.append(f"E14 獨白寫抽象情緒「{w}」：獨白要寫「具體的賬」（我給他生了五個孩子），不寫抽象感受")
                break

    for s in first_content_lines(text, 3):
        if _vo_line(s):
            fails.append("E15 前 3 秒出現獨白/旁白：黃金 3 秒必須是場內衝突（獨白開場＝軟開場，踩紅線 1）")
            break

    # E16 時長虛標 / E17 長檔降級
    # v4.9.1 修復回植：正則「秒」字可選（寫【本集時長】180 也能識別），E16 擴為全檔生效
    m_dur = re.search(r"【本集時長】[:：]?\s*(\d{2,4})(?:\s*秒)?", text)
    if m_dur:
        dlg_chars = 0
        action_lines = 0
        for line in text.splitlines():
            s = line.strip()
            v = _vo_line(s)
            d = _is_dialogue(s)
            if v is not None:
                dlg_chars += len(re.sub(r"[\s，。！？；：、…—]", "", v[1]))
            elif d is not None:
                dlg_chars += len(re.sub(r"[\s，。！？；：、…—]", "", d))
            elif s.startswith("△"):
                action_lines += 1
        est = dlg_chars / DLG_PER_SEC + action_lines * act_credit + 5
        claimed = int(m_dur.group(1))
        if claimed > est * 1.20:
            fails.append(
                f"E16 時長虛標：標註 {claimed}s，按台詞量最多可拆 {est:.0f}s"
                f"（純台詞 {dlg_chars} 字÷4.5字/s【參考語速】 ＋ {action_lines} 動作拍×{act_credit}s[{mode}] ＋ 留白）——"
                "參考語速 4.5 字/s（局部上限 6.33 × 對白佔比 0.7），容差 ±20%；補足台詞量或改標真實時長；"
                "動作行字數不參與時長換算，禁止用氛圍 △ 行湊體量虛標")

        if profile == "long" and claimed < LONG_MIN_SEC:
            fails.append(
                f"E17 長檔降級：標註 {claimed}s 低於長檔下限 {LONG_MIN_SEC}s——掛著長檔名頭、交的是標準檔體量"
                f"（純台詞僅 {dlg_chars} 字，可拆 {est:.0f}s）。兩條出路：① 補足純台詞量做成真長檔"
                "（150s≈670字 / 180s≈800字 / 195s≈870字 純台詞【參考中值】）；"
                "② 明確改 --format standard（90~120 秒）。"
                "禁止用動作行湊體量後標短時長來規避 E16")

    for prev in prev_texts:
        prev_set = set(re.sub(r"\s", "", p) for p in (_is_dialogue(l) for l in prev.splitlines()) if p)
        for d in my_lines:
            dd = re.sub(r"\s", "", d)
            if dd in prev_set and len(dd) >= 8:
                warns.append(f"E8 台詞與前集復讀: {dd[:16]}…")

    for w in REDLINE_WORDS:
        if w in text:
            fails.append(f"E10 合規一票否決類直觀描寫「{w}」")

    # ---- E19 15秒窗口台詞密度 + E24 連續乾聊斷層檢測（v4.9 新增）----
    run_chars = 0
    run_lines = 0
    max_dry_run = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        d = _is_dialogue(s)
        if d is not None:
            run_chars += len(re.sub(r"[\s，。！？；：、…—]", "", d))
            run_lines += 1
            if run_lines > max_dry_run:
                max_dry_run = run_lines
            continue
        if run_chars > WIN15_MAX_CHARS:
            warns.append(f"E19 15秒窗口台詞超量：連續對白 {run_chars} 字超過 {WIN15_MAX_CHARS} 字上限"
                         f"（對應 {run_chars / 15:.2f} 字/s 觸頂 7.0 字/s），建議插入 △動作行斷點或拆分")
        run_chars = 0
        run_lines = 0
    if run_chars > WIN15_MAX_CHARS:
        warns.append(f"E19 15秒窗口台詞超量：連續對白 {run_chars} 字超過 {WIN15_MAX_CHARS} 字上限"
                     f"（對應 {run_chars / 15:.2f} 字/s 觸頂 7.0 字/s），建議插入 △動作行斷點或拆分")
    if max_dry_run > DRY_DLG_RUN_MAX:
        warns.append(f"E24 乾聊斷層：連續 {max_dry_run} 行對白無 △ 動作支撐（上限 {DRY_DLG_RUN_MAX} 行），"
                     "畫面易淪為站樁廣播劇——建議每 2~4 句對白穿插一條強視覺 △（物理結果/身份反差/物證對抗）")

    # ---- E20 動作單段≤40字 + E21 對白/動作黃金比 25%~70% + E26 無效微動作 + E27 機械鏡頭標籤堆砌 ----
    act_total = 0
    dlg_total = 0
    weak_act_hit = None
    slowmo_cnt = 0
    closeup_tag_cnt = 0
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("△"):
            body = re.sub(r"^△\s*", "", s)
            if "【慢鏡頭】" in body or "[慢鏡頭]" in body:
                slowmo_cnt += 1
            if "【特寫】" in body or "[特寫]" in body:
                closeup_tag_cnt += 1
            clean_act = re.sub(r"[\s，。！？；：、…—\-·“”\"‘’（）()《》!?.]", "", body)
            n = len(clean_act)
            if n > 40:
                warns.append(f"E20 動作單段{n}字(>40)，建議拆為兩個△鏡頭")
            # v4.9.1 修復回植：弱微動作即使被湊長的氛圍描寫包住（淨字數>14）也須告警；
            # 但行內含強動作標記（物證砸碎/肢體對抗等）的組合 △ 不誤報
            if weak_act_hit is None:
                for w in WEAK_MICRO_ACTIONS:
                    if w in body:
                        if not any(m in body for m in STRONG_ACT_MARKERS):
                            weak_act_hit = body
                        break
            act_total += n
        else:
            d = _is_dialogue(s)
            if d is not None:
                dlg_total += len(re.sub(r"[\s，。！？；：、…—\-·“”\"‘’（）()《》!?.]", "", d))
    if weak_act_hit is not None:
        warns.append(f"E26 無效微動作：『△ {weak_act_hit}』鏡頭缺乏可見物理結果或物證對抗——"
                     "請改為三大視覺錨點（物理破壞/身份反差忙活/物證亮牌），見 references/craft-quality-layer.md §四·補")
    if slowmo_cnt >= 2 or closeup_tag_cnt >= 6:
        warns.append(f"E27 機械鏡頭標籤堆砌：本集含 {slowmo_cnt} 處【慢鏡頭】、{closeup_tag_cnt} 處【特寫】標籤——"
                     "文字劇本嚴禁靠機械刷屏分鏡標籤充當戲劇高潮，請直接寫出可見的物理結果與動作張力")

    denom = dlg_total + act_total
    if denom > 0:
        ratio = dlg_total / denom
        pct = int(round(ratio * 100))
        if ratio > 0.70:
            warns.append(f"E21 對白佔比{pct}%>70%，缺少肢體衝突與視聽調度")
        else:
            _lo = 0.10 if mode == "行動型" else (0.15 if mode == "混合" else 0.25)
            if ratio < _lo:
                warns.append(f"E21 對白佔比{pct}%<{int(_lo*100)}%，缺乏唇槍舌戰" + (f"（{mode}已放寬）" if mode != "對話型" else ""))

    # ---- E22 台詞用語/錯別字 + E25 謎語黑話與未翻譯設定詞檢測（v4.9 新增）----
    _hit = set()
    _jargon_hit = set()
    for _raw in text.splitlines():
        _s = _raw.strip()
        if not _s or _s.startswith(("【", "[", "#", ">", "△")):
            continue
        for _bad, _good in TYPO_LITERALS:
            if _bad in _s and _bad not in _hit:
                _hit.add(_bad)
                warns.append(f"E22 台詞用語：『{_bad}』疑為『{_good}』")
        for _pat, _note in TYPO_REGEX:
            _m = re.search(_pat, _s)
            if _m and _pat not in _hit:
                _hit.add(_pat)
                warns.append(f"E22 台詞用語：『{_m.group(0)}』——{_note}")
        for _jw in OBSCURE_JARGON_WORDS:
            if _jw in _s and _jw not in _jargon_hit:
                _jargon_hit.add(_jw)
                warns.append(f"E25 謎語黑話告警：台詞含晦澀詞『{_jw}』——須當句用大白話直給翻譯為具體利害（多少錢/誰死誰活/什麼物證）")


    # ---- v5.1 視聽可拍性四門禁（E37~E40）----
    seen_before = ""
    scene_blocks = []
    cur_sc = None
    cur_first_act = None
    for _raw in text.splitlines():
        _s = _raw.strip()
        if not _s:
            continue
        if _s.startswith(("[場景]", "【場景】")):
            if cur_sc is not None:
                scene_blocks.append((cur_sc, cur_first_act or ""))
            cur_sc = re.sub(r"^(?:\[場景\]|【場景】)\s*[:：]?\s*", "", _s)
            cur_first_act = None
            continue
        if _s.startswith("△"):
            _body = re.sub(r"^△\s*", "", _s)
            if cur_sc is not None and cur_first_act is None:
                cur_first_act = _body
            for _nw in UNSHOOTABLE_NEG_ACTIONS:
                if _nw in _body:
                    fails.append(f"E37 否定式偽動作「{_nw}」：無法轉為視聽畫面，請改為正向可見動作")
                    break
            if "接過" in _body and not re.search(r"從[^，。！？\n]{1,12}(?:手裡|手中|手上)接過|接過[^，。！？\n]{1,10}遞來", _body):
                warns.append(f"E38 道具交接缺來源：『△ {_body[:22]}』請寫明從哪位在場角色手裡接過")
        else:
            _d = _is_dialogue(_s)
            if _d is not None:
                _qm = re.search(r"什麼([\u4e00-\u9fa5]{2,4})[？?]", _d)
                if _qm:
                    _kw = _qm.group(1)
                    if _kw not in E39_IGNORE_WORDS and _kw not in seen_before:
                        warns.append(f"E39 疑似未提先知（幽靈反問）：台詞突然反問「什麼{_kw}？」，請確認前文已鋪墊該專名")
        seen_before += _s + "\n"
    if cur_sc is not None:
        scene_blocks.append((cur_sc, cur_first_act or ""))
    for _i in range(len(scene_blocks) - 1):
        _s1, _ = scene_blocks[_i]
        _s2, _a2 = scene_blocks[_i + 1]
        if _s1 == _s2 and not any(v in _a2 for v in SCENE_TRANSITION_VERBS):
            warns.append(f"E40 同空間假切場：相鄰兩場均為「{_s2}」且新場首條△缺乏位移或時間過渡詞")

    return fails, warns, nc


_PUNCT = "，。！？；：、…—－·“”（）()《》!?."
_QUOTES = "\"'" + "\u2018\u2019"
_STRIP_RE = re.compile("[" + re.escape(_PUNCT + _QUOTES) + r"\s]")

FRAG_RUN = 5        # N12: 連續短對白行數閾值（每行淨字數 <= 4）
FRAG_LEN = 4
DUMP_ACT = 12       # N13: 動作行數閾值
DUMP_AVG = 14       # N13: 動作行平均淨字數上限
NEAR_LO = 15        # N14: "貼近下限"容差
BRK_MIN = 20        # N14: 斷章段淨字數下限


def collect_notes(text, profile="auto"):
    """保護性反例提示（NOTE 級）—— 明確不是缺陷，提示「可能過度修正了」。"""
    profile = resolve_profile(text, profile)
    prof = PROFILES[profile]
    mode = conflict_mode(text)
    notes = []

    # N12 碎句化：連續 >=FRAG_RUN 行對白，每行淨字數 <=FRAG_LEN
    run, run_start = 0, ""
    for line in text.splitlines():
        d = _is_dialogue(line)
        if d is None:
            continue
        clean = _STRIP_RE.sub("", d)
        if len(clean) <= FRAG_LEN:
            if run == 0:
                run_start = clean
            run += 1
            if run >= FRAG_RUN:
                notes.append("N12 連續 %d 行以上短對白（≤%d 字），起於「%s」：疑為繞開單句上限而剁碎完整句。"
                             "完整直說不是缺陷——權力壓制/羞恥/正式場合下話可能更客氣更完整，而非更碎" % (FRAG_RUN, FRAG_LEN, run_start))
                break
        else:
            run = 0

    # N13 堆動作：動作行 >=DUMP_ACT 且均淨字數 <=DUMP_AVG 且對白行 <= 本檔下限
    act, dia = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("△"):
            act.append(len(_STRIP_RE.sub("", re.sub(r"^△\s*", "", s))))
        else:
            d = _is_dialogue(s)
            if d is not None:
                dia.append(d)
    if mode == "對話型" and act and len(act) >= DUMP_ACT and (sum(act) / len(act)) <= DUMP_AVG and len(dia) <= prof["lines"]:
        notes.append("N13 動作行 %d 條、均 %.1f 字，對白僅 %d 行：疑為湊 E1 體量堆低信息動作行。"
                     "動作多不等於有戲——應合併重複證明、讓同一動作兼任人物/線索/情緒" % (len(act), sum(act) / len(act), len(dia)))

    # N14 貼下限：體量 <= 下限+NEAR_LO 且斷章段淨字數 <BRK_MIN
    nc = net_chars(text)
    lo, _hi = net_band(text, profile)
    m = re.search(r"【本集斷章卡點】\s*[:：]?\s*(.*)", text)
    brk = len(_STRIP_RE.sub("", m.group(1))) if m else 0
    if nc <= lo + NEAR_LO and brk < BRK_MIN:
        notes.append("N14 體量 %d 貼近本檔下限 %d、斷章段僅 %d 字：疑為達標而壓掉必要過程或斷章過乾。"
                     "必要過程不能為卡線而刪；若本集本身成立（餘波集/快節奏轉折集），在交付說明寫明理由即可" % (nc, lo, brk))

    return notes


GOOD = """第【1】集：【龍王令·開局羞辱】
【黃金前3秒鉤子】：極端羞辱
【情緒流變】：當眾受辱 ➔ 隱忍握拳 ➔ 亮令反殺 ➔ 絕命斷章
【本集時長】：105 秒
[場景]：內景·頂級私人會所·夜
[人物]：林辰（隱忍龍王）、陳峰（囂張富二代）、蘇清雪（未婚妻）

△ 特寫：點燃的雪茄狠狠摁在林辰洗得發白的衣領上，青煙直冒，火星墜落。
△ 中景：陳峰摟著蘇清雪，滿臉鄙夷，包廂內保鏢環立。
陳峰（吐出菸圈）：跪下，把這杯髒水喝了，十萬塊救命錢，本少當場轉給你。
蘇清雪（冷漠）：林辰，別不知好歹，認清你自己的身份。
△ 特寫：林辰低垂的眼眸驟抬，垂在身側的右拳緩緩握緊，指節泛白。
林辰（聲音極低）：三年前你陳家跪著求我救命時，也是這副嘴臉？
陳峰（惱羞成怒）：你找死！給我廢了他雙手！
△ 四名保鏢暴起撲上，林辰反手抓住領頭手腕順勢一擰，骨裂聲起，保鏢倒飛砸碎整面酒櫃。
△ 玻璃碎裂，酒水橫流，全場死寂，陳峰踉蹌後退撞翻茶几。
陳峰（色厲內荏）：你……你敢動手？你知道我爸是誰嗎？
△ 中景：包廂門被推開，聞訊趕來的酒店經理滿頭大汗擠進人群，站在一旁不敢出聲。
蘇清雪（攥緊手包）：林辰，你今天要是踏出這個門，咱倆的婚事就算徹底完了。
林辰（撣了撣袖口）：婚事？當年你蘇家跪著退婚的時候，怎麼不記得提這兩個字？
△ 蘇清雪被噎得臉色一陣青一陣白，捏著包帶的指節收緊，再沒敢抬頭。
林辰：在江城，能讓我跪的，只有已故的先人。
△ 林辰從懷中掏出一枚九龍玄鐵令，重重拍在桌上，震得酒杯齊齊炸裂。
林辰（字字如刀）：傳我龍王令，十分鐘內，讓江城陳氏集團徹底破產。
△ 特寫：陳峰死死盯著令牌上的九龍圖騰，雙腿劇烈發抖，手機瘋狂震動，來電顯示"父親"。
林辰（聲音極低）：三年了，你陳家欠的賬，一筆一筆都在這兒。
陳峰（嘶啞）：我……我錯了，我這就去給你賠罪。
林辰：賠罪的話，留著跟我的律師說。
△ 陳峰的膝蓋一軟，扶著茶几才沒跪下去。
蘇清雪（發顫）：林辰，我們好歹有過情分，你別趕盡殺絕。
林辰（淡淡）：情分？你踩著它上台的時候，忘了？
△ 滿堂保鏢誰也不敢上前，齊齊往門邊退。
林辰：今天走出這扇門的，我一個都不追究。
△ 話音一落，保鏢們爭先恐後湧向門口。
陳峰（急）：你連他們也收買了？
林辰：我用不著收買。他們只是比你，看得清形勢。
蘇清雪：林辰，看在過去的情分上，放過陳家吧。
陳峰：爸……爸，你在哪兒啊……
蘇清雪：這些事，我什麼都不知道。
△ 陳峰把臉埋進手裡，肩膀一抽一抽地抖。
△ 陳峰癱坐在地，手機屏幕還亮著，來電仍在閃。

【本集斷章卡點】：陳峰顫抖著接通電話，那頭傳來絕望哭嚎："逆子，你到底得罪了誰？陳家徹底完了！"林辰一步踏出，居高臨下逼近。（黑屏：下滑立即解鎖第2集）
"""

BAD = """第【1】集
清晨，林辰起床拉開窗簾，太陽昇起。他在路上慢慢走。
陳峰：林辰，你要知道，三年前你害死了我父親，侵佔了我們家三千萬的財產，今天我一定要讓你血債血償，把我的東西全部還回來！
林辰：好的。
△ 他把斷肢撿起來。
"""


def self_test():
    ok = 1
    f, w, nc = validate(GOOD)
    if f:
        print("FAIL self-test: GOOD 樣例不應 FAIL:", f); ok = 0
    if nc < 100:
        print("FAIL self-test: GOOD 淨字數異常", nc); ok = 0
    f, w, _ = validate(BAD)
    if not any("E1" in x for x in f):
        print("FAIL self-test: BAD 應報 E1 或字數異常"); ok = 0
    if not any("E4" in x for x in f):
        print("FAIL self-test: BAD 應報 E4 前3秒無衝突"); ok = 0
    if not any("E6" in x for x in f):
        print("FAIL self-test: BAD 應報 E6 缺斷章"); ok = 0
    if not any("E10" in x for x in f):
        print("FAIL self-test: BAD 應報 E10 紅線詞"); ok = 0
    if not any("E5" in x for x in w):
        print("FAIL self-test: BAD 應報 E5 開篇禁詞"); ok = 0

    # 迴歸1: 字段行不應灌入 E1 體量
    hdr_only = "第【1】集\n【所屬階段】：第X幕・（第 1/80 集 ｜ 往返第 N 回合）\n【黃金前3秒鉤子】：極端羞辱型（婚禮當眾）\n【情緒流變】：受辱 ➔ 隱忍 ➔ 反殺 ➔ 絕命斷章\n【本集時長】：108 秒\n[場景]：內景·會所·夜\n[人物]：林辰、陳峰\n"
    if net_chars(hdr_only) != 0:
        print("FAIL self-test: 純字段/標記行應計 0 字，實得", net_chars(hdr_only)); ok = 0

    # 迴歸2: 以 △ 開場的廢鏡頭劇本，E4 必須攔截
    boring = "第【1】集\n[場景]：內景·客廳·日\n[人物]：甲、乙\n△ 他慢慢走進客廳，端起茶杯喝了一口。\n△ 他看了看窗外。\n甲：今天天氣不錯。\n乙：是啊。\n甲：那先這樣。\n乙：好。\n【本集斷章卡點】：兩人告別。（黑屏）\n"
    f, w, _ = validate(boring)
    if not any("E4" in x for x in f):
        print("FAIL self-test: △ 開場的廢鏡頭劇本應報 E4"); ok = 0

    # 迴歸3: 漫劇檔體量(330~620)應可用
    anime = "第【1】集：漫劇\n【情緒流變】：受辱 ➔ 隱忍 ➔ 反殺 ➔ 絕命斷章\n[場景]：內景·堂·日\n[人物]：甲、乙\n" + "".join(f"△ 具體的物理動作行編號{i}，可被鏡頭拍到的行為事件推進本集衝突。\n" for i in range(18)) + "甲：你確定要這麼做？\n乙：我確定。\n甲：那就別怪我。\n乙：來吧。\n【本集斷章卡點】：燈滅人散，只餘一擊。（黑屏：下滑解鎖）\n"
    f, w, _ = validate(anime)
    if any("E1" in x for x in f):
        print("FAIL self-test: 漫劇檔不應報 E1 區衝突:", [x for x in f if 'E1' in x]); ok = 0

    # 迴歸4: 台詞上限 25（WARN 非攔截）
    longline = "第【1】集\n[場景]：內景\n[人物]：甲\n△ 拍桌。\n甲：這是超過二十五個字的長複合句用來觸發告警檢查是否生效一二三四五六七八。\n【本集斷章卡點】：黑屏（黑屏）\n"
    f, w, _ = validate(longline)
    if not any("E2" in x for x in w):
        print("FAIL self-test: >25 字台詞應報 E2"); ok = 0

    # 迴歸5: 長檔（150~195 秒彈性）
    long_body = ("".join(f"△ 受力事件{i}：巴掌扇到半空被反手抓住，衝突再升一級。\n" for i in range(10))
                 + "".join(f"林辰：第{i}句攻防颱詞，拋出新信息並抬價施壓。\n" for i in range(48)))
    long_good = ("第【1】集：長檔樣例（長檔·約3分鐘）\n【本集時長】：180 秒\n"
                 "[場景]：內景·會所·夜\n[場景]：內景·走廊·夜\n[人物]：林辰、陳峰\n"
                 + long_body
                 + "【本集中段小鉤】：手機亮起病危通知單，繳費截止今晚，對面按下掛斷鍵。\n"
                 + "△ 林辰反手擰腕，骨裂聲起，鐵棍滾落。\n"
                 + "【本集斷章卡點】：電話那頭傳來絕望哭嚎，陳峰雙腿發抖。（黑屏：下滑解鎖第2集）\n")
    f, w, nc = validate(long_good)
    if f:
        print("FAIL self-test: 長檔樣例不應 FAIL:", f, "體量", nc); ok = 0
    if not (NET_LONG_MIN <= nc <= NET_LONG_MAX):
        print(f"FAIL self-test: 長檔樣例體量 {nc} 應在 {NET_LONG_MIN}~{NET_LONG_MAX}"); ok = 0
    f, _, _ = validate(long_good.replace("【本集中段小鉤】", "【中段】"))
    if not any("E11" in x for x in f):
        print("FAIL self-test: 長檔缺中段小鉤應報 E11"); ok = 0
    f, _, _ = validate(long_good.replace(
        "".join(f"林辰：第{i}句攻防颱詞，拋出新信息並抬價施壓。\n" for i in range(48)),
        "".join(f"林辰：第{i}句攻防颱詞，拋出新信息並抬價施壓。\n" for i in range(16))))
    if not any("E16" in x for x in f):
        print("FAIL self-test: 台詞量不足仍標 180 秒應報 E16 時長虛標:", f); ok = 0
    f, _, _ = validate(long_good.replace("【本集時長】：180 秒", "【本集時長】：110 秒"), profile="long")
    if not any("E17" in x for x in f):
        print("FAIL self-test: 長檔標 110 秒應報 E17 長檔降級:", f); ok = 0
    for _d in (150, 180, 195):
        f, _, _ = validate(long_good.replace("【本集時長】：180 秒", f"【本集時長】：{_d} 秒"), profile="long")
        if any("E17" in x for x in f):
            print(f"FAIL self-test: 長檔標 {_d} 秒不應報 E17:", [x for x in f if "E17" in x]); ok = 0
    f, w, _ = validate(GOOD, profile="long")
    if not any("E11" in x for x in f):
        print("FAIL self-test: 標準檔樣本按 long 顯式機檢應報 E11"); ok = 0
    f, _, _ = validate(BAD, profile="long")
    if not any("E1" in x for x in f):
        print("FAIL self-test: 極端空稿應報 E1"); ok = 0
    f, _, _ = validate(long_good.replace("【本集時長】：180 秒", "【本集時長】：60 秒"), profile="manju")
    if any("E1" in x for x in f):
        print("FAIL self-test: 體量超參考帶上限不應 FAIL:", [x for x in f if "E1" in x]); ok = 0
    f, _, _ = validate(long_good + "[場景]：內景·車庫·夜\n[場景]：內景·天台·夜\n")
    if not any("E3" in x for x in f):
        print("FAIL self-test: 長檔 4 場景應報 E3"); ok = 0

    # ---- 保護性反例（NOTE 級）迴歸 ----
    n = collect_notes(GOOD)
    if n:
        print("FAIL self-test: GOOD 樣例不應產生 NOTE:", n); ok = 0
    n = collect_notes(long_good)
    if n:
        print("FAIL self-test: 長檔樣例不應產生 NOTE:", n); ok = 0

    frag = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
            "甲：跪下。\n乙：憑什麼。\n甲：閉嘴。\n乙：你敢。\n甲：再說。\n乙：罷了。\n"
            "【本集斷章卡點】：巴掌落下，滿堂死寂，門外腳步聲驟起，全家齊齊轉頭望去，畫面定住。（黑屏：下滑立即解鎖第2集）\n")
    if not any("N12" in x for x in collect_notes(frag)):
        print("FAIL self-test: 連續短對白應報 N12 碎句化"); ok = 0

    dump = ("第【1】集\n[場景]：內景\n[人物]：甲\n"
            + "".join("△ 抬手。\n" for _ in range(14))
            + "甲：你來了。\n"
            + "【本集斷章卡點】：門開，光湧進來，甲緩緩抬頭，畫面定住，下滑立即解鎖下一集內容。\n")
    if not any("N13" in x for x in collect_notes(dump)):
        print("FAIL self-test: 堆低信息動作行應報 N13"); ok = 0

    thin = ("第【1】集\n[場景]：內景\n[人物]：甲\n△ 把刀拍在桌上。\n甲：說。\n"
            "【本集斷章卡點】：黑屏。\n")
    if not any("N14" in x for x in collect_notes(thin)):
        print("FAIL self-test: 體量貼下限且斷章過乾應報 N14"); ok = 0

    for sample in (frag, dump, thin, GOOD):
        f, _, _ = validate(sample)
        bad = [x for x in f if re.match(r"^N\d", x)]
        if bad:
            print("FAIL self-test: NOTE 級不應出現在 FAIL 列表:", bad); ok = 0

    # ---- 獨白 / 旁白（VO）迴歸 ----
    vo_fill = ("第【1】集\n[場景]：內景·堂屋·日\n[人物]：周韶華、二兒媳\n"
               "△ 巴掌扇到半空被反手抓住，滿堂死寂。\n"
               "二兒媳：周韶華你說是不是。\n"
               "△ 周韶華的手攥緊圍裙，指節發白。\n"
               "內心獨白：我給他生了五個孩子。\n"
               "△ 二兒媳抬手指著她鼻尖。\n"
               "周韶華：我說是。\n"
               "△ 滿堂人齊齊轉頭。\n"
               "旁白：老實人反抗了。\n"
               "二兒媳：你說。\n"
               "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    f, w, _ = validate(vo_fill)
    if not any("E9" in x for x in w):
        print("FAIL self-test: 獨白不應計入對白行（應報 E9 不足）"); ok = 0
    if any("E12" in x or "E13" in x or "E15" in x for x in f):
        print("FAIL self-test: 合規的獨白樣本不應報 E12/E13/E15:", f); ok = 0

    vo28 = "我這一輩子給他生了五個孩子，他走的那天我還在燈下縫他的棉襖。"
    vo_long = ("第【1】集：長檔樣例（長檔·約3分鐘）\n[場景]：內景·堂屋·日\n[人物]：周韶華\n"
               "△ 巴掌扇到半空被反手抓住，滿堂死寂。\n"
               "周韶華：你回來了。\n"
               "△ 二兒媳抬手指著她鼻尖，滿堂人齊齊轉頭，目光全部釘在她臉上。\n"
               + f"內心獨白：{vo28}\n"
               + "【本集中段小鉤】：手機亮起病危通知單，繳費截止今晚。\n"
               + "△ 反手擰腕，鐵棍滾落。\n甲：跪下。\n"
               + "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    f, w, _ = validate(vo_long)
    if any(x.startswith("E2 ") for x in w):
        print("FAIL self-test: 獨白不應按台詞 25 字上限報 E2:", [x for x in w if x.startswith("E2 ")]); ok = 0
    if any("E12" in x for x in f):
        print("FAIL self-test: 長檔 28 字獨白不應報 E12(上限 30):", [x for x in f if "E12" in x]); ok = 0

    f, _, _ = validate(vo_fill.replace("旁白：老實人反抗了。", "內心獨白：這一世我誰都不欠了。"))
    if not any("E12" in x for x in f):
        print("FAIL self-test: 標準檔 2 處內心獨白應報 E12"); ok = 0

    f, _, _ = validate("第【1】集\n[場景]：內景·堂屋·日\n[人物]：甲\n△ 巴掌扇到半空被反手抓住。\n"
                       "內心獨白：我給他生了五個孩子。\n旁白：老實人反抗了。\n"
                       "甲：你說是不是。\n乙：我說是。\n丙：我說不是。\n"
                       "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    if not any("E13" in x for x in f):
        print("FAIL self-test: 連續兩條獨白應報 E13"); ok = 0

    f, _, _ = validate("第【1】集\n[場景]：內景·堂屋·日\n[人物]：甲\n△ 巴掌扇到半空被反手抓住。\n"
                       "甲：你說是不是。\n乙：我說是。\n丙：我說不是。\n丁：我說是。\n"
                       "內心獨白：這一世我誰都不欠了。\n"
                       "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    if not any("E13" in x for x in f):
        print("FAIL self-test: 獨白緊貼斷章應報 E13"); ok = 0

    f, _, _ = validate("第【1】集\n[場景]：內景·堂屋·日\n[人物]：甲\n"
                       "內心獨白：我給他生了五個孩子。\n△ 巴掌扇到半空被反手抓住。\n"
                       "甲：你說是不是。\n乙：我說是。\n"
                       "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    if not any("E15" in x for x in f):
        print("FAIL self-test: 前3秒獨白應報 E15"); ok = 0

    f, w, _ = validate(vo_fill.replace("內心獨白：我給他生了五個孩子。", "內心獨白：這一切都要從三十年前說起。"))
    if not any("E14" in x for x in w):
        print("FAIL self-test: 獨白交代設定應報 E14"); ok = 0

    # ---- 對白語氣供給（E18 · v3.4.3 / v5.0）迴歸 ----
    f, w, _ = validate(GOOD.replace("蘇清雪（冷漠）：", "蘇清雪（生氣）："))
    if not any("E18a" in x for x in w):
        print("FAIL self-test: 神態短語空泛情緒詞應報 E18a:", [x for x in w if "E18" in x]); ok = 0
    t2 = GOOD
    for a, b in (("（吐出菸圈）", "（把玩打火機）"), ("（冷漠）", "（抱臂）"),
                 ("（聲音極低）", "（盯著他）"), ("（惱羞成怒）", "（踹翻椅子）"),
                 ("（字字如刀）", "（指著令牌）"), ("（色厲內荏）", "（後退半步）"),
                 ("（嘶啞）", "（攥拳）"), ("（發顫）", "（低頭）"), ("（淡淡）", "（轉開臉）")):
        t2 = t2.replace(a, b)
    f, w, _ = validate(t2)
    if not any("E18b" in x for x in w):
        print("FAIL self-test: 全篇對白零語氣詞應報 E18b:", [x for x in w if "E18" in x]); ok = 0
    t3 = GOOD.replace("蘇清雪（冷漠）：", "蘇清雪（抱臂後退｜冷漠疏離）：")
    f, w, _ = validate(t3)
    if any("E18a" in x or "E18b" in x for x in w):
        print("FAIL self-test: 合規語氣供給不應報 E18:", [x for x in w if "E18" in x]); ok = 0
    t4 = GOOD.replace("林辰（聲音極低）：三年前你陳家跪著求我救命時，也是這副嘴臉？",
                      "林辰：他競然敢這麼說話。")
    f, w, _ = validate(t4)
    if not any("E22" in x for x in w):
        print("FAIL self-test: 錯別字應報 E22:", [x for x in w if "E22" in x]); ok = 0
    _act_body = ("[場景]：內景·樓道·夜\n[人物]：陳默、張叔\n"
                 + "".join(f"△ 準備動作{i}：他把加固鋼板一塊塊擰上去，火星四濺，處境又安全一層。\n" for i in range(14))
                 + "張叔（嗤笑）：你這是要把整棟樓拆了重蓋一遍啊？\n△ 陳默沒抬頭，繼續擰螺絲。\n"
                 + "張叔（揚聲）：我跟物業打過招呼了，明天就來人拆。\n△ 陳默把螺絲擰到底，手背青筋繃起。\n"
                 + "張叔（敲了敲鋼板）：一宿一宿折騰，你到底圖個什麼？\n△ 陳默彎腰，把最後一顆鉚釘敲進去。\n"
                 + "陳默（平靜）：明天要停電，你現在下樓還來得及。\n△ 陳默轉身，把水桶推到門口。\n"
                 + "張叔（大笑）：停電？就你信這個，瘋子。\n【本集中段小鉤】：路燈全滅，整片小區陷入黑暗。\n"
                 + "【本集斷章卡點】：樓下傳來第二聲悶響，備用發電機沒響。（黑屏：下滑解鎖）\n")
    _hdr = "第【1】集\n【質疑者配角】：樓下張叔\n【本集時長】：180 秒\n"
    f1, w1, _ = validate(_hdr + "【衝突形態】：行動型\n" + _act_body, profile="long")
    f2, w2, _ = validate(_hdr + _act_body, profile="long")
    if not any("E9" in x for x in w2) or not any("E21" in x for x in w2):
        print("FAIL self-test: 無形態標記的對白少年應報 E9/E21:", w2); ok = 0
    if any("E9" in x for x in w1) or any("E21" in x for x in w1):
        print("FAIL self-test: 行動型不應報 E9/E21:", w1); ok = 0
    _t6 = ("第【1】集\n【質疑者配角】：張叔\n【本集時長】：150 秒\n[場景]：內景·樓頂\n[人物]：陳默、張叔\n"
           + "".join(f"△ 準備動作{i}：他把鋼板一塊塊擰上去，火光四濺，處境又安全一層。\n" for i in range(20))
           + "".join(f"陳默：第{i}句台詞，字數大概就是二十個字左右。\n" for i in range(20)))
    _fa, _, _ = validate(_t6, profile="long")
    _fb, _, _ = validate("【衝突形態】：行動型\n" + _t6, profile="long")
    if not any("E16" in x for x in _fa):
        print("FAIL self-test: 對話型台詞少應報 E16"); ok = 0
    if any("E16" in x for x in _fb):
        print("FAIL self-test: 行動型不應報 E16（動作拍權重）×2.5:", [x for x in _fb if "E16" in x]); ok = 0
    _t7 = ("第【1】集\n【質疑者配角】：張叔\n【本集時長】：150 秒\n[場景]：內景·樓頂\n[人物]：陳默、張叔\n"
           + "".join(f"△ 準備動作{i}：他把加固鋼板一塊塊擰上去，火星四濺，處境又安全一層。\n" for i in range(14))
           + "".join(f"陳默：第{i}句話，說完我就接著幹活。\n" for i in range(6)))
    _f7n, _w7n, _ = validate(_t7, profile="long")
    _f7m, _w7m, _ = validate("【衝突形態】：混合\n" + _t7, profile="long")
    if not any("E9" in x for x in _w7n) or not any("E21" in x for x in _w7n):
        print("FAIL self-test: 對話型應報 E9/E21:", _w7n); ok = 0
    if any("E9" in x for x in _w7m) or any("E21" in x for x in _w7m):
        print("FAIL self-test: 混合型不應報 E9/E21:", _w7m); ok = 0
    _t8 = ("第【1】集\n【質疑者配角】：張叔\n[場景]：內景\n[人物]：陳默、張叔\n"
           + "".join("△ 他抬手。\n" for _ in range(14))
           + "張叔：你瘋了。\n陳默：嗯。\n張叔：真的瘋了。\n陳默：嗯。\n"
           + "【本集斷章卡點】：門被風吹開，鋼板在夜裡晃了一下，燈滅了。（黑屏：下滑立即解鎖第2集）\n")
    if not any("N13" in x for x in collect_notes(_t8, "long")):
        print("FAIL self-test: 對話型堆動作應報 N13"); ok = 0
    if any("N13" in x for x in collect_notes("【衝突形態】：行動型\n" + _t8, "long")):
        print("FAIL self-test: 行動型不應報 N13（堆動作豁免）"); ok = 0
    _t9 = ("第【1】集\n【本集時長】：150 秒\n[場景]：內景·樓道\n[人物]：陳默、張叔\n"
           "△ 他把三十箱礦泉水一箱箱搬上樓，垛在門口。\n"
           + "陳默：嗯。\n張叔：嗯。\n陳默：嗯。\n張叔：嗯。\n陳默：嗯。\n張叔：嗯。\n陳默：嗯。\n張叔：嗯。\n"
           "【本集斷章卡點】：燈滅了，門卻亮著。（黑屏：下滑解鎖）\n")
    _f9a, _, _ = validate(_t9, profile="long")
    _f9b, _, _ = validate("【衝突形態】：行動堅持型\n" + _t9, profile="long")
    if not any("E4" in x for x in _f9a):
        print("FAIL self-test: 無形態標記時反常動作開場應報 E4"); ok = 0
    if any("E4" in x for x in _f9b):
        print("FAIL self-test: 行動型反常動作開場不應報 E4:", [x for x in _f9b if "E4" in x]); ok = 0

    # ---- E19 15秒窗口台詞密度迴歸 ----
    e19 = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
           + "".join(f"甲：第{i}輪連續攻防颱詞，把新證據新代價和施壓一步一步講透抬價壓上。\n" for i in range(6))
           + "乙：我知道了。\n"
           + "【本集斷章卡點】：滿堂死寂，畫面定住。（黑屏：下滑立即解鎖第2集）\n")
    f, w, _ = validate(e19)
    if not any("E19" in x for x in w):
        print("FAIL self-test: 連續對白超95字應報 E19 WARN:", w); ok = 0
    e19_ok = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
              "甲：第一輪連續攻防颱詞，把新證據新代價一步一步講透抬價。\n△ 甲反手摁住對方手腕。\n"
              "乙：第二輪連續攻防颱詞，把新代價和施壓一步一步講透抬價。\n△ 乙後退半步。\n"
              "甲：第三輪連續攻防颱詞，把新證據一步一步講透抬價壓上。\n"
              "【本集斷章卡點】：滿堂死寂，畫面定住。（黑屏：下滑立即解鎖第2集）\n")
    f, w, _ = validate(e19_ok)
    if any("E19" in x for x in w):
        print("FAIL self-test: 帶動作行斷點的對白不應報 E19:", w); ok = 0

    # ---- E20 動作單段≤40字 / E21 對白動作黃金比迴歸 ----
    e20 = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n"
           "△ 特寫：陳峰死死盯著桌上令牌上的九龍圖騰，雙腿劇烈發抖手機瘋狂震動不停，來電顯示父親兩個字整個人癱軟在地上再也站不起來。\n"
           "甲：跪下。\n乙：你敢。\n甲：閉嘴。\n乙：罷了。\n"
           "【本集斷章卡點】：門被踹開，滿堂死寂。（黑屏：下滑立即解鎖第2集）\n")
    f, w, _ = validate(e20)
    if not any(x.startswith("E20 ") for x in w):
        print("FAIL self-test: 單條△動作>40字應報 E20 WARN:", w); ok = 0
    bal_ok = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
              "甲：你今天必須把這筆賬給我算清楚。\n△ 甲反手摁住對方手腕。\n"
              "乙：我沒什麼好跟你算清楚的。\n△ 乙後退半步。\n"
              "甲：那就別怪我翻臉不認人。\n"
              "【本集斷章卡點】：滿堂死寂。（黑屏：下滑解鎖）\n")
    f, w, _ = validate(bal_ok)
    if any(x.startswith("E20 ") for x in w):
        print("FAIL self-test: 短△鏡頭不應報 E20:", w); ok = 0
    if any(x.startswith("E21 ") for x in w):
        print("FAIL self-test: 均衡對白動作比不應報 E21:", w); ok = 0
    e21_high = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 拍桌。\n"
                + "".join(f"甲：第{i}輪唇槍舌戰，拋出新證據新代價並步步抬價施壓。\n" for i in range(8))
                + "【本集斷章卡點】：滿堂死寂。（黑屏：下滑解鎖）\n")
    f, w, _ = validate(e21_high)
    if not any(x.startswith("E21 ") and ">70%" in x for x in w):
        print("FAIL self-test: 對白佔比>70%應報 E21 WARN:", w); ok = 0
    e21_low = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n"
               + "".join(f"△ 第{i}拍具體物理動作，鏡頭可拍的行為事件推進衝突再升級。\n" for i in range(8))
               + "甲：來。\n"
               + "【本集斷章卡點】：滿堂死寂。（黑屏：下滑解鎖）\n")
    f, w, _ = validate(e21_low)
    if not any(x.startswith("E21 ") and "<25%" in x for x in w):
        print("FAIL self-test: 對白佔比<25%應報 E21 WARN:", w); ok = 0

    # ---- v4.9 新增：E24 乾聊斷層 / E25 謎語黑話 / E26 無效微動作迴歸 ----
    e24_dry = ("第【1】集\n[場景]：內景·堂·日\n[人物]：甲、乙\n△ 巴掌扇到半空被反手抓住。\n"
               "甲（厲聲）：把錢交出來！\n乙（冷笑）：沒錢！\n甲：你找死！\n乙：你敢動我？\n"
               "甲：你看我敢不敢！\n乙：有本事來啊！\n甲：今天饒不了你！\n"
               "【本集斷章卡點】：滿堂死寂。（黑屏：下滑解鎖）\n")
    _, w24, _ = validate(e24_dry)
    if not any(x.startswith("E24 ") for x in w24):
        print("FAIL self-test: 連續7行對白無△應報 E24 WARN:", w24); ok = 0
    if any(x.startswith("E24 ") for x in validate(GOOD)[1]):
        print("FAIL self-test: GOOD 樣例不應報 E24"); ok = 0

    e25_jargon = GOOD.replace("三年了，你陳家欠的賬，一筆一筆都在這兒。", "你的氣運錨點已經觸發因果閉環。")
    _, w25, _ = validate(e25_jargon)
    if not any(x.startswith("E25 ") for x in w25):
        print("FAIL self-test: 含晦澀黑話應報 E25 WARN:", w25); ok = 0

    e26_weak = GOOD.replace("△ 陳峰的膝蓋一軟，扶著茶几才沒跪下去。", "△ 陳峰眼神微動。")
    _, w26, _ = validate(e26_weak)
    if not any(x.startswith("E26 ") for x in w26):
        print("FAIL self-test: 無效微動作應報 E26 WARN:", w26); ok = 0

    # ---- v5.0 新增：E18c 括號常態套話 / E27 機械鏡頭標籤堆砌迴歸 ----
    e18c_canned = GOOD.replace("蘇清雪（冷漠）：", "蘇清雪（眼神微冷）：")
    _, w18c, _ = validate(e18c_canned)
    if not any(x.startswith("E18c ") for x in w18c):
        print("FAIL self-test: 括號含眼神微冷應報 E18c WARN:", w18c); ok = 0

    e27_cam = GOOD.replace("△ 玻璃碎裂，酒水橫流", "△ 【慢鏡頭】玻璃碎裂，酒水橫流").replace(
        "△ 陳峰的膝蓋一軟", "△ 【慢鏡頭】陳峰的膝蓋一軟")
    _, w27, _ = validate(e27_cam)
    if not any(x.startswith("E27 ") for x in w27):
        print("FAIL self-test: 單集>=2處【慢鏡頭】應報 E27 WARN:", w27); ok = 0


    # ---- v5.1 新增：E37~E40 視聽可拍性四門禁迴歸 ----
    e37_bad = GOOD.replace("△ 陳峰的膝蓋一軟，扶著茶几才沒跪下去。", "△ 林辰非但沒跪，反而看都沒看一眼。")
    f37, _, _ = validate(e37_bad)
    if not any(x.startswith("E37 ") for x in f37):
        print("FAIL self-test: 否定式偽動作應報 E37 FAIL:", f37); ok = 0

    e38_bad = GOOD.replace("△ 陳峰的膝蓋一軟，扶著茶几才沒跪下去。", "△ 林辰接過密信塞進懷裡。")
    _, w38, _ = validate(e38_bad)
    if not any(x.startswith("E38 ") for x in w38):
        print("FAIL self-test: 無來源接過道具應報 E38 WARN:", w38); ok = 0

    e39_bad = GOOD.replace("林辰：賠罪的話，留著跟我的律師說。", "林辰：什麼赤霄玉佩？你瘋了吧！")
    _, w39, _ = validate(e39_bad)
    if not any(x.startswith("E39 ") for x in w39):
        print("FAIL self-test: 未提先知反問應報 E39 WARN:", w39); ok = 0

    e40_bad = GOOD.replace("【本集斷章卡點】：", "[場景]：內景·頂級私人會所·夜\n△ 陳峰站在原地發抖。\n【本集斷章卡點】：")
    _, w40, _ = validate(e40_bad)
    if not any(x.startswith("E40 ") for x in w40):
        print("FAIL self-test: 同空間假切場應報 E40 WARN:", w40); ok = 0

    print("[+] self-test PASSED" if ok else "[-] self-test FAILED")
    return 0 if ok else 1


def parse_args(args):
    """返回 (path, profile, prev_paths)；用法錯誤拋 SystemExit(2)"""
    path, profile, prevs = None, "auto", []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--prev":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                prevs.append(args[i]); i += 1
            continue
        if a == "--long":
            profile = "long"
        elif a == "--manju":
            profile = "manju"
        elif a == "--format" or a.startswith("--format="):
            val = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if "=" not in a:
                i += 1
            if val not in PROFILES:
                print(f"[-] --format 只接受 {'/'.join(PROFILES)}，收到「{val}」"); raise SystemExit(2)
            profile = val
        elif a.startswith("--"):
            print(f"[-] 未知參數「{a}」"); raise SystemExit(2)
        elif path is None:
            path = a
        i += 1
    return path, profile, prevs


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    if args[0] == "--self-test":
        return self_test()
    try:
        path, profile, prevs = parse_args(args)
    except SystemExit as e:
        return e.code or 2
    if not path:
        print(__doc__); return 2
    try:
        text = open(path, encoding="utf-8-sig").read()
    except FileNotFoundError:
        print(f"[-] 找不到劇本文件: {path}"); return 2
    except IsADirectoryError:
        print(f"[-] 路徑是目錄，不是劇本文件: {path}"); return 2
    except UnicodeDecodeError:
        print(f"[-] 文件不是 UTF-8 文本，無法讀取: {path}"); return 2
    except OSError as e:
        print(f"[-] 無法讀取劇本文件: {path}（{e}）"); return 2
    for p in prevs:
        try:
            open(p, encoding="utf-8-sig").read()
        except FileNotFoundError:
            print(f"[-] 找不到前集文件: {p}"); return 2
        except (UnicodeDecodeError, OSError):
            print(f"[-] 無法讀取前集文件: {p}"); return 2
    prev_texts = [open(p, encoding="utf-8-sig").read() for p in prevs]
    profile = resolve_profile(text, profile)
    fails, warns, nc = validate(text, prev_texts, profile)
    notes = collect_notes(text, profile)
    print(f"== {path}  [{profile} {PROFILES[profile]['label']}]  正文體量≈{nc} ==")
    for x in fails:
        print("[-] FAIL:", x)
    for x in warns:
        print("[!] WARN:", x)
    for x in notes:
        print("[i] NOTE:", x, "  ← 保護性反例，不要求修改")
    if fails:
        print("結果: FAILED（修復後重跑）"); return 1
    tail = []
    if warns:
        tail.append("含 WARN 請複核")
    if notes:
        tail.append("含 NOTE（非缺陷，勿過度修正）")
    print("結果: PASSED" + ("（" + "；".join(tail) + "）" if tail else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
