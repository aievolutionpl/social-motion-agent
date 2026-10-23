# Mapa całej biblioteki

Mapa przypiętych źródeł. Każdy wpis opisuje zastosowanie i punkt wejścia. Aktualne wersje: SOURCE_VERSIONS.md. Stan runtime: VALIDATION.md.

## hypermotion

**Edytor motion + CLI/MCP.** Natywne sceny .hype, semantyczny layout, kamera i eksport. Opcjonalny edytor; główny renderer dystrybucji to HyperFrames.

- Lokalnie: `tools/repos/hypermotion`.
- Czytaj: `tools/repos/hypermotion/README.md + AGENTS.md + skills/`.
- Wymagania: Desktop i CLI; build Windows i render niezweryfikowane.
- Snapshot: `e510cd60c0d2`, licencja `Apache-2.0`, 2 plików SKILL.md.

## anatomy

**Ilustracje techniczne.** Buduje precyzyjne figury i mechanizmy w SVG/WebGL/3D. Włącz jako scenę explainera, a nie cały proces montażowy.

- Lokalnie: `tools/repos/anatomy`.
- Czytaj: `tools/repos/anatomy/SKILL.md + examples/`.
- Wymagania: Node 20.10+ i Chromium do kontroli.
- Snapshot: `1482e8469b0a`, licencja `MIT`, 1 plików SKILL.md.

## open-design

**Studio i biblioteka projektowa.** Systemy marki, projektowanie, templates i generowanie artefaktów; duży monorepo. Wybierz pojedynczy moduł.

- Lokalnie: `tools/repos/open-design`.
- Czytaj: `tools/repos/open-design/QUICKSTART.md + skills/ + design-templates/`.
- Wymagania: Node24, pnpm10.33.2; osobne uruchomienie.
- Snapshot: `3b0df90f305c`, licencja `Apache-2.0`, 549 plików SKILL.md.

## motion-anything

**Biblioteka i edytor animacji.** Przepisy ruchu i router doboru; lokalny serwer node cli/bin/motion.js serve 4399. Eksport do sprawdzenia.

- Lokalnie: `tools/repos/motion-anything`.
- Czytaj: `tools/repos/motion-anything/skills/motion-anything/SKILL.md + recipes/`.
- Wymagania: Node18+ i dostępny silnik agenta/BYOK.
- Snapshot: `b016900d9ee9`, licencja `Apache-2.0`, 230 plików SKILL.md.

## video-agent-skills

**Social i montaż nagrań.** Scenariusze, edycja take'ów, b-roll, clips, vox, tłumaczenia. Czytaj wybrany skill z jego engine, nie cały pakiet.

- Lokalnie: `tools/repos/video-agent-skills`.
- Czytaj: `tools/repos/video-agent-skills/skills/editing/SKILL.md`.
- Wymagania: Node20+, FFmpeg; dodatkowe narzędzia według skilla.
- Snapshot: `480801ade3f6`, licencja `MIT`, 13 plików SKILL.md.

## openclip-agent-skills

**Instrukcje do usługi OpenClip.** Zleca transkrypcję, clipping i edycję zdalnemu MCP. Pobranie instrukcji nie podłącza konta.

- Lokalnie: `tools/repos/openclip-agent-skills`.
- Czytaj: `tools/repos/openclip-agent-skills/skills/openclip/SKILL.md`.
- Wymagania: Konto/OAuth i dostępny OpenClip MCP; niepołączone.
- Snapshot: `ea02c98db69c`, licencja `MIT`, 10 plików SKILL.md.

## claude-motion

**Remotion, SFX i symulacje.** React/Remotion oraz osobna ścieżka HTML render(t); wspólna oś czasu, proceduralne audio i review klatek.

- Lokalnie: `tools/repos/claude-motion`.
- Czytaj: `tools/repos/claude-motion/AGENTS.md + .claude/skills/ + sims/`.
- Wymagania: Node20+, Python3, FFmpeg; lokalne zależności przed użyciem.
- Snapshot: `e627941543d9`, licencja `MIT`, 4 plików SKILL.md.

## claude-motion-design

**HTML frame-by-frame.** Sceny seek(t), Playwright, subframes i miks. Dobry dla deterministycznych filmów launch/typography.

- Lokalnie: `tools/repos/claude-motion-design`.
- Czytaj: `tools/repos/claude-motion-design/skill/motion-design/SKILL.md`.
- Wymagania: Python, Playwright/Chromium, NumPy, Pillow.
- Snapshot: `3d90d349ef3f`, licencja `MIT`, 1 plików SKILL.md.

## motion-skills

**Hub iart.** Kieruje do 18 pobranych paczek tematycznych. Nie zawiera właściwych plików SKILL.md.

- Lokalnie: `tools/repos/motion-skills`.
- Czytaj: `tools/repos/motion-skills/README.md`.
- Wymagania: Wybierz jedną paczkę i jej skill.
- Snapshot: `bb5a3ce66611`, licencja `MIT`, 0 plików SKILL.md.

## awesome-motion-design-agent-skills

**Reżyseria i QA.** Pięć skilli, rubryki, specyfikacje i mapa dalszych źródeł. Używaj do doboru stacku i kontroli.

- Lokalnie: `tools/repos/awesome-motion-design-agent-skills`.
- Czytaj: `tools/repos/awesome-motion-design-agent-skills/skills/ + rubrics/ + playbooks/`.
- Wymagania: Wybrany renderer lub provider jest osobnym narzędziem.
- Snapshot: `b45d60fa5b0f`, licencja `CC0-1.0`, 5 plików SKILL.md.

## awesome-opus5-5-videos

**Referencje i prompty.** Prompty i linki do filmów; wybierz konkretne odniesienie do rytmu, kadru lub narracji. Nie jest rendererem.

- Lokalnie: `tools/repos/awesome-opus5-5-videos`.
- Czytaj: `tools/repos/awesome-opus5-5-videos/prompts/ + data/videos.json`.
- Wymagania: Filmy pod linkami nie są lokalnie pobrane.
- Snapshot: `92aee2f586ac`, licencja `MIT`, 0 plików SKILL.md.

## remotion-official-skills

**Oficjalne instrukcje Remotion.** Router do tworzenia, markup, renderowania, map, multimediów i napisów. Techniczne API sprawdzaj w oficjalnych docs.

- Lokalnie: `tools/repos/remotion-official-skills`.
- Czytaj: `tools/repos/remotion-official-skills/skills/remotion-best-practices/SKILL.md`.
- Wymagania: Skille nie zawierają gotowego środowiska Remotion.
- Snapshot: `039e8a2fc78b`, licencja `not_detected`, 12 plików SKILL.md.

## motion-video-skill

**Działający lokalny renderer HTML.** Sceny HTML/CSS/SVG, kontrola seek, Chromium i FFmpeg; node scripts/video.mjs init/check/render z katalogu filmu.

- Lokalnie: `tools/repos/motion-video-skill`.
- Czytaj: `tools/repos/motion-video-skill/SKILL.md + references/cli.md`.
- Wymagania: Wymaga osobnego zainstalowania zależności i testu renderu.
- Snapshot: `0a21eb76468f`, licencja `MIT`, 1 plików SKILL.md.

## openscreen

**Nagrywanie aplikacji i tutoriale.** Wybrany silnik screen capture, zoomów, kursora i eksportu pokazów stron/aplikacji. Lokalny adapter scripts/openscreen.py; trasy showcase i tutorial.

- Lokalnie: `tools/repos/openscreen`.
- Czytaj: `tools/repos/openscreen/plugin/skills/openscreen-demo/SKILL.md + website/docs/cli.md`.
- Wymagania: Runtime instalowany osobno; ustaw OPENSCREEN_EXECUTABLE. Testy adaptera nie potwierdzają live capture.
- Snapshot: `1e91710962e4`, licencja `MIT`, 2 plików SKILL.md.

## ux-ui-agent-skills

**Doktryna UX/UI i bramki jakości.** Anti-slop, tokeny, typografia, rytm, stany i 52 bramki mierzone w Chrome. U nas stosowane do ramek HTML wideo przez skill motion-ui-polish i scripts/polish_check.py; reszta (138 systemów, komponenty, adaptery) to biblioteka referencyjna.

- Lokalnie: `tools/repos/ux-ui-agent-skills`.
- Czytaj: `tools/repos/ux-ui-agent-skills/CLAUDE.md + taste/design-taste.md + .claude/rules/ + scripts/`.
- Wymagania: Doktryna działa od ręki; bramki: npm install --ignore-scripts w katalogu repo i Chrome. Bramki przeglądarkowe wymagają osobnego uruchomienia.
- Snapshot: `55156b40e3a9`, licencja `MIT`, 27 plików SKILL.md.

## awesome-ai-motion

**Katalog 637 efektów ruchu.** Karty efektów z parametrami, easingiem i promptami, 11 receptur (hook, before/after, shorts, quote card), decyzje po celu i medium, 128 gotowych szablonów HTML. Przeszukiwany przez studio.py motion, nie czytany w całości.

- Lokalnie: `tools/repos/awesome-ai-motion`.
- Czytaj: `tools/repos/awesome-ai-motion/SKILL.md + index.json + references/decision-tables.md`.
- Wymagania: Katalog i szablony HTML dostępne lokalnie; render.mjs wymaga Playwright (niezainstalowany, niepotrzebny do wyszukiwania).
- Snapshot: `1e3c249073c6`, licencja `MIT`, 1 plików SKILL.md.

## iart-tiktok-video-skills

**Paczka skilli iart.** Shorty 9:16, hook, captions i countdown

- Lokalnie: `tools/repos/iart-tiktok-video-skills`.
- Czytaj: `tools/repos/iart-tiktok-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `2a775336b5a6`, licencja `MIT`, 4 plików SKILL.md.

## iart-text-message-video-skills

**Paczka skilli iart.** Historie w formie wiadomości tekstowych

- Lokalnie: `tools/repos/iart-text-message-video-skills`.
- Czytaj: `tools/repos/iart-text-message-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `3a800e1e9b96`, licencja `MIT`, 1 plików SKILL.md.

## iart-youtube-video-skills

**Paczka skilli iart.** Intro/outro YouTube i audiogramy

- Lokalnie: `tools/repos/iart-youtube-video-skills`.
- Czytaj: `tools/repos/iart-youtube-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `f3df381d65ab`, licencja `MIT`, 2 plików SKILL.md.

## iart-ecommerce-video-skills

**Paczka skilli iart.** Prezentacja produktów i film sprzedażowy

- Lokalnie: `tools/repos/iart-ecommerce-video-skills`.
- Czytaj: `tools/repos/iart-ecommerce-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `2bd0dd19c9b2`, licencja `MIT`, 3 plików SKILL.md.

## iart-ad-video-skills

**Paczka skilli iart.** Reklamy, launch i testimonial

- Lokalnie: `tools/repos/iart-ad-video-skills`.
- Czytaj: `tools/repos/iart-ad-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `0de0f2a1c1f4`, licencja `MIT`, 3 plików SKILL.md.

## iart-data-animation-skills

**Paczka skilli iart.** Wykresy, infografiki i prezentacje wideo

- Lokalnie: `tools/repos/iart-data-animation-skills`.
- Czytaj: `tools/repos/iart-data-animation-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `8ce2709c3992`, licencja `MIT`, 3 plików SKILL.md.

## iart-explainer-video-skills

**Paczka skilli iart.** Explainery, diagramy, izometria i whiteboard

- Lokalnie: `tools/repos/iart-explainer-video-skills`.
- Czytaj: `tools/repos/iart-explainer-video-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `3e2d411b725d`, licencja `MIT`, 5 plików SKILL.md.

## iart-map-animation-skills

**Paczka skilli iart.** Mapy i opowieści geograficzne

- Lokalnie: `tools/repos/iart-map-animation-skills`.
- Czytaj: `tools/repos/iart-map-animation-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `390ca98bbcf2`, licencja `MIT`, 1 plików SKILL.md.

## iart-web-animation-skills

**Paczka skilli iart.** Animacja interfejsów i stron

- Lokalnie: `tools/repos/iart-web-animation-skills`.
- Czytaj: `tools/repos/iart-web-animation-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `b6dba3eb7597`, licencja `MIT`, 9 plików SKILL.md.

## iart-motion-design-skills

**Paczka skilli iart.** Zasady animacji, kompozycja, kolor, beat sync i branding

- Lokalnie: `tools/repos/iart-motion-design-skills`.
- Czytaj: `tools/repos/iart-motion-design-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `3c129f769d90`, licencja `MIT`, 9 plików SKILL.md.

## iart-kinetic-typography-skills

**Paczka skilli iart.** Animacja typografii

- Lokalnie: `tools/repos/iart-kinetic-typography-skills`.
- Czytaj: `tools/repos/iart-kinetic-typography-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `fccc94bd325d`, licencja `MIT`, 1 plików SKILL.md.

## iart-freelance-motion-skills

**Paczka skilli iart.** Proces studia i dostarczanie projektów motion

- Lokalnie: `tools/repos/iart-freelance-motion-skills`.
- Czytaj: `tools/repos/iart-freelance-motion-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `d85c2b484693`, licencja `MIT`, 5 plików SKILL.md.

## iart-webgl-animation-skills

**Paczka skilli iart.** Sceny 3D i efekty WebGL

- Lokalnie: `tools/repos/iart-webgl-animation-skills`.
- Czytaj: `tools/repos/iart-webgl-animation-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `50697d659fbf`, licencja `MIT`, 3 plików SKILL.md.

## iart-manim-skills

**Paczka skilli iart.** Animacja matematyczna z Manim; wymaga środowiska Python/Manim

- Lokalnie: `tools/repos/iart-manim-skills`.
- Czytaj: `tools/repos/iart-manim-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `a15833c44de5`, licencja `MIT`, 1 plików SKILL.md.

## iart-generative-illustration-skills

**Paczka skilli iart.** Ilustracje generatywne; brak głównego pliku licencji w snapshotcie

- Lokalnie: `tools/repos/iart-generative-illustration-skills`.
- Czytaj: `tools/repos/iart-generative-illustration-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `e7d62437c875`, licencja `not_detected`, 1 plików SKILL.md.

## iart-javascript-animation-skills

**Paczka skilli iart.** Animacja canvas kodem oraz soundtrack

- Lokalnie: `tools/repos/iart-javascript-animation-skills`.
- Czytaj: `tools/repos/iart-javascript-animation-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `f7d0882a3132`, licencja `MIT`, 2 plików SKILL.md.

## iart-lower-thirds-skills

**Paczka skilli iart.** Belki podpisów, także przezroczyste

- Lokalnie: `tools/repos/iart-lower-thirds-skills`.
- Czytaj: `tools/repos/iart-lower-thirds-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `aa8ef7ed9fa5`, licencja `MIT`, 1 plików SKILL.md.

## iart-b-roll-skills

**Paczka skilli iart.** Przebitki do mówiącej osoby zbudowane z treści wypowiedzi

- Lokalnie: `tools/repos/iart-b-roll-skills`.
- Czytaj: `tools/repos/iart-b-roll-skills/README.md + skills/`.
- Wymagania: Czytaj wymagania wybranego SKILL.md; nie instaluj całego zestawu w ciemno.
- Snapshot: `a51e34b0a8de`, licencja `MIT`, 1 plików SKILL.md.
