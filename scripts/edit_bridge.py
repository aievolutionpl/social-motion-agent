"""Most karty produkcji z edycją: fx.py i vstudio edit, z automatycznym probe i contact sheet.

Źródłem są zarejestrowane assety produkcji (assets.json); oryginałów nie nadpisujemy.
Wynik trafia do renders/<nazwa>.mp4, a zapis operacji do notes/edit-<nazwa>.json.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import fx
from studio_core import WORKSPACE, contact_sheet, fingerprint, local, now, probe_job, read, record_render, sha, write

VSTUDIO = Path(os.environ.get("VSTUDIO_SCRIPT", str(WORKSPACE / "tools/video-studio/vstudio.py")))
VSTUDIO_OPS = ("trim", "concat", "speed", "reframe", "subs", "loudnorm", "cut-silence")
OPS = ("fx",) + VSTUDIO_OPS
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def edit(folder: Path, op: str, asset_ids: list[str], name: str, spec: str | None = None,
         inline: list[str] | None = None, extra: list[str] | None = None) -> dict:
    if op not in OPS:
        raise ValueError("Nieznana operacja; dostępne: " + ", ".join(OPS))
    if not NAME.match(name):
        raise ValueError("Nazwa renderu: litery, cyfry, kropka, myślnik i podkreślnik")
    manifest = {item["id"]: item for item in read(folder / "assets.json")["items"]}
    missing = [a for a in asset_ids if a not in manifest]
    if not asset_ids or missing:
        raise ValueError("Podaj zarejestrowane --asset (asset-add); brak: " + ", ".join(missing or ["żadnego"]))
    sources = [local(folder, manifest[a]["path"]) for a in asset_ids]
    out = folder / "renders" / (name + ".mp4")
    if out.exists():
        raise ValueError("Render o tej nazwie już istnieje; użyj nowej nazwy")
    log = {"op": op, "assets": asset_ids, "source_sha256": [sha(s) for s in sources], "started_at": now()}
    source_fingerprint = fingerprint(folder)
    if op == "fx":
        if len(sources) != 1:
            raise ValueError("fx przyjmuje dokładnie jeden asset")
        effects = (fx.load_spec(local(folder, spec)) if spec else []) + [fx.parse_inline(e) for e in inline or []]
        if not effects:
            raise ValueError("fx wymaga --spec (plik w katalogu produkcji) lub --effect")
        log["effects"] = effects
        try:
            fx.apply(sources[0], out, effects)
        except fx.FxError as exc:
            raise ValueError(str(exc)) from exc
    else:
        if not VSTUDIO.is_file():
            raise ValueError("Optional video-studio unavailable; set VSTUDIO_SCRIPT to your installation")
        out.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-I", str(VSTUDIO), "edit", op, *map(str, sources), *(extra or []), "-o", str(out)]
        log["command"] = [Path(c).name if c == str(VSTUDIO) else c for c in command[2:]]
        result = subprocess.run(command, capture_output=True, text=True, timeout=3600)
        if result.returncode or not out.is_file():
            out.unlink(missing_ok=True)
            raise ValueError("vstudio: " + (result.stderr or result.stdout)[-1500:])
    relative = out.relative_to(folder).as_posix()
    record_render(folder, relative, source_fingerprint, "edit-" + op)
    technical = probe_job(folder, relative)
    sheet = contact_sheet(folder, relative)
    log.update(render=relative, render_sha256=sha(out), probe_passed=technical["passed"],
               probe_failures=technical["failures"], contact_sheet=sheet.relative_to(folder).as_posix(),
               finished_at=now())
    write(folder / "notes" / f"edit-{name}.json", log)
    return {"render": relative, "probe_passed": technical["passed"], "probe_failures": technical["failures"],
            "duration_sec": technical["duration_sec"], "contact_sheet": str(sheet), "reviewed": False,
            "next": "Obejrzyj contact sheet i klatki, odsłuchaj audio, potem review.json dla tego SHA"}
