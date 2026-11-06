"""Install a portable local skill, preserving existing installations."""
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
SKILLS = (NAME, "kinetic-walk-talk")


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


def install(destination: Path, *, execute: bool = False, source: Path | None = None, name: str = NAME) -> dict:
    if name not in SKILLS:
        raise ValueError("Unknown portable skill")
    source = source or ROOT / "skills" / name
    files = inventory(source)
    if "SKILL.md" not in files:
        raise ValueError("Missing skill entrypoint")
    destination = destination.expanduser().resolve()
    target = destination / name
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError("Refusing to install through a skill link")
    result = {"skill": name, "destination": str(target), "files": len(files),
              "executed": False, "network_calls": 0}
    if target.exists():
        if target.is_dir() and inventory(target) == files:
            return dict(result, status="already-current")
        raise ValueError("Existing skill differs; preserve it. Review changes or choose --dest for a separate installation.")
    if not execute:
        return dict(result, status="planned")
    destination.mkdir(parents=True, exist_ok=True)
    # Stage a complete package before exposing it to the agent's skill index.
    with tempfile.TemporaryDirectory(prefix="." + name + "-", dir=destination) as temp:
        staged = Path(temp) / name
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
    parser.add_argument("--skill", choices=SKILLS, default=NAME)
    parser.add_argument("--dest", type=Path, help="Explicit skill parent directory; overrides the agent profile")
    parser.add_argument("--execute", action="store_true", help="Copy files; default only reports the plan")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.dest or default_destination(args.agent), execute=args.execute, name=args.skill), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
