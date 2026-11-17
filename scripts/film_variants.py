"""Render three playable directions; publish a gallery only after all three are complete."""
import hashlib
import html
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import studio_core as core
from editor_workspace import probe
from footage_selects import shortlist
from style_feedback import STYLES, collection, summary

RECIPE_VERSION = 1


def video_filter(style, width, height, fps):
    fit = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
           f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")
    if style == "kinetic":
        # Small, periodic camera pushes keep the cut and its speech in sync.
        fit += (f",zoompan=z='1+0.055*pow(sin(on*PI/({fps}*1.5)),2)':"
                f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={fps}")
    elif style == "studio":
        card_w, card_h = max(2, int(width * .82) // 2 * 2), max(2, int(height * .82) // 2 * 2)
        fit = (f"split=2[plate][subject];[plate]scale={width}:{height}:force_original_aspect_ratio=increase,"
               f"crop={width}:{height},gblur=sigma=18,eq=brightness=-0.12[matte];"
               f"[subject]scale={card_w}:{card_h}:force_original_aspect_ratio=decrease,"
               f"pad={card_w}:{card_h}:(ow-iw)/2:(oh-ih)/2[card];"
               f"[matte][card]overlay=x='(W-w)/2':y='(H-h)/2+H*.018*sin(t*1.4)',setsar=1,fps={fps}")
    return "[0:v:0]" + fit + ",format=yuv420p[v]"


def encode(source, target, style, width, height, fps, start=None, duration=None):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-filter_complex_threads", "1"]
    if start is not None:
        args += ["-ss", str(start)]
    args += ["-i", str(source)]
    if duration is not None:
        args += ["-t", str(duration)]
    args += ["-filter_complex", video_filter(style, width, height, fps), "-map", "[v]", "-map", "0:a:0?",
             "-c:v", "libx264", "-threads", "2", "-preset", "veryfast", "-crf", "19",
             "-c:a", "aac" if start is not None else "copy", "-movflags", "+faststart", str(target)]
    subprocess.run(args, check=True, timeout=3600)


def opening_sources(folder, query):
    assets = core.read(folder / "assets.json")["items"]
    usable = {}
    for asset in assets:
        path = core.local(folder, asset["path"])
        # Registered assets may include fonts, documents, stills or sound effects.
        if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"):
            continue
        try:
            info = probe(path)
        except (ValueError, OSError):
            continue
        video = next((s for s in info["streams"] if s["codec_type"] == "video" and not s.get("disposition", {}).get("attached_pic")), None)
        length = core.video_duration(video or {}) or float(info["format"].get("duration", 0))
        if video and math.isfinite(length) and length > .05:
            if core.sha(path) != asset["sha256"]:
                raise ValueError("Registered footage has changed")
            usable[asset["id"]] = (length, asset)
    if not usable:
        raise ValueError("Register a video with asset-add before rendering moving openings")
    cuts = []
    for item in shortlist(folder, query)["candidates"]:
        if item["asset_id"] in usable:
            length, asset = usable[item["asset_id"]]
            seconds = min(3, item["out_sec"] - item["in_sec"], length - item["in_sec"])
            if seconds >= .1:
                cuts.append({"asset": asset["path"], "sha256": asset["sha256"], "start": item["in_sec"],
                             "duration": seconds, "quote": item["quote"], "reason": item["reason"]})
    items = list(usable.values())
    while len(cuts) < 3:
        i = len(cuts)
        length, asset = items[i % len(items)]
        seconds = min(3, length)
        cuts.append({"asset": asset["path"], "sha256": asset["sha256"], "start": (length - seconds) * i / 2,
                     "duration": seconds, "quote": "", "reason": "Próbka obrazu z nagrania"})
    return cuts


def render_set(folder, master=None, *, openings=False, query=""):
    job = core.read(folder / "job.json")
    preference = summary(folder.parent, job.get("style_profile", "local"))
    fp = core.fingerprint(folder)
    if openings:
        sources = opening_sources(folder, query)
        factor = min(1, 540 / max(job["width"], job["height"]))
        width, height = [max(2, int(n * factor) // 2 * 2) for n in (job["width"], job["height"])]
    else:
        master = master or job.get("render")
        if not master:
            raise ValueError("Render a master before building the three films")
        src = core.local(folder, master)
        if src.suffix.lower() != ".mp4":
            raise ValueError("Expected an MP4 master")
        receipt = core.render_provenance(folder, master)
        checksum = core.sha(src)
        if receipt.get("fingerprint") != fp or receipt.get("render_sha256") != checksum:
            raise ValueError("Master no longer matches its render receipt")
        sources = [{"asset": src.relative_to(folder).as_posix(), "sha256": checksum}] * 3
        width, height = job["width"], job["height"]
    key_data = [RECIPE_VERSION, fp, sources, preference["profile"], preference["style_order"], width, height]
    digest = hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:20]
    key = ("openings-" if openings else "films-") + digest
    dest = core.local(folder, "previews/" + key, exists=False)
    if not dest.exists():
        temp = Path(tempfile.mkdtemp(prefix=".film-review-", dir=dest.parent))
        try:
            versions = []
            for (style, label), item in zip(STYLES.items(), sources):
                path = core.local(folder, item["asset"])
                target = temp / (style + ".mp4")
                if style == "editorial" and not openings:
                    shutil.copyfile(path, target)
                else:
                    encode(path, target, style, width, height, job["fps"], item.get("start"), item.get("duration"))
                info = probe(target)
                picture = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
                expected = item.get("duration", job["duration_sec"])
                if ((picture["width"], picture["height"]) != (width, height)
                        or abs(core.video_duration(picture) - expected) > max(.15, 2 / job["fps"])):
                    raise ValueError("Incomplete variant: " + style)
                checksum = core.sha(target)
                if not openings:
                    core.record_render(folder, target.relative_to(folder).as_posix(), fp,
                                       f"film-variants/{RECIPE_VERSION}/{style} from {item['sha256']}")
                versions.append({"style": style, "label": label, "file": target.name, "sha256": checksum,
                                 "duration": core.video_duration(picture), "source": item})
            if core.fingerprint(folder) != fp or any(core.sha(core.local(folder, i["asset"])) != i["sha256"] for i in sources):
                raise ValueError("Sources changed during review render")
            versions.sort(key=lambda item: preference["style_order"].index(item["style"]))
            manifest = {"id": key, "job_id": job["id"], "profile": preference["profile"], "title": job["title"],
                        "kind": "openings" if openings else "films", "variants": versions}
            core.write(temp / "manifest.json", manifest)
            template = (core.ROOT / "templates/film-review.html").read_text(encoding="utf-8")
            page = template.replace("<!--TITLE-->", html.escape(job["title"])).replace(
                "/*FILMS*/", json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c"))
            (temp / "index.html").write_text(page, encoding="utf-8")
            try:
                temp.rename(dest)
            except OSError:
                if not (dest / "manifest.json").is_file():
                    raise
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    _, manifest = collection(folder, key)
    for variant in manifest["variants"]:
        if core.sha(core.local(dest, variant["file"])) != variant["sha256"]:
            raise ValueError("Gallery file changed; restore the original review or render with a new name")
    return {"gallery": (dest / "index.html").relative_to(folder).as_posix(), "collection": key,
            "films": [str((dest / v["file"]).relative_to(folder).as_posix()) for v in manifest["variants"]],
            "serve": ["python", "-S", "studio.py", "variants", "serve", str(folder), "--collection", key],
            "preferred_style": preference["style_order"][0], "reviewed": False}


def after_render(folder, result):
    if result.get("probe_passed", True):
        result["variants"] = render_set(folder, result["render"])
    return result
