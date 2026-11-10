# ShotCraft Motion Pack | Social Motion Agent

## Implementation status (this repository)

- **10 curated reference shots** in `config/shotcraft-recipes.json`, each linked to the upstream source.
- **5 interactive Canvas previews** in `examples/shotcraft-motion/index.html`, seekable and deterministic; not production video renderers.
- **4 frame-accurate storyboard sequences** in `studio.py shotcraft plan`, with explicit missing-assets and evidence warnings.
- **One actual 15-second GSAP/HyperFrames composition source** at `examples/shotcraft-motion/film/index.html`. Uses synthetic typography/cards and no licensed external media, so it can be edited into a new production after brand and material replacement. A CI lint gate checks renderer syntax when the runtime is installed; a final MP4 and review still require an explicit render and QA.

Quick try:

```bash
python -S studio.py shotcraft list
python -S studio.py shotcraft plan app-launch --duration 15 --fps 30 --brand "Brand" --cta "Visit"
python -m http.server 8000  # Open /examples/shotcraft-motion/
npm ci
node scripts/prepare-example.mjs
node node_modules/hyperframes/bin/hyperframes.mjs lint examples/shotcraft-motion/film
```



A curated, **reference-based** extension for premium product demos and social video. Inspired by [Video ShotCraft](https://github.com/Vincentwei1021/video-shotcraft) by Vincentwei1021. This document is original integration guidance, **not copied source code**. Source assets and implementations remain upstream under their respective licenses (Video ShotCraft: Apache-2.0); do not relicense upstream assets as this repository's own work.

## Production contract
1. Inspect user assets, platform, brand, duration, rights, and intended viewer action. Never invent customer metrics or replicate confidential UI.
2. Offer 2–3 distinct creative directions with a concise shot list, typography, motion energy, and sound approach. Respect the user's explicit choice or delegation. Do not re-ask known preferences.
3. Choose at most 2–4 **hero** motion techniques for a 15-second spot. One dominant action per shot, a readable settled state, and an ending hold. Adapt color/type/layout to the actual brand.
4. Build a beat/shot timeline with durations, frame counts and cut positions. For music-led edits measure beats/transients; don't assume an arbitrary BPM. For silent films, rely on clear visual rhythm.
5. Prototype a representative scene first. For real product demonstrations, capture real UI and anonymize sensitive data rather than inventing screens.
6. Implement with the existing HyperFrames/GSAP route where practical; use a separate Remotion project only if the shot requires its specific composition/renderer. Do not claim a Remotion recipe runs directly in HyperFrames.
7. Render preview, inspect actual frames and audio, gather timestamped feedback, then revise. Run existing editor QA and release checks; do not claim unrun tests passed.

## Curated shot recipes (read upstream card AND its linked demo before recreating exact motion)
| ID | Upstream card | Best for | Adaptation / failure check |
|---|---|---|---|
| carousel-3d | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/carousel-3d.md) | product feature gallery, campaign variants | depth/parallax; avoid unreadable perspective text |
| deck-deal-flyin | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/deck-deal-flyin.md) | multiple offers/features | one coherent acceleration, no repetitive glowing cards |
| card-stack | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/card-stack.md) | before/after process or multiple outcomes | pause at each legible state |
| flying-words | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/typography/flying-words.md) | hook and payoff keywords | 3–6 words, readable contrast and landing |
| type-rhythm-sync | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/typography/type-rhythm-sync.md) | music-driven headlines | use measured beat grid; check readability |
| value-stagger-gradient | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/value-stagger-gradient.md) | real KPIs, progress, stats | source each value; avoid misleading animation |
| chart-live-moves | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/data/chart-live-moves.md) | data storytelling | accurate scale, labels and units |
| before-after-slider-scrub | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/data/before-after-slider-scrub.md) | edit transformations, UI improvements | same camera/scene where comparison claims are made |
| page-waterfall-wall | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/page-waterfall-wall.md) | real website/app showcase | use approved real captures and mask PII |
| draw-svg-trace | [recipe](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/shots/ui-entrance/draw-svg-trace.md) | explainers, flows, diagrams | keep line sequence meaningful |

Upstream lookup: [Gallery](https://vincentwei1021.github.io/video-shotcraft/) and [gallery/api/library.json](https://github.com/Vincentwei1021/video-shotcraft/blob/main/gallery/api/library.json). Match recipe ID and variant to the actual demo implementation before attempting close reproduction. Do not blindly vendor the entire upstream library.

## Ready-to-adapt 15-second structures

### Premium product reel (9:16)
- 0.0–2.5 s: real product hero + flying-words hook.
- 2.5–5.5 s: carousel-3d reveals three benefits.
- 5.5–9.5 s: actual interface/footage with a controlled camera move.
- 9.5–12.5 s: credible proof or before/after.
- 12.5–15 s: single CTA, hold long enough to read.

### App launch (16:9)
- 0–3 s: problem and hero feature.
- 3–7 s: page-waterfall-wall with real, sanitized screens.
- 7–11 s: deck-deal-flyin to group features.
- 11–13 s: one truthful result or key benefit.
- 13–15 s: brand lockup and CTA.

### Educational explainer (4:5)
- 0–3 s: one clear problem.
- 3–7 s: draw-svg-trace explains process.
- 7–11 s: chart-live-moves only if sourced data exists; otherwise an illustrative labeled diagram.
- 11–15 s: solution, one action, readable end card.

## Technical notes
- ShotCraft demos are Remotion/React; the existing HyperFrames route uses HTML/GSAP. Port the motion **principle**, not TSX imports. If exact reproduction is needed, create an isolated Remotion composition with explicit dependencies and check its license.
- Render deterministically: frame-derived timing and seeded pseudo-randomness; avoid wall-clock animation and unseeded randomness.
- Reserve static holds and transition handles in the timeline. Don't stack 3D rotation, zoom, glow and word scatter simultaneously.
- Test 9:16, 4:5, 16:9 safe areas, text legibility on mobile, contrast, audio peaks, frame boundaries and real export.
- Attribute copied third-party code/media individually in THIRD_PARTY_NOTICES.md and confirm asset permissions before publishing.

## Example agent request
> Create a premium 15-second 9:16 product reel. Use the ShotCraft Motion Pack for a 3D feature carousel and a flying-words opener. Start with two different style proposals and a second-by-second storyboard. Use my original product assets, preserve the brand, make a representative preview, then render and QA. No fabricated claims.
