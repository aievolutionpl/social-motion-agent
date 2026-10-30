"""Atlas 12 stylów wideo i wyszukiwarka 1100+ promptów (awesome-opus-5-5-video-styles + awesome-opus5-5-videos).

Łączy:
- 12 kanonicznych receptur stylów (Style Lock Recipes) z HiAPIAI/awesome-opus-5-5-video-styles (CC BY 4.0)
- 703 prompty kodowanego wideo z yihui-dev/awesome-opus5-5-videos (MIT)
- 5-liniowy Direction i reguły ramp kolorystycznych z heydamir/unslop (CC BY 4.0)

Działa również przed pobraniem submodułów (wbudowane receptury 12 stylów, kontrakty seek(t) i wzorce architektoniczne).
Po pobraniu tools/repos/awesome-opus-5-5-video-styles oraz tools/repos/awesome-opus5-5-videos przeszukuje pełne bazy.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from studio_core import ROOT

STYLES_REPO = ROOT / "tools/repos/awesome-opus-5-5-video-styles"
VIDEOS_REPO = ROOT / "tools/repos/awesome-opus5-5-videos"
VIDEOS_JSON = VIDEOS_REPO / "data/videos.json"

CATEGORIES = ("motion", "explainer", "3d", "game")
TECH_TAGS = ("canvas", "svg", "gsap", "three.js", "glsl", "webgl", "web-audio", "particles", "css", "ai-image", "playable")

SUBAGENT_BLUEPRINT = {
    "direction_5_lines": {
        "product": "Co produkt robi i dla kogo, w jednym prostym zdaniu (bez żargonu i hype'u).",
        "character": "2-3 konkretne słowa (np. 'spokojny, precyzyjny, ciepły'); zakazane: clean, modern, sleek, minimal, premium.",
        "world": "Świat i materiał produktu (np. papier i tusz, nocne przyrządy pomiarowe, warsztat); decyduje o rampie neutralnej (graphite/warm/ink).",
        "moments": "1 lub 2 miejsca, gdzie żyje kolor i bogactwo detalu (renderowany obiekt, główny wykres, scena świata); reszta interfejsu pozostaje cicha.",
        "signature": "Jeden mały detal charakterystyczny wyłącznie dla tego produktu, użyty konsekwentnie."
    },
    "prompt_to_code_sections": {
        "inputs": "Wymagane stany UI, tekst, dane liczbowe z punktem odniesienia oraz tempo (BPM / czas trwania).",
        "direction": "Styl z 12 kanonicznych receptur, rampa kolorów, typografia oraz jawna lista elementów zakazanych (Banned).",
        "structure": "Podział na takty/sekundy: co dzieje się w każdym bicie (akcja -> zmiana stanu -> czytelny hold).",
        "build": [
            "Jedna czysta funkcja czasu window.seek(t): zero CSS transitions w trakcie renderu, zero setTimeout, zero Math.random() między klatkami.",
            "Sprężyny jako zamknięte odpowiedzi skokowe (closed-form step responses); wielokrotna zmiana celu to suma sprężyn od chwil t_i.",
            "Dla płynnych przejść (liquid tabs / toggle) prowadząca i tylna krawędź jadą na dwóch różnych sprężynach.",
            "Bezpośrednia manipulacja kursorem: podczas przeciągania wartość wynika z pozycji kursora, po puszczeniu wraca sprężyną.",
            "Dla pętli (loop): klatka ostatnia identyczna z pierwszą (pozycja kursora, liczniki, maski i prędkość włącznie)."
        ],
        "gotchas": [
            "Nigdy nie nakładaj will-change na kontenery skalowane przez kamerę (rozmywa tekst w Chromium).",
            "Tekst wymieniany wewnątrz morfującego kontenera musi mieć własne czasy wyjścia i wejścia, inaczej się nakłada.",
            "Nie wywołuj getImageData wewnątrz pętli klatkowej; próbkuj obraz raz do offscreen canvasu przed startem."
        ]
    }
}

STYLES: dict[str, dict] = {
    "typography": {
        "slug": "typography",
        "name": "Kinetic typography",
        "summary": "Duża typografia, animowane litery, plakatowe bumpery i mocne cięcia pod rytm.",
        "style_recipe": (
            "Style: kinetic typography. One or two bold typefaces, huge words that snap, stretch, mask "
            "and wipe on the beat; a strict grid; 2-3 colours with one electric accent; hard cuts every "
            "0.5-1 s; no stock imagery."
        ),
        "ramp": "ink",
        "theme": "dark",
        "fps": 60,
        "recommended_tech": ["svg", "gsap", "css"],
        "tokens": {
            "--bg-0": "#0b0d14",
            "--bg-1": "#11141c",
            "--surface": "#1a1e28",
            "--ink": "#eef0f5",
            "--accent": "#ff4d2d"
        },
        "anti_slop": [
            "Brak gradientowego tekstu i neonowych poświat na słowach.",
            "Jedna dominująca myśl na ekran; słowa zatrzymują się na czytelny hold (min. 0.5 s + 0.3 s na słowo).",
            "Ruch wyłącznie przez transform i clip-path/overflow:hidden, nigdy przez animowanie font-size."
        ],
        "build_contract": "Każde słowo w kontenerze overflow:hidden; wejście translateY(110% -> 0%) z easeOut(3) lub stepSpring."
    },
    "productui": {
        "slug": "productui",
        "name": "Product UI promo",
        "summary": "Filmy premierowe SaaS i aplikacji: prawdziwe stany UI, kursor, karty i przepływ jednej akcji.",
        "style_recipe": (
            "Style: product launch film. Recreate the product's real UI states as crisp vector screens, "
            "a moving cursor that clicks through one flow, smooth spring easing, soft shadows on a "
            "light or graphite background, a single headline per beat, logo lockup at the end."
        ),
        "ramp": "graphite",
        "theme": "dark",
        "fps": 60,
        "recommended_tech": ["svg", "gsap", "canvas", "css"],
        "tokens": {
            "--bg-0": "#141415",
            "--bg-1": "#0f0f10",
            "--surface": "#19191b",
            "--ink": "#ededed",
            "--accent": "#4cc38a"
        },
        "anti_slop": [
            "Cichy interfejs (quiet chrome) na rampie graphite; kolor tylko w 1-2 momentach (np. główny wykres lub karta wyniku).",
            "Zakaz 4 identycznych kart obok siebie, zakaz emoji jako ikon, zakaz fioletowo-niebieskich poświat.",
            "Zagnieżdżony promień: r_wewn = max(4px, r_zewn - padding)."
        ],
        "build_contract": "Jeden kształt/okno morfuje między stanami przez seek(t); kursor prowadzi akcję: ruch -> klik (scale 0.96) -> zmiana stanu -> hold."
    },
    "explainer": {
        "slug": "explainer",
        "name": "Explainers & data viz",
        "summary": "Wykresy, wzory, mapy, osie czasu i mechanizmy budowane krok po kroku.",
        "style_recipe": (
            "Style: explainer. One idea per scene, built step by step: axes draw on, values count up, "
            "arrows point, labels fade in next to what they name. Clean off-white or dark background, "
            "one highlight colour for the thing that matters."
        ),
        "ramp": "warm",
        "theme": "dark",
        "fps": 30,
        "recommended_tech": ["svg", "canvas", "gsap"],
        "tokens": {
            "--bg-0": "#161513",
            "--bg-1": "#12110f",
            "--surface": "#1c1a18",
            "--ink": "#efe9de",
            "--accent": "#f59e0b"
        },
        "anti_slop": [
            "Jeden główny wykres na ekranie; pozostałe serie na stopniach neutralnych, akcent tylko na kluczowym wniosku.",
            "Każda liczba ma jednostkę i punkt odniesienia (np. '+18% vs Q3', nigdy samo '+18%!!').",
            "Przyczyna pojawia się na ekranie przed skutkiem."
        ],
        "build_contract": "Rysowanie linii przez stroke-dashoffset zależny od progress(t, start, dur); liczniki z tabular-nums."
    },
    "cinematic3d": {
        "slug": "cinematic3d",
        "name": "Cinematic 3D",
        "summary": "Filmowe sceny Three.js / WebGL: materiały PBR, światło kluczowe, głębia ostrości i ruch kamery.",
        "style_recipe": (
            "Style: cinematic 3D in Three.js/WebGL. Physically based materials, one strong key light "
            "with soft shadows, depth of field, slow dolly or orbit camera moves, subtle film grain and "
            "colour grade. 24 fps, 2.39:1 letterbox optional."
        ),
        "ramp": "ink",
        "theme": "dark",
        "fps": 24,
        "recommended_tech": ["three.js", "glsl", "webgl", "canvas"],
        "tokens": {
            "--bg-0": "#07080d",
            "--bg-1": "#0b0d14",
            "--surface": "#11141c",
            "--ink": "#eef0f5",
            "--accent": "#38bdf8"
        },
        "anti_slop": [
            "Zero bezcelowych błyszczących kul (glossy blobs/orbs) i fioletowych mgławic.",
            "Jedno wyraźne źródło światła (key light) zamiast płaskiego oświetlenia ze wszystkich stron.",
            "Tekst HTML nakładany na spokojną, pustą część kadru 3D."
        ],
        "build_contract": "Pozycja kamery, światła i uniformy shaderów obliczane wyłącznie z czasu t wewnątrz window.seek(t) i renderowane jawnie."
    },
    "handdrawn": {
        "slug": "handdrawn",
        "name": "Hand-drawn, sketch & comic",
        "summary": "Ołówkowe linie, szkice tablicowe, komiksowy raster i ludzki, ręcznie rysowany charakter.",
        "style_recipe": (
            "Style: hand-drawn. Every shape is drawn as wobbly pencil or ink lines on off-white paper, "
            "redrawn slightly every few frames (line boil). Limited palette: ink black plus one accent "
            "colour. No gradients, no 3D, no glossy UI. Hand-lettered labels only where needed."
        ),
        "ramp": "warm",
        "theme": "light",
        "fps": 12,
        "recommended_tech": ["svg", "canvas"],
        "tokens": {
            "--bg-0": "#f7f4ee",
            "--bg-1": "#efe9df",
            "--surface": "#fdfbf7",
            "--ink": "#1f1b16",
            "--accent": "#dc2626"
        },
        "anti_slop": [
            "Brak nowoczesnych gradientów, cieni UI i perfekcyjnych geometrycznych prostokątów.",
            "Line boil deterministyczny: 3 warianty ścieżki przełączane przez Math.floor(t * 8) % 3 (bez Math.random())."
        ],
        "build_contract": "Kontury SVG z feTurbulence/feDisplacementMap o deterministycznym seedzie lub 3 pre-obliczone ścieżki na kształt."
    },
    "collage": {
        "slug": "collage",
        "name": "Collage, cutout & sand",
        "summary": "Wycinanki papierowe, kolaż magazynowy, faktura papieru i animacja poklatkowa na dwójkach (12 fps).",
        "style_recipe": (
            "Style: handmade collage. Build every frame from flat cut-out pieces (paper, photo scraps, "
            "card) with torn edges, soft drop shadows and visible paper texture; pieces move in stop- "
            "motion steps on twos (12 fps). Warm, slightly faded colours."
        ),
        "ramp": "warm",
        "theme": "light",
        "fps": 12,
        "recommended_tech": ["canvas", "svg", "css"],
        "tokens": {
            "--bg-0": "#efe9df",
            "--bg-1": "#e5dec9",
            "--surface": "#f7f4ee",
            "--ink": "#1f1b16",
            "--accent": "#d9534f"
        },
        "anti_slop": [
            "Ruch kwantowany do 12 fps: stepped_t = Math.floor(t * 12) / 12.",
            "Twarde wycięte krawędzie z lekkim cieniem kontaktowym zamiast miękkich blurów."
        ],
        "build_contract": "Kwantyzacja czasu wewnątrz seek(t): const qt = Math.floor(t * 12) / 12; wszystkie transformacje liczone od qt."
    },
    "pixel": {
        "slug": "pixel",
        "name": "Pixel art",
        "summary": "8-bitowe sprite'y, ekrany retro gier, stała paleta 16-32 kolorów i skalowanie nearest-neighbour.",
        "style_recipe": (
            "Style: pixel art. Render the scene at 320x180 on a fixed 16-32 colour palette and scale it "
            "up with nearest-neighbour (no smoothing, no anti-aliasing). Sprites animate in 2-4 frame "
            "cycles; parallax background layers; chiptune audio."
        ),
        "ramp": "ink",
        "theme": "dark",
        "fps": 30,
        "recommended_tech": ["canvas", "css"],
        "tokens": {
            "--bg-0": "#0b0d14",
            "--bg-1": "#11141c",
            "--surface": "#1a1e28",
            "--ink": "#eef0f5",
            "--accent": "#fbbf24"
        },
        "anti_slop": [
            "Obowiązkowe image-rendering: pixelated oraz ctx.imageSmoothingEnabled = false.",
            "Fonty wyłącznie pikselowe (PressStart2P, Silkscreen, Jersey10 z assets/fonts/)."
        ],
        "build_contract": "Niskorozdzielczy bufor Canvas (np. 320x180 lub 180x320 dla 9:16) skalowany całkowitoliczbowo bez wygładzania."
    },
    "cartoon": {
        "slug": "cartoon",
        "name": "Flat cartoon",
        "summary": "Płaskie postacie wektorowe, gruby obrys, squash-and-stretch i nasycona paleta.",
        "style_recipe": (
            "Style: flat 2D cartoon. Bold rounded shapes with thick dark outlines, flat fills with one "
            "shade tone, squash-and-stretch on every move, big expressive eyes. Bright, saturated "
            "palette; simple layered backgrounds."
        ),
        "ramp": "warm",
        "theme": "light",
        "fps": 24,
        "recommended_tech": ["svg", "canvas", "gsap"],
        "tokens": {
            "--bg-0": "#fdfbf7",
            "--bg-1": "#f7f4ee",
            "--surface": "#ffffff",
            "--ink": "#171717",
            "--accent": "#ef4444"
        },
        "anti_slop": [
            "Jednolita grubość obrysu i płaskie wypełnienia bez fotorealistycznych tekstur.",
            "Zachowanie objętości przy squash-and-stretch: scaleX * scaleY ~= 1."
        ],
        "build_contract": "Transformacje grup SVG z zachowaniem objętości: scale(sx, 1/sx) przy lądowaniu i wybiciu."
    },
    "lowpoly": {
        "slug": "lowpoly",
        "name": "Low-poly & voxel",
        "summary": "Fasetowana geometria, voksele, izometryczna kamera i sprężyste wejścia obiektów.",
        "style_recipe": (
            "Style: low-poly / voxel. Faceted flat-shaded geometry (or cubes), isometric or high three- "
            "quarter camera, pastel palette with one saturated accent, soft ambient occlusion, objects "
            "bounce and pop in with overshoot."
        ),
        "ramp": "graphite",
        "theme": "light",
        "fps": 30,
        "recommended_tech": ["three.js", "canvas", "svg"],
        "tokens": {
            "--bg-0": "#f5f7fa",
            "--bg-1": "#eceff4",
            "--surface": "#ffffff",
            "--ink": "#111827",
            "--accent": "#2563eb"
        },
        "anti_slop": [
            "Flat shading (flatShading: true) zamiast gładkich materiałów Phong.",
            "Kamera ortograficzna / izometryczna o stałym kącie."
        ],
        "build_contract": "Wejścia poszczególnych bloków ze staggerem i sprężyną backOut / stepSpring zależną od czasu t."
    },
    "generative": {
        "slug": "generative",
        "name": "Generative & neon",
        "summary": "Proceduralne cząsteczki, pola przepływu (flow fields), shadery GLSL i geometria zsynchronizowana z bitem.",
        "style_recipe": (
            "Style: generative art. Everything is procedural: particles, flow fields, shaders or tiling "
            "geometric patterns driven by time and audio. Dark background with neon or a bold 3-4 "
            "colour palette; motion locked to the beat."
        ),
        "ramp": "ink",
        "theme": "dark",
        "fps": 60,
        "recommended_tech": ["glsl", "webgl", "canvas", "particles"],
        "tokens": {
            "--bg-0": "#07080d",
            "--bg-1": "#0b0d14",
            "--surface": "#11141c",
            "--ink": "#eef0f5",
            "--accent": "#22d3ee"
        },
        "anti_slop": [
            "Cząsteczki nie mogą zasłaniać ani obniżać kontrastu głównej typografii.",
            "Wszystkie pozycje cząsteczek wyliczane z deterministycznego seeda i czasu t (zero dryfu stanu)."
        ],
        "build_contract": "Pozycja i-tej cząsteczki: f(seed_i, t) jako zamknięty wzór trygonometryczny/szumowy bez mutacji stanu."
    },
    "retro": {
        "slug": "retro",
        "name": "Retro, terminal & old film",
        "summary": "Terminale CRT, zielony/bursztynowy luminofor, oscyloskopy, ASCII/glify oraz taśma archiwalna.",
        "style_recipe": (
            "Style: retro. Either monochrome film (grain, gate weave, flicker, vignette, 18 fps) or a "
            "CRT terminal (green or amber phosphor, scanlines, ASCII art, type-on text with a blinking "
            "cursor). No modern gradients."
        ),
        "ramp": "ink",
        "theme": "dark",
        "fps": 30,
        "recommended_tech": ["canvas", "css", "svg"],
        "tokens": {
            "--bg-0": "#080b08",
            "--bg-1": "#0c120c",
            "--surface": "#111a11",
            "--ink": "#d1fae5",
            "--accent": "#4cc38a"
        },
        "anti_slop": [
            "Brak współczesnych kart SaaS i gradientów; konsekwentny monofoniczny luminofor lub sepiowa taśma.",
            "Wpis tekstu znak po znaku: text.slice(0, Math.floor(progress * text.length))."
        ],
        "build_contract": "Efekt glifów/ASCII z pre-renderowanym atlasem znaków (drawGlyphs z templates/motion-helpers.js) i scanlines w CSS."
    },
    "photoreal": {
        "slug": "photoreal",
        "name": "Photoreal & live action",
        "summary": "Prawdziwe nagrania lub fotorealistyczne ujęcia cięte pod bit z powściągliwą typografią i wspólnym gradingiem.",
        "style_recipe": (
            "Style: photoreal edit. Use the supplied real footage or photos (or call a video model for "
            "new shots), cut on the beat, add restrained typography, colour-match every shot to one "
            "grade, and keep motion graphics minimal."
        ),
        "ramp": "warm",
        "theme": "dark",
        "fps": 24,
        "recommended_tech": ["canvas", "ai-image", "css"],
        "tokens": {
            "--bg-0": "#12110f",
            "--bg-1": "#161513",
            "--surface": "#1c1a18",
            "--ink": "#efe9de",
            "--accent": "#e5a93c"
        },
        "anti_slop": [
            "Nie wklejaj tekstu ani fałszywych przycisków wewnątrz generowanych obrazów; tekst nakładaj w kodzie na spokojne tło.",
            "Dopasuj krawędzie obrazu do koloru strony maską lub wspólnym duotonem/gradingiem."
        ],
        "build_contract": "Montaż przez studio.py render-assembly lub kontrolowany ruch kamery (push/drift) z czytelnymi podpisami .pill-caption."
    },
}

BUILTIN_EXEMPLARS: list[dict] = [
    {
        "slug": "twoclipping-402193",
        "title": "Continuous UI Shape Morph on 120 BPM Beat Grid",
        "style": "productui",
        "category": "motion",
        "tech_tags": ["svg", "css"],
        "has_remake": True,
        "source": "awesome-opus5-5-videos",
        "highlights": [
            "Jeden element morfuje przez 12 stanów UI (button -> loader -> island -> player -> slider -> toggle -> liquid tabs -> chart -> cmd+K -> toast) bez żadnego cięcia.",
            "Dwie niezależne sprężyny dla krawędzi wiodącej i tylnej dają efekt płynnego rozciągania (liquid morph).",
            "Pełna pętla: ostatnia klatka identyczna z pierwszą."
        ],
        "prompt": (
            "<direction>Dribbble-level UI motion. One shape, never cut: every state is the same element morphing "
            "its size, radius and color while its content swaps with a short blur. A cursor drives every change "
            "with real clicks and drags. Light warm-gray canvas, black and white components, one clean UI font (Geist). "
            "Springs everywhere, a tiny overshoot at most. Banned: bouncy easing, particle bursts, glows, gradients on UI chrome.</direction>\n"
            "<build>1. One HTML file. Every style is computed from time inside seek(t): no CSS transitions, no timers, no state carried between frames.\n"
            "2. Springs are closed-form step responses.\n"
            "3. The tab indicator's two edges ride different springs so the leading edge stretches ahead of the trailing one.</build>"
        )
    },
    {
        "slug": "techhalla-kinetic-bumper",
        "title": "Kinetic Identity Bumper with Masked Beat Snaps",
        "style": "typography",
        "category": "motion",
        "tech_tags": ["svg", "gsap", "css"],
        "has_remake": True,
        "source": "awesome-opus-5-5-video-styles",
        "highlights": [
            "Siatka Szwajcarska z dużym kontrastem skali (hero 17cqmin vs label 2.1cqmin).",
            "Twarde cięcia co 0.6-1.0 s i maskowane wejścia wierszy z czytelnym zatrzymaniem."
        ],
        "prompt": (
            "Create a 15-second kinetic typography identity bumper. Strict Swiss grid, two weights (400 and 500), "
            "one electric accent on a deep ink ramp. Words enter via overflow-hidden line masks synchronized to "
            "the beat grid, with generous reading holds on key metrics."
        )
    },
    {
        "slug": "transformer-step-explainer",
        "title": "Step-by-Step Mechanism & Data Explainer",
        "style": "explainer",
        "category": "explainer",
        "tech_tags": ["svg", "canvas", "gsap"],
        "has_remake": True,
        "source": "awesome-opus-5-5-video-styles",
        "highlights": [
            "Przyczyna przed skutkiem: najpierw rysują się osie i wejścia, potem przepływ, na końcu wynik z porównaniem.",
            "Jeden kolor akcentu wskazuje aktywną ścieżkę uwagi, reszta diagramu pozostaje na stopniach neutralnych."
        ],
        "prompt": (
            "Build a 30-second technical explainer animation. One mechanism per scene: draw axes and nodes first, "
            "animate token flow along SVG paths using stroke-dashoffset, then highlight the resulting metric with "
            "a clear baseline comparison (+24% vs baseline)."
        )
    },
    {
        "slug": "unslop-redline-story",
        "title": "Unslop Redline UI Transformation Story Video",
        "style": "productui",
        "category": "motion",
        "tech_tags": ["css", "svg", "canvas"],
        "has_remake": True,
        "source": "unslop",
        "highlights": [
            "Ekran naprawia się w miejscu krok po kroku (Spacing -> Color & Icons -> Type & Copy -> Details) z falą opóźnienia od lewego górnego rogu.",
            "Czerwone linie pomiarowe (#ff4d6a) liczą odstępy i promienie na żywo, zmieniając kolor na biały (#f5f5f5) po naprawie."
        ],
        "prompt": (
            "Create a 10-second transformation video where a vibecoded dashboard unslops itself in place across "
            "4 passes (Spacing, Color and icons, Type and copy, Details) with live redline gap/radius callouts "
            "that turn white as each pass settles."
        )
    },
]


@lru_cache(maxsize=1)
def _load_videos_json() -> list[dict]:
    if not VIDEOS_JSON.is_file():
        return []
    return json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_style_markdown_entries() -> list[dict]:
    entries: list[dict] = []
    styles_dir = STYLES_REPO / "styles"
    if not styles_dir.is_dir():
        return entries
    pattern = re.compile(
        r'<a id="(c\d+)"></a>\s*### (?:\d+\.\s*)?([^\n]+)\n+([^\n]*)\n+```text\n(.*?)\n```',
        re.DOTALL,
    )
    for md_file in sorted(styles_dir.glob("*.md")):
        style_slug = md_file.stem
        if style_slug not in STYLES:
            continue
        text = md_file.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        for match in pattern.finditer(text):
            anchor, title, meta_line, prompt_body = match.groups()
            entries.append({
                "slug": f"{style_slug}-{anchor}",
                "anchor": anchor,
                "title": title.strip(),
                "style": style_slug,
                "category": "explainer" if style_slug == "explainer" else ("3d" if style_slug in ("cinematic3d", "lowpoly") else "motion"),
                "tech_tags": list(STYLES[style_slug]["recommended_tech"]),
                "has_remake": "skillry.dev" in meta_line,
                "source": "awesome-opus-5-5-video-styles",
                "prompt": prompt_body.strip(),
            })
    return entries


def list_styles() -> dict:
    style_entries = _load_style_markdown_entries()
    videos = _load_videos_json()
    counts_by_style: dict[str, int] = {slug: 0 for slug in STYLES}
    for item in style_entries:
        counts_by_style[item["style"]] = counts_by_style.get(item["style"], 0) + 1
    return {
        "total_styles": len(STYLES),
        "upstream_styles_loaded": bool(style_entries),
        "upstream_videos_loaded": bool(videos),
        "upstream_style_prompts": len(style_entries),
        "upstream_video_prompts": len(videos),
        "styles": [
            {
                "slug": s["slug"],
                "name": s["name"],
                "summary": s["summary"],
                "ramp": s["ramp"],
                "theme": s["theme"],
                "fps": s["fps"],
                "recommended_tech": s["recommended_tech"],
                "style_recipe": s["style_recipe"],
                "upstream_prompts": counts_by_style.get(s["slug"], 0),
            }
            for s in STYLES.values()
        ],
        "attributions": [
            "HiAPIAI/awesome-opus-5-5-video-styles (CC BY 4.0)",
            "yihui-dev/awesome-opus5-5-videos (MIT)",
            "Damir Sokolovsky @heydamir / unslop (CC BY 4.0)",
        ],
        "subagent_blueprint": SUBAGENT_BLUEPRINT,
    }


def recipe(style: str | None = None) -> dict:
    if not style:
        return {"total_styles": len(STYLES), "styles": list(STYLES.values()), "subagent_blueprint": SUBAGENT_BLUEPRINT}
    key = style.strip().casefold()
    if key not in STYLES:
        raise ValueError(f"Nieznany styl {style!r}; dostępne: {', '.join(sorted(STYLES))}")
    info = dict(STYLES[key])
    matching = [e for e in _load_style_markdown_entries() if e["style"] == key][:5]
    if not matching:
        matching = [e for e in BUILTIN_EXEMPLARS if e["style"] == key]
    info["examples"] = [
        {"slug": e["slug"], "title": e.get("title", e["slug"]), "tech_tags": e.get("tech_tags", []), "prompt_preview": e["prompt"][:280]}
        for e in matching
    ]
    info["subagent_blueprint"] = SUBAGENT_BLUEPRINT
    return info


def _all_searchable_entries() -> list[dict]:
    combined: list[dict] = list(BUILTIN_EXEMPLARS)
    seen = {e["slug"] for e in combined}
    for e in _load_style_markdown_entries():
        if e["slug"] not in seen:
            combined.append(e)
            seen.add(e["slug"])
    for v in _load_videos_json():
        slug = v.get("slug")
        if not slug or slug in seen:
            continue
        tags = [t.casefold() for t in v.get("tech_tags", [])]
        inferred_style = "explainer" if v.get("category") == "explainer" else (
            "cinematic3d" if "three.js" in tags or v.get("category") == "3d" else (
                "generative" if "glsl" in tags or "particles" in tags else "productui"
            )
        )
        combined.append({
            "slug": slug,
            "title": f"{v.get('author', slug)} ({v.get('category', 'motion')})",
            "style": inferred_style,
            "category": v.get("category", "motion"),
            "tech_tags": tags,
            "has_remake": bool(v.get("has_remake")),
            "source": "awesome-opus5-5-videos",
            "prompt": v.get("prompt", ""),
        })
        seen.add(slug)
    return combined


def find(query: str = "", style: str | None = None, category: str | None = None,
         tech: str | None = None, remake_only: bool = False, limit: int = 12) -> dict:
    if style and style.casefold() not in STYLES:
        raise ValueError(f"Nieznany styl {style!r}; dostępne: {', '.join(sorted(STYLES))}")
    if category and category.casefold() not in CATEGORIES:
        raise ValueError(f"Nieznana kategoria {category!r}; dostępne: {', '.join(CATEGORIES)}")
    if tech and tech.casefold() not in TECH_TAGS:
        raise ValueError(f"Nieznany tag techniczny {tech!r}; dostępne: {', '.join(TECH_TAGS)}")

    tokens = query.casefold().split()
    style_f = style.casefold() if style else None
    cat_f = category.casefold() if category else None
    tech_f = tech.casefold() if tech else None

    ranked: list[tuple[int, str, dict]] = []
    for item in _all_searchable_entries():
        if style_f and item.get("style") != style_f:
            continue
        if cat_f and item.get("category") != cat_f:
            continue
        if tech_f and tech_f not in [t.casefold() for t in item.get("tech_tags", [])]:
            continue
        if remake_only and not item.get("has_remake"):
            continue
        haystack = " ".join([
            item.get("slug", ""),
            item.get("title", ""),
            item.get("style", ""),
            item.get("category", ""),
            " ".join(item.get("tech_tags", [])),
            item.get("prompt", ""),
        ]).casefold()
        if not all(t in haystack for t in tokens):
            continue
        score = sum(
            4 if t == item.get("slug", "").casefold() or t == item.get("style", "").casefold()
            else 2 if t in item.get("title", "").casefold() or t in item.get("slug", "").casefold()
            else 1
            for t in tokens
        ) + (1 if item.get("has_remake") else 0)
        ranked.append((-score, item["slug"], item))

    ranked.sort(key=lambda r: r[:2])
    capped = max(1, min(limit, 50))
    return {
        "total_matches": len(ranked),
        "filters": {"query": query, "style": style_f, "category": cat_f, "tech": tech_f, "remake_only": remake_only},
        "results": [
            {
                "slug": item["slug"],
                "title": item.get("title", item["slug"]),
                "style": item.get("style"),
                "category": item.get("category"),
                "tech_tags": item.get("tech_tags", []),
                "has_remake": item.get("has_remake", False),
                "source": item.get("source"),
                "prompt_preview": item.get("prompt", "")[:240],
            }
            for _, _, item in ranked[:capped]
        ],
    }


def show(ident: str, remake: bool = False) -> dict:
    needle = ident.strip().casefold()
    for item in _all_searchable_entries():
        if item["slug"].casefold() == needle or item.get("anchor", "").casefold() == needle:
            style_info = STYLES.get(item.get("style", "productui"), STYLES["productui"])
            card = {
                **item,
                "style_recipe": style_info["style_recipe"],
                "recommended_ramp": style_info["ramp"],
                "recommended_tokens": style_info["tokens"],
                "build_contract": style_info["build_contract"],
                "subagent_note": (
                    "Przetłumacz prompt na deterministyczną kompozycję HTML/Canvas/SVG sterowaną przez window.seek(t). "
                    "Zastosuj tokeny z templates/frame-tokens.css i sprawdź wynik przez studio.py polish."
                ),
            }
            if remake:
                card["subagent_blueprint"] = SUBAGENT_BLUEPRINT
            return card
    raise ValueError(f"Nie znaleziono promptu {ident!r}; użyj: studio.py styles find <fraza>")
