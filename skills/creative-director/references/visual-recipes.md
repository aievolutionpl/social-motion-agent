# Visual recipe menu & 12 Opus 5.5 Style Locks

Choose by subject, evidence and viewing context. A recipe is a coherent starting point; it does not guarantee quality or reach. Do not combine several visual languages simply to demonstrate more capabilities.

## Core narrative & editorial recipes

| Recipe | Composition and material | Motion | Strong use |
| --- | --- | --- | --- |
| Editorial story | Strong typographic hierarchy, purposeful whitespace, real images with captions | Measured cuts, restrained image movement, generous reading holds | Knowledge, premium service, a story with credible details |
| Kinetic message | Short phrases, one emphasized word or figure, intentional scale shifts | Phrase-level timing, controlled masks, transitions that preserve reading order | A concise launch message or a genuinely useful insight |
| Product demonstration | Real interface, faithful crops, a visible input and outcome | Action → state change → hold; occasional contextual zoom | Software, tutorials, explaining what the product does |
| Documentary montage | Supplied footage, environment details, people and materials | Cuts follow the action or narration; motivated transitions | A place, process, craft or service with real footage |
| Mechanism explainer | Simplified diagrams with stable labels and consistent shapes | Reveal cause before effect; keep the focal relationship visible | Technical education, workflows, system explanation |
| Data story | Truthful scales, units, sources, one highlighted finding | Build the chart, isolate the insight, retain a comparison baseline | Reports and evidence-based narratives |
| Material product study | Accurate product silhouette, purposeful light, texture and close-ups | Controlled rotation/crop, stable detail holds, repeatable reveal | Physical products with usable imagery or a verified model |
| Graphic poster sequence | Bold type, deliberate fields of color, limited motifs | Rhythmic composition changes and match cuts | Events, culture and brands whose identity supports the treatment |

## 12 Canonical Coded-Video Styles (`studio.py styles`)

Adapted from `HiAPIAI/awesome-opus-5-5-video-styles` (CC BY 4.0) and `yihui-dev/awesome-opus5-5-videos` (MIT), paired with `unslop` neutral ramps (`heydamir/unslop`, CC BY 4.0). Because code-rendered video draws every frame in HTML/Canvas/SVG/Three.js, **you must lock the style explicitly** before writing scene code:

```bash
python -S studio.py styles list
python -S studio.py styles recipe <style>
python -S studio.py styles find "<query>" --style <style>
```

| Style slug | Ramp & FPS | Style Lock Recipe | Deterministic `seek(t)` contract |
| --- | --- | --- | --- |
| `typography` | `ink` (dark), 60 fps | One or two bold typefaces, huge words that snap, stretch, mask and wipe on the beat; strict grid; 2–3 colors with one electric accent; hard cuts every 0.5–1 s; no stock imagery. | Overflow-hidden line masks (`translateY(110% -> 0%)`) with `easeOut(3)` or `stepSpring`; min hold 0.5 s + 0.3 s/word. |
| `productui` | `graphite` (dark/light), 60 fps | Crisp vector UI states, moving cursor clicking through one real flow, smooth spring easing, quiet chrome on a tinted ramp, one bright moment per screen. | Continuous shape morph via `springTimeline(t, keyframes)` and dual-edge `liquidSpan(t, keyframes)`. Never put `will-change` on camera-scaled containers. |
| `explainer` | `warm` (dark/light), 30 fps | One idea per scene built step by step: axes draw on, values count up with `tabular-nums`, arrows point, labels fade in next to what they name; one highlight color. | SVG paths drawn via `stroke-dashoffset` from `progress(t, start, dur)`; cause revealed before effect. |
| `cinematic3d` | `ink` (dark), 24 fps | Three.js/WebGL scene with PBR materials, one strong key light with soft shadows, depth of field, slow dolly/orbit camera, subtle film grain. | Camera position, lights and shader uniforms computed purely from `t` inside `window.seek(t)` with explicit `renderer.render(scene, camera)`. |
| `handdrawn` | `warm` (light), 12 fps | Wobbly pencil/ink lines on off-white paper (`#f7f4ee`), deterministic line boil, ink black (`#1f1b16`) plus one accent (`#dc2626`). No gradients or glossy UI. | Quantized time `qt = Math.floor(t * 8) % 3` switching between 3 pre-computed SVG paths or `feTurbulence` seeds. |
| `collage` | `warm` (light), 12 fps | Flat cut-out paper/photo pieces with torn edges, soft contact shadows and paper texture; stop-motion steps on twos (12 fps). | Quantize time inside `seek(t)`: `const qt = Math.floor(t * 12) / 12` so all transforms step on twos. |
| `pixel` | `ink` (dark), 30 fps | 320×180 low-res buffer on a fixed 16–32 color palette scaled up with nearest-neighbor (`image-rendering: pixelated`); 2–4 frame sprite cycles. | Offscreen 320×180 canvas drawn with `ctx.imageSmoothingEnabled = false` and integer scaling. Use bundled pixel fonts (`PressStart2P`, `Silkscreen`, `Jersey10`). |
| `cartoon` | `warm` (light), 24 fps | Bold rounded vector shapes with thick dark outlines, flat fills, volume-preserving squash-and-stretch (`scaleX * scaleY ~= 1`). | SVG group transforms driven by `stepSpring` and `backOut`. |
| `lowpoly` | `graphite` (light), 30 fps | Faceted flat-shaded geometry or voxels, isometric or high 3/4 orthographic camera, pastel palette with one saturated accent, overshoot pop-ins. | Staggered block entrances (`stagger(start, gap, i)`) with `backOut(1.7)` or `stepSpring`. |
| `generative` | `ink` (dark), 60 fps | Procedural particles, flow fields, GLSL shaders or geometric tiling driven by `t` and beat peaks on a dark background. | Closed-form trigonometric/noise particle positions `f(seed_i, t)` with zero frame-to-frame state drift. |
| `retro` | `ink` (dark), 30 fps | Monochrome archival film (18 fps, vignette, gate weave) or CRT terminal (green/amber phosphor, scanlines, ASCII/glyph matrix). | Use `bakeGlyphAtlas` + `drawGlyphs(ctx, baked, t)` from `templates/motion-helpers.js` and deterministic character slicing. |
| `photoreal` | `warm` (dark), 24 fps | Supplied real footage or photos cut on the beat, restrained typography in `.pill-caption`, unified color grade. | Assemble with `studio.py render-assembly` or animate stills with `studio.py background --motion push|drift`. |

## Add a specialist when its output is needed

- **Style & prompt search:** `python -S studio.py styles list|recipe|find|show` (`.agents/skills/style-atlas/SKILL.md`).
- **Motion effects catalogue:** `python -S studio.py motion find|show|recipe` (`.agents/skills/motion-effect-picker/SKILL.md`).
- **Polish & Unslop gate:** `python -S studio.py polish` and `studio.py unslop-story` (`.agents/skills/motion-ui-polish/SKILL.md`).
- **Captions:** spoken material or muted social viewing; verify against final audio.
- **Audio design:** narration/music/SFX (`studio.py sfx find`), intentional cue sheet and actual listening review.
- **Screen capture:** a real interaction must be demonstrated; use the authorized app/window (`studio.py route showcase|tutorial`).
