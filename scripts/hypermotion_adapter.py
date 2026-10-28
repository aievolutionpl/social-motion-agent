"""Render explicit local .hype files using an installed Hyper Motion CLI/app.

Flags follow psiddharthdesign/hypermotion at e510cd60c0d2632863b5a3f78dba71b905c75ff2.
This adapter installs nothing and never renders the desktop's implicit current scene.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

from studio_core import check_job, fingerprint, local, now, probe_job, read, record_render, sha, write

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MISSING = ("Hyper Motion CLI unavailable. Install @psiddharthdesign/hypermotion and its compatible "
           "desktop app separately, or set HYPERMOTION_CLI to the installed bin/hypermotion.mjs. "
           "The source library alone is not a working render runtime.")


def command(*args: str) -> list[str]:
    selected = os.environ.get("HYPERMOTION_CLI") or shutil.which("hypermotion")
    if not selected or not Path(selected).is_file():
        raise ValueError(MISSING)
    cli = Path(selected).resolve()
    if cli.suffix.lower() in (".cmd", ".bat", ".ps1"):
        # Bypass npm's Windows shell wrapper, retaining paths as argv elements.
        candidates = (cli.parent / "node_modules/@psiddharthdesign/hypermotion/bin/hypermotion.mjs",
                      cli.parent.parent / "@psiddharthdesign/hypermotion/bin/hypermotion.mjs")
        cli = next((path for path in candidates if path.is_file()), None)
        if cli is None:
            raise ValueError(MISSING + " Cannot resolve this shell wrapper; point HYPERMOTION_CLI at its .mjs entry.")
    if cli.suffix.lower() in (".mjs", ".js", ".cjs"):
        node = shutil.which("node")
        if not node:
            raise ValueError("Node.js is required to run the installed Hyper Motion CLI.")
        return [node, str(cli), *args]
    return [str(cli), *args]


def render(folder: Path, name: str = "hypermotion", scene: str = "source/index.hype") -> dict:
    folder = folder.resolve()
    if not NAME.fullmatch(name):
        raise ValueError("Render name must contain letters, digits, underscores or hyphens (1-64 characters).")
    errors = check_job(folder, "assets")
    if errors:
        raise ValueError("\n".join(errors))
    source = local(folder, scene)
    if source.suffix.lower() != ".hype" or not source.is_relative_to((folder / "source").resolve()):
        raise ValueError("Hyper Motion requires a .hype file inside this job's source directory.")
    target = local(folder, "renders/" + name + ".mp4", exists=False)
    if target.exists():
        raise ValueError("Render already exists. Choose a new --name; originals are never overwritten.")
    prefix = command()
    log = local(folder, "notes/hypermotion-" + name + ".log", exists=False)
    lock = target.with_suffix(".lock")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ValueError("Render already running or interrupted; inspect the lock before retrying.") from None
    staging = target.with_name(name + "-" + uuid.uuid4().hex[:8] + ".partial.mp4")
    env = os.environ.copy()
    env["HYPERMOTION_RENDER_TIMEOUT_MS"] = "1800000"
    env.pop("ELECTRON_RUN_AS_NODE", None)
    try:
        with handle:
            handle.write(str(os.getpid()))
        source_fingerprint = fingerprint(folder)
        with log.open("w", encoding="utf-8") as stream:
            operations = [([*prefix, "validate", str(source), "--json"], 90),
                          ([*prefix, "render", "--scene", str(source), "-o", str(staging),
                            "--quality", "comp", "--fps", str(read(folder / "job.json")["fps"])], 1830)]
            for argv, timeout in operations:
                result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, cwd=folder,
                                        env=env, timeout=timeout, shell=False,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if result.returncode:
                    raise ValueError(f"Hyper Motion failed ({result.returncode}); inspect {log.relative_to(folder)}")
        if not staging.is_file() or staging.stat().st_size == 0:
            raise ValueError("Hyper Motion did not produce a non-empty video.")
        if target.exists():
            raise ValueError("Render appeared during export; existing output was preserved.")
        staging.rename(target)
        record_render(folder, target.relative_to(folder).as_posix(), source_fingerprint, "hypermotion")
    except subprocess.TimeoutExpired:
        raise ValueError(f"Hyper Motion timed out; inspect {log.relative_to(folder)} and the desktop app before retrying.") from None
    finally:
        staging.unlink(missing_ok=True)
        for suffix in (".done", ".error"):
            Path(str(staging) + suffix).unlink(missing_ok=True)
        lock.unlink(missing_ok=True)
    technical = probe_job(folder, target.relative_to(folder).as_posix())
    result = {"render": target.relative_to(folder).as_posix(), "render_sha256": sha(target),
              "probe_passed": technical["passed"], "probe_failures": technical["failures"],
              "reviewed": False, "log": log.relative_to(folder).as_posix(), "finished_at": now()}
    write(folder / "notes" / ("hypermotion-" + name + ".json"), result)
    return result
