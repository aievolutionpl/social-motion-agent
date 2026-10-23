"""Build a full ZIP from committed Git trees, never from untracked local files."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def build(destination):
    if destination.exists():
        raise ValueError('Refusing to overwrite existing archive')
    sources = json.loads(git(ROOT, 'show', 'HEAD:sources.lock.json'))['sources']
    commit = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    files = []
    seen = set()
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for repo, revision, prefix in [(ROOT, commit, '')] + [(ROOT / s['path'], s['commit'], s['path'] + '/') for s in sources]:
            with tempfile.TemporaryDirectory() as temp:
                archive = Path(temp) / 'tree.zip'
                subprocess.run(['git', '-C', str(repo), 'archive', '--format=zip', '--output', str(archive), revision], check=True)
                with zipfile.ZipFile(archive) as tree:
                    for info in tree.infolist():
                        if info.is_dir():
                            continue
                        name = prefix + info.filename
                        parts = PurePosixPath(name).parts
                        if name == '.gitmodules':
                            continue
                        if '..' in parts or '.git' in parts or PurePosixPath(name).is_absolute() or name in seen:
                            raise ValueError('Unsafe or duplicate archive path: ' + name)
                        seen.add(name)
                        raw = tree.read(info)
                        output.writestr('social-motion-agent/' + name, raw)
                        files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        # Upstream export-ignore attributes must not remove workshop materials.
        for source in sources:
            repo = ROOT / source['path']
            names = git(repo, 'ls-tree', '-r', '--name-only', '-z', source['commit']).decode().split('\0')
            for relative in filter(None, names):
                name = source['path'] + '/' + relative
                if name in seen:
                    continue
                if '..' in PurePosixPath(name).parts or '.git' in PurePosixPath(name).parts:
                    raise ValueError('Unsafe source path: ' + name)
                raw = git(repo, 'show', source['commit'] + ':' + relative)
                output.writestr('social-motion-agent/' + name, raw)
                seen.add(name)
                files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        manifest = {'schema_version': 1, 'commit': commit, 'sources': sources, 'files': files}
        output.writestr('social-motion-agent/bundle-manifest.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(destination) as bundle:
        assert bundle.testzip() is None, 'CRC verification failed'
        media = json.loads(bundle.read('social-motion-agent/assets/media-manifest.json'))['files']
        catalogue = json.loads(bundle.read('social-motion-agent/skills/catalog.json'))['entries']
        for entry in media + catalogue:
            raw = bundle.read('social-motion-agent/' + entry['path'])
            if entry.get('sha256'):
                lf = raw.replace(b'\r\n', b'\n')
                assert entry['sha256'] in [hashlib.sha256(v).hexdigest() for v in (raw, lf, lf.replace(b'\n', b'\r\n'))], entry['path']
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.zip.sha256').write_text(digest + '  ' + destination.name + '\n', encoding='utf-8')
    print(json.dumps({'zip': str(destination), 'files': len(files), 'sources': len(sources), 'media': len(media), 'catalogue': len(catalogue), 'bytes': destination.stat().st_size, 'sha256': digest}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    build(parser.parse_args().destination.resolve())
