# -*- coding: utf-8 -*-
"""
script_feed_diff.py · 「劇本 ↔ 投餵稿」台詞對照校驗器
用法：python script_feed_diff.py --script <劇本.md> --feed <投餵稿.md> [--names 陳建國,陳建軍,陳建民]

目的：攔截 P4 投餵層「內容級漏執行」——
      投餵稿可以壓縮動作行、合併鏡頭，但**劇本台詞不得憑空缺失**
      （尤其題眼句 / 反應鏡的因）。缺失即報 FAIL。
定位：與 gate_check.py（六道閘門）、validate_prompt.py（C1~C26＋增量主碼 C27~C30 機檢）互補，
      專治「格式全對、內容漏句」。
"""
import re, sys, io, argparse, os

if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    """歸一化：去標點/空白，只留漢字字母數字"""
    return re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', s)


def parse_script(path, names):
    """抽上游台詞：(角色, 提示, 台詞原文)。自動識別「劇本格式」與「分鏡稿格式」。"""
    with open(path, encoding='utf-8') as source:
        txt = source.read()
    out = []
    name_pat = '|'.join(names)
    # 分鏡稿格式：台詞：角色（提示）："..."  或  台詞：無（畫外音延續）：角色："..."
    if re.search(r'^台詞：', txt, re.M):
        for m in re.finditer(r'^台詞：(.+)$', txt, re.M):
            seg = m.group(1)
            # 修正：引號改貪婪 `(.*)"` —— 分鏡稿每行僅一句台詞；
            # 舊的 `[^"]+` 會被台詞內嵌引號（「先認一句"我做得夠好了"」）截斷。
            for q in re.finditer(r'(' + name_pat + r')(（[^）]*）)?：?"(.*)"', seg):
                out.append((q.group(1), (q.group(2) or '').strip('（）'), q.group(3)))
        return out
    # 劇本格式：角色（提示）：台詞
    for m in re.finditer(r'^(' + name_pat + r')(（[^）]*）)?：(.+)$', txt, re.M):
        t = m.group(3).strip()
        if not t or t.startswith('▲') or t.startswith('△'):
            continue
        out.append((m.group(1), (m.group(2) or '').strip('（）'), t))
    return out


def parse_feed(path):
    """抽投餵稿台詞：(角色, 語氣, 台詞原文)"""
    with open(path, encoding='utf-8') as source:
        txt = source.read()
    from gate_check import parse_lines
    return [(role, tone, line) for role, tone, line, _ in parse_lines(txt)]


def ngram_cov(a, b, n=4):
    """a 的 n-gram 有多大比例出現在 b 中（對「長句拆多鏡」友好，是缺失判定的主判據）"""
    a, b = norm(a), norm(b)
    if len(a) < n:
        return 1.0 if (a and a in b) else 0.0
    grams = [a[i:i + n] for i in range(len(a) - n + 1)]
    return sum(1 for g in grams if g in b) / len(grams)


def best_match(line, pool, thr=0.55):
    """在 pool 中找與 line 最相似的投餵台詞（按最長公共子串比率）"""
    a = norm(line)
    if not a:
        return None, 0.0
    best, score = None, 0.0
    for item in pool:
        b = norm(item[2])
        if not b:
            continue
        # 修正：超短台詞（≤3 字，如「嗯。」「怎麼？」）走最長公共子串會因
        # 窗口下限 j-i>=3 恆為空 → 一律判 0，誤報為「投餵獨有」。改為包含判定。
        if len(a) <= 3 or len(b) <= 3:
            s = 1.0 if (a in b or b in a) else 0.0
            if s > score:
                best, score = item, s
            continue
        # 用較長者滑動，找最長公共連續子串
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        lo, hi = 0, 0
        for i in range(len(short)):
            for j in range(i + 3, len(short) + 1):
                if short[i:j] in long_:
                    if j - i > hi - lo:
                        lo, hi = i, j
        ov = hi - lo
        s = ov / max(len(a), 1)
        if s > score:
            best, score = item, s
    return (best, score) if score >= thr else (None, score)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--script', required=True)
    ap.add_argument('--feed', required=True)
    ap.add_argument('--names', default='陳建國,陳建軍,陳建民,李秀蘭,王秀蘭')
    ap.add_argument('--thr', type=float, default=0.55)
    a = ap.parse_args()

    script = parse_script(a.script, a.names.split(','))
    feed = parse_feed(a.feed)
    with open(a.feed, encoding='utf-8') as source:
        feed_raw = source.read()

    print(f'=== 劇本↔投餵 台詞對照 ===')
    print(f'劇本：{os.path.basename(a.script)}（{len(script)} 句）')
    print(f'投餵：{os.path.basename(a.feed)}（{len(feed)} 句）\n')

    missing, weak = [], []
    feed_all = norm("".join(x[2] for x in feed))
    print('--- 上游台詞逐句核對（4-gram 覆蓋率，對拆鏡友好）---')
    for i, (role, hint, line) in enumerate(script, 1):
        if not norm(line):
            # 修正：純標點/符號台詞（如「陳建民：……」）去標點後為空，
            # 4-gram 無從判定。舊版一律判 0.0，把合法的「沉默標註」誤報為缺失；
            # 現改用原文匹配。
            s = 1.0 if line.strip() in feed_raw else 0.0
        else:
            s = ngram_cov(line, feed_all, 4)
        if s < 0.5:
            missing.append((i, role, hint, line, s)); tag = '❌ 缺失'
        elif s < 0.85:
            weak.append((i, role, line, s)); tag = f'⚠ 部分覆蓋 {s:.2f}'
        else:
            tag = f'✓ {s:.2f}'
        print(f'{i:2d}. [{tag}] {role}：{line[:46]}')

    # 投餵稿有、劇本無（新增/改寫，僅提示）
    print('\n--- 投餵稿獨有（劇本無，可能是合理改寫或噪聲）---')
    extra = 0
    for role, tone, line in feed:
        if not norm(line):
            # 純標點台詞（如「……」）：與上游按原文比對
            if any(line.strip() == x[2].strip() for x in script):
                continue
        elif any(best_match(line, [x], a.thr)[0] for x in script):
            continue
        # 反向匹配
        found = False
        for x in script:
            bm, bs = best_match(x[2], [(role, tone, line)], a.thr)
            if bm:
                found = True
                break
        if not found:
            extra += 1
            print(f'   + {role}（{tone}）：{line[:46]}')
    if extra == 0:
        print('   （無）')

    print('\n=== 彙總 ===')
    print(f'劇本 {len(script)} 句 / 投餵 {len(feed)} 句')
    print(f'❌ 缺失 {len(missing)} 句 / ⚠ 弱匹配 {len(weak)} 句 / 投餵獨有 {extra} 句')
    if missing:
        print('\n★ 缺失明細（必須補進投餵稿，否則該鏡無因/題眼丟失）：')
        for i, role, hint, line, s in missing:
            print(f'   劇本第 {i} 句 · {role}{("（" + hint + "）") if hint else ""}：{line}')
    sys.exit(2 if missing else (1 if weak else 0))


def self_test():
    """★P11 新增（2026-10-24）：本腳本此前完全游離在自測體系外。
    它對賬的是「劇本每一句台詞是否都進了投餵稿」，判錯的方向兩邊都致命——
    假報缺失會讓作者去補本來就在的台詞；漏報缺失就是台詞在鏡頭上憑空消失。
    這裡把兩條核心判據的正反例釘死。"""
    ok = True
    if norm("你好，世界！A1") != "你好世界A1":
        print("FAIL self-test: norm 未剝離標點", repr(norm("你好，世界！A1"))); ok = False
    if abs(ngram_cov("他推開門走了進去", "他推開門走了進去") - 1.0) > 1e-9:
        print("FAIL self-test: ngram_cov 自比對不為 1.0"); ok = False
    if ngram_cov("他推開門走了進去", "完全不同的一句話內容") >= 0.2:
        print("FAIL self-test: ngram_cov 對無關句給了不應有的相似度"); ok = False
    # 超短台詞（「嗯」「怎麼？」）走包含判定——舊實現因窗口下限 j-i>=3 恆為 0，
    # 每句「嗯」都被誤報成「投餵獨有」。
    if ngram_cov("嗯", "他說嗯了一聲") != 1.0:
        print("FAIL self-test: 超短台詞包含判定失效（舊 bug 復發）"); ok = False
    hit, _ = best_match("嗯。", [("林風", "", "嗯")])
    if hit is None:
        print("FAIL self-test: best_match 未匹配到超短台詞（會誤報缺失）"); ok = False
    hit2, sc2 = best_match("這句話在池子里根本不存在吧", [("林風", "", "今天天氣不錯")])
    if hit2 is not None:
        print(f"FAIL self-test: best_match 對無關句誤匹配（score={sc2:.2f}）"); ok = False
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(0 if self_test() else 1)
    main()
