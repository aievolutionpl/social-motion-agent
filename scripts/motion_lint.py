"""Statyczny lint „film, nie prezentacja” dla scen HTML sterowanych czasem.

Sprawdza kod, nie gust: zegar systemowy i losowość w ścieżce renderu, brak kontraktu
window.seek(t)/pauzowanej osi, układ slajdów (≥3 sekcje przełączane przez opacity),
trzy poziomy tekstu w jednej scenie, wideo z autoplay/loop, przejścia CSS na własnym
zegarze i will-change. Idee testów mechanicznych: bangtutorial/bang-motion (MIT),
napisane od nowa dla kontraktu Social Motion. Uzupełnia `studio.py polish` (pomiary w
przeglądarce) i przegląd prawdziwych klatek; nie zastępuje żadnego z nich.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

CLOCK = re.compile(r"\b(?:Date\.now|performance\.now)\s*\(|\bnew\s+Date\s*\(")
RANDOM = re.compile(r"\bMath\.random\s*\(")
SEEK = re.compile(r"window\.seek\s*=|window\.__timelines\b|paused\s*:\s*true")
TOGGLE = re.compile(r"autoAlpha|opacity|display\s*[:=]|visibility")
CSS_CLOCK = re.compile(r"(?<![\w-])(?:transition|animation)\s*:\s*(?!\s*none\b)[^;}\n]+", re.IGNORECASE)
WILL_CHANGE = re.compile(r"will-change\s*:", re.IGNORECASE)
COMMENTS = re.compile(r"/\*.*?\*/|(?<![:\"'\\])//[^\n]*", re.DOTALL)
KICKER = re.compile(r"\b(?:kicker|eyebrow|overline|pretitle|tagline-top)\b")
TITLE = re.compile(r"\b(?:title|headline|heading|hero)\b")
BODY = re.compile(r"\b(?:body|subtitle|subhead|lead|description|copy|credit|caption)\b")
SCENE_CLASS = re.compile(r"\b(?:scene|slide)\b")


class _Scenes(HTMLParser):
    """Zbiera sekcje-sceny i poziomy tekstu wewnątrz nich; reszta dokumentu jest ignorowana."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scenes, self.stack, self.videos = [], [], []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class") or ""
        if tag == "video":
            self.videos.append({k: attrs.get(k) for k in ("src", "autoplay", "loop") if k in attrs})
        if tag in ("br", "img", "input", "meta", "link", "source", "hr", "path", "circle", "rect", "line", "use"):
            return
        self.depth += 1
        if tag == "section" or SCENE_CLASS.search(cls):
            self.stack.append({"depth": self.depth, "id": attrs.get("id") or cls or tag, "tiers": set()})
            self.scenes.append(self.stack[-1])
        elif self.stack:
            tiers = self.stack[-1]["tiers"]
            if KICKER.search(cls):
                tiers.add("kicker")
            elif tag in ("h1", "h2", "h3") or TITLE.search(cls):
                tiers.add("title")
            elif tag == "p" or BODY.search(cls):
                tiers.add("body")

    def handle_endtag(self, tag):
        if tag in ("br", "img", "input", "meta", "link", "source", "hr", "path", "circle", "rect", "line", "use"):
            return
        if self.stack and self.stack[-1]["depth"] == self.depth:
            self.stack.pop()
        self.depth = max(0, self.depth - 1)


def lint(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Brak pliku {path}")
    raw = path.read_text(encoding="utf-8")
    scripts = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", raw, re.DOTALL | re.IGNORECASE))
    styles = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", raw, re.DOTALL | re.IGNORECASE))
    styles += "\n" + "\n".join(re.findall(r"\bstyle=\"([^\"]*)\"", raw))
    code = COMMENTS.sub("", scripts)
    errors, warnings = [], []

    for match in RANDOM.finditer(code):
        start = max(0, match.start() - 30)
        errors.append({"check": "random", "context": code[start:match.end() + 10].strip(),
                       "message": "Math.random() makes frames unrepeatable; derive variation from a seeded hash of index/t"})
    for match in CLOCK.finditer(code):
        warnings.append({"check": "system-clock", "message": f"{match.group(0).strip()} found; allowed only in a preview driver "
                         "that calls seek(elapsed); visual state must be a pure function of t"})
    if not SEEK.search(code):
        errors.append({"check": "seek-contract", "message": "No window.seek(t), window.__timelines or paused timeline; "
                       "capture cannot seek an absolute frame"})

    parser = _Scenes()
    parser.feed(raw)
    scenes = parser.scenes
    if len(scenes) >= 3 and TOGGLE.search(code):
        warnings.append({"check": "slide-deck", "scenes": len(scenes),
                         "message": f"{len(scenes)} section/scene blocks switched by opacity/visibility read as a slide deck; "
                         "change scenes by moving the world/camera, an object-carried transition or a motivated cut "
                         "(cartoon-stage cuts between fully living stages are a valid exception)"})
    for scene in scenes:
        if {"kicker", "title", "body"} <= scene["tiers"]:
            warnings.append({"check": "text-tiers", "scene": scene["id"],
                             "message": "kicker + title + body in one scene is a slide layout; keep at most one big line "
                             "plus one world label (UI mockups and short in-world documents count as objects)"})
    for video in parser.videos:
        if "autoplay" in video or "loop" in video:
            warnings.append({"check": "video-clock", "src": video.get("src"),
                             "message": "<video autoplay/loop> runs on its own clock; bind currentTime to t and animate its container"})
    for match in CSS_CLOCK.finditer(styles):
        warnings.append({"check": "css-clock", "declaration": match.group(0).strip()[:80],
                         "message": "CSS transitions/animations are not seekable during capture; drive the property from seek(t)"})
    if WILL_CHANGE.search(styles):
        warnings.append({"check": "will-change", "message": "will-change on camera-scaled containers rasterizes text blurry at zoom"})

    return {"file": str(path), "passed": not errors, "errors": errors, "warnings": warnings,
            "metrics": {"scenes": len(scenes), "videos": len(parser.videos)},
            "note": "Static code checks only. Run studio.py polish and review real frames; passing is not creative approval."}
