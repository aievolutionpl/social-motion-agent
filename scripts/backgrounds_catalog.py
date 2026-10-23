"""Indeks teł z assets/backgrounds: pomiar jasności, zajętości i spokojnych stref na tekst.

Obrazy są tylko czytane. Opisy (nastrój, zastosowanie) napisane ręcznie po obejrzeniu obrazów w META;
liczby (jasność, nasycenie, zajętość, spokojne strefy) mierzy Pillow. Uruchom przez `python -I`
(potrzebny Pillow z site-packages):

    python -I scripts/backgrounds_catalog.py build
    python -I scripts/backgrounds_catalog.py check
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "assets/backgrounds"
INDEX = FOLDER / "index.json"
IMAGES = {".webp", ".png", ".jpg", ".jpeg"}
ROWS, COLS = ("top", "middle", "bottom"), ("left", "center", "right")
META = {
    "bg-01-silk-purple-orange.webp": ("Błyszczący jedwab: fiolet, magenta i pomarańcz na czerni, bardzo energiczny.",
        ["energia", "premium", "hook", "kolorowy"], "hook, tytuł otwierający, przebitka między scenami; tekst na pille lub panelu"),
    "bg-02-navy-glow.webp": ("Prawie pusty ciemny granat z miękką niebieską poświatą u góry. Najspokojniejsze tło.",
        ["spokojne", "neutralne", "tekst", "tech"], "domyślne tło pod napisy, liczby, wykresy i dłuższy tekst; każda marka"),
    "bg-03-amber-arc.webp": ("Prawie czerń z ciepłym bursztynowym łukiem światła w prawym dolnym rogu.",
        ["spokojne", "ciepłe", "premium", "kinowe"], "cytat, tytuł, lektor z jednym zdaniem; tekst w górnej i lewej części"),
    "bg-04-blue-wires-orange.webp": ("Granat z półprzezroczystymi falami niebieskimi i fioletowymi, kropkami i siatką; pomarańczowy akcent w rogu. Środek pusty.",
        ["tech", "AI", "spokojne", "wielowarstwowe"], "explainer AI i technologii, slajd z tekstem na środku, tło sceny z dashboardem"),
    "bg-05-gold-glow-silk.webp": ("Czerń ze złotą miękką poświatą na środku i cienkimi złotymi krzywymi.",
        ["luksus", "spokojne", "ciepłe", "premium"], "wynik, liczba lub hasło na środku, marki premium i finanse"),
    "bg-06-gold-ring.webp": ("Czerń ze złotymi koncentrycznymi pierścieniami i pustym kołem na środku.",
        ["luksus", "kadr", "logo", "premium"], "logo, liczba, portret lub ikona w pustym kole; reflektor na jedną rzecz"),
    "bg-07-neon-shard-burst.webp": ("Wybuch neonowych szklanych odłamków: niebieski, magenta, pomarańcz, rozchodzące się od środka. Bardzo gęste.",
        ["energia", "wybuch", "gęste", "hook"], "krótki hook, przejście, flash, akcent na uderzenie dźwiękowe; tekst tylko na panelu"),
    "bg-08-iridescent-glass-swirl.webp": ("Opalizujący szklany wir: cyjan, fiolet, pomarańcz. Nasycony i dynamiczny.",
        ["kolorowy", "płynne", "gęste", "kreatywne"], "tło przejścia, intro kreatywne i AI, krótki hook; tekst na pille"),
    "bg-09-blue-orange-glitch.webp": ("Czerń z niebieskimi i pomarańczowymi diagonalnymi odłamkami i pikselowym glitchem. Agresywne.",
        ["glitch", "cyber", "gęste", "kontrast"], "przejście glitch, cyberbezpieczeństwo, awaria, mocny hook; tekst na panelu"),
}


def measure(path: Path) -> dict:
    from PIL import Image, ImageFilter, ImageStat
    image = Image.open(path).convert("RGB")
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    sat = ImageStat.Stat(image.convert("HSV").split()[1]).mean[0] / 255
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0] / 255
    width, height = image.size
    cells = []
    for r, row in enumerate(ROWS):
        for c, col in enumerate(COLS):
            box = (c * width // 3, r * height // 3, (c + 1) * width // 3, (r + 1) * height // 3)
            s = ImageStat.Stat(gray.crop(box))
            cells.append({"zone": f"{row}-{col}", "mean": round(s.mean[0] / 255, 3), "std": round(s.stddev[0] / 255, 3)})
    calm = sorted(cells, key=lambda z: (z["std"], z["mean"]))[:3]
    busy = round(edges * 10, 3)
    return {"width": width, "height": height, "brightness": round(stat.mean[0] / 255, 3), "saturation": round(sat, 3),
            "busy": busy, "calm_zones": [z["zone"] for z in calm],
            "text": ("napis wprost na tle w spokojnych strefach" if busy < 0.1 and stat.mean[0] / 255 < 0.25
                     else "napis w spokojnych strefach albo na pille (tło barwne)" if busy < 0.25 and stat.mean[0] / 255 < 0.25
                     else "napis tylko na panelu lub pille (tło zbyt gęste lub jasne)")}


def build() -> dict:
    files = sorted(p for p in FOLDER.iterdir() if p.is_file() and p.suffix.lower() in IMAGES)
    items = []
    for path in files:
        about, tags, use = META.get(path.name, ("(brak opisu, uzupełnij META w scripts/backgrounds_catalog.py)", [], ""))
        items.append({"file": path.name, "path": f"assets/backgrounds/{path.name}", "about": about, "tags": tags, "use": use,
                      **measure(path)})
    data = {"generated_at": datetime.now(timezone.utc).isoformat(), "count": len(items), "items": items}
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FOLDER / "INDEX.md").write_text(markdown(data), encoding="utf-8")
    return data


def markdown(data: dict) -> str:
    lines = ["# Indeks teł", "", f"Generowany przez `python -I scripts/backgrounds_catalog.py build` ({data['count']} plików). "
             "Opisy pisane ręcznie, liczby mierzone. Zasady użycia: [README.md](README.md).", "",
             "Jasność 0 do 1 (ciemne tło daje bezpieczny kontrast tekstu). Zajętość: im wyższa, tym gęstszy obraz i tym bardziej potrzebny panel pod tekstem.", "",
             "| plik | rozmiar | jasność | nasycenie | zajętość | spokojne strefy | tekst |", "|---|---|---|---|---|---|---|"]
    for i in data["items"]:
        lines.append(f"| `{i['file']}` | {i['width']}x{i['height']} | {i['brightness']} | {i['saturation']} | {i['busy']} | "
                     f"{', '.join(i['calm_zones'])} | {i['text']} |")
    lines += ["", "## Opisy i zastosowanie", ""]
    for i in data["items"]:
        lines += [f"### {i['file']}", "", i["about"], "", f"- Tagi: {', '.join(i['tags'])}", f"- Użyj do: {i['use']}", ""]
    return "\n".join(lines)


def check() -> list[str]:
    if not INDEX.is_file():
        return ["Brak index.json; uruchom build"]
    indexed = {i["file"] for i in json.loads(INDEX.read_text(encoding="utf-8"))["items"]}
    present = {p.name for p in FOLDER.iterdir() if p.is_file() and p.suffix.lower() in IMAGES}
    return [f"Nowy plik bez wpisu: {n}" for n in sorted(present - indexed)] + [f"Wpis bez pliku: {n}" for n in sorted(indexed - present)]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args(argv)
    if args.command == "build":
        data = build()
        print(json.dumps({"indexed": data["count"]}, indent=2))
        return 0
    problems = check()
    print(json.dumps({"passed": not problems, "problems": problems}, ensure_ascii=False, indent=2))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
