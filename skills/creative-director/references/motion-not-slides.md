# Motion, not slides

Read for openers, promos, bumpers, kinetic typography and explainers built as HTML/Canvas scenes, and for any revision that "feels like a presentation". It adds a structural test, a style-brief template and direction menus to [Video direction](video-direction.md); it does not replace the job records, render adapters or review gates. Original wording for Social Motion Agent, adapted from the ideas in [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion/tree/c1aa65e921c970d858705fcb4a53a8294d1a4131) (MIT, notice in `../licenses/bang-motion-MIT.txt`).

The menus are starting points chosen per brief. The user's brand, an approved direction and the target project's choices come first; nothing here is a font ban, an animation quota or a reason to override supplied assets.

```bash
python -S studio.py directions list                       # menu sizes
python -S studio.py directions list opener_concepts       # 19 concepts
python -S studio.py directions brief --for "AI note app for students"            # 3 concept + 3 direction candidates
python -S studio.py directions brief --kind explainer --for "how a container port works"
python -S studio.py directions compare "FP1" "FP2"         # novelty of two structure fingerprints
python -S studio.py motion lint output/jobs/<id>/source/index.html
```

`brief` ranks candidates by the words of the brief and shows the `match` score; it is a conversation starter, not a creative decision. Present the candidates, recommend one with a product reason and wait for a requested choice.

## Why scenes become slides

A model organizes information as heading → explanation → supporting evidence. That is right for a document and wrong for a film: a promo states one thing per shot and lets motion and sound carry the feeling. When a scene "lacks information", it is usually correct.

## Structural test — check the code, not the feeling

Run these before showing a draft. Failing one means rework, not polish.

1. **Sections switched by opacity.** Three or more `<section>`/`.scene` blocks turned on and off with opacity, `autoAlpha` or visibility is a slide deck whatever the transition. Change scenes because the world or camera moves, an object carries the change, or a motivated cut lands. Exception: a cartoon-stage explainer may cut between stages when every stage is fully alive (10+ moving things).
2. **A persistent visual thread.** One subject that stays (continuous action) or one collage/paper/white world the camera travels. Full-bleed photos replacing each other with no shared world is a slideshow; so is one picture + one sentence per scene even with camera moves. An explainer scene builds 3–5 elements per phrase.
3. **Text tiers.** Kicker + title + body/credit in one scene is a slide layout. Keep at most one big number/sentence plus one world label. A stamp, document or date block of ≤3 short lines counts as an object. UI mockups are read as images and keep their real density.
4. **Ken Burns as the only motion.** Every second needs motion from the chosen background-motion language, not just a 1.0→1.05 photo zoom.
5. **One transition everywhere.** Fade + scale bump + light leak on every cut is a template. Mix a whip, a cut to an instrument (map, speedometer, profile), a push-through when motivated.
6. **Miniatures.** A world so zoomed out that houses are thumbnail-size and empty ground fills half the frame reads as a slide even when everything moves. Split the world into frame-size stages.
7. **The template skeleton (openers).** Text zooms up then exits left; three aligned feature tiles; a typed search bar; hook → feature → feature → promise → logo → CTA. Two or more of these without a concept that demands them is a template with a new skin.

`studio.py motion lint` checks 1 and 3 mechanically, plus the Social Motion render contract (no `Math.random()`, no system clock in visual state, `window.seek(t)` or a paused timeline, no `<video autoplay/loop>`, no CSS transitions/animations on their own clock, no `will-change` on camera-scaled containers). It is static: follow it with `studio.py polish` and real frames.

## Style brief before code

Write the brief and a rundown (`second | scene | line | visual`) and show them before building; rebuilding a rundown is cheap, rebuilding code is not. `studio.py directions brief` prints the fields:

- subject and three adjectives for the feeling it should leave;
- three concept candidates, one chosen with a reason from the product (*what is most convincing when SEEN*, not easiest to build);
- **structure fingerprint**: `concept · scene count · main object per scene · opening · ending`;
- palette: main color from the brand (logo, icon, site, packaging), background, accent — every hex with its source or `derived: reason`;
- display font with character + companion; a product-UI concept uses the product's UI font;
- text emphasis: none, or exactly one highlight form for the whole film;
- background plan per segment: one direction, or which segment changes, to what, why and with what visible trigger;
- motion signature (objects/text) and background motion (world) as two separate choices;
- background surface with at least two layers; one object render family;
- asset sources (user material, authorized generation, licensed stock) and a shot list; generated people are fictional, logos and brand text are added in code;
- which boundaries get a transition and which are plain cuts; one special moment for the most expensive effect, once.

**Reference = rhythm, not skin.** From a supplied reference take shot duration, transition type, attention order, energy and motion language. Do not take its palette, fonts, textures, layout, ornament shapes, sentences, scene order or one-off signature moment. "Make it like this" means "this energetic". Say so in one sentence and offer a version born from the subject.

**Different from the previous project.** Two products differ in at least three of palette, font, background language and motion signature, and in structure: a different concept or ≥3 of 5 fingerprint parts (`directions compare`). New colors on an old scene order is still a template. Do not open old project folders for "examples".

## Direction menus

`config/motion-directions.json` holds the full menus; the canvas laboratory (`examples/motion-styles/`) has a seekable example for the directions marked below.

| Style direction | Background · type · signature motion | Lab preset |
| --- | --- | --- |
| Cinematic dark | near-black gradient, bloom only on objects · bold grotesk · push-through, light in front of the lens | — |
| Poster color-block | solid fields per scene · ultra-heavy giant cropped words · block wipes, words slam into the frame edge | `poster-color-block` |
| Editorial light | white/cream, hairlines · display serif + small grotesk · lines draw, calm camera | — |
| Paper & print | paper, collage, tape · handwriting + serif · objects fly in and land at an angle | `cartoon-collage` |
| Retro / analog | faded color, grain, scanlines · 70s–90s geometric · controlled glitch, freeze | — |
| Brutalist mono | black/white hard grid · mono + condensed · hard cuts, shifting blocks, cursor | `brutalist-mono` |
| Pastel playful | stacked pastels, round shapes · heavy rounded sans · elastic bounce | — |
| Luxury dark | black + gold, soft sheen · tall tracked serif · slow motion, one light sweep, depth | `luxury-dark` |
| Flat pop with photos | neutral light ↔ brand color fields · rounded heavy sans · cutouts pop, stickers burst, fields snap with a trigger | `flat-pop` |
| Grainy gradient | deep base, glowing 2–3 color shapes, fine grain · small grotesk · layers open, camera through openings, guide orb | `grainy-gradient` |

Explainer modes: **continuous action** (one subject never leaves, viewpoint and instruments change — `continuous-action`), **cartoon collage** (`cartoon-collage`), **visual journalism** (`visual-journalism`), **white catalog** (`white-catalog`), **vintage sketch** (`vintage-sketch`) and **cartoon stage** (one living stage per scene, jointed characters, zoom 1.08–1.95 inside the stage, short cut/slide between stages, no captions). Two consecutive films on the same direction row is a warning sign: choose another row or combine two deliberately. They complement the Style Atlas (`studio.py styles`) and the two explainer directions in [Explainer styles](explainer-styles.md).

Nineteen opener concepts: one continuous shot · pure typography · problem → gone · before/after · journey inside the UI · product macro · object metaphor · living number · one feature fully demoed · diegetic question → answer · rhythmic collage · logo as stage · object relay · brand system showcase · claim → how → result · living UI ecosystem · flat pop with photos · through the gradient shapes · product tour with claims. Take each concept's principle and motion language; build new beats from the user's product. Example sequences are not scripts, the opening and ending differ from any example, and a signature moment is used at most once and transformed by the brand.

Canonical components (zoom-text exit, three tiles, typed input, push-through between every scene, light leak at the cut, centered logo + CTA) are allowed only when the concept demands them, at most two per opener. Openings and endings menus are in the JSON (`directions list openings|endings`).

## Background never sits still, text pocket stays calm

- Choose one background-motion language (two if segments change): textured surface + breathing camera, travelling gradient, floating blobs, living grain, one light sweep per segment, rotating brand geometry, rising particles, breathing grid, ghost type, parallax photo, horizontal flow (only when the subject is speed/flow), snapping color fields. Avoid reusing the previous project's choice.
- Surface: at least two layers (base + glow/texture/blobs) from palette colors; flat single color only for poster color-block (with grain) or flat pop (fields change fast and are always filled with moving shapes).
- Background color may change whenever the content needs it, with a visible trigger (object covers the lens, UI action, push into a field, cut on the beat) — never an unexplained cross-fade.
- Under text the background is dark (≤25% luminance) or light (≥80%), never busy midtone; background elements in the pocket stay dim (opacity ≤ .35), ≤ 40 bright elements visible; grayscale-test the frame. Glow belongs to objects; headings stay clean with a thin shadow.
- Grainy gradients: gradients inside the shapes plus one fine monochrome grain layer over everything, offset from `t` (`grainOffset` in `templates/motion-helpers.js`). Encode with high quality (e.g. libx264 `-crf 10-12 -tune grain`) and check the MP4 for banding, not only the browser.

## Camera, rhythm and transitions

- **Shot size, not breathing.** "Zoom in-out" means the camera approaches the element that is speaking (medium close-up/close-up) and returns to wide when the composition needs the whole frame. A few percent of breathing is a base layer, not the answer to a static film. Text appears after the camera arrives. Labels and captions live on a screen layer outside the camera rig. Use `shotCamera`, `frameOn` and `cameraTransform` from `templates/motion-helpers.js`; keep one scale system per wrapper and overscan the world so edges never show.
- **Asymmetric rhythm.** Enter slow and decisive (0.7–1.3 s, power4.out), exit fast (0.35–0.55 s, power2.in) — `enterExit`. Symmetric timing feels mechanical. Two consecutive scenes do not share text size, entry direction and position.
- **Directional motion blur.** Blur along the motion (`feGaussianBlur stdDeviation="x y"`, `directionalBlur`), widen the filter box so tails are not clipped, and remove the filter when the blur reaches zero.
- **Transition menu.** 3D push-through · card rotating in from depth · object with thickness passing the lens · soft light sweep (40–60% of frame) · brand-shape mask reveal · whip with directional blur (never reveal the world edge) · rack focus · overlapping choreography without a cut · background swap behind any of these. Use the effect only where a boundary needs it; flat full-frame color bars and thin sweeping lines are weak defaults. A push-through is motivated (diving into a screen, through a logo opening), about once per film.
- **Living UI.** For app/SaaS, at least one act assembles the product's real components, uses them and produces a result; a zoomed static screenshot is not a demo. Follow important clicks (close → click → back), not every click.

## Explainer specifics

- One question about style, ratio, duration and voice together when unknown; default 16:9, 9:16 only when requested; no subtitles unless requested. Scene count follows the content, not duration ÷ 6.
- Every person, company, place or product named appears in that scene; facts are sourced, illustrative quantities are labelled.
- Viewpoints change: no three consecutive scenes from the same angle; each fact gets its instrument (map, speedometer, elevation profile, race on a map, interior, front view).
- Phone readability on a 1080 stage: body ≥ 44 px, labels ≥ 34 px, credits ≥ 30 px; `studio.py polish` measures the real render.
- Collage camera choreography: close-up → glide → zoom out, not elements fading in and out on a fixed frame.
- With a voice-over, the decoded recording is the master timeline. Without one, deliver the full VO script with the draft so the user can record or authorize generation; never synthesize a voice without permission.

## Review

Capture 6–20 key seconds (scene starts, text arrivals, transitions) at real display size and judge like a director: cropped or overlapping text, text arriving before the camera, slide feel. Fix and capture again; rendering every frame is not verification. Then render with the existing adapter, probe and review the encoded file as described in [Review and delivery](review-and-delivery.md). Passing the lint or the structural test is not creative approval.
