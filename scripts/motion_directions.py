"""Menu kierunków „motion, nie slajdy”: style, koncepty openerów, tryby explainerów, tło i przejścia.

Dane: config/motion-directions.json (oryginalne opisy, idee z bangtutorial/bang-motion, MIT).
Wszystko jest deterministyczne i offline. Menu to propozycje do briefu, nie limity ani zakazy:
marka i jawne decyzje użytkownika mają pierwszeństwo.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from studio_core import ROOT

DATA = ROOT / "config/motion-directions.json"
MENUS = ("style_directions", "explainer_modes", "opener_concepts", "background_motion", "surfaces",
         "render_families", "transitions", "openings", "endings", "canonical_components")
FINGERPRINT_PARTS = ("concept", "scenes", "objects", "opening", "ending")


@lru_cache(maxsize=1)
def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.casefold()) if len(t) > 1}


def list_menus(menu: str | None = None) -> dict:
    data = load()
    if menu is None:
        return {"source": data["source"], "note": data["note"],
                "menus": {name: len(data[name]) for name in MENUS},
                "usage": "studio.py directions list MENU · show SLUG · brief --for 'product, audience' · compare FP1 FP2"}
    if menu not in MENUS:
        raise ValueError(f"Nieznane menu {menu!r}; dostępne: {', '.join(MENUS)}")
    return {"menu": menu, "items": data[menu]}


def show(slug: str) -> dict:
    data = load()
    for menu in MENUS:
        for item in data[menu]:
            if isinstance(item, dict) and (item.get("slug") == slug or (menu == "opener_concepts" and str(item.get("id")) == slug)):
                result = {"menu": menu, **item}
                preset = item.get("preset")
                if preset:
                    result["example"] = "examples/motion-styles/index.html?style=" + preset
                return result
    raise ValueError(f"Nie ma pozycji {slug!r}; użyj: studio.py directions list MENU")


def _rank(items: list[dict], wanted: set[str], keys: tuple[str, ...], limit: int) -> list[dict]:
    ranked = []
    for index, item in enumerate(items):
        tags = set()
        for key in keys:
            value = item.get(key, "")
            tags |= _tokens(" ".join(value) if isinstance(value, list) else str(value))
        score = len(tags & wanted)
        ranked.append((-score, index, item, score))
    ranked.sort(key=lambda r: r[:2])
    return [{**r[2], "match": r[3]} for r in ranked[:limit]]


def brief(subject: str, kind: str = "opener", previous: str | None = None) -> dict:
    """Szkielet style briefu: trzy kandydackie koncepty + kierunki dobrane po słowach z briefu.

    Dopasowanie jest leksykalne i jawne (pole `match`); to punkt startu do rozmowy z
    użytkownikiem, nie automatyczna decyzja kreatywna.
    """
    if not subject.strip():
        raise ValueError("Podaj --for 'produkt, odbiorca, nastrój', np. 'fintech app for students'")
    if kind not in ("opener", "explainer"):
        raise ValueError("kind: opener albo explainer")
    data, wanted = load(), _tokens(subject)
    result = {"subject": subject, "kind": kind,
              "fields": data["style_brief_fields"],
              "fingerprint_template": " · ".join(FINGERPRINT_PARTS),
              "checks": ["Show the brief and rundown before code; wait for a requested approval",
                         "Every palette color states its brand source or 'derived: reason'",
                         "At most two canonical components, each demanded by the concept",
                         "Run studio.py motion lint on the built HTML, then inspect real frames"]}
    if kind == "opener":
        result["concept_candidates"] = _rank(data["opener_concepts"], wanted, ("good_for", "premise", "name"), 3)
        result["canonical_components"] = data["canonical_components"]
    else:
        result["explainer_modes"] = _rank(data["explainer_modes"], wanted, ("best_for", "look", "name"), 3)
    result["direction_candidates"] = _rank(data["style_directions"], wanted, ("good_for", "name"), 3)
    if previous:
        result["previous_fingerprint"] = parse_fingerprint(previous)
        result["novelty_rule"] = "new concept, or at least 3 of 5 fingerprint parts different (studio.py directions compare)"
    return result


def parse_fingerprint(text: str) -> dict:
    parts = [p.strip() for p in re.split(r"\s*[·|]\s*", text.strip()) if p.strip()]
    if len(parts) != len(FINGERPRINT_PARTS):
        raise ValueError("Odcisk struktury ma 5 części: " + " · ".join(FINGERPRINT_PARTS))
    return dict(zip(FINGERPRINT_PARTS, parts))


def _same(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return a.strip().casefold() == b.strip().casefold()
    return len(ta & tb) / len(ta | tb) >= 0.6


def compare(first: str, second: str) -> dict:
    """Porównaj dwa odciski struktury; nowy film to inny koncept albo ≥3 z 5 różnych części."""
    a, b = parse_fingerprint(first), parse_fingerprint(second)
    different = [part for part in FINGERPRINT_PARTS if not _same(a[part], b[part])]
    concept_changed = "concept" in different
    return {"first": a, "second": b, "different": different, "different_count": len(different),
            "concept_changed": concept_changed,
            "distinct": concept_changed or len(different) >= 3,
            "rule": "distinct = different concept, or >= 3 of 5 parts different; lexical check, review the rundown too"}
