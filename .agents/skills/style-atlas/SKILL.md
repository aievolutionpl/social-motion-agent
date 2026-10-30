---
name: style-atlas
description: Lock a distinct coded-video style from 12 canonical recipes (awesome-opus-5-5-video-styles), search 1100+ viral coded-video prompts (awesome-opus5-5-videos), and apply the 5-line Unslop Direction and 9-pass redline review (heydamir/unslop) before coding any HTML/Canvas/SVG/Three.js/GSAP scene.
---

# Style Atlas & Unslop Subagent Guide

Use this skill whenever a subagent or main agent plans or codes a motion video, UI promo, kinetic typography bumper, 3D WebGL scene, explainer or before/after transformation story.

## 1. Lock the style before writing code

Models writing rendering code (HTML, Canvas, SVG, Three.js, GLSL, GSAP) drift in aesthetic from run to run unless the visual style is explicitly locked. Query the local Style Atlas first:

```powershell
python -S studio.py styles list
python -S studio.py styles recipe productui
python -S studio.py styles recipe typography
python -S studio.py styles find "saas launch" --style productui --limit 6
python -S studio.py styles find "shader" --tech glsl --remake
python -S studio.py styles show twoclipping-402193
```

The 12 canonical styles (`typography`, `productui`, `explainer`, `cinematic3d`, `handdrawn`, `collage`, `pixel`, `cartoon`, `lowpoly`, `generative`, `retro`, `photoreal`) return:
- A copy-ready **Style Lock Recipe** (`style_recipe`)
- Recommended neutral ramp (`graphite`, `warm`, `ink`), theme (`dark`, `light`), FPS and tech stack
- Exact CSS token overrides for `templates/frame-tokens.css`
- Style-specific anti-slop rules and a deterministic `window.seek(t)` build contract

## 2. Write the 5-line Unslop Direction

Derived from `heydamir/unslop` (Damir Sokolovsky `@heydamir`, CC BY 4.0). Before touching HTML/CSS/JS, write five lines from the product itself:

1. **Product:** What it does and for whom, in one plain sentence.
2. **Character:** 2–3 concrete words (e.g., `calm, exact, warm` or `fast, technical, playful`). Banned template words: `clean`, `modern`, `sleek`, `minimal`, `premium`.
3. **World:** The physical material or environment the product belongs to (paper and ink → `data-ramp="warm"`; instruments and night shifts → `data-ramp="ink"`; neutral workspace → `data-ramp="graphite"`).
4. **Moments:** 1 or 2 places that carry rich color and material detail (a rendered object, a multi-series chart, or a world scene). Everything around them (the chrome) stays quiet.
5. **Signature:** One small detail unique to this product (e.g., keycaps, route line, live pulse dot, domain glyph matrix), used consistently.

## 3. Code with the Opus 5.5 + Unslop Architecture Contract

1. **Pure function of time (`window.seek(t)`):**
   Every style, transform, SVG `stroke-dashoffset`, canvas draw and counter is computed purely from `t`. No `setTimeout`, no `requestAnimationFrame` drift during capture, no `Math.random()` inside the frame loop.
2. **Closed-form springs & liquid spans (`templates/motion-helpers.js`):**
   - Use `stepSpring(t, t0, zeta, omega)` and `springTimeline(t, keyframes)` for multi-step UI state morphs.
   - Use `liquidSpan(t, keyframes)` so the leading edge rides a faster spring than the trailing edge on tabs, toggles and highlights.
   - Use `bakeGlyphAtlas` + `drawGlyphs(ctx, baked, t)` or `drawHalftone` for custom code-treated visuals without calling `getImageData` inside `seek(t)`.
3. **Camera & text sharpness gotchas:**
   - Never put `will-change: transform` on an element that the camera scales up, or Chromium rasterizes the text as a blurry bitmap.
   - When text swaps inside a morphing container, give old text and new text separate exit/enter windows so they never overlap.
   - For seamless loops, `seek(0)` and `seek(DURATION)` must produce identical positions, cursor coordinates, counters and velocities.

## 4. Run the 9-Pass Unslop Check & Polish Gate

Apply passes in order: **1. Spacing (4px grid)** → **2. Color (1 ramp, quiet chrome, 1 accent)** → **3. Icons (no emoji, 1 stroke)** → **4. Copy (no `!!`, no hype words, numbers always show comparison baseline)** → **5. Type (400–600 weights, tabular-nums)** → **6. Layout** → **7. Details (nested radius: `inner = outer - padding >= 4`)** → **8. Visuals** → **9. Motion**.

Verify every coded scene with the automated gate:

```powershell
python -S studio.py polish output/jobs/ID/source/scene.html --format 9:16 --seek 4.2 --shot output/jobs/ID/previews/scene-916.png
```

To generate a standalone 4-pass Before→After Redline Transformation Story HTML (`unslop` method by `@heydamir`):

```powershell
python -S studio.py unslop-story output/jobs/ID/source/story.html --ramp graphite --duration 8
```

## Credits

- Style classification and Style Lock Recipes adapted from `HiAPIAI/awesome-opus-5-5-video-styles` (CC BY 4.0).
- Coded-video prompt patterns adapted from `yihui-dev/awesome-opus5-5-videos` (MIT).
- Unslop 5-line Direction, 9-pass redline review, tinted ramps, glyph/halftone code treatments and story redline morph adapted from `heydamir/unslop` by Damir Sokolovsky (`@heydamir`, CC BY 4.0).
