"""Scan only public source files (or the Git index), without printing secret values."""
from pathlib import Path
import re
import os
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
        result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True)
        paths = [ROOT / p.decode("utf-8") for p in result.stdout.split(b"\0") if p]
        mode = "git-index"
    else:
        paths = []
        for directory, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP]
            paths.extend(Path(directory) / name for name in files if name != "gsap.min.js")
        mode = "source-tree"
    failures = []
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
