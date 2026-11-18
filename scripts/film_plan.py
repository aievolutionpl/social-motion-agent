"""Resolve one film brief into an existing route and the next local actions."""
import re
import unicodedata
from pathlib import Path

import creative_skills
import studio_core as core
import style_feedback

# Specific formats precede broad words such as "rolka" and "produkt".
RULES = (
    ("kinetic-walk-talk", r"walk[ -]?(and[ -]?)?talk|id[aą]c\w* prezent|chodz\w* prezent|za (?:jego |jej )?(?:sylwetk|osob|prezenter)|behind (?:the )?(?:person|subject|presenter)"),
    ("kinetic-launch", r"kinetic[ -]launch|kinetyczn\w* (?:teaser|premier)|typograph\w* launch"),
    ("tutorial", r"tutorial|poradnik|krok po kroku|step.by.step"),
    ("showcase", r"nagran\w* ekranu|screen record|demo (?:aplikac|produkt|app)|app demo"),
    ("repurpose", r"repurpose|przerob|z podcastu"), ("shorts", r"rolk|reel|short|tiktok"),
    ("explainer", r"explain|wyjasn|wytlumacz"), ("launch", r"launch|premier|teaser"),
    ("youtube", r"youtube|rozdzial"), ("editing", r"zmontuj|montaz|footage|wywiad|edit"),
    ("captions", r"napis|caption|subtitl"), ("typography", r"typograf|typograph"),
    ("broll", r"b.roll|przebit"), ("audio", r"dzwiek|audio|miks"), ("maps", r"map[asy]?\b"),
    ("data", r"wykres|chart|dane"), ("simulation", r"symulac|simulation"),
    ("thumbnail", r"miniatur|thumbnail"), ("review", r"recenz|review|ocen"),
    ("polish", r"dopracuj|polish"), ("styles", r"style|stylow"), ("motion", r"animac|motion"),
)


def plan(brief, folder=None, *, kind=None, profile=None):
    if not isinstance(brief, str) or not brief.strip():
        raise ValueError("Provide the film brief")
    plain = unicodedata.normalize("NFKD", brief.casefold().replace("ł", "l"))
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    job = core.read(folder / "job.json") if folder else {}
    if kind:
        selected = kind
    elif job:
        selected = job["kind"]
    else:
        selected = next((name for name, pattern in RULES if re.search(pattern, plain)), "editing")
    config = core.routes()[selected]
    setup = creative_skills.plan("video")
    assets = core.read(folder / "assets.json")["items"] if folder else []
    ids = {item["id"] for item in assets}
    footage = [a for a in assets if Path(a["path"]).suffix.lower() in (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")]
    missing = []
    if selected in ("editing", "shorts", "repurpose", "kinetic-walk-talk", "tutorial", "showcase") and not footage:
        missing.append("Nagranie źródłowe" if selected not in ("tutorial","showcase") else "Nagranie ekranu aplikacji")
    if selected == "kinetic-walk-talk":
        walk = {}
        if folder and (folder / "source/walk-talk.json").is_file():
            walk = core.read(folder / "source/walk-talk.json")
        if re.search(r"za (?:jego |jej )?(?:sylwetk|osob|prezenter)|behind", plain) and walk.get("foreground_asset") not in ids:
            missing.append("Maska alfa prezentera do tekstu za sylwetką")
        if not walk.get("captions"):
            missing.append("Zmierzone czasy wypowiedzi")
    if selected == "kinetic-launch":
        missing.append("Sprawdź dostępność silnika przez studio.py kinetic doctor")
    command = ["python", "-S", "studio.py"]
    aspect_match = re.search(r"(?<!\d)(9:16|16:9|4:5|1:1)(?!\d)", plain)
    aspect = aspect_match[0] if aspect_match else ("9:16" if selected in ("shorts", "kinetic-walk-talk") or "pion" in plain else "16:9")
    duration_match = re.search(r"(\d+(?:[.,]\d+)?)[ -]*(?:sek|sec|s\b)", plain)
    duration = float(duration_match[1].replace(",", ".")) if duration_match else 20.0
    if folder is None:
        commands = [command + ["new", brief, "--kind", selected, "--profile", profile or "local",
                               "--format", aspect, "--duration", str(duration)]]
    elif not assets and missing:
        commands = [command + ["asset-add", str(folder), "--help"]]
    elif selected == "kinetic-walk-talk":
        commands = [command + ["walk-talk", "compose", str(folder)]] if walk else [
            command + ["walk-talk", "prepare", str(folder), "--mode", "footage"]]
    elif footage:
        commands = [command + ["selects", str(folder), "--query", brief], command + ["variants", "openings", str(folder), "--query", brief]]
    else:
        commands = [command + ["resume", str(folder)]]
    memory = style_feedback.summary(folder.parent if folder else core.ROOT / "output/jobs",
                                    profile or job.get("style_profile", "local"))
    return {"brief": brief, "route": selected, "purpose": config["purpose"], "engine": config["engine"],
            "skills": list(dict.fromkeys([setup["entrypoint"], *config["skills"]])),
            "optional_skills": config.get("optional_skills", []), "sources": setup["sources"],
            "assets": [a["id"] for a in assets], "missing": missing, "next_commands": commands,
            "format": job.get("format", aspect), "duration_sec": job.get("duration_sec", duration),
            "variant_count": 3, "preferences": memory}
