"""Pinned local HyperFrames adapter. No cloud render, publishing or paid API calls."""
from __future__ import annotations
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from studio_core import ROOT, check_job, fingerprint, local, now, probe_job, read, record_render, sha, write

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

def cli_path() -> Path:
    return ROOT / "node_modules/hyperframes/bin/hyperframes.mjs"

def command(action: str, source: Path, *args: str) -> list[str]:
    node = shutil.which("node")
    if not node or not cli_path().is_file():
        raise ValueError("HyperFrames unavailable. Install Node 22+ and run npm ci in the repository.")
    return [node, str(cli_path()), action, str(source), *args]

def render(folder: Path, name: str = "hyperframes", quality: str = "standard") -> dict:
    if not NAME.fullmatch(name):
        raise ValueError("Render name must contain letters, digits, underscores or hyphens (1-64 characters).")
    if quality not in ("draft", "standard", "high"):
        raise ValueError("Invalid render quality.")
    errors = check_job(folder, "assets")
    if errors:
        raise ValueError("\n".join(errors))
    source = local(folder, "source/index.html").parent
    target = folder / "renders" / (name + ".mp4")
    if target.exists():
        raise ValueError("Render already exists. Choose a new --name; originals are never overwritten.")
    # Reserve the name before launching a renderer, including across processes.
    lock = target.with_suffix(".lock")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ValueError("Render already running or interrupted; inspect the lock before retrying.") from None
    staging = target.with_name(name + "-" + uuid.uuid4().hex[:8] + ".partial.mp4")
    log = folder / "notes" / ("hyperframes-" + name + ".log")
    env = os.environ.copy()
    env["DO_NOT_TRACK"] = "1"
    source_fingerprint = fingerprint(folder)
    try:
        with handle:
            handle.write(str(os.getpid()))
        with log.open("w", encoding="utf-8") as stream:
            for argv in (
                command("lint", source),
                command("render", source, "--output", str(staging), "--fps", str(read(folder / "job.json")["fps"]),
                        "--quality", quality, "--workers", "1", "--no-browser-gpu"),
            ):
                result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT,
                                        cwd=ROOT, env=env, timeout=1800)
                if result.returncode:
                    raise ValueError(f"HyperFrames failed ({result.returncode}); inspect {log.relative_to(folder)}")
        if not staging.is_file() or staging.stat().st_size == 0:
            raise ValueError("HyperFrames did not produce a non-empty video.")
        staging.rename(target)
        record_render(folder, target.relative_to(folder).as_posix(), source_fingerprint, "hyperframes")
    finally:
        staging.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)
    technical = probe_job(folder, target.relative_to(folder).as_posix())
    result = {"render": target.relative_to(folder).as_posix(), "render_sha256": sha(target),
              "probe_passed": technical["passed"], "probe_failures": technical["failures"],
              "reviewed": False, "log": log.relative_to(folder).as_posix(), "finished_at": now()}
    write(folder / "notes" / ("hyperframes-" + name + ".json"), result)
    return result
