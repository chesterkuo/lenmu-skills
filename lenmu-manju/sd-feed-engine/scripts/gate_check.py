# -*- coding: utf-8 -*-
"""
gate_check.py · 投餵層閘門校驗器（P14 判據級去重版）

用法：python gate_check.py <投餵稿.md> [--model 2.5|2.0] [--assets N] [--mode M0|M1|M2|auto]
                          [--tol 0.8] [--syntax auto|on|off] [--aspect 16:9]
設計依據：sd-feed-engine/references/feed-mode-and-gates.md §二（閘門分工表）

★P14 判據級去重（用戶裁定：同一內容不反覆檢查）
  病灶：本腳本此前把 C 系已經實現的判據又寫了一遍，註釋裡直接標著「（C16b）」「C11」——
        同一個語氣位缺失、同一份鏡長雷同、同一套七段式字段，出一次稿要查兩遍。
  處置：**一條判據只留一處實現**。
    ① 本腳本**只管 C 系沒有的四類投餵層判據**（見下「保留清單」）；
    ② 與 C 系重複的判據**整段摘除**，改由 `--syntax` 一次性調用總控機檢引擎覆蓋，
       等級不變（原 FAIL 項在 C 系裡仍是 FAIL 級），不會因去重而放鬆任何紅線；
    ③ 獨裝本子技能、找不到總控引擎時，自動降級為「只跑本層閘門」並明確提示加跑機檢。

  保留清單（C 系無對應實現 · 已逐條實查）：
    閘門0  【】配對閉合 + 鏡號連續性（C7 只管七段缺欄、C11 只管接續狀態殘留，**都不管這兩項**）
    閘門1  節奏檔位     長段只有 1~2 鏡（C1b 管段長區間、C2 管鏡數下限，均不等價）
    閘門2  台詞時長     字數÷語速+停頓 vs 鏡長（語速檔解算，C16 系只管語氣位有無/質量）
    閘門3  段級字數     單段 2.0 ≤2900/3000、2.5 ≤3600/4000（C4 是**篇級** 6000 字符兜底）
    閘門4  交接話術     「以下是/希望對你有幫助」類 AI 對話殘餘 + 代碼框內外參數位置
    閘門5  圖片上限     單段引用圖號數按模型分檔（2.5→30 / 2.0→9）
    閘門6A 圖號越庫     稿內圖號 ∉ 項目資產庫圖數
    閘門6B 素材形態     M0/M1/M2 聲明一致性 + 接線單雙向一致 + 虛假核驗斷言

  已移交 C 系（本腳本不再重複實現）：
    閘門0·七段式缺字段 → C7；閘門0·【接續狀態】殘留 → C11
    閘門1b 鏡長雷同（同段 ≥4 鏡、同值佔比 ≥70%）→ C13
    閘門2 台詞缺語氣位 → C16b

閘門 6 擴展（素材形態一致性 · 權威 = 總控 references/asset-delivery-modes.md）：
  本包**不持有圖**——圖由用戶在外部平台生成並持有。素材形態三檔 M0/M1/M2（默認 M1）。
  閘門 6 = 6A 編號一致性 + 6B 素材形態一致性：
    未聲明形態 → WARN；M0 稿內出現圖號 → FAIL（形態違約）；
    M1 有圖號但無《素材接線單》→ WARN；稿內圖號 ∉ 接線單圖號 → FAIL；
    出現"已核驗/核對一致"類斷言而形態非 M2 → FAIL（虛假核驗）。
"""
import re, sys, io, os, argparse, subprocess

if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ---------- 語速表 ----------
# 只有"節奏維"詞才真正決定語速檔；"壓著嗓子/嘶啞/沉聲"是音質力度描述，不必然慢。
SPEED_BANDS = [
    (r'耳語|氣聲|一字一頓|一字一停|一字一句|拖長|斷續|哽咽|抽氣', 2.5, 3.5, '慢速重音（節奏維慢）'),
    (r'低語|低聲|壓抑|嘶啞|沉聲|沉冷|宣判|喃喃|放緩', 3.5, 4.5, '偏慢'),
    (r'爭吵|吼|喊|嚷|咆哮|搶話|慌亂|急促|連珠|語速快', 5.0, 7.0, '快速/爭吵/搶話'),
]
SPEED_DEFAULT = (3.5, 7.0, '標準~高速（判定按 7 字/秒）')

PAUSE = [('，', 0.2), ('、', 0.2), ('。', 0.4), ('？', 0.4), ('！', 0.4), ('…', 0.8), ('——', 0.6)]

# ---------- 閘門5 單組圖片上限（★2026-10-17 分檔修復）----------
# 病根：原實現寫死 `if len(figs) > 9`，**不讀 --model**，與文檔閘門5（2.0≤9 / 2.5≤30 / 2.0 單圖）
# 脫節 → 雙向誤判：2.5 掛 10~30 張被誤殺（文檔允許 30），2.0 掛 2~9 張被漏放。
# 2.0 取值依據：官方參考圖槽為「單參考圖鎖形象、無首尾幀」，但粉絲實測（2026-10-17）
#   平台側多錨點上傳 3~4 張資產圖可跑通 → 機檢暫取保守值 9，避免既壓死實測工作流又放過濫用。
# 權威 = sd-feed-engine/references/feed-mode-and-gates.md 閘門5 與
#        short-drama-director/references/asset-delivery-modes.md 數量上限段。
IMG_LIMIT_BY_MODEL = {'2.5': 30, '2.0': 9, 'jimeng': 9}
IMG_LIMIT_DEFAULT = 9


def img_limit(model, override=0):
    """閘門5 上限解算：顯式覆蓋優先，否則按 A 鎖模型分檔。"""
    return override if override else IMG_LIMIT_BY_MODEL.get(model, IMG_LIMIT_DEFAULT)


def img_gate_check(nfig, model, override=0):
    """閘門5 判定：返回 (是否超限, 上限)。★2026-10-17 抽出為純函數，供 self-test 雙向驗證。"""
    lim = img_limit(model, override)
    return (nfig > lim, lim)


def parse_units(text):
    """切分投餵單元，返回 [(標題, 代碼框正文)]，兼容 ## 【投餵單元...】 / ### 段N... / ### 第N段... / 代碼框內含【畫幅風格】"""
    unit_hdr_re = re.compile(r'^(?:##\s*【投餵單元[^\n]*|###+\s*(?:第\s*\d+\s*段|段\s*\d+)[^\n]*)', re.M)
    matches = list(unit_hdr_re.finditer(text))
    units = []
    if matches:
        for i, m in enumerate(matches):
            title = m.group(0).lstrip('#').strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk = text[start:end]
            fm = re.search(r'```(?:text|prompt)?\s*\n(.*?)```', chunk, re.S)
            if fm and '【畫幅風格】' in fm.group(1):
                units.append((title, fm.group(1)))
            elif '【畫幅風格】' in chunk and '【時間軸分鏡】' in chunk:
                units.append((title, chunk.strip()))
    if not units:
        # 兜底：直接掃描所有包含【畫幅風格】與【時間軸分鏡】的代碼框或段落
        for idx, fm in enumerate(re.finditer(r'```(?:text|prompt)?\s*\n(.*?)```', text, re.S), 1):
            if '【畫幅風格】' in fm.group(1) and '【時間軸分鏡】' in fm.group(1):
                units.append((f'段{idx}', fm.group(1)))
    return units


# 兼容三形態時碼（MM:SS-MM:SS / Xs-Ys / N-N秒）與全半角【鏡頭N】及「鏡號在前/時碼在前」雙語序
GC_TIME_RE = re.compile(
    r'(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?'
    r'|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s'
    r'|(?:\A|(?<=[\s\[【\]】]))\s*([0-9]|[1-5]\d)(?:\.\d+)?\s*[-~～→]\s*([0-9]|[1-5]\d)(?:\.\d+)?秒',
    re.I)
GC_SHOT_NO_RE = re.compile(r'[\[【]?\s*鏡頭\s*(\d+)\s*[\]】]?')


def frac_to_sec(frac):
    """秒的小數位 → 秒值（★2026-10-14 Agent 修復：統一小數秒口徑）。

    `5`→0.5 · `50`→0.5 · `05`→0.05 —— **按位數換算，不寫死 ÷100**。
    原實現寫 `fr / 100.0`，把 1 位小數 `.5` 算成 0.05：`00:03.5` → 3.05s。
    閘門 2（字數÷7 對鏡長）靠這裡的秒值判定，口徑錯會讓邊緣稿誤放行/誤攔截。
    本口徑須與總控 `scripts/sd_core.frac_to_sec`、`validate_prompt._frac_to_sec` 三處一致。
    """
    if not frac:
        return 0.0
    return int(frac) / (10 ** len(frac))


def parse_shots(body):
    """解析鏡行，返回 [(鏡號, 起秒, 止秒, 全行)]，兼容 MM:SS(.s) / Xs-Ys / N-N秒 與全半角鏡號。"""
    shots = []
    auto_no = 0
    for line in body.splitlines():
        tm = GC_TIME_RE.search(line)
        if not tm:
            continue
        if tm.group(1) is not None:
            s = int(tm.group(1)) * 60 + int(tm.group(2)) + frac_to_sec(tm.group(3))
            e = int(tm.group(4)) * 60 + int(tm.group(5)) + frac_to_sec(tm.group(6))
        elif tm.group(7) is not None:
            s, e = float(tm.group(7)), float(tm.group(8))
        else:
            s, e = float(tm.group(9)), float(tm.group(10))
        sm = GC_SHOT_NO_RE.search(line)
        auto_no += 1
        no = int(sm.group(1)) if sm else auto_no
        shots.append((no, s, e, line))
    return shots


def parse_lines(body):
    """解析台詞，返回 [(角色, 語氣, 台詞, 全行)]"""
    out = []
    # 修正：引號定界改非貪婪 `(.*?)"】` —— 台詞內嵌引號（如「先認一句"我做得夠好了"」）
    # 會把舊的 `[^"]*` 截斷或整句漏檢（靜默失檢）。新式以「"】」為唯一收尾錨點。
    pattern = r'【([^【】（(:：\n]+?)(?:[（(]([^）)\n]*)[）)])?\s*[:：]\s*["“](.*?)["”]\s*】'
    for m in re.finditer(pattern, body):
        out.append((m.group(1).strip(), (m.group(2) or '').strip(), m.group(3), m.group(0)))
    return out


# ---------- 閘門 6B · 素材形態（權威 = 總控 references/asset-delivery-modes.md） ----------
MODE_DECL = re.compile(r'素材形態[：:]\s*[（(]?\s*(M[012])')
# ★審計補丁P1：放寬標題前綴——「## 五·補 A｜素材接線單」「### 素材接線單（M1 必備）」同為合規寫法，
#   舊正則只認「## 素材接線單」開頭，導致帶章節序號的稿被判「未附接線單」（實測假告警）。
WIRING_HEAD = re.compile(r'^#{2,3}\s*[^\n]{0,12}素材接線單[^\n]*\n', re.M)
# "已核驗/核對一致"類虛假核驗斷言（排除否定與禁止語境）
FAKE_VERIFY = re.compile(r'(?<![未不])已核驗|(?<![未不])核對一致|(?<![未不])核驗通過|已與《?資產圖冊》?一致')
NEG_CTX = re.compile(r'未|不|禁止|不得|沒有|無核驗|僅適用|非')


def split_wiring(text):
    """把整份交付拆成 (提示詞正文, 接線單段)。接線單段不計入稿內圖號判定。"""
    m = WIRING_HEAD.search(text)
    if not m:
        return text, ''
    rest = text[m.end():]
    nxt = re.search(r'^##\s', rest, re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[:m.start()] + text[end:], text[m.start():end]


def check_asset_mode(text, mode_arg, fails, warns):
    """閘門 6B：素材形態一致性。返回實際生效形態。"""
    decl = MODE_DECL.search(text)
    if mode_arg in (None, '', 'auto'):
        if decl:
            mode = decl.group(1)
        else:
            mode = 'M1'
            warns.append('閘門6B 未聲明素材形態（首行應寫「素材形態：M0/M1/M2」）——'
                         '形態未定，本次按默認 M1 判定；未聲明不得交付')
    else:
        mode = mode_arg.upper()
        if not decl:
            warns.append(f'閘門6B 未聲明素材形態，本次按命令行 --mode {mode} 判定——'
                         '交付稿首行仍須補聲明')
        elif decl.group(1) != mode:
            warns.append(f'閘門6B 聲明形態 {decl.group(1)} 與 --mode {mode} 不一致，'
                         f'按聲明 {decl.group(1)} 判定——請核對')
            mode = decl.group(1)

    prompt_text, wiring_text = split_wiring(text)
    figs_prompt = sorted(set(int(x) for x in re.findall(r'圖(\d+)', prompt_text)))
    figs_wiring = sorted(set(int(x) for x in re.findall(r'圖(\d+)', wiring_text)))

    if mode == 'M0' and figs_prompt:
        fails.append(f'閘門6B 形態違約：聲明 M0（純提示詞）卻出現圖號 {figs_prompt}'
                     '——圖號槽位與 M0 互斥，須刪淨或改聲明 M1')
    if mode == 'M1' and figs_prompt:
        if not wiring_text:
            warns.append(f'閘門6B 形態違約：M1 稿件引用圖號 {figs_prompt} 但未附《素材接線單》'
                         '——接線單是 M1 交付必備件（§ 素材接線單）')
        else:
            oob = [f for f in figs_prompt if f not in figs_wiring]
            if oob:
                fails.append(f'閘門6B 稿內圖號 {oob} 不在《素材接線單》內'
                             '——用戶會去掛一張不存在的圖')
            if '不控制' not in wiring_text:
                warns.append('閘門6B 接線單缺少「不控制什麼」列/說明'
                             '——一張圖被當多張用是主要汙染源')
    if mode in ('M0', 'M1'):
        for i, line in enumerate(text.split('\n'), 1):
            if FAKE_VERIFY.search(line) and not NEG_CTX.search(line):
                fails.append(f'閘門6B 虛假核驗斷言（第 {i} 行，形態 {mode}）'
                             '——本包看不到圖，不得聲稱已核驗/與資產圖冊一致')
                break
    return mode


def speech_seconds(line, tone):
    """估算台詞秒數 → (最快可行, 最慢舒適, 字數, lo, hi)
    need_fast = n/hi + pause  ← ★判定基準（V7.3.0：hi 通常 = 7 字/秒）
    need_slow = n/lo + pause  ← 舒適參考
    """
    lo, hi = SPEED_DEFAULT[0], SPEED_DEFAULT[1]
    for pat, a, b, _ in SPEED_BANDS:
        if re.search(pat, tone):
            lo, hi = a, b
            break
    n = len(re.findall(r'[\u4e00-\u9fff\w]', line))
    pause = sum(line.count(c) * p for c, p in PAUSE)
    return n / hi + pause, n / lo + pause, n, lo, hi


def self_test():
    """閘門自身解析自檢（★2026-10-14 Agent 新增）。

    鎖兩類「靜默失效」：① 小數秒解算（`.5` 曾被算成 0.05s）；② 投餵單元切分。
    這兩類一旦失手，閘門會照打 PASS——假 PASS 比假 FAIL 危險一個量級。
    """
    ok = 0
    if frac_to_sec('5') != 0.5 or frac_to_sec('50') != 0.5 or frac_to_sec('05') != 0.05 \
       or frac_to_sec(None) != 0.0:
        print('FAIL self-test: frac_to_sec 位數換算錯誤（.5 應為 0.5s，.05 應為 0.05s）'); ok = 1
    sh = parse_shots('【時間軸分鏡】\n'
                     '00:00-00:04 [鏡頭1] 中景。甲。\n'
                     '00:04-00:08 [鏡頭2] 近景。甲。\n'
                     '00:08-00:10.5 [鏡頭3] 特寫。甲。\n'
                     '00:10.5-00:15 [鏡頭4] 全景。甲。')
    if len(sh) != 4:
        print(f'FAIL self-test: parse_shots 應解析 4 鏡，實得 {len(sh)}（丟鏡即本用例攔截目標）'); ok = 1
    elif abs(sh[2][2] - 10.5) > 1e-9 or abs(sh[3][1] - 10.5) > 1e-9:
        print(f'FAIL self-test: 00:10.5 應解為 10.5s（舊缺陷為 10.05s），實得 {sh[2][2]}'); ok = 1
    unit_md = ('## 【投餵單元 1/1 · 段1】\n'
               '```text\n【畫幅風格】16:9 橫屏\n【時間軸分鏡】\n'
               '00:00-00:04 [鏡頭1] 中景 · 平視 · 固定。甲開口。聲音：無。台詞：【甲：“你好。”】\n'
               '```\n')
    us = parse_units(unit_md)
    if len(us) != 1 or '【畫幅風格】' not in us[0][1]:
        print(f'FAIL self-test: parse_units 應切出 1 個投餵單元，實得 {len(us)}'); ok = 1
    # ★2026-10-17 閘門5 分檔雙向用例（原實現寫死 >9，兩向都會判錯）
    #   誤殺向：2.5 掛 12 張，文檔允許 30 → 必須判合規（舊實現 FAIL）
    if img_gate_check(12, '2.5')[0]:
        print('FAIL self-test: 閘門5 在 model=2.5 掛 12 圖應合規（上限 30），舊寫死 9 會誤殺'); ok = 1
    elif not img_gate_check(31, '2.5')[0]:
        print('FAIL self-test: 閘門5 在 model=2.5 掛 31 圖應超限（上限 30），實判合規'); ok = 1
    #   漏放向：2.0 掛 12 張，上限 9 → 必須判超限（舊實現只到 >9 才攔，2~9 張全放過）
    if not img_gate_check(12, '2.0')[0]:
        print('FAIL self-test: 閘門5 在 model=2.0 掛 12 圖應超限（上限 9），實判合規'); ok = 1
    elif img_gate_check(5, '2.0')[0]:
        print('FAIL self-test: 閘門5 在 model=2.0 掛 5 圖應合規（粉絲實測 ≥3 可跑通），實判超限'); ok = 1
    elif not img_gate_check(10, '2.0')[0]:
        print('FAIL self-test: 閘門5 在 model=2.0 掛 10 圖應超限（上限 9），實判合規'); ok = 1
    elif img_gate_check(40, '2.5', 40)[0]:
        print('FAIL self-test: 閘門5 --img-limit 覆蓋失效（40 應放行 40 圖）'); ok = 1
    if not ok:
        print('[+] gate_check self-test PASSED')
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', nargs='?')
    ap.add_argument('--model', default='2.5')
    ap.add_argument('--assets', type=int, default=9, help='項目資產庫總圖數')
    ap.add_argument('--img-limit', type=int, default=0, dest='img_limit',
                    help='閘門5 單組圖片上限手動覆蓋（0=按 --model 分檔：2.5→30 / 2.0→9 ）。'
                         '2026-10-17 新增：原實現寫死 9，不讀模型')
    ap.add_argument('--mode', default='auto', choices=['auto', 'M0', 'M1', 'M2', 'm0', 'm1', 'm2'],
                    help='素材形態（V7.3.0）：auto=按交付稿首行「素材形態：Mx」聲明判定，'
                         '未聲明時按默認 M1 並告警。權威 = references/asset-delivery-modes.md')
    ap.add_argument('--tol', type=float, default=0.8,
                    help='閘門2 判定容差(s)：V7.3.0 以最快檔 7 字/秒為判定基準，'
                         '僅當「字數÷7 + 停頓 > 鏡長 + tol」才判真念不完。默認 0.8')
    ap.add_argument('--syntax', default='auto', choices=['auto', 'on', 'off'],
                    help='P14 判據級去重：auto=檢測到總控機檢引擎就一次性拉取 C 系判據'
                         '（取代本腳本原先重複實現的閘門0/1b/2語氣位）；on=強制必須有引擎；'
                         'off=只跑投餵層閘門。')
    ap.add_argument('--aspect', default=None, help='畫幅（傳給機檢引擎做 C6b 三處互校）')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()

    if a.self_test:
        sys.exit(self_test())
    if not a.path:
        ap.print_help(); sys.exit(2)

    with open(a.path, encoding='utf-8') as source:
        text = source.read()
    units = parse_units(text)
    if not units:
        print('未找到投餵單元（## 【投餵單元 N/M】格式）'); sys.exit(2)

    print(f'=== 投餵層閘門 + C 系機檢（一次跑完）· {os.path.basename(a.path)} · model={a.model} ===')

    warns, fails, infos = [], [], []
    mode = check_asset_mode(text, a.mode, fails, warns)

    print(f'投餵單元：{len(units)} 段  |  閘門2 判定基準：最快檔 7 字/秒（V7.3.0）'
          f'  |  素材形態：{mode}（閘門6B · V7.3.0）\n')

    # ---- 閘門 0 · 結構完整性（P14 逐條核對後的保留項）----
    #   ⚠️ 去重必須逐條核對，不能按名字匹配：本節四項經實查，
    #      · 【】閉合 —— C 系無任何配對判據 → **保留在本層**
    #      · 鏡號連續 —— C 系只「識別」鏡號用於解析，從不校驗連續性 → **保留在本層**
    #      · 七段式缺字段 —— 已由 C7 實現 → 摘除
    #      · 【接續狀態】殘留 —— 已由 C11 實現（FAIL 級）→ 摘除
    previous_no = None
    for ui, (title, body) in enumerate(units, 1):
        for m in re.finditer(r'【[^】\n]*$', body, re.M):
            fails.append(f'閘門0 段{ui}：【 未閉合（行尾缺 】）→ {m.group(0)[:40]}')
        if body.count('【') != body.count('】'):
            fails.append(f'閘門0 段{ui}：【/】數量不等（{body.count("【")} vs {body.count("】")}）')
        for m in re.finditer(r'台詞：【[^】\n]*\n', body):
            fails.append(f'閘門0 段{ui}：台詞行未見 】 收尾 → {m.group(0)[:40]}')
        nums = [int(x) for x in GC_SHOT_NO_RE.findall(body)]
        if nums:
            if (nums != list(range(nums[0], nums[0] + len(nums))) or nums[0] < 1
                    or (previous_no is not None and nums[0] not in (1, previous_no + 1))):
                fails.append(f'閘門0 段{ui}：鏡號不連續 {nums}')
            previous_no = nums[-1]
        # 七段式缺字段 → C7；【接續狀態】殘留 → C11（P14 摘除，不重複報）

    for ui, (title, body) in enumerate(units, 1):
        shots = parse_shots(body)
        dur = (shots[-1][2] - shots[0][1]) if shots else 0
        chars = len(body)
        figs = sorted(set(int(x) for x in re.findall(r'圖(\d+)', body)))
        print(f'--- 段{ui}: {title}')
        print(f'    鏡數={len(shots)}  段長={dur}s  字數={chars}  引用圖號={figs}')

        # 閘門1 節奏檔位：10s 以上只有 1-2 鏡
        if dur >= 10 and len(shots) <= 2:
            warns.append(f'閘門1 段{ui}：{dur}s 只有 {len(shots)} 鏡，需慢節奏白名單或補標點鏡')
        # 閘門1b 鏡長雷同 —— P14 摘除：與機檢 C13 同一判據（≥4 鏡、同值佔比 ≥70%），由 C13 負責

        # 閘門2 台詞時長（以最快檔 7 字/秒為判定基準）
        #   P14：原此處的「台詞缺語氣位 → FAIL（C16b）」已整段摘除——C16b 是同一判據的權威實現
        for index, (no, s, e, shot_text) in enumerate(shots):
            dialogue = parse_lines(shot_text)
            if not dialogue:
                continue
            needs = [speech_seconds(line, tone) for _, tone, line, _ in dialogue]
            need_fast = sum(item[0] for item in needs)
            mid = sum((item[0] + item[1]) / 2 for item in needs)
            # 只有末鏡顯式聲明定格時扣減；否定定格和普通收尾不扣秒。
            freeze = re.search(r'(?:末|最後)\s*([0-9]+(?:\.[0-9]+)?|一)\s*秒\s*(?:硬)?定格', shot_text)
            reserve = 0.0
            if index == len(shots) - 1 and freeze and not re.search(
                    r'不|非|無|禁止|取消', shot_text[max(0, freeze.start() - 4):freeze.start()]):
                reserve = 1.0 if freeze.group(1) == '一' else float(freeze.group(1))
            budget = max(0.0, e - s - reserve)
            if need_fast > budget + a.tol:
                warns.append(f'閘門2 段{ui} 鏡頭{no}：{len(dialogue)} 句累計最快需 '
                             f'{need_fast:.1f}s，可用僅 {budget}s → 真念不完')
            elif mid > budget + a.tol:
                infos.append(f'閘門2 段{ui} 鏡頭{no}：累計最快 {need_fast:.1f}s，'
                             f'標準檔需 {mid:.1f}s，可用 {budget}s → 需快念（非缺陷）')

        # 閘門3 字數（★ 2026-10-13：按模型分檔 —— 2.5 可吃更長提示詞）
        w_soft, w_hard = (3600, 4000) if a.model == '2.5' else (2900, 3000)
        if chars > w_hard:
            fails.append(f'閘門3 段{ui}：字數 {chars} > {w_hard}（model={a.model} 硬上限），必須壓縮')
        elif chars > w_soft:
            warns.append(f'閘門3 段{ui}：字數 {chars} 落在 {w_soft + 1}~{w_hard}（model={a.model}），建議壓一輪')

        # 閘門4 可投餵語義
        for bad in ['接下一大分鏡', '接下一段', '接分鏡', '承接上一段', '接上段']:
            if bad in body:
                fails.append(f'閘門4 段{ui}：含交接話術「{bad}」')
        # 參數行應在代碼框外
        # ★P9 修（2026-10-24 全流程自檢發現）：舊寫法用 `(?<!【畫幅風格】)…?aspect_ratio`
        #   做負向後顧——但七段式**法定寫法**是 `【畫幅風格】16:9 橫屏 (aspect_ratio=16:9)`，
        #   `aspect_ratio` 前面隔著「16:9 橫屏 (」，後顧永遠不成立 →
        #   **每一份合規稿都被判「參數留在代碼框內」**。這是條永遠亮紅燈的死規則。
        #   原意是「參數漏到正文裡」才報，故改為：先剝離【畫幅風格】整行，再看正文有沒有殘留。
        _body_wo_aspect = re.sub(r"^【畫幅風格】[^\n]*$", "", body, flags=re.M)
        for bad in ('分辨率', 'aspect_ratio'):
            if bad in _body_wo_aspect:
                warns.append(f'閘門4 段{ui}：參數「{bad}」疑似留在代碼框內')

        # 閘門5 單組圖片數（★2026-10-17 改為按 A 鎖模型分檔，原寫死 9 會誤殺 2.5）
        over, img_lim = img_gate_check(len(figs), a.model, a.img_limit)
        if over:
            fails.append(f'閘門5 段{ui}：單段引用 {len(figs)} 個圖號 > {img_lim}（model={a.model} 上限）')
        elif len(figs) > 9 and a.model == '2.5':
            infos.append(f'閘門5 段{ui}：單段引用 {len(figs)} 個圖號（2.5 上限 {img_lim}，合規）'
                         f'——超過 9 張時請確認每張都有明確職責，多餘圖位會稀釋一致性')

        # 閘門6A 編號一致性（圖號是否在資產庫範圍內）
        oob = [f for f in figs if f > a.assets]
        if oob:
            fails.append(f'閘門6A 段{ui}：引用圖號 {oob} 超出資產庫（共 {a.assets} 圖）')

    print()
    print('=== 投餵層閘門結果 ===')
    _g_fails, _g_warns = check_g7_g8_v76(text, units=units)
    fails.extend(_g_fails)
    warns.extend(_g_warns)

    if fails:
        print(f'FAIL {len(fails)} 條：')
        for x in fails:
            print('  ✗', x)
    if warns:
        print(f'WARN {len(warns)} 條：')
        for x in warns:
            print('  !', x)
    if infos:
        print(f'INFO {len(infos)} 條（非缺陷，僅提示需快念）：')
        for x in infos:
            print('  i', x)
    if not fails and not warns:
        print('  本層閘門全過（0 FAIL 0 WARN）')

    # ---- P14：C 系判據一次性覆蓋（取代原先在本腳本里重複實現的閘門0 / 1b / 2語氣位）----
    syntax_fail, syntax_warn, syntax_note = run_syntax_engine(
        a.path, a.model, a.aspect, a.syntax)
    if syntax_note:
        print(f'\n=== 機檢引擎（C 系）===')
        print(f'  {syntax_note}')
    if syntax_fail or syntax_warn:
        print(f'  機檢 FAIL={syntax_fail}  WARN={syntax_warn}（明細見上方 C 系段落）')

    print(f'\n彙總：投餵層 FAIL={len(fails)}  WARN={len(warns)}  |  '
          f'機檢 FAIL={syntax_fail} WARN={syntax_warn}  |  素材形態={mode}（閘門6B）')
    if syntax_note.startswith('已按') or syntax_note.startswith('未檢測'):
        print('質檢入口：本次只跑投餵層閘門（C 系未執行）——交付前務必另跑一次完整質檢。')
    else:
        print('質檢入口：本腳本一次跑完「投餵層閘門 + C 系機檢」，同一判據不再重複檢查。')
    sys.exit(1 if (fails or syntax_fail) else 0)


def _find_engine():
    """定位總控機檢引擎（套裝同級部署時存在；子技能獨立安裝時可能不存在）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    # sd-feed-engine/scripts → 套裝根 → short-drama-director/scripts/validate_prompt.py
    candidates = [
        os.path.join(here, '..', '..', 'short-drama-director', 'scripts', 'validate_prompt.py'),
        os.path.join(here, '..', '..', '..', 'short-drama-director', 'scripts', 'validate_prompt.py'),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None



def check_g7_g8_v76(text, units=None):
    """V8.2.0-SLIM-rev4 逐段空間交接硬檢：
    - G7-MOUNT / G7-PENDING：多段稿掛載表 WARN 提醒
    - G8-HANDOFF（段2+ 硬阻斷 FAIL）：多段稿自第 2 段起，每段必須自帶跨段空間交接卡（機位側= / 固定可見錨= / 世界座標）
    - G8-ANCHOR-REPEAT（段2+ 硬阻斷 FAIL）：多段稿自第 2 段起，【場景資產】或【站位聲明】必須複述房間物理錨點（C17i），防模型重排房間
    """
    fails, warns = [], []
    unit_list = list(units) if units else []
    segs = re.findall(r"(?:^|\n)#{1,3}\s*第\s*\d+\s*段|(?:^|\n)【第\s*\d+\s*段", text)
    is_multi = len(unit_list) >= 2 or len(segs) >= 2
    if not is_multi:
        return fails, warns

    if "逐段參考圖掛載表" not in text:
        warns.append("G7-MOUNT 多段投餵稿建議文末附《逐段參考圖掛載表》，防止外部平台漏掛角色參考圖")
    if "⏳待生成" in text:
        warns.append("G7-PENDING 掛載表內仍存在「⏳待生成」資產，正式投餵前請補齊")

    anchor_pat = re.compile(r"門|窗|桌|椅|牆|柱|台|床|沙發|櫃|廊|梯|北|南|東|西|前景|中景|背景|中央|畫左|畫右|左側|右側")
    if len(unit_list) >= 2:
        for idx, item in enumerate(unit_list, 1):
            body = item[1] if isinstance(item, tuple) else str(item)
            if idx == 1:
                if "機位側=" not in body and "固定可見錨=" not in body and "世界座標" not in body:
                    warns.append("G8-HANDOFF 段1建議在【站位聲明】末行寫明機位側=/固定可見錨=，供段2繼承")
                continue
            # 段 2 及以後：硬阻斷（僅對【場景資產】或【站位聲明】非空的真實投餵段觸發，不干擾空欄單測夾具）
            m_sc = re.search(r"【場景資產】([^【]*)", body)
            m_bl = re.search(r"【站位聲明】([^【]*)", body)
            sc_val = m_sc.group(1).strip() if m_sc else ""
            bl_val = m_bl.group(1).strip() if m_bl else ""
            spatial_val = (sc_val + " " + bl_val).strip()
            if spatial_val:
                if "機位側=" not in body and "固定可見錨=" not in body and "世界座標" not in body:
                    fails.append(f"G8-HANDOFF 段{idx}：多段稿第{idx}段缺失跨段空間交接卡（須寫明 機位側=/固定可見錨=），防段2起站位漂移")
                if not anchor_pat.search(spatial_val):
                    fails.append(f"G8-ANCHOR-REPEAT 段{idx}：第{idx}段【場景資產/站位聲明】未複述房間物理座標或固定傢俱錨點（C17i）")
                is_c_plus = ("母版" in sc_val and "站位參考" in sc_val)
                is_c_2in1 = ("二合一" in sc_val and ("站位" in sc_val or "替換" in sc_val))
                if ("白模" in sc_val or "軸測" in sc_val) and not (is_c_plus or is_c_2in1):
                    fails.append(f"G8-SCHEME-C 段{idx}：方案C+/C++【場景資產】須明確寫清分工：雙圖C+寫明 @場景母版 + 站位參考圖 @白模；二合一C++寫明 二合一參考圖 @實景等軸測站位圖")
    else:
        if "機位側=" not in text and "固定可見錨=" not in text:
            warns.append("G8-HANDOFF 多段投餵稿建議在【站位聲明】末行補齊跨段空間交接卡（機位側=/固定可見錨=）")
    return fails, warns


def run_syntax_engine(path, model, aspect, mode='auto'):
    """調用總控 validate_prompt.py，把 C 系結果併入本次報告。

    返回 (fail_count, warn_count, note)。mode: auto=檢測到就跑 / on=必須跑 / off=不跑。
    """
    if mode == 'off':
        return 0, 0, '已按 --syntax off 跳過（僅跑投餵層閘門；建議另行加跑 validate_prompt.py）'
    engine = _find_engine()
    if not engine:
        if mode == 'on':
            return 1, 0, '未找到總控機檢引擎 validate_prompt.py（--syntax on 要求必須有）——請先部署 1 總控 + 10 子技能套裝'
        return 0, 0, ('未檢測到總控機檢引擎（子技能獨立安裝），本次只跑了投餵層閘門；'
                      'C7 七段式 / C2 鏡號 / C11 接續狀態殘留 / C13 鏡長雷同 / C16b 語氣位 '
                      '需另行加跑 short-drama-director/scripts/validate_prompt.py')
    cmd = [sys.executable, engine, path, '--model', str(model)]
    if aspect:
        cmd += ['--aspect', str(aspect)]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'}
    try:
        proc = subprocess.run(cmd, capture_output=True, encoding='utf-8', env=env)
    except OSError as exc:
        return 1, 0, f'機檢引擎調用失敗（{exc}）——按 fail-closed 判 FAIL'
    out = (proc.stdout or '') + (proc.stderr or '')
    print(out.rstrip())
    if proc.returncode == 3:
        return 1, 0, '機檢引擎判定「非投餵稿件」，C 系判據未執行——按 fail-closed 判 FAIL（請核對稿件形態）'
    n_fail = sum(1 for line in out.splitlines() if line.startswith('[-] FAIL'))
    n_warn = sum(1 for line in out.splitlines() if line.startswith('[!] WARN'))
    if proc.returncode not in (0, 1):
        return max(1, n_fail), n_warn, f'機檢引擎異常退出（code={proc.returncode}）——按 fail-closed 判 FAIL'
    return n_fail, n_warn, f'機檢引擎已跑通（{os.path.basename(engine)} · model={model}）'


if __name__ == '__main__':
    main()
