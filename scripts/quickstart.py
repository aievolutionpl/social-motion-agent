"""Idempotent local setup and browser verification. Never installs system packages."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import environment

ROOT = Path(__file__).resolve().parents[1]


def run(*, browser=False, smoke=False):
    report = environment.inspect(ROOT)
    if not report['ready']:
        report = environment.setup(ROOT)
    if not report['ready']:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    node = report['runtime_checks']['node']['path']
    commands = []
    if browser or smoke:
        commands.append([node, str(ROOT / 'node_modules/playwright/cli.js'), 'install', 'chromium'])
    if smoke:
        commands.append([sys.executable, '-S', str(ROOT / 'studio.py'), 'demo', '--format', '16:9', '--render'])
    for command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=900)
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"Setup step failed: {type(exc).__name__}. Fix the local runtime and retry.")
            return 1
        if result.returncode:
            return result.returncode
    print('Local dependencies ready. Provider accounts and optional engines are not installed.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--smoke', action='store_true', help='Also render the bundled demo')
    args = parser.parse_args()
    sys.exit(run(browser=args.browser, smoke=args.smoke))
