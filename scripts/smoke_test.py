"""Generate synthetic test cards/audio, assemble and inspect real MP4 files. No API."""
import json
import subprocess
import sys
import uuid
from pathlib import Path

from assembly import assemble
import studio_core as core


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", *args], check=True, timeout=60)


def main():
    base = core.ROOT / "output/system" / ("smoke-" + uuid.uuid4().hex[:8])
    folder = core.create_job("SYNTHETIC TECHNICAL TEST", "editing", "16:9", 2, "pl", base)
    job = core.read(folder / "job.json")
    job.update(width=320, height=180, fps=12)
    core.write(folder / "job.json", job)
    brief = core.read(folder / "brief.json")
    brief["audio_required"] = True
    core.write(folder / "brief.json", brief)
    cards = []
    for color in ("navy", "orange"):
        path = base / (color + ".png")
        ffmpeg("-f", "lavfi", "-i", f"color={color}:s=320x180", "-frames:v", "1", str(path))
        cards.append(core.register_asset(folder, path, "synthetic lavfi", "own test fixture", "encoder test"))
    audio_ids = []
    for hz in (440, 220):
        path = base / f"tone-{hz}.wav"
        ffmpeg("-f", "lavfi", "-i", f"sine=frequency={hz}:duration=2:sample_rate=48000", str(path))
        audio_ids.append(core.register_asset(folder, path, "synthetic lavfi", "own test fixture", "audio mux test")["id"])
    clips = [{"asset_id": item["id"], "duration_sec": 1, "in_sec": 0, "fit": "contain"} for item in cards]
    results = []
    for mode, voice, music in (("voice", audio_ids[0], None), ("music", None, audio_ids[1]), ("ducked_mix", *audio_ids)):
        core.write(folder / "timeline.json", {"clips": clips, "audio": {"voice": voice, "music": music, "music_gain": 0.12}})
        render = assemble(folder)
        report = core.probe_job(folder, render.relative_to(folder).as_posix())
        if not report["passed"]:
            raise RuntimeError(report["failures"])
        results.append({"mode": mode, "render": str(render), "passed": report["passed"],
                        "dimensions": [report["width"], report["height"]], "fps": report["fps"],
                        "duration_sec": report["duration_sec"], "audio_streams": report["audio_streams"]})
    sheet = core.contact_sheet(folder, render.relative_to(folder).as_posix())
    # Verify editing keeps dialogue from a supplied video by default.
    video_asset = core.register_asset(folder, render, "synthetic rendered fixture", "own test fixture", "keep original clip audio")
    core.write(folder / "timeline.json", {"clips": [{"asset_id": video_asset["id"], "duration_sec": 2, "in_sec": 0, "fit": "contain", "keep_audio": True}], "audio": {}})
    kept = assemble(folder)
    kept_report = core.probe_job(folder, kept.relative_to(folder).as_posix())
    if not kept_report["passed"] or not kept_report["audio_streams"]:
        raise RuntimeError("Original clip audio was lost")
    results.append({"mode": "original_clip_audio", "render": str(kept), "passed": True, "audio_streams": kept_report["audio_streams"]})
    core.write(folder / "timeline.json", {"clips": [
        {"asset_id": video_asset["id"], "duration_sec": 1, "fit": "contain"},
        {"asset_id": cards[0]["id"], "duration_sec": 1, "fit": "contain"}],
        "audio": {"music": audio_ids[1], "music_gain": 0.1}})
    mixed = assemble(folder)
    mixed_report = core.probe_job(folder, mixed.relative_to(folder).as_posix())
    if not mixed_report["passed"]:
        raise RuntimeError(mixed_report["failures"])
    results.append({"mode": "clip_audio_plus_music_and_still", "render": str(mixed), "passed": True, "audio_streams": mixed_report["audio_streams"]})
    # Deliberately keep intake/review pending: this is a technical fixture, not a film approved by a user.
    try:
        core.package_job(folder)
        raise RuntimeError("An unreviewed test was incorrectly accepted")
    except ValueError:
        pass
    payload = {"synthetic_only": True, "paid_calls": 0, "results": results,
               "contact_sheet": str(sheet), "unreviewed_packaging_rejected": True, "job": str(folder)}
    core.write(core.ROOT / "output/system/smoke-latest.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
