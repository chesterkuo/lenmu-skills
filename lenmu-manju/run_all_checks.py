#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""漫劇老李 AIGC 全流程 Skill (V8.2.0-SLIM) 根目錄統一自檢入口

用法:
    python run_all_checks.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CHECKS = [
    ("包級完整性校驗 (check_package.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/check_package.py")]),
    ("鎖憑證機檢自檢 (check_locks.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/check_locks.py"), "--self-test"]),
    ("交付契約核銷自檢 (audit_contract.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/audit_contract.py"), "--self-test"]),
    ("投餵層閘門自檢 (gate_check.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/gate_check.py"), "--self-test"]),
    ("劇本滾動狀態包自檢 (rolling_checkpoint.py)", [sys.executable, os.path.join(ROOT, "sd-script-engine/scripts/rolling_checkpoint.py"), "--self-test"]),
    ("劇本可拍性機檢 (validate_episode.py)", [sys.executable, os.path.join(ROOT, "sd-script-engine/scripts/validate_episode.py"), "--self-test"]),
    ("投餵包 JSON/CSV 導出自檢 (export_feed_bundle.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/export_feed_bundle.py"), "--self-test"]),
    ("提示詞一鍵防字幕清洗自檢 (autofix_feed.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/autofix_feed.py"), "--self-test"]),
    ("離線看板編譯與另冊掛載自檢 (build_board_lite.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/build_board_lite.py"), "--self-test"]),
    ("統一階段門禁入口自檢 (run_stage.py)", [sys.executable, os.path.join(ROOT, "run_stage.py"), "--self-test"]),
    ("Lenmu 接線器自檢 (lenmu_wiring.py · fork 增補)", [sys.executable, os.path.join(ROOT, "sd-lenmu-engine/scripts/lenmu_wiring.py"), "--self-test"]),
]


def main():
    failed = []
    for label, cmd in CHECKS:
        print(f"\n=== {label} ===")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            sys.stdout.write(res.stdout[-1500:] if res.stdout else "")
            if res.stderr:
                sys.stderr.write(res.stderr[-1000:])
            failed.append(label)
            print(f"[-] FAILED: {label}")
        else:
            lines = [l for l in res.stdout.splitlines() if l.strip()]
            for l in lines[-3:]:
                print(l)
            print(f"[+] PASSED: {label}")
    if failed:
        print(f"\n[-] 未全部通過 ({len(failed)} 項): {failed}")
        return 1
    print(f"\n[+] 全部 {len(CHECKS)} 項全流程總檢 PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
