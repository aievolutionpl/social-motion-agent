"""Efekty wideo jako presety FFmpeg: jedna specyfikacja JSON, jeden render.

Czasy efektów (start, end) liczone są w osi czasu WYJŚCIOWEJ, czyli po speed_ramp.
Nie używa sieci ani zewnętrznych bibliotek; wymaga ffmpeg i ffprobe w PATH.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

GRADES = {
    "punchy": "eq=contrast=1.12:saturation=1.25:gamma=0.97",
    "warm": "eq=saturation=1.1,colorbalance=rs=0.06:gs=0.01:bs=-0.06:rh=0.05:bh=-0.04",
    "cool": "eq=saturation=1.05,colorbalance=rs=-0.05:bs=0.07:rh=-0.03:bh=0.05",
    "cinematic": "eq=contrast=1.1:saturation=0.95:gamma=0.95,colorbalance=rs=-0.04:bs=0.05:rh=0.07:bh=-0.05",
    "mono": "hue=s=0,eq=contrast=1.15",
}
# Parametry i wartości domyślne każdego efektu; None oznacza parametr wymagany.
EFFECTS = {
    "punch_in": {"start": None, "end": None, "zoom": 1.2, "ramp": 0.25, "x": 0.5, "y": 0.5},
    "shake": {"start": None, "end": None, "amount": 0.015, "speed": 40.0},
    "flash": {"start": None, "alpha": 0.9},
    "glitch": {"start": None, "end": None, "shift": 10},
    "grade": {"preset": "punchy"},
    "vignette": {"strength": 0.6},
    "fade": {"in": 0.0, "out": 0.0},
    "speed_ramp": {"start": None, "end": None, "factor": 0.5},
    # sfx: file = id z SOUND EFFECTS/index.json, nazwa pliku albo ścieżka; gain 0 = domyślny z katalogu; duration 0 = cały plik
    "sfx": {"file": None, "start": None, "gain": 0.0, "duration": 0.0, "fade": 0.04},
}
STRING_KEYS = ("type", "preset", "file")
SFX_GAIN_CAP = 0.5       # decyzja właściciela: efekty dźwiękowe nigdy na 100%


class FxError(ValueError):
    pass


def num(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise FxError(f"{name}: oczekiwano liczby, otrzymano {value!r}") from None
    if not math.isfinite(number):
        raise FxError(f"{name}: wartość musi być skończona")
    return number


def normalize(effect: dict, duration: float) -> dict:
    kind = effect.get("type")
    if kind not in EFFECTS:
        raise FxError(f"Nieznany efekt {kind!r}. Dostępne: {', '.join(EFFECTS)}")
    unknown = set(effect) - set(EFFECTS[kind]) - {"type"}
    if unknown:
        raise FxError(f"{kind}: nieznane parametry {sorted(unknown)}")
    item = {**EFFECTS[kind], **{k: v for k, v in effect.items() if k != "type"}, "type": kind}
    for key, value in item.items():
        if key in STRING_KEYS:
            continue
        if value is None:
            raise FxError(f"{kind}: wymagany parametr {key}")
        item[key] = num(value, f"{kind}.{key}")
    if kind == "grade" and item["preset"] not in GRADES:
        raise FxError(f"grade: nieznany preset, dostępne: {', '.join(GRADES)}")
    if "start" in item and not 0 <= item["start"] < duration:
        raise FxError(f"{kind}: start poza filmem (0 do {duration:.2f} s)")
    if "end" in item and not item["start"] < item["end"] <= duration + 1e-6:
        raise FxError(f"{kind}: end musi być większy od start i nie większy niż długość")
    if kind == "punch_in" and not 1.0 < item["zoom"] <= 3.0:
        raise FxError("punch_in.zoom musi być w zakresie (1, 3]")
    if kind == "speed_ramp" and not 0.25 <= item["factor"] <= 4.0:
        raise FxError("speed_ramp.factor musi być w zakresie 0.25 do 4")
    if kind == "vignette" and not 0 < item["strength"] <= 1:
        raise FxError("vignette.strength musi być w zakresie (0, 1]")
    if kind == "flash" and not 0 < item["alpha"] <= 1:
        raise FxError("flash.alpha musi być w zakresie (0, 1]")
    if kind == "sfx":
        if not isinstance(item["file"], str) or not item["file"].strip():
            raise FxError("sfx: wymagany parametr file (id dźwięku, nazwa pliku albo ścieżka)")
        if not 0 <= item["gain"] <= SFX_GAIN_CAP:
            raise FxError(f"sfx.gain musi być w zakresie 0 do {SFX_GAIN_CAP} (0 = domyślny z katalogu); efekty nigdy na 100%")
        if item["duration"] < 0 or item["fade"] < 0:
            raise FxError("sfx.duration i sfx.fade nie mogą być ujemne")
    return item


def audio_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, timeout=60)
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise FxError(f"Nie da się odczytać długości dźwięku: {path.name}") from None


def sfx_graph(items: list[dict], out_duration: float, base_label: str | None) -> tuple[list[str], list[str]]:
    """Zwraca (dodatkowe wejścia -i, części filter_complex) miksujące efekty do etykiety [aout]."""
    from sfx_catalog import resolve
    inputs, parts, labels = [], [], []
    for n, item in enumerate(items):
        try:
            path, default = resolve(item["file"])
        except ValueError as exc:
            raise FxError(str(exc)) from exc
        gain = item["gain"] or default
        length = min(item["duration"] or audio_duration(path), audio_duration(path))
        fade = min(item["fade"], length / 2)
        delay = int(round(item["start"] * 1000))
        inputs += ["-i", str(path)]
        parts.append(f"[{n + 1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{length:.3f},asetpts=PTS-STARTPTS,"
                     f"volume={gain:.3f},afade=t=in:d=0.005,afade=t=out:st={max(0.0, length - fade):.3f}:d={max(fade, 0.001):.3f},"
                     f"adelay={delay}|{delay}[sx{n}]")
        labels.append(f"[sx{n}]")
    if base_label:
        parts.append(f"{base_label}aresample=48000,aformat=channel_layouts=stereo[base]")
    else:
        parts.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{out_duration:.3f}[base]")
    parts.append(f"[base]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first:dropout_transition=0,"
                 "alimiter=limit=0.95[aout]")
    return inputs, parts


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, timeout=60)
    if out.returncode:
        raise FxError("ffprobe nie odczytał pliku: " + out.stderr.strip()[-300:])
    info = json.loads(out.stdout)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    if not video:
        raise FxError("Brak ścieżki wideo")
    top, bottom = video.get("avg_frame_rate", "0/1").split("/")
    return {"width": int(video["width"]), "height": int(video["height"]),
            "fps": float(top) / float(bottom) if float(bottom) else 30.0,
            "duration": float(info["format"]["duration"]),
            "has_audio": any(s.get("codec_type") == "audio" for s in info["streams"])}


def ramp_segments(ramps: list[dict], duration: float) -> list[tuple[float, float, float]]:
    """Podział osi źródłowej na (od, do, współczynnik); zakresy nie mogą się nakładać."""
    segments, cursor = [], 0.0
    for ramp in sorted(ramps, key=lambda r: r["start"]):
        if ramp["start"] < cursor - 1e-9:
            raise FxError("speed_ramp: zakresy nie mogą się nakładać")
        if ramp["start"] > cursor:
            segments.append((cursor, ramp["start"], 1.0))
        segments.append((ramp["start"], ramp["end"], ramp["factor"]))
        cursor = ramp["end"]
    if cursor < duration:
        segments.append((cursor, duration, 1.0))
    return segments


def window(item: dict) -> str:
    return f"between(t,{item['start']:.4f},{item['end']:.4f})"


def video_filters(items: list[dict], meta: dict, out_duration: float) -> list[str]:
    width, height = meta["width"], meta["height"]
    chain = []
    for item in items:
        kind = item["type"]
        if kind == "grade":
            chain.append(GRADES[item["preset"]])
        elif kind == "vignette":
            chain.append(f"vignette=angle={0.3 + item['strength'] * 0.9:.3f}:mode=backward")
        elif kind == "punch_in":
            a, b, r, z = item["start"], item["end"], max(item["ramp"], 0.04), item["zoom"]
            progress = f"max(0,min(1,min((t-{a:.4f})/{r:.4f},({b:.4f}-t)/{r:.4f})))"
            factor = f"(1+({z - 1:.4f})*{progress})"
            cx, cy = item["x"], item["y"]
            chain.append(f"scale=w='iw*{factor}':h='ih*{factor}':eval=frame")
            chain.append(f"crop={width}:{height}:x='max(0,min(iw-{width},iw*{cx:.4f}-{width}*{cx:.4f}))'"
                         f":y='max(0,min(ih-{height},ih*{cy:.4f}-{height}*{cy:.4f}))'")
        elif kind == "shake":
            amp = item["amount"] * min(width, height)
            gate = window(item)
            chain.append(f"scale={int(width * 1.08) // 2 * 2}:{int(height * 1.08) // 2 * 2}")
            chain.append(f"crop={width}:{height}:x='(iw-ow)/2+if({gate},{amp:.2f}*sin(t*{item['speed']:.2f}),0)'"
                         f":y='(ih-oh)/2+if({gate},{amp:.2f}*cos(t*{item['speed'] * 0.83:.2f}),0)'")
        elif kind == "glitch":
            shift = int(item["shift"])
            chain.append(f"rgbashift=rh=-{shift}:bh={shift}:gv={shift // 2}:enable='{window(item)}'")
        elif kind == "flash":
            t0 = item["start"]
            for offset, scale in ((0.0, 1.0), (0.04, 0.55), (0.08, 0.25)):
                chain.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@{item['alpha'] * scale:.3f}:t=fill:"
                             f"enable='between(t,{t0 + offset:.4f},{t0 + offset + 0.04:.4f})'")
        elif kind == "fade":
            if item["in"] > 0:
                chain.append(f"fade=t=in:st=0:d={item['in']:.3f}")
            if item["out"] > 0:
                chain.append(f"fade=t=out:st={max(0.0, out_duration - item['out']):.4f}:d={item['out']:.3f}")
    return chain


def build_command(src: Path, out: Path, effects: list[dict], meta: dict) -> tuple[list[str], float]:
    items = [normalize(e, meta["duration"]) for e in effects]
    ramps = [i for i in items if i["type"] == "speed_ramp"]
    others = [i for i in items if i["type"] != "speed_ramp"]
    segments = ramp_segments(ramps, meta["duration"]) if ramps else []
    out_duration = sum((b - a) / f for a, b, f in segments) if segments else meta["duration"]
    for item in others:
        if "end" in item and item["end"] > out_duration + 1e-6:
            raise FxError(f"{item['type']}: end {item['end']:.2f} s przekracza długość wyniku {out_duration:.2f} s")
    chain = video_filters(others, meta, out_duration)
    parts, audio = [], meta["has_audio"]
    if segments:
        for n, (a, b, f) in enumerate(segments):
            parts.append(f"[0:v]trim={a:.4f}:{b:.4f},setpts=(PTS-STARTPTS)/{f:.4f}[v{n}]")
            if audio:
                parts.append(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,atempo={f:.4f}[a{n}]")
        joined = "".join(f"[v{n}]" + (f"[a{n}]" if audio else "") for n in range(len(segments)))
        parts.append(f"{joined}concat=n={len(segments)}:v=1:a={1 if audio else 0}[vc]" + ("[ac]" if audio else ""))
        head = "[vc]"
    else:
        head = "[0:v]"
    parts.append(head + (",".join(chain) if chain else "null") + "[vout]")
    sfx_items = [i for i in others if i["type"] == "sfx"]
    extra_inputs: list[str] = []
    if sfx_items:
        base = ("[ac]" if segments else "[0:a]") if audio else None
        extra_inputs, sfx_parts = sfx_graph(sfx_items, out_duration, base)
        parts += sfx_parts
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-i", str(src), *extra_inputs,
               "-filter_complex", ";".join(parts), "-map", "[vout]"]
    if sfx_items:
        command += ["-map", "[aout]"]
    elif audio:
        command += ["-map", "[ac]" if segments else "0:a:0"]
    command += ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-r", f"{meta['fps']:.3f}"]
    if audio or sfx_items:
        command += ["-c:a", "aac", "-b:a", "192k"]
    command += ["-movflags", "+faststart", str(out)]
    return command, out_duration


def apply(src: Path, out: Path, effects: list[dict]) -> dict:
    if not src.is_file():
        raise FxError(f"Brak pliku: {src}")
    if out.exists():
        raise FxError(f"Wynik już istnieje (każdy render ma nową nazwę): {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = probe(src)
    command, out_duration = build_command(src, out, effects, meta)
    result = subprocess.run(command, capture_output=True, text=True, timeout=3600)
    if result.returncode:
        out.unlink(missing_ok=True)
        raise FxError("FFmpeg: " + result.stderr[-2000:])
    return {"output": str(out), "expected_duration_sec": round(out_duration, 3),
            "effects": [e.get("type") for e in effects], "source": meta}


def parse_inline(text: str) -> dict:
    """'punch_in:start=1,end=2.2,zoom=1.3' -> słownik efektu."""
    kind, _, rest = text.partition(":")
    effect = {"type": kind}
    for pair in filter(None, rest.split(",")):
        key, sep, value = pair.partition("=")
        if not sep:
            raise FxError(f"Zły zapis parametru {pair!r}; użyj klucz=wartość")
        effect[key.strip()] = value.strip()
    return effect


def load_spec(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    effects = data["effects"] if isinstance(data, dict) else data
    if not isinstance(effects, list):
        raise FxError("Specyfikacja ma zawierać listę 'effects'")
    return effects


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="Pokaż efekty i ich parametry domyślne")
    p = sub.add_parser("apply", help="Nałóż efekty na wideo")
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--spec", type=Path, help="JSON z listą efektów")
    p.add_argument("--effect", action="append", default=[], help="np. punch_in:start=1,end=2.2,zoom=1.3")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            print(json.dumps({"effects": EFFECTS, "grade_presets": list(GRADES)}, ensure_ascii=False, indent=2))
            return 0
        effects = (load_spec(args.spec) if args.spec else []) + [parse_inline(e) for e in args.effect]
        if not effects:
            raise FxError("Podaj --spec lub co najmniej jeden --effect")
        print(json.dumps(apply(args.source, args.output, effects), ensure_ascii=False, indent=2))
        return 0
    except (FxError, OSError, KeyError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
