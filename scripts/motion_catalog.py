"""Wyszukiwarka katalogu awesome-ai-motion: 637 efektów ruchu, 11 receptur, bez czytania całego indeksu.

Czyta tylko tools/repos/awesome-ai-motion/index.json (oryginał pozostaje bez zmian).
Pola opisowe zwraca po angielsku, jeśli katalog je ma; nazwy parametrów bywają koreańskie,
ale wartości, zakresy, easing i snippet są niezależne od języka.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from studio_core import ROOT

REPO = ROOT / "tools/repos/awesome-ai-motion"
INDEX = REPO / "index.json"
PURPOSES = {"주목 끌기": "attention", "설명": "explanation", "비교": "comparison", "순서·흐름": "sequence",
            "강조": "emphasis", "전환": "transition", "데이터 증명": "data", "피드백": "feedback",
            "분위기": "atmosphere", "브랜딩": "branding"}
MEDIA = {"설명 영상": "explainer", "숏폼": "shorts", "스크롤덱": "scrolldeck", "발표": "presentation",
         "제품 시연": "product-demo", "데이터 스토리": "data-story", "웹 UI": "web-ui"}
LEVELS = {"기본": "basic", "중급": "intermediate", "고급": "advanced"}


@lru_cache(maxsize=1)
def load() -> dict:
    if not INDEX.is_file():
        raise ValueError("Brak tools/repos/awesome-ai-motion/index.json; sklonuj repozytorium zgodnie z tools/INDEX.md")
    return json.loads(INDEX.read_text(encoding="utf-8"))


def english(table: dict, values) -> list[str]:
    return [table.get(v, v) for v in values or []]


def wanted(table: dict, value: str | None) -> set[str]:
    """Filtr po angielskiej nazwie lub koreańskim oryginale; None oznacza brak filtra."""
    if not value:
        return set()
    value = value.casefold()
    found = {ko for ko, en in table.items() if value in (en, ko.casefold())}
    if not found:
        raise ValueError(f"Nieznana wartość {value!r}; dostępne: {', '.join(sorted(table.values()))}")
    return found


def summary(item: dict) -> dict:
    return {"slug": item["slug"], "name": item.get("en"), "family": item.get("family"),
            "level": LEVELS.get(item.get("level"), item.get("level")),
            "purposes": english(PURPOSES, item.get("purposes")), "media": english(MEDIA, item.get("media")),
            "what": item.get("oneLinerEn") or item.get("oneLiner"), "rendered": item.get("render") == "done"}


def find(query: str = "", purpose: str | None = None, medium: str | None = None, family: str | None = None,
         level: str | None = None, rendered: bool = False, limit: int = 12) -> dict:
    data = load()
    purposes, media, levels = wanted(PURPOSES, purpose), wanted(MEDIA, medium), wanted(LEVELS, level)
    tokens = query.casefold().split()
    ranked = []
    for item in data["effects"]:
        if purposes and not purposes & set(item.get("purposes", [])):
            continue
        if media and not media & set(item.get("media", [])):
            continue
        if levels and item.get("level") not in levels:
            continue
        if family and item.get("family") != family:
            continue
        if rendered and item.get("render") != "done":
            continue
        haystack = " ".join(str(item.get(k, "")) for k in ("slug", "en", "ko", "oneLinerEn", "conveysEn")).casefold()
        haystack += " " + " ".join(map(str, item.get("aka", []))).casefold() + " " + " ".join(map(str, item.get("useWhenEn", []))).casefold()
        if not all(t in haystack for t in tokens):
            continue
        name = (item.get("en") or "").casefold()
        score = sum(3 if t == item["slug"] else 2 if t in item["slug"] or t in name else 1 for t in tokens)
        ranked.append((-score, item["slug"], item))
    ranked.sort(key=lambda r: r[:2])
    return {"total_matches": len(ranked), "families_available": sorted(data["families"]),
            "effects": [summary(r[2]) for r in ranked[:max(1, min(limit, 100))]]}


def show(slug: str) -> dict:
    item = next((e for e in load()["effects"] if e["slug"] == slug), None)
    if not item:
        raise ValueError(f"Nie ma efektu {slug!r}; użyj: studio.py motion find <fraza>")
    files = {k: str(REPO / v) for k, v in (item.get("files") or {}).items()}
    return {**summary(item), "conveys": item.get("conveysEn") or item.get("conveys"),
            "use_when": item.get("useWhenEn") or item.get("useWhen"), "avoid": item.get("avoid"),
            "good_example": item.get("goodExample"), "params": item.get("params"), "ease": item.get("ease"),
            "snippet": item.get("snippet"), "pairs_with": item.get("pairsWith"),
            "engines": item.get("engines"), "prompts": item.get("promptsEn") or item.get("prompts"),
            "files": files, "html_template": files.get("html") if item.get("render") == "done" else None,
            "runtime": item.get("runtime"),
            "note": "snippet zakłada runtime katalogu (GSAP); u nas ruch ma być czystą funkcją czasu: "
                    "przelicz czas na postęp t/duration i użyj tych samych wartości oraz easingu"}


def recipe(slug: str | None = None) -> dict:
    recipes = load()["recipes"]
    if not slug:
        return {"recipes": [{"slug": r["slug"], "name": r.get("en"), "duration": r.get("duration"), "what": r.get("oneLinerEn")}
                            for r in recipes]}
    item = next((r for r in recipes if r["slug"] == slug), None)
    if not item:
        raise ValueError(f"Nie ma receptury {slug!r}; bez argumentu wypisze listę")
    files = {k: str(REPO / v) for k, v in (item.get("files") or {}).items()}
    return {"slug": slug, "name": item.get("en"), "what": item.get("oneLinerEn"), "style": item.get("styleEn"),
            "structure": item.get("structureEn"), "duration": item.get("duration"), "steps": item.get("steps"),
            "avoid": item.get("avoid"), "prompts": item.get("promptsEn") or item.get("prompts"), "files": files}
