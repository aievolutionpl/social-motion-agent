"""Local walk-and-talk planning and deterministic footage typography; no provider calls."""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

import studio_core as core

NAME = "kinetic-walk-talk"
MODES = ("footage", "recording", "ai")
COLORS = {"white": "#ffffff", "black": "#101010", "orange": "#ff8a00",
          "blue": "#28a8e8", "cyan": "#64f4ff"}
IMAGES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEOS = {".mp4", ".mov", ".webm"}


def catalog_entry():
    path = f"skills/{NAME}/SKILL.md"
    return {"name": NAME, "kind": "skill", "source": "social-motion-agent", "path": path,
            "description": "Walk and talk reels: kinetic captions, text behind the presenter, camera punches and sound cues",
            "sha256": core.sha(core.ROOT / path), "activation": "local"}


def job(folder):
    info = core.read(folder / "job.json")
    if info["kind"] != NAME or info["format"] != "9:16":
        raise ValueError("Walk-talk requires a kinetic-walk-talk job in 9:16")
    return info


def prepare(folder: Path, mode="footage"):
    info = job(folder)
    if mode not in MODES:
        raise ValueError("Unknown walk-talk mode")
    target = folder / "source/walk-talk.json"
    plan = folder / "source/walk-talk-plan.md"
    if target.exists() or plan.exists():
        raise ValueError("Walk-talk sources already exist; preserve and edit them")
    core.write(target, {"schema_version": 1, "mode": mode,
                       "background_asset": None, "foreground_asset": None, "audio_asset": None,
                       "captions": [], "accents": [], "punches": [], "sound_cues": []})
    plan.write_text(
        "# Walk & Talk production plan\n\n"
        f"Mode: {mode}. Duration: {info['duration_sec']} s. Format: 9:16.\n\n"
        "Use the real brief, final voice timing and registered assets. This plan does not approve intake, "
        "create footage, synthesize speech or confirm a listening review.\n\n"
        "| Time | Spoken phrase | Shot / gesture | Small captions | Hero word / depth | Transition | Sound cue |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n\n"
        "Record a presenter walking toward a smoothly retreating camera, or generate short consistent "
        "clean shots with an authorized provider. Assemble a full-length base first. For text behind "
        "the subject, prepare a matching full-frame transparent foreground with identical timing and crop.\n\n"
        "Register the base, optional foreground and optional premixed soundtrack with studio.py asset-add. "
        "Populate source/walk-talk.json with the returned IDs. Small captions follow actual speech; "
        "accents emphasize selected ideas. sound_cues are editorial notes, not audio synthesis.\n\n"
        "Keep the original base sound, or explicitly replace it with one full-length premix containing "
        "voice, music and SFX. Search the local library with studio.py sfx find. Follow its gain cap.\n\n"
        "Compose with studio.py walk-talk compose JOB, then use the normal render-html, probe, sheet, "
        "review and pack workflow. Inspect moving masks, Polish glyphs, phone readability and the actual mix.\n",
        encoding="utf-8")
    return {"spec": target.relative_to(folder).as_posix(), "plan": plan.relative_to(folder).as_posix(),
            "mode": mode, "generated_media": False, "reviewed": False}


def number(value, label, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def validate(spec, duration):
    if not isinstance(spec, dict) or spec.get("schema_version") != 1 or spec.get("mode") not in MODES:
        raise ValueError("Invalid walk-talk spec version or mode")
    if not isinstance(spec.get("background_asset"), str) or not spec["background_asset"].strip():
        raise ValueError("Register a full-length background_asset before composing")
    for key in ("foreground_asset", "audio_asset"):
        if spec.get(key) is not None and (not isinstance(spec[key], str) or not spec[key].strip()):
            raise ValueError(f"{key} must be an asset ID or null")
    for key in ("captions", "accents", "punches", "sound_cues"):
        if not isinstance(spec.get(key), list):
            raise ValueError(f"{key} must be a list")
        for item in spec[key]:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid {key} item")
            start = number(item.get("start"), key + ".start", 0, duration)
            end = number(item.get("end"), key + ".end", 0, duration)
            if end <= start:
                raise ValueError(f"{key}: end must follow start")
            if key in ("captions", "accents"):
                text = item.get("text")
                if not isinstance(text, str) or not text.strip() or len(text) > 180:
                    raise ValueError(f"{key}: supply 1-180 characters of text")
            if key == "accents":
                if item.get("color", "blue") not in COLORS:
                    raise ValueError("Unknown accent color")
                if not isinstance(item.get("behind_subject", False), bool):
                    raise ValueError("behind_subject must be boolean")
                if item.get("behind_subject") and not spec.get("foreground_asset"):
                    raise ValueError("Text behind the subject requires an aligned foreground_asset with alpha")
                for field, default, lo, hi in (("x", 50, 10, 90), ("y", 23, 10, 80), ("size", 140, 44, 260)):
                    number(item.get(field, default), field, lo, hi)
            if key == "punches":
                number(item.get("zoom", 1.12), "zoom", 1, 1.3)
            if key == "sound_cues" and not isinstance(item.get("note"), str):
                raise ValueError("Sound cues require an editorial note")
    for key in ("captions", "punches"):
        ordered = sorted(spec[key], key=lambda item: item["start"])
        if any(a["end"] > b["start"] for a, b in zip(ordered, ordered[1:])):
            raise ValueError(f"Overlapping {key}")
    return spec


def media(folder, asset_id, role, duration, fps):
    registry = core.read(folder / "assets.json")["items"]
    item = next((entry for entry in registry if entry["id"] == asset_id), None)
    if not item:
        raise ValueError(f"Unknown {role} asset ID: {asset_id}")
    path = core.local(folder, item["path"])
    if core.sha(path) != item["sha256"]:
        raise ValueError(f"Changed registered asset: {asset_id}")
    extensions = {".wav", ".mp3", ".m4a", ".ogg"} if role == "audio" else IMAGES | VIDEOS
    if path.suffix.lower() not in extensions:
        raise ValueError(f"Unsupported {role} media type")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                            capture_output=True, check=True, timeout=30)
    metadata = json.loads(result.stdout)
    streams = metadata.get("streams", [])
    kind = "audio" if role == "audio" else "video"
    stream = next((entry for entry in streams if entry["codec_type"] == kind), None)
    if not stream:
        raise ValueError(f"Missing {kind} stream for {role}")
    if path.suffix.lower() not in IMAGES:
        length = core.video_duration(stream) if kind == "video" else float(stream.get("duration", 0))
        if not length and kind == "video":
            # WebM commonly stores per-stream length in tags, not stream.duration.
            stamp = stream.get("tags", {}).get("DURATION", "")
            if re.fullmatch(r"\d+:\d+:\d+(?:\.\d+)?", stamp):
                hours, minutes, seconds = map(float, stamp.split(":"))
                length = hours * 3600 + minutes * 60 + seconds
        if not length and kind == "audio":
            length = float(metadata.get("format", {}).get("duration", 0))
        if not math.isfinite(length) or length + 1 / fps < duration:
            raise ValueError(f"{role} must cover the full job duration")
    return {"path": path, "sha256": item["sha256"], "id": asset_id,
            "image": path.suffix.lower() in IMAGES, "stream": stream,
            "has_audio": any(s["codec_type"] == "audio" for s in streams)}


def compose(folder: Path):
    info = job(folder)
    spec = validate(core.read(folder / "source/walk-talk.json"), info["duration_sec"])
    target = folder / "source/index.html"
    if target.exists():
        raise ValueError("Composition exists; preserve it before composing a new version")
    gsap = core.ROOT / "node_modules/gsap/dist/gsap.min.js"
    if not gsap.is_file():
        raise ValueError("Run studio.py setup to install the pinned GSAP dependency")
    loaded = {"background": media(folder, spec["background_asset"], "background", info["duration_sec"], info["fps"])}
    for role in ("foreground", "audio"):
        if spec.get(role + "_asset"):
            loaded[role] = media(folder, spec[role + "_asset"], role, info["duration_sec"], info["fps"])
    if "foreground" in loaded:
        base, front = loaded["background"]["stream"], loaded["foreground"]["stream"]
        if (base["width"], base["height"]) != (front["width"], front["height"]):
            raise ValueError("Background and foreground must have identical dimensions and crop")
    # Resolve and verify all inputs before writing any composition files.
    assets = folder / "source/media"
    copies = [(gsap, folder / "source/gsap.min.js")]
    for role, data in loaded.items():
        destination = assets / ("walk-talk-" + role + data["path"].suffix.lower())
        copies.append((data["path"], destination))
        data["url"] = "./media/" + destination.name
    font = core.ROOT / "examples/premium-intro/source/media/Inter.ttf"
    for src, name in ((font, "walk-talk-font.ttf"),
                      (font.with_name("Inter-OFL.txt"), "walk-talk-font-OFL.txt")):
        copies.append((src, assets / name))
    for src, dst in copies:
        if not src.is_file() or (dst.exists() and core.sha(src) != core.sha(dst)):
            raise ValueError("Missing source or differing composition dependency: " + dst.name)
    duration = info["duration_sec"]
    def mount(role, z):
        data = loaded[role]
        common = f'class="media {role}" style="z-index:{z}" src="{data["url"]}"'
        if data["image"]:
            return f'<img {common} alt="">'
        sound = 'data-has-audio="true"' if role == "background" and "audio" not in loaded and data["has_audio"] else 'muted data-volume="0"'
        return f'<video {common} data-start="0" data-duration="{duration}" data-track-index="{z}" {sound} playsinline></video>'
    layers = [mount("background", 0)]
    animations = []
    for kind, records in (("caption", spec["captions"]), ("accent", spec["accents"])):
        for index, item in enumerate(records):
            identity = f"{kind}-{index}"
            start, end = item["start"], item["end"]
            if kind == "caption":
                style, track = "", 4
            else:
                track = 1 if item.get("behind_subject") else 3
                style = (f'left:{item.get("x", 50)}%;top:{item.get("y", 23)}%;'
                         f'font-size:{item.get("size", 140)}px;color:{COLORS[item.get("color", "blue")]};')
            layers.append(f'<div id="{identity}" class="{kind} clip" data-start="{start}" data-duration="{end-start}" '
                          f'data-track-index="{track}" style="z-index:{track};{style}">{html.escape(item["text"])}</div>')
            enter = min(0.2, (end - start) / 3)
            animations.append(f'tl.set("#{identity}",{{autoAlpha:1}},{start});')
            animations.append(f'tl.fromTo("#{identity}",{{scale:.86,y:24,filter:"blur(6px)"}},'
                              f'{{scale:1,y:0,filter:"blur(0px)",duration:{enter},ease:"back.out(1.3)",immediateRender:false}},{start});')
            animations.append(f'tl.set("#{identity}",{{autoAlpha:0}},{end});')
    if "foreground" in loaded:
        layers.append(mount("foreground", 2))
    if "audio" in loaded:
        layers.append(f'<audio src="{loaded["audio"]["url"]}" data-start="0" data-duration="{duration}" data-track-index="5" data-volume="1"></audio>')
    for item in spec["punches"]:
        start, end = item["start"], item["end"]
        ramp = min(0.15, (end - start) / 3)
        zoom = item.get("zoom", 1.12)
        animations += [f'tl.to("#world",{{scale:{zoom},duration:{ramp},ease:"power2.out"}},{start});',
                       f'tl.to("#world",{{scale:1,duration:{ramp},ease:"power2.inOut"}},{end-ramp});']
    page = (core.ROOT / "templates/walk-talk.html").read_text(encoding="utf-8")
    values = {"WIDTH": info["width"], "HEIGHT": info["height"], "DURATION": duration,
              "FPS": info["fps"], "LANG": html.escape(info["language"], quote=True),
              "LAYERS": "\n".join(layers), "ANIMATION": "\n".join(animations)}
    page = re.sub(r"@@([A-Z]+)@@", lambda match: str(values[match[1]]), page)
    for src, dst in copies:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
    with target.open("x", encoding="utf-8") as stream:
        stream.write(page)
    return {"composition": "source/index.html", "reviewed": False, "generated_media": False,
            "foreground_alpha_verified": False, "sound_cues_are_notes_only": True,
            "audio": "replacement-premix" if "audio" in loaded else "base-track",
            "next": "Complete production records, render-html, probe, sheet and review the actual output"}
