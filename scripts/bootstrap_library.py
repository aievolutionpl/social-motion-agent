"""Install the complete pinned upstream source library, without running upstream code."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]

def sources():
    entries = json.loads((ROOT / "sources.lock.json").read_text(encoding="utf-8"))["sources"]
    seen = set()
    for entry in entries:
        name = entry["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) or name in seen:
            raise ValueError("Invalid or duplicate library ID")
        seen.add(name)
        if entry["path"] != "tools/repos/" + name:
            raise ValueError("Invalid library path")
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git", entry["url"]):
            raise ValueError("Only canonical HTTPS GitHub repository URLs are accepted")
        if not re.fullmatch(r"[a-f0-9]{40}", entry["commit"]):
            raise ValueError("A full pinned commit SHA is required")
    return entries

def run(*args, cwd=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    result = subprocess.run(["git", "-c", "core.longpaths=true", *args], cwd=cwd, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=300)
    if result.returncode:
        raise ValueError(result.stderr[-1200:].strip() or "Git failed")
    return result.stdout.strip()

def inspect(entry):
    target = ROOT / entry["path"]
    if not target.exists() or not any(target.iterdir()):
        return "missing"
    if not target.is_dir() or not target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Library target escapes repository")
    top = Path(run("rev-parse", "--show-toplevel", cwd=target)).resolve()
    if top != target.resolve():
        raise ValueError("Existing path is not an independent Git checkout")
    head = run("rev-parse", "HEAD", cwd=target)
    if head != entry["commit"]:
        raise ValueError("Existing checkout has a different commit; preserve it and inspect manually")
    if run("status", "--porcelain", "--untracked-files=no", cwd=target):
        raise ValueError("Existing checkout has tracked modifications; preserve them")
    return "ready"

def install(entry, check=False):
    state = inspect(entry)
    if state == "ready" or check:
        return {"id":entry["id"], "state":state, "commit":entry["commit"]}
    target = ROOT / entry["path"]
    staging = ROOT / "output/library-setup" / (entry["id"] + "-" + uuid.uuid4().hex[:8])
    staging.mkdir(parents=True)
    # Fetch the recorded revision itself, never silently upgrade to default HEAD.
    run("init", str(staging))
    # Repository-local setting keeps later Git inspections usable on Windows too.
    # It does not alter the user's global Git configuration.
    run("config", "core.longpaths", "true", cwd=staging)
    run("remote", "add", "origin", entry["url"], cwd=staging)
    run("fetch", "--depth", "1", "origin", entry["commit"], cwd=staging)
    run("checkout", "--detach", entry["commit"], cwd=staging)
    if run("rev-parse", "HEAD", cwd=staging) != entry["commit"]:
        raise ValueError("Downloaded commit mismatch")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.parent.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Library parent escapes repository")
    if target.exists():
        # Remove only an empty Git-created placeholder, never existing content.
        if not target.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Unsafe target")
        target.rmdir()
    staging.rename(target)
    return {"id":entry["id"], "state":"ready", "commit":entry["commit"]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Offline integrity check; do not download")
    parser.add_argument("--only", action="append", help="Install/check only the named source; repeatable")
    parser.add_argument("--jobs", type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    entries = sources()
    if args.only:
        unknown = set(args.only) - {e["id"] for e in entries}
        if unknown:
            parser.error("Unknown source ID: " + ", ".join(sorted(unknown)))
        entries = [e for e in entries if e["id"] in args.only]
    lock = ROOT / "output/library-setup.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lock.open("x", encoding="utf-8") as stream:
            stream.write(str(os.getpid()))
    except FileExistsError:
        parser.error("Library setup is running or was interrupted. Inspect output/library-setup.lock before retrying.")
    results = []
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            pending = {pool.submit(install, e, args.check): e["id"] for e in entries}
            for future in as_completed(pending):
                try:
                    result = future.result()
                except (OSError, ValueError, subprocess.SubprocessError) as exc:
                    result = {"id":pending[future], "state":"error", "error":str(exc)}
                results.append(result)
                print(json.dumps(result, ensure_ascii=False), flush=True)
        report = {"sources":len(results), "ready":sum(r["state"] == "ready" for r in results), "results":results}
        (ROOT / "output/library-status.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"sources":report["sources"], "ready":report["ready"]}))
        return int(report["ready"] != report["sources"])
    finally:
        lock.unlink(missing_ok=True)

if __name__ == "__main__":
    raise SystemExit(main())
