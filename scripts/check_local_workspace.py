"""Verify the optional local preservation ledger without modifying any files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PureWindowsPath


def local(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError('Empty local path')
    windows = PureWindowsPath(value)
    if windows.drive or windows.root or '..' in windows.parts:
        raise ValueError('Path must stay inside this project')
    path = (root / value.replace('\\', '/')).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError('Path leaves this project')
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def check(root: Path, manifest: dict) -> dict:
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or manifest.get('role') != 'canonical-local-workspace':
        raise ValueError('Unsupported local workspace ledger')
    records, jobs = manifest.get('preserved_files'), manifest.get('required_jobs')
    if not isinstance(records, list) or not isinstance(jobs, list):
        raise ValueError('Missing preservation records or required production list')
    errors, verified, cache = [], 0, {}
    for record in records:
        if not isinstance(record, dict):
            errors.append('Invalid preservation record')
            continue
        value = record.get('path')
        try:
            path = local(root, value)
            if not path.is_file():
                raise ValueError('Preserved file is missing')
            if path not in cache:
                cache[path] = sha256(path)
            if cache[path] != record.get('sha256'):
                raise ValueError('Preserved file differs from its recorded SHA-256')
            verified += 1
        except (OSError, ValueError) as error:
            errors.append(f'{value}: {error}')
    checked_jobs = 0
    for identifier in jobs:
        try:
            if not isinstance(identifier, str) or len(PureWindowsPath(identifier).parts) != 1 or identifier in {'.', '..'}:
                raise ValueError('Invalid production identifier')
            folder = local(root, f'output/jobs/{identifier}')
            card = json.loads((folder / 'job.json').read_text(encoding='utf-8-sig'))
            if not isinstance(card, dict) or card.get('id') != identifier:
                raise ValueError('Production identity mismatch')
            if card.get('render'):
                render = local(folder, card['render'])
                if not render.is_file():
                    raise ValueError('Render referenced by this production is missing')
            checked_jobs += 1
        except (OSError, ValueError, TypeError) as error:
            errors.append(f'output/jobs/{identifier}: {error}')
    return {'passed': not errors, 'preserved_records_verified': verified,
            'required_jobs_verified': checked_jobs, 'errors': errors}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ledger = root / 'output/workspace-state/local-workspace.json'
    if not ledger.is_file():
        print(json.dumps({'passed': False, 'error': 'No local preservation ledger in this checkout.'}))
        return 1
    try:
        result = check(root, json.loads(ledger.read_text(encoding='utf-8')))
    except (OSError, ValueError) as error:
        result = {'passed': False, 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
