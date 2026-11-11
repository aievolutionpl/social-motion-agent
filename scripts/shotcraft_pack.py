"""Curated ShotCraft shot selection + deterministic, frame-accurate storyboards.

Reference recipes and executable browser demos are clearly distinguished from
production renderers. No third-party code/media or network services are required.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "shotcraft-recipes.json"
BRAND_LOCKUP = "brand-lockup"


@lru_cache(maxsize=1)
def catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    validate(data)
    return data


def validate(data: dict | None = None) -> dict:
    if data is None:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported ShotCraft registry version")
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("ShotCraft registry has no shots")
    ids = [s.get("id") for s in shots]
    if len(set(ids)) != len(ids) or any(not isinstance(v, str) or not v for v in ids):
        raise ValueError("Shot IDs must be unique, non-empty strings")
    for s in shots:
        if not s.get("source", "").startswith("https://github.com/"):
            raise ValueError(f"Missing upstream link for {s['id']}")
        if not isinstance(s.get("preview"), bool):
            raise ValueError(f"Missing preview capability flag for {s['id']}")
    seqs = data.get("sequences")
    if not isinstance(seqs, dict) or not seqs:
        raise ValueError("ShotCraft sequences are missing")
    for slug, seq in seqs.items():
        if not seq.get("scenes") or seq.get("format") not in ("9:16", "4:5", "16:9", "1:1"):
            raise ValueError(f"Invalid sequence {slug}")
        for scene in seq["scenes"]:
            if scene["shot"] not in (*ids, BRAND_LOCKUP):
                raise ValueError(f"{slug} contains unknown shot {scene['shot']}")
            if not isinstance(scene.get("seconds"), (int, float)) or not math.isfinite(scene["seconds"]) or scene["seconds"] <= 0:
                raise ValueError(f"{slug} has invalid shot duration")
    return {"passed": True, "shot_count": len(shots), "sequence_count": len(seqs),
            "browser_previews": sum(s["preview"] for s in shots)}


def list_shots() -> dict:
    data = catalog()
    return {
        "shots": [{"id": s["id"], "category": s["category"], "description": s["description"],
                   "preview": s["preview"]} for s in data["shots"]],
        "sequences": [{"id": slug, "title": seq["title"], "format": seq["format"]}
                      for slug, seq in data["sequences"].items()],
        "gallery": data["gallery"],
        "notice": "Browser demos are seekable design examples, not pre-rendered MP4 or HyperFrames presets.",
    }


def show(shot_id: str) -> dict:
    if shot_id == BRAND_LOCKUP:
        return {"id": BRAND_LOCKUP, "origin": "original", "preview": False,
                "description": "Hold on a verified brand mark and one readable CTA."}
    for shot in catalog()["shots"]:
        if shot["id"] == shot_id:
            return dict(shot)
    raise ValueError(f"Unknown ShotCraft shot: {shot_id}. Try: studio.py shotcraft list")


def plan(sequence: str, duration: float = 15, fps: int = 30, brand: str = "", cta: str = "") -> dict:
    data = catalog()
    if sequence not in data["sequences"]:
        raise ValueError(f"Unknown sequence {sequence!r}. Available: {', '.join(data['sequences'])}")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 5 <= duration <= 120:
        raise ValueError("Duration must be between 5 and 120 seconds")
    if not isinstance(fps, int) or fps not in (24, 25, 30, 50, 60):
        raise ValueError("FPS must be 24, 25, 30, 50 or 60")
    if len(brand) > 120 or len(cta) > 160:
        raise ValueError("Brand / CTA text too long")
    seq = data["sequences"][sequence]
    frames = round(duration * fps)
    steps = seq["scenes"]
    pool = frames - len(steps)
    weights = [step["seconds"] for step in steps]
    fractions = [pool * weight / sum(weights) for weight in weights]
    whole = [math.floor(value) for value in fractions]
    extra = pool - sum(whole)
    priority = sorted(range(len(steps)), key=lambda index: (-(fractions[index] - whole[index]), index))
    for i in priority[:extra]:
        whole[i] += 1
    shot_map = {s["id"]: s for s in data["shots"]}
    output = []
    head = 0
    for step, count in zip(steps, whole):
        end = head + count + 1
        shot_id = step["shot"]
        detail = shot_map.get(shot_id)
        output.append({
            "shot": shot_id,
            "purpose": step["goal"],
            "start_frame": head,
            "end_frame_exclusive": end,
            "duration_frames": end - head,
            "start_seconds": round(head / fps, 4),
            "end_seconds": round(end / fps, 4),
            "preview": bool(detail and detail["preview"]),
            "recipe": detail["source"] if detail else None,
            "implementation": "browser demo only" if detail and detail["preview"] else "reference to adapt",
        })
        head = end
    assert head == frames
    missing = []
    if not brand:
        missing.append("brand name / visual identity")
    if not cta:
        missing.append("one clear CTA")
    if any(s["shot"] in ("value-stagger-gradient", "chart-live-moves") for s in output):
        missing.append("verified data for metrics or replace shot with a labelled illustration")
    if any(s["shot"] == "page-waterfall-wall" for s in output):
        missing.append("approved anonymized real UI captures")
    if any(s["shot"] == "type-rhythm-sync" for s in output):
        missing.append("music rights and measured beat timestamps, or silent timing")
    return {
        "sequence": sequence, "title": seq["title"], "format": seq["format"],
        "duration_seconds": frames / fps, "fps": fps, "total_frames": frames,
        "brand": brand or None, "cta": cta or None, "shots": output,
        "needs_confirmation_or_assets": missing,
        "workflow": ["choose direction", "confirm assets", "make representative preview",
                     "implement with existing rendering pipeline", "inspect rendered frames",
                     "review feedback", "final QA"],
        "capability": "Storyboard only. Browser previews are not production renderers.",
    }
