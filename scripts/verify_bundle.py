"""Verify an extracted full release without Git or third-party packages."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def verify():
    manifest = ROOT / 'bundle-manifest.json'
    if not manifest.is_file():
        print('No bundle manifest. This command is for the full release ZIP.')
        return 1
    data = json.loads(manifest.read_text(encoding='utf-8'))
    errors = []
    for item in data['files']:
        path = (ROOT / item['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            errors.append(item['path'])
            continue
        if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append(item['path'])
    print(json.dumps({'files': len(data['files']), 'sources': len(data['sources']),
                      'passed': not errors, 'errors': errors}, indent=2))
    return int(bool(errors))

if __name__ == '__main__':
    sys.exit(verify())
