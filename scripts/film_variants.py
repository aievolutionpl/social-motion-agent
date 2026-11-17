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

RECIPE_VERSION = 3


def video_filter(style, width, height, fps, frames, treatment):
    fit = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
           f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")
    if style == "kinetic":
        # Keep the whole composition legible. A second panel tracks a detail
        # from the same shot, so both views and the original audio stay in sync.
        wide = width >= height
        span = width if wide else height
        strip = max(2, int(span * .22) // 2 * 2)
        if span > strip:
            lead_w, lead_h = (width - strip, height) if wide else (width, height - strip)
            detail_w, detail_h = (strip, height) if wide else (width, strip)
            zoom, period = {"gentle": (.04, 2.5), "energetic": (.23, 1.0)}.get(treatment, (.14, 1.5))
            rule = max(1, round(min(width, height) * .003))
            divider = f"w={rule}:h=ih" if wide else f"w=iw:h={rule}"
            stack = "hstack" if wide else "vstack"
            fit = (f"split=2[whole][detail];[whole]scale={lead_w}:{lead_h}:force_original_aspect_ratio=decrease,"
                   f"pad={lead_w}:{lead_h}:(ow-iw)/2:(oh-ih)/2:color=0x101419,setsar=1,fps={fps}[lead];"
                   f"[detail]scale={detail_w}:{detail_h}:force_original_aspect_ratio=increase,"
                   f"crop={detail_w}:{detail_h}:(iw-ow)*0.35:(ih-oh)*0.43,setsar=1,fps={fps},"
                   f"zoompan=z='1+{zoom}*pow(sin(on*PI/({fps}*{period})),2)':"
                   f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={detail_w}x{detail_h}:fps={fps},"
                   f"eq=saturation=.28:contrast=1.10,drawbox=x=0:y=0:{divider}:color=white@0.55:t=fill[inset];"
                   f"[lead][inset]{stack}=inputs=2:shortest=1,setsar=1")
    elif style == "studio":
        fraction = {"large": .92, "small": .70}.get(treatment, .82)
        card_w, card_h = [max(2, int(size * fraction) // 2 * 2) for size in (width, height)]
        fit = (f"split=2[plate][subject];[plate]scale={width}:{height}:force_original_aspect_ratio=increase,"
               f"crop={width}:{height},gblur=sigma=18,eq=brightness=-0.12[matte];"
               f"[subject]scale={card_w}:{card_h}:force_original_aspect_ratio=decrease,"
               f"pad={card_w}:{card_h}:(ow-iw)/2:(oh-ih)/2[card];"
               f"[matte][card]overlay=x='(W-w)/2':y='(H-h)/2+H*.018*sin(t*1.4)',setsar=1,fps={fps}")
    # Some FFmpeg versions drop the last frame when fps receives EOF. Hold that
    # frame if needed, then trim to the actual source frame count.
    return "[0:v:0]" + fit + f",tpad=stop_mode=clone:stop=2,trim=end_frame={frames},format=yuv420p[v]"


def encode(source, target, style, width, height, fps, duration, start, treatment):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-filter_complex_threads", "1"]
    if start is not None:
        args += ["-ss", str(start)]
    args += ["-i", str(source)]
    if start is not None:
        args += ["-t", str(duration)]
    frames = max(1, round(duration * fps))
    args += ["-filter_complex", video_filter(style, width, height, fps, frames, treatment), "-map", "[v]", "-map", "0:a?",
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
    preference = summary(folder.parent, job.get("style_profile", "local"), exclude_job=job["id"])
    fp = core.fingerprint(folder)
    if openings:
        sources = opening_sources(folder, query)
        factor = min(1, 540 / max(job["width"], job["height"]))
        width, height = [max(2, int(n * factor) // 2 * 2) for n in (job["width"], job["height"])]
    else:
        if master is None:
            master = job.get("render")
            parts = Path(master).parts if master else ()
            if len(parts) == 3 and parts[0] == "previews" and parts[1].startswith("films-"):
                _, previous = collection(folder, parts[1])
                selected = next((v for v in previous["variants"] if v["file"] == parts[2]), None)
                if selected:
                    master = selected["source"]["asset"]
        if not master:
            raise ValueError("Render a master before building the three films")
        src = core.local(folder, master)
        if src.suffix.lower() != ".mp4":
            raise ValueError("Expected an MP4 master")
        receipt = core.render_provenance(folder, master)
        checksum = core.sha(src)
        if receipt.get("fingerprint") != fp or receipt.get("render_sha256") != checksum:
            raise ValueError("Master no longer matches its render receipt")
        picture = next(s for s in probe(src)["streams"] if s["codec_type"] == "video")
        duration = core.video_duration(picture)
        if not duration or abs(duration - job["duration_sec"]) > max(.15, 2 / job["fps"]):
            raise ValueError("Master picture duration does not match the brief")
        sources = [{"asset": src.relative_to(folder).as_posix(), "sha256": checksum, "duration": duration}] * 3
        width, height = job["width"], job["height"]
    key_data = [RECIPE_VERSION, fp, sources, preference["profile"], preference["treatments"], width, height]
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
                treatment = preference["treatments"].get(style, "default")
                if style == "editorial" and not openings:
                    shutil.copyfile(path, target)
                else:
                    encode(path, target, style, width, height, job["fps"], item["duration"], item.get("start"), treatment)
                info = probe(target)
                picture = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
                expected = item["duration"]
                if ((picture["width"], picture["height"]) != (width, height)
                        or abs(core.video_duration(picture) - expected) > .51 / job["fps"] + 1e-5):
                    raise ValueError("Incomplete variant: " + style)
                checksum = core.sha(target)
                if not openings:
                    core.record_render(folder, target.relative_to(folder).as_posix(), fp,
                                       f"film-variants/{RECIPE_VERSION}/{style} from {item['sha256']}")
                versions.append({"style": style, "label": label, "file": target.name, "sha256": checksum,
                                 "duration": core.video_duration(picture), "source": item, "treatment": treatment})
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
            "preferred_style": manifest["variants"][0]["style"], "reviewed": False}


def after_render(folder, result):
    if result.get("probe_passed", True):
        result["variants"] = render_set(folder, result["render"])
    return result
