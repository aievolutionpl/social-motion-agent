"""Scan only public source files (or the Git index), without printing secret values."""
from pathlib import Path
import re
import os
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"node_modules", ".git", "output", "__pycache__", ".venv", ".serena", ".ruff_cache"}
FORBIDDEN = {"output", "node_modules", ".env", "credentials", ".council", ".serena", ".atlas"}
PATTERNS = [
    ("personal home path", re.compile(r"(?i)(?:[A-Z]:[\\/]+Users[\\/]+[^/\\\s]+|/" + r"Users/[^/\s]+|/" + r"home/[^/\s]+)")),
    ("access token", re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,})")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

def inspect(path, raw):
    problems = []
    rel = path.relative_to(ROOT)
    if any(part in FORBIDDEN for part in rel.parts) or (path.name.startswith(".env") and path.name != ".env.example"):
        problems.append("forbidden file")
    if raw[:4] in (b"\x89PNG", b"GIF8") or path.suffix in (".jpg", ".webp"):
        return problems
    if path.suffix.lower() in {".wav", ".mp3", ".ttf", ".mp4"}:
        manifest = json.loads((ROOT / "assets/media-manifest.json").read_text(encoding="utf-8"))
        entry = next((p for p in manifest["files"] if p["path"] == rel.as_posix()), None)
        if not entry or entry["sha256"] != hashlib.sha256(raw).hexdigest():
            problems.append("media missing or different from integrity manifest")
        return problems
    if len(raw) > 2_000_000:
        problems.append("unexpected large non-image file")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return problems + ["unexpected binary"]
    for label, pattern in PATTERNS:
        if pattern.search(text):
            problems.append(label)
    return problems

def main():
    indexed = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    own_repo = indexed.returncode == 0 and Path(indexed.stdout.strip()).resolve() == ROOT.resolve()
    if own_repo:
        result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--stage", "-z"], capture_output=True, check=True)
        paths = []
        linked = []
        for record in result.stdout.split(b"\0"):
            if not record:
                continue
            metadata, name = record.decode("utf-8").split("\t", 1)
            mode_bits, commit, _stage = metadata.split()
            if mode_bits == "160000":
                linked.append((name, commit))
            else:
                paths.append(ROOT / name)
        mode = "git-index"
    else:
        paths = []
        for directory, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP]
            if Path(directory) == ROOT / "tools":
                dirs[:] = [d for d in dirs if d != "repos"]
            paths.extend(Path(directory) / name for name in files if name != "gsap.min.js")
        linked = []
        mode = "source-tree"
    failures = []
    if linked:
        lock_data = subprocess.run(["git", "-C", str(ROOT), "show", ":sources.lock.json"],
                                   capture_output=True, check=True).stdout
        expected = {s["path"]: s["commit"] for s in json.loads(lock_data)["sources"]}
        for name, commit in linked:
            if expected.get(name) != commit:
                failures.append((name, ["submodule differs from pinned source manifest"]))
    for path in paths:
        if path.is_symlink():
            failures.append((path.relative_to(ROOT), ["symlinks are not publishable"]))
            continue
        # Inspect the staged bytes, not a potentially cleaner working copy.
        raw = subprocess.run(["git", "-C", str(ROOT), "show", ":" + path.relative_to(ROOT).as_posix()],
                             capture_output=True, check=True).stdout if own_repo else path.read_bytes()
        findings = inspect(path, raw)
        if findings:
            failures.append((path.relative_to(ROOT), findings))
    for path, findings in failures:
        print(f"{path}: {', '.join(findings)}")
    print(f"Release scan: {len(paths)} files, {len(failures)} findings ({mode}).")
    return bool(failures)

if __name__ == "__main__":
    sys.exit(main())
