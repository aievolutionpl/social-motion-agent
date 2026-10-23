"""Katalog efektów dźwiękowych z folderu SOUND EFFECTS: pomiar, klasyfikacja, indeks i wyszukiwanie.

Pliki audio są tylko czytane. Zapisujemy wyłącznie SOUND EFFECTS/index.json i SOUND EFFECTS/INDEX.md.
Klasyfikacja wynika z nazw plików i pomiarów (czas, szczyt, średnia głośność); nikt tego nie odsłuchał,
więc kategorie są podpowiedzią, a przed użyciem w filmie dźwięk trzeba usłyszeć w miksie.

    python -S scripts/sfx_catalog.py build     # pomiar i zapis indeksu
    python -S scripts/sfx_catalog.py check     # czy indeks zna wszystkie pliki i żaden nie zniknął
    python -S scripts/sfx_catalog.py find whoosh --category transition
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "SOUND EFFECTS"
INDEX = FOLDER / "index.json"
AUDIO = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aac"}
GAIN_CAP = 0.5           # decyzja właściciela: efekty nigdy na 100%, najwyżej połowa głośności
# Pierwsza pasująca reguła wyznacza kategorię główną; pozostałe dopasowania stają się tagami.
RULES = [
    ("riser", r"riser|rise_|dsgnrise|rising|build.?up", "narastanie napięcia przed uderzeniem, hookiem lub cięciem"),
    ("impact", r"impact|impt_|bass drop|punch|boom|hit\b|stab|explosion|rifle|cinematic impact|echo impact", "uderzenie na akcent, cięcie, pojawienie się tytułu"),
    ("transition", r"whoosh|woosh|swoosh|swish|swipe|zoom by|whip|cool whip|cloud sweep|whsh_|dsgnwhsh|power down|delay sw|delay wo|space woosh|speed", "ruch kamery, przejście sceny, wjazd elementu"),
    ("camera", r"camera|shutter|capture", "zdjęcie, zrzut, flash, moment uchwycenia"),
    ("ui", r"keyget|heartget|click|ding|pop|notification|iphone|line break|download|network connect|erased data|digital count|ticking|tick|chaching|switch", "interfejs: kliknięcie, powiadomienie, potwierdzenie, licznik"),
    ("typing", r"keyboard|typing|mac typing|\bkey\b", "pisanie, wpisywanie komendy, terminal"),
    ("glitch-tech", r"glitch|terminal|reboot|restart|noise|radio snow|portal|teleport|sci-fi|digital|rewind|reverse|static|charging", "awaria, hologram, teleport, motyw techniczny"),
    ("ambience", r"rain|wind\b|ice crack|liquid|sewer", "tło i atmosfera, tylko cicho pod spodem"),
    ("meme", r"fart|kids|awww|suspense|meme|yeyy", "żart i komedia; tylko gdy ton filmu na to pozwala"),
    ("foley", r"glass|egg|paper|plastic|door|gear|sword|clock|heartbeat|crunch|crumble", "dźwięki przedmiotów: szkło, papier, drzwi, mechanizm"),
]
BASE_GAIN = {"riser": 0.35, "impact": 0.35, "transition": 0.4, "camera": 0.45, "typing": 0.35, "ui": 0.4,
             "glitch-tech": 0.4, "ambience": 0.2, "meme": 0.4, "foley": 0.4, "other": 0.4}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def sound_id(path: Path) -> str:
    parts = [p for p in re.split(r"_", path.stem) if p]
    if len(parts) >= 2:                                    # paczki: PREFIKS_Opis dźwięku_Autor_Kolekcja
        return slug(parts[0] + " " + " ".join(re.split(r"[ ,]+", parts[1])[:3]))
    return slug(path.stem)[:48]


def classify(name: str) -> tuple[str, list[str]]:
    hits = [(cat, why) for cat, pattern, why in RULES if re.search(pattern, name.casefold())]
    if not hits:
        return "other", []
    return hits[0][0], [c for c, _ in hits[1:]]


def run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def measure(path: Path) -> dict:
    probe = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,channels:format=duration,bit_rate",
                 "-of", "json", str(path)])
    info = json.loads(probe.stdout or "{}")
    stream = (info.get("streams") or [{}])[0]
    fmt = info.get("format", {})
    vol = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"])
    mean = re.search(r"mean_volume:\s*(-?[\d.]+) dB", vol.stderr)
    peak = re.search(r"max_volume:\s*(-?[\d.]+) dB", vol.stderr)
    return {"duration_sec": round(float(fmt.get("duration", 0) or 0), 2), "codec": stream.get("codec_name"),
            "sample_rate": int(stream.get("sample_rate", 0) or 0), "channels": stream.get("channels"),
            "mean_db": float(mean.group(1)) if mean else None, "peak_db": float(peak.group(1)) if peak else None}


def entry(path: Path) -> dict:
    data = measure(path)
    category, tags = classify(path.name)
    gain = BASE_GAIN[category]
    if data["peak_db"] is not None and data["peak_db"] > -1 and (data["mean_db"] or -99) > -14:
        gain = round(gain * 0.85, 2)       # głośny, gęsty materiał: niżej niż domyślnie
    notes = []
    if data["duration_sec"] > 8:
        notes.append("długi: przytnij parametrem duration albo użyj jako tło")
    if data["peak_db"] is not None and data["peak_db"] < -20:
        notes.append("cichy materiał: możliwe, że potrzebuje wyższego gain (nadal najwyżej 0.5)")
    return {"id": sound_id(path), "file": path.name, "category": category, "tags": tags, **data,
            "default_gain": min(gain, GAIN_CAP), "notes": notes}


def build() -> dict:
    files = sorted(p for p in FOLDER.iterdir() if p.is_file() and p.suffix.lower() in AUDIO)
    with ThreadPoolExecutor(max_workers=6) as pool:
        entries = list(pool.map(entry, files))
    seen: dict[str, int] = {}
    for item in entries:                                   # unikalne id
        n = seen.get(item["id"], 0)
        seen[item["id"]] = n + 1
        if n:
            item["id"] = f"{item['id']}-{n + 1}"
    by_stem: dict[str, list[dict]] = {}
    for item in entries:
        by_stem.setdefault(Path(item["file"]).stem.casefold(), []).append(item)
    for group in by_stem.values():                         # ta sama nazwa w wav i mp3
        if len(group) > 1:
            best = next((g for g in group if g["file"].lower().endswith(".wav")), group[0])
            for g in group:
                if g is not best:
                    g["duplicate_of"] = best["id"]
    data = {"generated_at": datetime.now(timezone.utc).isoformat(), "folder": FOLDER.name, "gain_cap": GAIN_CAP,
            "count": len(entries), "categories": {c: why for c, _, why in RULES}, "sounds": entries}
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FOLDER / "INDEX.md").write_text(render_markdown(data), encoding="utf-8")
    return data


def render_markdown(data: dict) -> str:
    lines = ["# Indeks efektów dźwiękowych", "",
             f"Generowany przez `scripts/sfx_catalog.py build` ({data['count']} plików). Nie edytuj ręcznie. "
             "Kategorie wynikają z nazw plików i pomiarów, nie z odsłuchu. Zasady użycia: [README.md](README.md).", "",
             "Kolumny: id (do `sfx:file=ID`), czas w sekundach, szczyt i średnia w dB, domyślny gain (0 do 1, nigdy powyżej 0.5).", ""]
    for cat, why in {**data["categories"], "other": "niesklasyfikowane po nazwie"}.items():
        items = [s for s in data["sounds"] if s["category"] == cat]
        if not items:
            continue
        lines += [f"## {cat} ({len(items)})", "", why.capitalize() + ".", "",
                  "| id | plik | s | szczyt | średnia | gain | uwagi |", "|---|---|---|---|---|---|---|"]
        for s in sorted(items, key=lambda x: x["id"]):
            note = "; ".join(s["notes"] + ([f"duplikat {s['duplicate_of']}"] if s.get("duplicate_of") else []))
            lines.append(f"| `{s['id']}` | {s['file']} | {s['duration_sec']} | {s['peak_db']} | {s['mean_db']} | {s['default_gain']} | {note} |")
        lines.append("")
    return "\n".join(lines)


def load() -> dict:
    if not INDEX.is_file():
        raise ValueError("Brak SOUND EFFECTS/index.json; uruchom: python -S scripts/sfx_catalog.py build")
    return json.loads(INDEX.read_text(encoding="utf-8"))


def check() -> list[str]:
    data = load()
    indexed = {s["file"] for s in data["sounds"]}
    present = {p.name for p in FOLDER.iterdir() if p.is_file() and p.suffix.lower() in AUDIO}
    return [f"Nowy plik bez wpisu: {n}" for n in sorted(present - indexed)] + [f"Wpis bez pliku: {n}" for n in sorted(indexed - present)]


def find(query: str = "", category: str | None = None, max_duration: float | None = None, limit: int = 15) -> dict:
    sounds = load()["sounds"]
    tokens = query.casefold().split()
    found = []
    for s in sounds:
        if s.get("duplicate_of"):
            continue
        if category and category not in [s["category"], *s["tags"]]:
            continue
        if max_duration is not None and s["duration_sec"] > max_duration:
            continue
        hay = f"{s['id']} {s['file']} {s['category']} {' '.join(s['tags'])}".casefold()
        if all(t in hay for t in tokens):
            found.append(s)
    return {"total_matches": len(found), "gain_cap": GAIN_CAP, "sounds": found[:max(1, min(limit, 100))]}


def resolve(name_or_path: str) -> tuple[Path, float]:
    """Zwraca (ścieżka pliku, domyślny gain). Przyjmuje id, nazwę pliku albo istniejącą ścieżkę."""
    direct = Path(name_or_path)
    if direct.is_file():
        return direct.resolve(), 0.4
    sounds = load()["sounds"]
    key = name_or_path.casefold()
    match = next((s for s in sounds if s["id"] == key), None) or next((s for s in sounds if s["file"].casefold() == key), None)
    if not match:
        near = [s["id"] for s in sounds if key in s["id"]][:6]
        raise ValueError(f"Nie ma dźwięku {name_or_path!r}" + (f"; podobne: {', '.join(near)}" if near else "; użyj studio.py sfx find"))
    target = match.get("duplicate_of") and next(s for s in sounds if s["id"] == match["duplicate_of"]) or match
    return FOLDER / target["file"], target["default_gain"]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("check")
    p = sub.add_parser("find")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--category")
    p.add_argument("--max-duration", type=float)
    p.add_argument("--limit", type=int, default=15)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            data = build()
            counts = {c: sum(1 for s in data["sounds"] if s["category"] == c) for c in sorted({s["category"] for s in data["sounds"]})}
            print(json.dumps({"indexed": data["count"], "by_category": counts}, ensure_ascii=False, indent=2))
        elif args.command == "check":
            problems = check()
            print(json.dumps({"passed": not problems, "problems": problems}, ensure_ascii=False, indent=2))
            return int(bool(problems))
        else:
            print(json.dumps(find(args.query, args.category, args.max_duration, args.limit), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
