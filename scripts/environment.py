"""Offline environment checks and explicit, project-local first-run setup."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import studio_core as core


def npm_command(npm: str, node: str) -> list[str]:
    # Windows npm.cmd is a shell wrapper. Prefer its JS entry point so paths
    # containing spaces work without shell quoting or a shell=True command.
    cli = Path(npm).parent / "node_modules/npm/bin/npm-cli.js"
    if Path(npm).suffix.lower() in (".cmd", ".bat") and cli.is_file():
        return [node, str(cli)]
    return [npm]


def probe(command: list[str]) -> dict:
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=15)
        lines = (result.stdout or result.stderr or "").strip().splitlines()
        return {"ok": result.returncode == 0 and bool(lines),
                "version": lines[0] if lines else None}
    except (OSError, subprocess.SubprocessError):
        return {"ok": False, "version": None}


def inspect(root: Path = core.ROOT) -> dict:
    """Check local executables and bundled dependencies without network requests."""
    paths = {name: shutil.which(name) for name in ("node", "npm", "ffmpeg", "ffprobe", "git")}
    paths["python"] = sys.executable
    tools = {name: bool(path) for name, path in paths.items()}
    checks = {"python": {"ok": sys.version_info[:2] >= (3, 11),
                         "version": ".".join(map(str, sys.version_info[:3])), "path": sys.executable}}
    issues = []
    next_steps = []
    for name in ("node", "npm", "ffmpeg", "ffprobe"):
        path = paths[name]
        command = npm_command(path, paths["node"]) if name == "npm" and path and paths["node"] else [path]
        flag = "-version" if name in ("ffmpeg", "ffprobe") else "--version"
        check = probe([*command, flag]) if path else {"ok": False, "version": None}
        check["path"] = path
        if name == "node" and check["ok"]:
            version = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?", check["version"])
            check["ok"] = bool(version and int(version.group(1)) >= 22)
        checks[name] = check
    hints = {
        "python": "Zainstaluj Python 3.11+ i uruchom polecenie ponownie tym interpreterem.",
        "node": "Zainstaluj Node.js 22+ (z npm), a następnie otwórz nowy terminal.",
        "npm": "Przywróć npm z instalacji Node.js i upewnij się, że jest dostępny w PATH.",
        "ffmpeg": "Zainstaluj FFmpeg i dodaj katalog z ffmpeg oraz ffprobe do PATH.",
        "ffprobe": "Dodaj ffprobe z instalacji FFmpeg do PATH.",
    }
    for name, check in checks.items():
        if not check["ok"]:
            issues.append("Niedostępny lub niezgodny runtime: " + name)
            next_steps.append(hints[name])

    missing = [{"route": key, "path": path}
               for key, route in core.read(root / "config/routes.json")["routes"].items()
               for path in route["skills"] if not core.local(root, path, exists=False).is_file()]
    if missing:
        issues.append("Brakuje wymaganych lokalnych instrukcji produkcji.")
        next_steps.append("Przywróć brakujące pliki repozytorium wskazane w missing_skill_paths.")
    prerequisites_ready = not issues

    expected = core.read(root / "package.json")["dependencies"]
    dependencies = []
    for name, entry in (("hyperframes", "bin/hyperframes.mjs"), ("gsap", "dist/gsap.min.js")):
        package = root / "node_modules" / name
        try:
            installed = core.read(package / "package.json").get("version")
        except (OSError, ValueError):
            installed = None
        dependencies.append({"name": name, "expected": expected[name], "installed": installed,
                             "ready": installed == expected[name] and (package / entry).is_file()})
    if not all(item["ready"] for item in dependencies):
        issues.append("Brakuje przypiętych zależności Node lub ich wersje są inne niż w projekcie.")
        next_steps.append("Uruchom python -S studio.py setup, aby odtworzyć zależności z package-lock.json.")

    ready = not issues
    if ready:
        next_steps.append("python -S studio.py demo --render")
    return {"checked_at": core.now(), "ready": ready, "prerequisites_ready": prerequisites_ready,
            "tools": tools, "runtime_checks": checks, "missing_skill_paths": missing,
            "node_dependencies": dependencies,
            "local_assembly_ready": checks["python"]["ok"] and checks["ffmpeg"]["ok"] and checks["ffprobe"]["ok"],
            "hyperframes_installed": dependencies[0]["ready"],
            "library_optional": True, "issues": issues, "next_steps": next_steps,
            "external_connections": "Not tested. No credentials read or network calls made.",
            "next": next_steps[0],
            "render_note": "First render may download Chrome. Browser startup is verified by demo --render."}


def setup(root: Path = core.ROOT, *, with_library: bool = False) -> dict:
    """Install locked project dependencies; optional upstream sources are explicit."""
    report = inspect(root)
    steps = []

    def finish(error: str | None = None) -> dict:
        if error:
            report["issues"].append(error)
            report["ready"] = False
            report["next_steps"] = [error, *report["next_steps"]]
            report["next"] = error
        report["setup"] = {"with_library": with_library, "steps": steps,
                           "passed": report["ready"] and not error}
        report["external_connections"] = "Provider accounts not tested. Only dependency installation commands listed in setup.steps were requested."
        core.write(root / "output/system/setup.json", report)
        return report

    if with_library and not report["tools"]["git"]:
        return finish("Zainstaluj Git i dodaj go do PATH przed uruchomieniem setup --with-library.")
    if not report["prerequisites_ready"]:
        return finish("Uzupełnij wymagane narzędzia i pliki wymienione w next_steps; instalacja nie została uruchomiona.")

    checks = report["runtime_checks"]
    commands = [("npm", [*npm_command(checks["npm"]["path"], checks["node"]["path"]),
                         "ci", "--ignore-scripts"], 600)]
    if with_library:
        commands.extend([
            ("library", [sys.executable, "-S", str(root / "scripts/bootstrap_library.py")], 1800),
            ("library-check", [sys.executable, "-S", str(root / "scripts/library_check.py")], 600),
        ])
    for name, command, timeout in commands:
        relative_log = f"output/system/setup-{name}.log"
        log = root / relative_log
        log.parent.mkdir(parents=True, exist_ok=True)
        step = {"name": name, "command": command, "log": relative_log, "passed": False}
        steps.append(step)
        try:
            with log.open("w", encoding="utf-8") as stream:
                result = subprocess.run(command, cwd=root, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=timeout)
            step["exit_code"] = result.returncode
            if result.returncode:
                return finish(f"Etap {name} nie powiódł się (kod {result.returncode}). Sprawdź {relative_log} i uruchom setup ponownie.")
        except (OSError, subprocess.SubprocessError) as exc:
            step["error"] = type(exc).__name__
            return finish(f"Etap {name} przerwany ({type(exc).__name__}). Sprawdź {relative_log} i uruchom setup ponownie.")
        step["passed"] = True
    report = inspect(root)
    return finish()
