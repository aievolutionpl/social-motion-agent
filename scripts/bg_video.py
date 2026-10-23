"""Tło z obrazu jako klip wideo: płynny najazd (push), dryf (drift) albo bez ruchu, w formacie produkcji.

Obraz jest przycinany do kadru (cover), próbkowany 2x przed zoompan, żeby ruch nie drżał, a najazd
ma ease in/out. Nie używa sieci. Wymaga ffmpeg w PATH.

    python -S scripts/bg_video.py assets/backgrounds/bg-02-navy-glow.webp out.mp4 --duration 8 --format 9:16 --motion push
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

FORMATS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080)}


def build_command(image: Path, out: Path, duration: float, fmt: str, motion: str, amount: float, fps: int) -> list[str]:
    width, height = FORMATS[fmt]
    frames = max(2, int(round(duration * fps)))
    big_w, big_h = width * 2, height * 2
    base = (f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase:flags=lanczos,crop={big_w}:{big_h},setsar=1")
    ease = f"(0.5-0.5*cos(PI*on/{frames}))"
    if motion == "push":
        zoom, x, y = f"1+{amount}*{ease}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "drift":
        zoom, x, y = f"1+{amount}", f"(iw-iw/zoom)*{ease}", "(ih-ih/zoom)/2"
    else:
        zoom, x, y = "1", "0", "0"
    chain = f"{base},zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s={width}x{height}:fps={fps},format=yuv420p"
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-loop", "1", "-framerate", str(fps),
            "-i", str(image), "-vf", chain, "-frames:v", str(frames), "-c:v", "libx264", "-crf", "16", "-preset", "medium",
            "-movflags", "+faststart", str(out)]


def render(image: Path, out: Path, duration: float, fmt: str = "9:16", motion: str = "push", amount: float = 0.12, fps: int = 30) -> dict:
    if not image.is_file():
        raise ValueError(f"Brak obrazu: {image}")
    if out.exists():
        raise ValueError(f"Wynik już istnieje (każdy render ma nową nazwę): {out}")
    if not 0.5 <= duration <= 120:
        raise ValueError("duration musi być w zakresie 0.5 do 120 s")
    if not 0 <= amount <= 0.5:
        raise ValueError("amount (siła najazdu lub dryfu) musi być w zakresie 0 do 0.5")
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(build_command(image, out, duration, fmt, motion, amount, fps), capture_output=True, text=True, timeout=900)
    if result.returncode:
        out.unlink(missing_ok=True)
        raise ValueError("FFmpeg: " + result.stderr[-1500:])
    return {"output": str(out), "format": fmt, "size": list(FORMATS[fmt]), "duration_sec": duration, "motion": motion, "fps": fps}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--format", choices=FORMATS, default="9:16")
    parser.add_argument("--motion", choices=("push", "drift", "none"), default="push")
    parser.add_argument("--amount", type=float, default=0.12)
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args(argv)
    try:
        print(render(args.image, args.output, args.duration, args.format, args.motion, args.amount, args.fps))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
