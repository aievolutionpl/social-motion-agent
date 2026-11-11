---
name: shotcraft-motion
description: Curated shot director and frame-accurate storyboard planning for short product ads, app showcases, and explainers. Original Canvas reference gallery plus Video ShotCraft recipes.
---

# ShotCraft Motion Pack

Optional **production-planning** layer for [Social Motion Agent](../../README.md), not a replacement for Creative Director or HyperFrames. The agent may use the 10 curated Video ShotCraft motion references; five have original deterministic browser preview implementations in this repository.

## Start with an actual brief
Read [Creative Director](../creative-director/SKILL.md), the existing [feedback loop](../creative-director/references/feedback-loop.md), and [ShotCraft guide](../../docs/SHOTCRAFT_MOTION_PACK.md). Reuse all known details and any user-selected style. For an open direction, offer two or three distinct, concrete approaches before a substantial production build. If the user explicitly delegates creative choices, make them without blocking.

## Inspect and plan
```bash
python -S studio.py shotcraft list
python -S studio.py shotcraft show carousel-3d
python -S studio.py shotcraft plan product-reel --duration 15 --fps 30 --brand "Example" --cta "Visit"
python -S studio.py shotcraft validate
```

Supported sequences: `product-reel` (9:16), `app-launch` (16:9), `education-explainer` (4:5), `kinetic-teaser` (9:16). Planner outputs shot timings as **start-inclusive, end-exclusive frame ranges**, sums to the exact requested total and highlights missing source material. Do not invent metrics, screenshots, music rights or customer claims. Swap a data-proof shot for a clearly labeled conceptual diagram when no verified numbers exist.

## Review the effect before production
From repository root, `python -m http.server 8000`, then open `http://localhost:8000/examples/shotcraft-motion/`. The gallery has five **seekable, deterministic, interactive Canvas demonstrations**. They are useful for choosing motion, not ready-to-render video compositions.

Before close recreation, open the linked upstream recipe card and its actual matched implementation from [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft). Adapt brand typography, color, subject matter, camera and timing. Never copy upstream assets without their license and attribution.

## Implement and verify
Build the scene using existing [HyperFrames/GSAP workflow](../../docs/PRODUCTION.md), FFmpeg footage workflow or a clearly isolated Remotion project where its rendering features are necessary. Don't import upstream TSX directly into HyperFrames. Render a representative scene, inspect actual frame exports/audio, apply timestamped feedback and run the full production QA checks. Gallery tests only verify browser demo behavior; they do **not** establish video render readiness.

## Example request
> Z materiałów w `media/` zrób 15 s 9:16 premium produktową rolkę. Weź `carousel-3d` i `flying-words` jako inspiracje, zachowaj styl marki. Pokaż dwa różne kierunki i storyboard. Bez wymyślonych statystyk. Po wyborze zrób scenę próbną, a potem prawdziwy render i sprawdź klatki.
