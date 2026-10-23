"""Local OpenScreen adapter: real app commands, bounded window capture, no shell."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def config():
    return json.loads((ROOT / "config/openscreen.json").read_text(encoding="utf-8-sig"))


def executable():
    settings = config()
    candidates = [os.environ.get("OPENSCREEN_EXECUTABLE"), str(ROOT / settings["executable"]),
                  str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Openscreen/Openscreen.exe"),
                  r"C:\Program Files\Openscreen\Openscreen.exe", shutil.which("openscreen")]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate).resolve()
    raise FileNotFoundError("OpenScreen runtime unavailable; read docs/OPENSCREEN.md or set OPENSCREEN_EXECUTABLE")


def events(text):
    result = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def invoke(args, timeout=90):
    env = os.environ.copy()
    env.pop("ELECTRON_RUN_AS_NODE", None)
    state = (ROOT / config()["user_data"]).resolve()
    command = [str(executable()), "--user-data-dir=" + str(state), *map(str, args)]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    parsed = events(result.stdout)
    failures = [event for event in parsed if event.get("event") == "error" or event.get("success") is False]
    if result.returncode or failures:
        detail = failures[-1] if failures else result.stderr.strip()[-1200:] or result.stdout.strip()[-1200:]
        raise RuntimeError(f"OpenScreen failed ({result.returncode}): {detail}. On this Windows host Electron CLI requires execution outside the restricted sandbox.")
    return result.stdout, parsed


def done(parsed):
    completed = [event for event in parsed if event.get("event") == "done" and event.get("success") is True]
    if not completed:
        raise RuntimeError("OpenScreen returned no successful done event; do not treat partial media as finished")
    return completed[-1]


def sources():
    _, parsed = invoke(["sources", "--json"])
    return done(parsed)["sources"]


def require_window(available, title):
    matches = [window for window in available.get("windows", [])
               if title.casefold() in window.get("name", "").casefold()]
    if len(matches) != 1:
        raise ValueError(f"Window selector must match exactly one window; matched {len(matches)}. Use a unique title. No display fallback.")
    return matches[0]


def output_path(value):
    path = Path(value).resolve()
    if path.exists():
        raise FileExistsError(f"Output already exists; choose a new version: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def input_file(value):
    path = Path(value).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check the actual CLI help; never records")
    sub.add_parser("help", help="Print the actual app command reference")
    p = sub.add_parser("sources", help="List capture sources; optional private local JSON")
    p.add_argument("--output", type=Path)
    p = sub.add_parser("project", help="Create a minimal project from an existing recording; never records")
    p.add_argument("--video", required=True)
    p.add_argument("--project", required=True)
    p = sub.add_parser("record", help="Record one uniquely named window; bounded duration")
    p.add_argument("--window", required=True)
    p.add_argument("--duration", required=True, type=float)
    p.add_argument("--project", required=True)
    for flag in ("mic", "system-audio", "camera"):
        p.add_argument("--" + flag, action="store_true")
    p = sub.add_parser("export")
    p.add_argument("--project", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--quality", choices=("medium", "good", "source"), default="good")
    p.add_argument("--fps", type=int, choices=(24, 30, 60), default=60)
    p.add_argument("--auto-zoom", action="store_true")
    p.add_argument("--voiceover")
    p.add_argument("--audio-mode", choices=("mix", "replace"), default="mix")
    p.add_argument("--audio-offset", type=float, default=0)
    for name in ("info", "pack", "captions"):
        p = sub.add_parser(name)
        p.add_argument("--project", required=True)
        if name == "pack":
            p.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command in ("doctor", "help"):
        text, _ = invoke(["help"], timeout=45)
        if args.command == "help":
            print(text)
        else:
            print(json.dumps(dict(executable=str(executable()),version=config()["version"],
                 cli_help_verified="record" in text and "export" in text and "mcp" in text,
                 ffmpeg=bool(shutil.which("ffmpeg")),ffprobe=bool(shutil.which("ffprobe")),
                 mcp_registered=False,capture_tested="see output/system/openscreen/verification.json"),indent=2))
    elif args.command == "sources":
        value = sources()
        if args.output:
            p = output_path(args.output)
            p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
            print(json.dumps(dict(path=str(p),window_count=len(value.get("windows",[])))))
        else:
            print(json.dumps(value,ensure_ascii=False,indent=2))
    elif args.command == "project":
        video = input_file(args.video)
        project = output_path(args.project)
        if project.suffix != ".openscreen" or project.parent != video.parent:
            raise ValueError("Save the .openscreen project beside its video so native media validation can load it")
        project.write_text(json.dumps(dict(version=2,media=dict(screenVideoPath=str(video)),editor={}),indent=2),encoding="utf-8")
        print(project)
    elif args.command == "record":
        if not args.window.strip() or not math.isfinite(args.duration) or args.duration <= 0:
            raise ValueError("A unique window title and finite positive duration are required")
        project = output_path(args.project)
        if project.suffix != ".openscreen":
            raise ValueError("Project must end in .openscreen")
        require_window(sources(),args.window)
        command = ["record","--window",args.window,"--duration",str(args.duration),"--project",str(project),"--json"]
        for flag in ("mic","system-audio","camera"):
            if getattr(args,flag.replace("-","_")):
                command.append("--"+flag)
        _, parsed = invoke(command,timeout=args.duration+90)
        print(json.dumps(done(parsed),ensure_ascii=False,indent=2))
    elif args.command == "export":
        project = input_file(args.project)
        output = output_path(args.output)
        if not math.isfinite(args.audio_offset) or args.audio_offset < 0:
            raise ValueError("Audio offset must be finite and nonnegative")
        command = ["export",str(project),"-o",str(output),"--quality",args.quality,"--fps",str(args.fps),"--json"]
        if args.auto_zoom:
            command.append("--auto-zoom")
        if args.voiceover:
            command += ["--audio",str(input_file(args.voiceover)),"--audio-mode",args.audio_mode,"--audio-offset",str(args.audio_offset)]
        _, parsed = invoke(command,timeout=1800)
        value = done(parsed)
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("Export reported done but output is missing or empty")
        print(json.dumps(value,ensure_ascii=False,indent=2))
    else:
        command = [args.command,str(input_file(args.project)),"--json"]
        if args.command == "pack":
            command += ["--out",str(output_path(args.output))]
        text, parsed = invoke(command,timeout=600 if args.command=="captions" else 90)
        print(text.strip() if args.command=="info" else json.dumps(done(parsed),ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout,"reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (ValueError,RuntimeError,OSError,subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise SystemExit(1)
