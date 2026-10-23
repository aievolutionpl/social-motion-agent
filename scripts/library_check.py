"""Verify every catalogue entry and media file without executing upstream code."""
import hashlib
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor
import bootstrap_library as bootstrap

ROOT = Path(__file__).resolve().parents[1]

def digest_matches(raw, expected):
    if hashlib.sha256(raw).hexdigest() == expected:
        return True
    # Git checkouts may normalize text line endings across Windows/Linux.
    lf = raw.replace(b"\r\n", b"\n")
    return any(hashlib.sha256(value).hexdigest() == expected for value in (lf, lf.replace(b"\n", b"\r\n")))

def local(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError("Missing or escaping file: " + value)
    return path

def check():
    errors = []
    entries = json.loads((ROOT / "skills/catalog.json").read_text(encoding="utf-8"))["entries"]
    media = json.loads((ROOT / "assets/media-manifest.json").read_text(encoding="utf-8"))["files"]
    sources = bootstrap.sources()
    def check_source(entry):
        try:
            state = bootstrap.inspect(entry)
            return None if state == "ready" else entry["id"] + ": " + state
        except (OSError, ValueError) as exc:
            return entry["id"] + ": " + str(exc)
    with ThreadPoolExecutor(max_workers=4) as pool:
        errors.extend(e for e in pool.map(check_source, sources) if e)
    for entry in entries:
        try:
            raw = local(entry["path"]).read_bytes()
            if entry.get("sha256") and not digest_matches(raw, entry["sha256"]):
                errors.append("Changed catalogue file: " + entry["path"])
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    for entry in media:
        try:
            raw = local(entry["path"]).read_bytes()
            if len(raw) != entry["bytes"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
                errors.append("Changed media: " + entry["path"])
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    return {"sources":len(sources), "catalogue_entries":len(entries), "media_files":len(media),
            "passed":not errors, "errors":errors}

if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(not report["passed"])
