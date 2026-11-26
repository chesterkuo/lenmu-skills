"""校驗器穩定性迴歸；僅用標準庫，臨時樣本不寫入項目。"""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
DIRECTOR = ROOT / 'short-drama-director/scripts'
FEED = ROOT / 'sd-feed-engine/scripts'
sys.path[:0] = [str(DIRECTOR), str(FEED)]
import validate_prompt as validator
import audit_contract as audit
import gate_check as gate
import script_feed_diff as diff


class StabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'sample.md'

    def unit(self, start=1, dialogue='', tail=''):
        return ('## 【投餵單元】\n```text\n【畫幅風格】\n【場景資產】\n'
                '【核心人物】\n【站位聲明】\n【時間軸分鏡】\n'
                f'00:00-00:02 [鏡頭{start}] 台詞：{dialogue} {tail}\n```\n')

    def cli(self, module, args):
        output = io.StringIO()
        with patch.object(sys, 'argv', [module.__file__, *args]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                module.main()
        return result.exception.code, output.getvalue()

    def test_dialogue_blocks(self):
        text = '台詞：【甲(正常)："先說一句\"你好\""】【乙（急促）：“再說一句”】【丙："缺語氣"】'
        self.path.write_text(text, encoding='utf-8')
        lines = gate.parse_lines(text)
        self.assertEqual([x[0] for x in lines], ['甲', '乙', '丙'])
        self.assertEqual(lines[0][2], '先說一句"你好"')
        self.assertEqual(diff.parse_feed(self.path), [x[:3] for x in lines])
        self.assertEqual(gate.parse_lines('【畫幅風格】台詞：無'), [])

    def test_budget_and_freeze(self):
        for dialogue, tail, overload in [
            ('【甲(正常)："一二三四五六七八九十"】', '', False),
            ('【甲(正常)："一二三四五六七八九十"】', '末1秒定格', True),
            ('【甲(正常)："一二三四五六七八九十"】', '不做末1秒定格', False),
            ('【甲(正常)："一二三四五六七八九"】【乙(正常)："一二三四五六七八九"】', '', True),
        ]:
            with self.subTest(tail=tail, dialogue=dialogue):
                self.path.write_text('素材形態：M0\n' + self.unit(dialogue=dialogue, tail=tail), encoding='utf-8')
                _, out = self.cli(gate, [str(self.path), '--tol', '0', '--syntax', 'off'])
                self.assertEqual('真念不完' in out, overload)

    def test_global_ids(self):
        # P14：閘門0 的「七段缺欄 / 接續狀態殘留」已移交 C 系，本層只留【】配對與鏡號連續；
        #   用例走 --syntax off，專測本層鏡號判據（否則夾具缺【音效】欄會被 C7 判 FAIL，測不到鏡號）。
        for first, second, valid in [(7, 8, True), (1, 1, True), (7, 9, False), (7, 7, False)]:
            self.path.write_text('素材形態：M0\n' + self.unit(first) + self.unit(second), encoding='utf-8')
            code, out = self.cli(gate, [str(self.path), '--syntax', 'off'])
            self.assertEqual(code == 0, valid, out)

    def test_scopes(self):
        # ★P2 口徑：feed-only 不再無條件豁免 CT2——只交投餵稿必須在稿內聲明「資產另冊」，
        #   否則按「資產缺失」FAIL。故夾具須帶上該聲明（2026-10-23 體檢修：本用例曾因此長期紅燈）。
        feed = 'M0\n資產另冊：三天_資產提示詞.md\n【時間軸分鏡】【站位聲明】'
        self.assertFalse(audit.audit_markdown(feed, delivery='feed-only')[0])
        self.assertTrue(audit.audit_markdown(feed, delivery='full-project')[0])
        self.assertTrue(audit.audit_markdown(feed, delivery='agent-bundle')[0])
        assets = ('全圖共4格 無臉全身 五官10項 Voice Description\n'
                  '場景母版 九宮格攝影機矩陣 標註降級條款\n'
                  '道具設定圖 正面視圖 45°側視圖 俯視圖 禁止手持\n')
        self.assertFalse(audit.audit_markdown(feed + assets, delivery='agent-bundle')[0])
        self.assertTrue(audit.audit_markdown('M0', delivery='feed-only')[0])
        with self.assertRaises(ValueError):
            audit.audit_markdown(feed, delivery='typo')

    def test_render_parity(self):
        # 同 test_scopes：feed-only 需聲明資產另冊（P2 口徑），否則 CT2 FAIL 導致期望值失效
        self.path.write_text('M0\n資產另冊：三天_資產提示詞.md\n【時間軸分鏡】【站位聲明】', encoding='utf-8')
        cases = [([], [], 0), (['--contract'], [], 1),
                 (['--delivery', 'feed-only'], [], 0),
                 (['--delivery', 'full-project'], [], 1),
                 ([], ['C20c 測試高危'], 1),
                 (['--allow-warn'], ['C20c 測試高危'], 0)]
        for args, warnings, expected in cases:
            with self.subTest(args=args, warnings=warnings):
                def fake(*a, **kw):
                    return [], list(warnings), {'duration_s': 2, 'shots': 1, 'chars': 10}
                with patch.object(validator, '_looks_like_feed', return_value=True), patch.object(validator, 'validate', side_effect=fake):
                    code, text = self.cli(validator, [*args, str(self.path)])
                    jcode, raw = self.cli(validator, [*args, str(self.path), '--json'])
                data = json.loads(raw)
                self.assertEqual((code, jcode), (expected, expected))
                self.assertEqual(bool(data['issues']), bool(expected))
                for issue in data['issues']:
                    self.assertIn(issue, text)
                for warn in data['warnings']:
                    self.assertIn(warn, text)

    def test_contract_fail_closed(self):
        self.path.write_text('【時間軸分鏡】', encoding='utf-8')
        for fault in ('missing', 'exception'):
            for json_flag in ([], ['--json']):
                with self.subTest(fault=fault, json_flag=json_flag):
                    failure = (patch.dict(sys.modules, {'audit_contract': None}) if fault == 'missing'
                               else patch.object(audit, 'audit_markdown', side_effect=RuntimeError('故障注入')))
                    with failure, patch.object(validator, '_looks_like_feed', return_value=True), patch.object(
                        validator, 'validate', side_effect=lambda *a, **kw: ([], [], {'duration_s': 0, 'shots': 0, 'chars': 0})):
                        code, out = self.cli(validator, [str(self.path), '--contract', '--allow-warn', *json_flag])
                    self.assertEqual(code, 1)
                    self.assertIn('fail closed', out)
                    if json_flag:
                        self.assertTrue(json.loads(out)['issues'])

    def test_diff_cli(self):
        script = self.path.with_name('script.md')
        script.write_text('甲：你好\n乙：再見\n', encoding='utf-8')
        for text, expected in [('【甲(正常)："你好"】【乙(正常)："再見"】', 0),
                               ('【甲(正常)："你好"】', 2)]:
            self.path.write_text(text, encoding='utf-8')
            code, _ = self.cli(diff, ['--script', str(script), '--feed', str(self.path), '--names', '甲,乙'])
            self.assertEqual(code, expected)

    def test_real_cli_parity(self):
        self.path.write_text('素材形態：M0\n' + self.unit(dialogue='【甲(正常)："你好"】'), encoding='utf-8')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
        command = [sys.executable, str(DIRECTOR / 'validate_prompt.py'), str(self.path), '--contract']
        text = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', env=env)
        machine = subprocess.run(command + ['--json'], capture_output=True, text=True, encoding='utf-8', env=env)
        self.assertEqual(text.returncode, machine.returncode)
        self.assertEqual(machine.returncode, 1)
        data = json.loads(machine.stdout)
        self.assertTrue(any(x.startswith('C31') for x in data['issues']))
        for issue in data['issues']:
            self.assertIn(issue, text.stdout)
        for warning in data['warnings']:
            self.assertIn(warning, text.stdout)

    def test_existing_self_tests(self):
        for folder, name in [(DIRECTOR, 'validate_prompt.py'), (DIRECTOR, 'audit_contract.py'), (FEED, 'gate_check.py')]:
            with self.subTest(name=name):
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
                run = subprocess.run([sys.executable, str(folder / name), '--self-test'],
                                     capture_output=True, text=True, encoding='utf-8', env=env)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
