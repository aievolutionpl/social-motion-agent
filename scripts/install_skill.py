"""Install the self-contained Creative Director skill, preserving existing skills."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "creative-director"


def default_destination(agent: str) -> Path:
    homes = {"codex": ("CODEX_HOME", ".codex"),
             "claude": ("CLAUDE_CONFIG_DIR", ".claude"),
             "hermes": ("HERMES_HOME", ".hermes")}
    variable, fallback = homes[agent]
    return Path(os.environ.get(variable) or Path.home() / fallback).expanduser() / "skills"


def inventory(folder: Path) -> dict[str, str]:
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("Skill packages cannot contain links: " + str(path))
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(destination: Path, *, execute: bool = False, source: Path | None = None) -> dict:
    source = source or ROOT / "skills" / NAME
    files = inventory(source)
    if "SKILL.md" not in files:
        raise ValueError("Missing skill entrypoint")
    destination = destination.expanduser().resolve()
    target = destination / NAME
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError("Refusing to install through a skill link")
    result = {"skill": NAME, "destination": str(target), "files": len(files),
              "executed": False, "network_calls": 0}
    if target.exists():
        if target.is_dir() and inventory(target) == files:
            return dict(result, status="already-current")
        raise ValueError("Existing skill differs; preserve it. Review changes or choose --dest for a separate installation.")
    if not execute:
        return dict(result, status="planned")
    destination.mkdir(parents=True, exist_ok=True)
    # Stage a complete package before exposing it to the agent's skill index.
    with tempfile.TemporaryDirectory(prefix=".creative-director-", dir=destination) as temp:
        staged = Path(temp) / NAME
        shutil.copytree(source, staged)
        if inventory(staged) != files:
            raise ValueError("Installed files differ from the source package")
        if target.exists():
            raise ValueError("Destination appeared during installation; preserving it")
        staged.rename(target)
    return dict(result, status="installed", executed=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "claude", "hermes"), default="codex")
    parser.add_argument("--dest", type=Path, help="Explicit skill parent directory; overrides the agent profile")
    parser.add_argument("--execute", action="store_true", help="Copy files; default only reports the plan")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.dest or default_destination(args.agent), execute=args.execute), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
