"""Plan and prepare a small, pinned skill selection. Never run upstream code."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath

import studio_core as core

MODES = ("video", "website", "ui-motion")


def check_bundle(root: Path, report: dict) -> tuple[int, list[str]]:
    """Verify selected exported sources using the full ZIP's integrity manifest.

    Like verify_bundle.py, this checks byte sizes and SHA-256 without Git.
    Limit the work to the selected source trees and this local skill package.
    A mismatched bundle is never repaired by fetching over its existing files.
    """
    errors = []
    checked = 0
    try:
        data = core.read(core.local(root, "bundle-manifest.json"))
        if data.get("schema_version") != 1:
            raise ValueError("Unsupported full-bundle manifest schema")
        locked = {entry["id"]: entry for entry in core.read(root / "sources.lock.json")["sources"]}
        bundled = {}
        for entry in data["sources"]:
            if entry["id"] in bundled:
                raise ValueError("Duplicate source in bundle manifest: " + entry["id"])
            bundled[entry["id"]] = entry
        prefixes = [PurePosixPath(report["entrypoint"]).parent.as_posix() + "/"]
        for source in report["sources"]:
            expected = locked[source["id"]]
            prefix = "tools/repos/" + source["id"]
            if expected["path"] != prefix:
                raise ValueError("Invalid selected source path: " + source["id"])
            archived = bundled.get(source["id"], {})
            if any(archived.get(key) != expected[key] for key in ("id", "url", "commit", "path", "license")):
                errors.append("Bundle source does not match sources.lock.json: " + source["id"])
            prefixes.append(prefix + "/")
        required = {item["path"] for item in report["read_on_demand"]}
        required.update(("sources.lock.json", "config/creative-skills.json"))
        listed = set()
        for item in data["files"]:
            name = item["path"]
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or path.as_posix() != name:
                raise ValueError("Unsafe bundle manifest path: " + name)
            if name in listed:
                raise ValueError("Duplicate file in bundle manifest: " + name)
            listed.add(name)
            if name not in required and not any(name.startswith(prefix) for prefix in prefixes):
                continue
            checked += 1
            try:
                file = core.local(root, name)
                if file.stat().st_size != item["bytes"] or core.sha(file) != item["sha256"]:
                    errors.append("Bundle file changed: " + name)
            except (OSError, ValueError) as exc:
                errors.append("Bundle file unavailable: " + name + ": " + str(exc))
        errors.extend("Required file missing from bundle manifest: " + name for name in sorted(required - listed))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append("Invalid full-bundle manifest: " + str(exc))
    return checked, errors


def plan(mode: str, root: Path = core.ROOT) -> dict:
    config = core.read(root / "config/creative-skills.json")
    if mode not in config["modes"]:
        raise ValueError("Unknown creative mode: " + mode)
    selected = config["modes"][mode]
    locked = {entry["id"]: entry for entry in core.read(root / "sources.lock.json")["sources"]}
    sources = [{key: locked[name][key] for key in ("id", "url", "commit", "license")}
               for name in selected["sources"]]
    paths = [config["entrypoint"], *selected["upstream"]]
    files = [{"path": path, "exists": core.local(root, path, exists=False).is_file()}
             for path in paths]
    return {"mode": mode, "purpose": selected["purpose"], "entrypoint": config["entrypoint"],
            "sources": sources, "read_on_demand": files, "runtime": selected["runtime"],
            "precedence": config["precedence"], "files_present": all(p["exists"] for p in files),
            "setup_command": f"python -S studio.py skills setup --mode {mode}",
            "source_setup_only": True, "runtime_verified": False}


def prepare(mode: str, *, check: bool = False, root: Path = core.ROOT) -> dict:
    report = plan(mode, root)
    manifest = root / "bundle-manifest.json"
    if manifest.exists() or manifest.is_symlink():
        checked, errors = check_bundle(root, report)
        report.update(action="check" if check else "setup", source_distribution="full-bundle",
                      exit_code=int(bool(errors)), passed=not errors and report["files_present"],
                      details=f"Checked {checked} selected bundle files against the integrity manifest; no Git, downloads or runtime execution.",
                      error="\n".join(errors) or None, bundle_files_checked=checked)
        return report
    command = [sys.executable, "-S", str(root / "scripts/bootstrap_library.py")]
    for source in report["sources"]:
        command += ["--only", source["id"]]
    if check:
        command.append("--check")
    # The existing installer preserves modified checkouts and fetches exact SHAs.
    result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=1200)
    report = plan(mode, root)
    report.update(action="check" if check else "setup", exit_code=result.returncode,
                  passed=result.returncode == 0 and report["files_present"],
                  details=result.stdout.strip(), error=result.stderr.strip() or None)
    return report
