"""Pinned local Kinetic Film integration. No provider calls or implicit downloads."""
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import uuid

from studio_core import (ROOT, check_job, create_job, fingerprint, local, now, probe_job,
                         read, record_render, register_asset, sha, write)

CACHE = ROOT / "tools/runtime/scenario-kinetic-film"
PIN = ROOT / "config/kinetic-source.json"
EXAMPLE = ROOT / "examples/kinetic-launch"
SIZES = {"720": (1280, 720), "1080": (1920, 1080), "4k": (3840, 2160)}
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")


def catalog_entry():
    path = "skills/kinetic-launch/SKILL.md"
    return {"name": "kinetic-launch", "kind": "skill", "source": "social-motion-agent", "path": path,
            "description": "Beat-synced Kinetic Film launch videos, CSS 3D camera, motion blur and verified local output",
            "sha256": sha(ROOT / path), "activation": "local"}


def verify_source(source):
    """Only accept the inspected engine revision, with no escaping links."""
    source = Path(source).resolve()
    pin = read(PIN)
    for relative, expected in pin["files"].items():
        part = PurePosixPath(relative)
        if part.is_absolute() or ".." in part.parts or "\\" in relative:
            raise ValueError("Invalid path in the Kinetic source pin")
        file = source.joinpath(*part.parts)
        if not file.resolve().is_relative_to(source) or not file.is_file() or sha(file) != expected:
            raise ValueError(f"Kinetic source missing or changed: {relative}. Use the documented pinned package; do not overwrite a modified engine.")
    return pin


def setup(source):
    """Copy only known, hash-verified source files to an ignored local runtime cache."""
    source = Path(source).resolve()
    pin = verify_source(source)
    if CACHE.exists():
        verify_source(CACHE)
        return {"ready": True, "already_present": True, "source_tree_sha256": pin["tree_sha256"]}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    staging = CACHE.with_name(".kinetic-" + uuid.uuid4().hex)
    try:
        for relative in pin["files"]:
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, destination)
        verify_source(staging)
        staging.rename(CACHE)
    finally:
        if staging.exists():
            if staging.resolve().parent != CACHE.parent.resolve():
                raise ValueError("Refusing cleanup outside the runtime directory")
            shutil.rmtree(staging)
    return {"ready": True, "already_present": False, "source_tree_sha256": pin["tree_sha256"],
            "provider_connected": False, "next": "studio.py kinetic doctor"}


def doctor():
    issues = []
    try:
        pin = verify_source(CACHE)
    except (OSError, ValueError) as exc:
        pin = {}
        issues.append(str(exc))
    for tool in ("node", "ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            issues.append(f"Missing {tool}")
    if not (ROOT / "node_modules/playwright/package.json").is_file():
        issues.append("Missing locked Node Playwright; run studio.py setup or npm ci --ignore-scripts")
    python = subprocess.run([sys.executable, "-I", "-c", "import numpy, cv2; print(numpy.__version__, cv2.__version__)"],
                            capture_output=True, text=True, timeout=30)
    if python.returncode:
        issues.append("Optional Python packages missing; install requirements-kinetic.txt with this Python interpreter")
    return {"ready": not issues, "issues": issues, "source_tree_sha256": pin.get("tree_sha256"),
            "python_packages": python.stdout.strip() if not python.returncode else None,
            "browser_export_tested": False, "provider_connected": False}


def _replace(path, before, after):
    text = path.read_text(encoding="utf-8")
    if text.count(before) != 1:
        raise ValueError(f"Unsupported upstream runtime: {path.name}")
    path.write_text(text.replace(before, after), encoding="utf-8")


def _adapt(runtime):
    """Compatibility changes stay in the job; the source cache is immutable."""
    shutil.copy2(ROOT / "scripts/kinetic_platform.py", runtime / "kinetic_platform.py")
    _replace(runtime / "browser.mjs", "'--enable-gpu'", "'--enable-gpu', '--allow-file-access-from-files'")
    _replace(runtime / "browser.mjs", "timeout: 120000", "timeout: 30000")
    _replace(runtime / "render.mjs", "MAXS = '99'", "MAXS = process.env.KINETIC_MAX_SAMPLES || '4'")
    _replace(runtime / "render.mjs", "process.exit(0);", "process.exit(errs.length ? 1 : 0);")
    _replace(runtime / "post.py", "import sys, struct, subprocess, os, numpy as np, cv2",
             "import sys, struct, subprocess, os, numpy as np, cv2\ncv2.setNumThreads(2)")
    _replace(runtime / "post.py", "ff.stdin.close(); ff.wait(); node.wait()",
             "ff.stdin.close(); ff_status = ff.wait(); node_status = node.wait()")
    _replace(runtime / "post.py", "sys.exit(0 if done == f1 - f0 else 1)",
             "sys.exit(0 if done == f1 - f0 and ff_status == 0 and node_status == 0 else 1)")
    _replace(runtime / "render.py",
             "try: ram = int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout) / 2 ** 30\nexcept Exception: ram = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 ** 30",
             "from kinetic_platform import memory_gib, workers_for\nram = memory_gib()")
    _replace(runtime / "render.py",
             "workers = a.workers or max(1, min(3 if a.res == '4k' else 6, int(ram // per), os.cpu_count() // 3))",
             "workers = workers_for(a.res, a.workers)")
    _replace(runtime / "render.py", "url, srv = serve(a.film); env = {**os.environ, 'FILM_URL': url}",
             "url, srv = serve(a.film)\nfrom pathlib import Path\nenv = {**os.environ, 'FILM_URL': Path(a.film).resolve().as_uri() + '/'}")
    _replace(runtime / "info.mjs", "const f = await pg.evaluate(() => window.__film ?",
             "const f = await pg.evaluate(async () => { const spec = (await import('./spec.js')).default; const end = spec.scenes.find(([block]) => block.name === 'Logo'); return window.__film ?")
    _replace(runtime / "info.mjs", "cues: __film.cues } : null);",
             "cues: __film.cues, endCardStart: end ? end[1] * 60 / spec.bpm : __film.dur } : null; });")
    _replace(runtime / "info.mjs", "if (errs.length) console.error('page errors:', errs.slice(0, 5));",
             "if (errs.length) { console.error('page errors:', errs.slice(0, 5)); process.exit(1); }")


def prepare(folder, example="starter"):
    folder = Path(folder).resolve()
    job = read(folder / "job.json")
    if job["kind"] != "kinetic-launch" or job["format"] != "16:9":
        raise ValueError("Kinetic Film currently requires --kind kinetic-launch and --format 16:9; portrait needs a separate composition.")
    if example not in ("starter", "social-motion-agent"):
        raise ValueError("Unknown Kinetic example")
    if example == "social-motion-agent" and job["duration_sec"] != 30:
        raise ValueError("The bundled Kinetic demo is exactly 30 seconds")
    if (folder / "source/kinetic").exists() or (folder / "source/kinetic-runtime").exists():
        raise ValueError("Kinetic composition exists; preserve edits and create another job.")
    pin = verify_source(CACHE)
    film = folder / "source/kinetic"
    runtime = folder / "source/kinetic-runtime"
    for relative in pin["files"]:
        if relative.startswith("engine/"):
            destination = film / relative.removeprefix("engine/")
        elif relative.startswith("scripts/"):
            destination = runtime / relative.removeprefix("scripts/")
        else:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CACHE / relative, destination)
    _adapt(runtime)
    if example == "social-motion-agent":
        for name in ("spec.js", "title.svg"):
            shutil.copy2(EXAMPLE / name, film / name)
        _replace(film / "index.html", "</style></head>",
                 ".made { font-size: 27px; letter-spacing: .025em; }\n.endline { font-size: 35px; }\n.btext { font-size: 48px; }\n</style></head>")
    else:
        template = (ROOT / "templates/kinetic-spec.js").read_text(encoding="utf-8")
        template = template.replace("__TITLE__", json.dumps(job["title"], ensure_ascii=False))
        template = template.replace("__BEATS__", str(job["duration_sec"] * 128 / 60))
        (film / "spec.js").write_text(template, encoding="utf-8")
    for font in sorted((film / "fonts").glob("*.ttf")):
        register_asset(folder, font, "Pinned Scenario Kinetic Film font", "Bundled font OFL text in source/kinetic/fonts", "Typography")
    audio_id = None
    if example == "social-motion-agent":
        (film / "audio").mkdir()
        shutil.copy2(EXAMPLE / "mix.wav", film / "audio/mix.wav")
        audio = register_asset(folder, EXAMPLE / "mix.wav", "Owner-authorized Kinetic demo mix", "See examples/kinetic-launch/provenance.json and docs/MEDIA_RIGHTS.md", "Demo music and SFX")
        audio_id = audio["id"]
    write(folder / "source/kinetic-settings.json", {"schema_version": 1, "source_tree_sha256": pin["tree_sha256"],
          "audio_asset_id": audio_id, "example": example})
    brief = read(folder / "brief.json")
    brief.update(engine="kinetic-film", engine_reason="Explicit kinetic-launch route; pinned local Scenario engine with motion blur")
    write(folder / "brief.json", brief)
    job["fps"] = 60
    write(folder / "job.json", job)
    return {"job": str(folder), "composition": "source/kinetic/spec.js", "engine": "kinetic-film",
            "next": "Complete the actual brief, research and storyboard; register a premixed score or explicitly disable audio. Then render-kinetic."}


def _run_json(argv, *, env=None, cwd=None):
    result = subprocess.run([str(x) for x in argv], capture_output=True, text=True, encoding="utf-8", errors="replace",
                            cwd=cwd, env=env, timeout=120, shell=False)
    if result.returncode:
        raise ValueError("Kinetic inspection failed: " + result.stderr[-1400:])
    try:
        return json.loads(result.stdout)
    except ValueError:
        raise ValueError("Kinetic inspection did not return valid JSON") from None


def quality(folder, target, info):
    """Same numeric gates as Kinetic Film, excluding the actual end-card block."""
    runtime = folder / "source/kinetic-runtime"
    data = _run_json(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-of", "json", target])
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    dynamics = _run_json([sys.executable, "-I", runtime / "dyn.py", target, "0", str(max(1, info["endCardStart"])),
                          folder / "notes" / (target.stem + "-dynamism.json")])
    holds = subprocess.run([sys.executable, "-I", str(runtime / "holds.py"), str(target), ".5", str(info["bpm"])],
                           capture_output=True, text=True, timeout=120, check=True)
    long_holds = [line.strip() for line in holds.stdout.splitlines() if "s (beat" in line
                  and float(line.split("s")[0]) < info["endCardStart"]
                  and float(line.split(")")[1].split("s")[0]) > .6]
    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"],
                            capture_output=True, text=True, timeout=300)
    checks = {"frames": int(video.get("nb_read_frames", 0)) == round(info["dur"] * info["fps"]),
              "size": target.stat().st_size < 1_000_000_000, "h264_level": video["codec_name"] == "h264" and 0 < int(video["level"]) <= 52,
              "full_decode": decode.returncode == 0 and not decode.stderr.strip(),
              "still_share": dynamics["still_share"] <= .4, "holds": not long_holds, "median_motion": dynamics["median_flow"] >= 2.5}
    loudness = None
    if any(s["codec_type"] == "audio" for s in data["streams"]):
        measure = subprocess.run(["ffmpeg", "-i", str(target), "-vn", "-af", "ebur128", "-f", "null", "-"],
                                 capture_output=True, text=True, timeout=180, check=True)
        values = re.findall(r"I:\s+(-?[\d.]+) LUFS", measure.stderr)
        loudness = float(values[-1]) if values else None
        checks["loudness"] = loudness is not None and -16 <= loudness <= -12
    return {"passed": all(checks.values()), "checks": checks, "dynamism": dynamics,
            "long_holds": long_holds, "loudness_lufs": loudness, "device_playback_tested": False}


def render(folder, name="kinetic", resolution="1080", samples=4, audio=None):
    folder = Path(folder).resolve()
    if not NAME.fullmatch(name) or resolution not in SIZES or samples not in (2, 4, 8):
        raise ValueError("Invalid Kinetic name, resolution or sample count")
    errors = check_job(folder, "assets")
    if errors:
        raise ValueError("\n".join(errors))
    if read(folder / "brief.json").get("engine") != "kinetic-film":
        raise ValueError("Prepare and explicitly select the kinetic-film engine first")
    film = local(folder, "source/kinetic/spec.js").parent
    runtime = local(folder, "source/kinetic-runtime/render.py").parent
    fingerprint(folder)  # Validate every source path before executing the job's inspector.
    settings = read(local(folder, "source/kinetic-settings.json"))
    audio_id = audio or settings.get("audio_asset_id")
    item = next((x for x in read(folder / "assets.json")["items"] if x["id"] == audio_id), None)
    if audio_id and not item:
        raise ValueError("--audio must be an asset ID registered with asset-add")
    if not item and read(folder / "brief.json").get("audio_required", True):
        raise ValueError("Register a premixed score and pass --audio ASSET_ID, or explicitly set audio_required=false")
    audio_file = local(folder, item["path"]) if item else None
    if item and sha(audio_file) != item["sha256"]:
        raise ValueError("Audio asset changed; register the new version first")
    target = local(folder, "renders/" + name + ".mp4", exists=False)
    if target.exists():
        raise ValueError("Render already exists; choose a new --name")
    lock = target.with_suffix(".lock")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ValueError("Kinetic render lock exists; inspect it before retrying") from None
    token = uuid.uuid4().hex[:8]
    work = target.parent / (".kinetic-" + name + "-" + token)
    picture = work / "picture.mp4"
    staging = target.with_name(name + "-" + token + ".partial.mp4")
    log = folder / "notes" / ("kinetic-" + name + ".log")
    env = {**os.environ, "FILM_URL": film.as_uri() + "/", "KINETIC_MAX_SAMPLES": str(samples),
           "GRAIN": ".4", "ENC": "-c:v libx264 -crf 16 -preset fast -level " + ("5.2" if resolution == "4k" else "4.2") + " -threads 2"}
    try:
        with handle:
            handle.write(str(os.getpid()))
        work.mkdir()
        info = _run_json(["node", runtime / "info.mjs"], env=env, cwd=film)
        job = read(folder / "job.json")
        if info["fps"] != 60 or not math.isclose(info["dur"], job["duration_sec"], abs_tol=1/60):
            raise ValueError("spec.js must match the job duration and use 60 FPS")
        if job["format"] != "16:9":
            raise ValueError("Kinetic Film requires a deliberately authored 16:9 composition")
        job.update(width=SIZES[resolution][0], height=SIZES[resolution][1], fps=60)
        write(folder / "job.json", job)
        settings["audio_asset_id"] = audio_id
        write(folder / "source/kinetic-settings.json", settings)
        source_fingerprint = fingerprint(folder)
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run([sys.executable, "-I", str(runtime / "render.py"), str(film), "--res", resolution,
                                      "--workers", "1", "--out", str(picture)], cwd=film, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT, timeout=3600, shell=False)
        if process.returncode or not picture.is_file():
            with log.open("a", encoding="utf-8") as stream:
                for worker_log in sorted((work / "parts").glob("*.log")):
                    stream.write("\n" + worker_log.read_text(encoding="utf-8", errors="replace"))
            raise ValueError(f"Kinetic renderer failed; inspect {log.relative_to(folder)}")
        command = ["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(picture)]
        if audio_file:
            command += ["-i", str(audio_file), "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "320k"]
        command += ["-c:v", "copy", "-t", str(info["dur"]), "-movflags", "+faststart", str(staging)]
        subprocess.run(command, capture_output=True, timeout=180, check=True, shell=False)
        if target.exists():
            raise ValueError("Render appeared during export; existing output was preserved")
        staging.rename(target)
        report = quality(folder, target, info)
        write(folder / "notes" / ("kinetic-" + name + "-quality.json"), report)
        if not report["passed"]:
            return {"render": target.relative_to(folder).as_posix(), "probe_passed": False, "quality": report,
                    "reviewed": False, "receipt_recorded": False, "log": log.relative_to(folder).as_posix()}
        record_render(folder, target.relative_to(folder).as_posix(), source_fingerprint, "kinetic-film")
    finally:
        handle.close()
        picture.unlink(missing_ok=True)
        staging.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)
        if work.resolve().parent != target.parent.resolve():
            raise ValueError("Refusing cleanup outside the render directory")
        if work.exists():
            shutil.rmtree(work)
    technical = probe_job(folder, target.relative_to(folder).as_posix())
    return {"render": target.relative_to(folder).as_posix(), "render_sha256": sha(target),
            "probe_passed": technical["passed"], "probe_failures": technical["failures"],
            "quality": report, "reviewed": False, "receipt_recorded": True, "log": log.relative_to(folder).as_posix()}


def demo():
    """Reproduce the owner's published composition without inventing a fresh intake."""
    folder = create_job("Kinetic launch demo", "kinetic-launch", "16:9", 30, "pl")
    prepare(folder, "social-motion-agent")
    brief = read(folder / "brief.json")
    brief.update(goal="Reproduce the published Social Motion Agent workflow demo", audience="People using creative AI agents",
                 direction="Oversized kinetic type, graphite/paper/orange, beat-synced CSS 3D camera", cta="Social Motion Agent on GitHub",
                 audio_required=True, captions_required=False)
    write(folder / "brief.json", brief)
    intake = read(folder / "intake.json")
    for question in intake["questions"]:
        question["answer"] = "Bundled owner-approved specification, not a new user answer; see examples/kinetic-launch/provenance.json."
    write(folder / "intake.json", intake)
    write(folder / "research.json", {"sources": [{"id": "demo", "title": "Kinetic demo source and provenance",
        "url": "https://github.com/aievolutionpl/social-motion-agent/tree/main/examples/kinetic-launch", "accessed_at": now(),
        "used_for": "Reproduce supplied composition and audio; this is a workflow illustration, not an agent execution recording"}],
        "claims": [], "conclusions": "No invented outcome statistics or paid generation. Inspect and listen before approval."})
    write(folder / "storyboard.json", read(EXAMPLE / "storyboard.json"))
    shutil.copy2(EXAMPLE / "script.md", folder / "source/script.md")
    (folder / "HANDOFF.md").write_text("# Kinetic demo reproduction\n\nLocal composition with supplied audio. No paid API calls. Render, inspect and listen before approval.\n", encoding="utf-8")
    return folder
