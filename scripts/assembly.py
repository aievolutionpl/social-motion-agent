"""Deterministic local assembly of registered stills/footage and optional audio."""
from __future__ import annotations

import math
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from studio_core import local, now, read, write


def run(args: list[str], log: Path) -> None:
    result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", *args],
                            capture_output=True, text=True, timeout=1800)
    with log.open("a", encoding="utf-8") as stream:
        stream.write(result.stderr + "\n")
    if result.returncode:
        raise ValueError("FFmpeg: " + result.stderr[-2500:])


def assemble(folder: Path) -> Path:
    job, timeline, manifest = (read(folder / name) for name in ("job.json", "timeline.json", "assets.json"))
    assets = {item["id"]: local(folder, item["path"]) for item in manifest["items"]}
    clips = timeline.get("clips", [])
    duration = sum(float(clip.get("duration_sec", 0)) for clip in clips)
    if not clips or not math.isfinite(duration) or abs(duration - job["duration_sec"]) > 1 / job["fps"]:
        raise ValueError("Timeline musi zawierać klipy o łącznym czasie zgodnym z job.duration_sec")
    width, height, fps = job["width"], job["height"], job["fps"]
    if not all(isinstance(x, int) and x > 0 for x in (width, height, fps)) or width % 2 or height % 2:
        raise ValueError("Wymiary muszą być dodatnie i parzyste; fps dodatni całkowity")
    for clip in clips:
        seconds, start = float(clip.get("duration_sec", 0)), float(clip.get("in_sec", 0))
        if clip.get("asset_id") not in assets or clip.get("fit") not in ("contain", "cover"):
            raise ValueError("Każdy klip wymaga zarejestrowanego asset_id i świadomego wyboru fit: contain/cover")
        if not math.isfinite(seconds) or seconds <= 0 or not math.isfinite(start) or start < 0:
            raise ValueError("Nieprawidłowy czas klipu")
    audio = timeline.get("audio", {})
    for key in ("voice", "music"):
        if audio.get(key) and audio[key] not in assets:
            raise ValueError("Audio odwołuje się do nieznanego assetu: " + key)
    gain = float(audio.get("music_gain", 0.12))
    if not math.isfinite(gain) or not 0 <= gain <= 1:
        raise ValueError("music_gain musi być w zakresie 0–1")
    work = folder / "renders" / ("work-" + uuid.uuid4().hex[:10])
    work.mkdir(parents=True, exist_ok=False)
    log = work / "ffmpeg.log"
    clip_audio = []
    for clip in clips:
        source = assets[clip["asset_id"]]
        image = source.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp")
        if image or not clip.get("keep_audio", True):
            clip_audio.append(False)
        else:
            probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "json", str(source)], capture_output=True, text=True, check=True, timeout=60)
            clip_audio.append(bool(json.loads(probe.stdout).get("streams")))
    preserve_audio = any(clip_audio)
    for index, clip in enumerate(clips):
        source = assets[clip["asset_id"]]
        seconds = float(clip["duration_sec"])
        image = source.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp")
        inputs = ["-loop", "1", "-framerate", str(fps), "-i", str(source)] if image else ["-ss", str(clip.get("in_sec", 0)), "-i", str(source)]
        scale = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2" if clip["fit"] == "contain" else
                 f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}")
        sound = ["-an"]
        if preserve_audio:
            if clip_audio[index]:
                sound = ["-map", "0:v:0", "-map", "0:a:0", "-af", "aresample=48000,apad", "-ac", "2", "-c:a", "aac"]
            else:
                inputs += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
                sound = ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac"]
        run([*inputs, "-t", str(seconds), "-vf", f"{scale},fps={fps},setsar=1,format=yuv420p",
             *sound, "-c:v", "libx264", "-threads", "2", "-crf", "20", "-preset", "fast",
             "-video_track_timescale", "90000", str(work / f"segment-{index:04d}.mp4")], log)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file 'segment-{i:04d}.mp4'\n" for i in range(len(clips))), encoding="utf-8")
    joined = work / "picture.mp4"
    run(["-f", "concat", "-safe", "1", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(joined)], log)
    target = folder / "renders" / ("assembly-" + uuid.uuid4().hex[:10] + ".mp4")
    voice, music = audio.get("voice"), audio.get("music")
    if voice or music:
        args = ["-i", str(joined)]
        filters = []
        if voice:
            args += ["-i", str(assets[voice])]
        if music:
            args += ["-stream_loop", "-1", "-i", str(assets[music])]
        if voice and music:
            filters += ["[1:a]aresample=48000,apad,asplit=2[vo][sc]",
                        f"[2:a]aresample=48000,volume={gain}[bg]",
                        "[bg][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=250[duck]",
                        "[vo][duck]amix=inputs=2:duration=longest:normalize=0[mix]"]
        else:
            volume = 1 if voice else gain
            filters += [f"[1:a]aresample=48000,volume={volume},apad[mix]"]
        if preserve_audio:
            filters = [value.replace("[mix]", "[overlay]") for value in filters]
            filters += ["[0:a][overlay]amix=inputs=2:duration=longest:normalize=0[mix]"]
        filters += ["[mix]loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
        run([*args, "-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-t", str(duration),
             "-movflags", "+faststart", str(target)], log)
    else:
        shutil.copy2(joined, target)
    job["render"] = target.relative_to(folder).as_posix()
    job["state"] = "rendered_unreviewed"
    job["history"].append({"at": now(), "event": "assembly_rendered", "path": job["render"], "log": log.relative_to(folder).as_posix()})
    write(folder / "job.json", job)
    return target
