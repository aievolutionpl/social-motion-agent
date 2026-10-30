---
name: motion-ui-polish
description: Make code-built video frames look designed instead of generated. Use whenever a film scene, title, dashboard, caption, lower third, chart, UI mock or any HTML/CSS/React frame is written in code for social-motion-agent. Gives starter tokens, unslop 5-line direction, 9-pass redline review, safe areas, minimum sizes, and a measured gate (studio.py polish).
---

# Motion UI Polish

Problem: frames coded by a model share tells that read as machine-made at once: indigo gradient, four equal cards, one radius and one flat shadow everywhere, tiny grey text, emoji as icons, shouty copy (`!!`), a coloured bar on one side of a card. This skill removes them before render, and measures what can be measured.

Project root is three levels above this folder. Doctrine sources: `tools/repos/ux-ui-agent-skills` (MIT) and `tools/repos/unslop` by Damir Sokolovsky (`@heydamir`, CC BY 4.0). Read only the parts a scene needs.

## Steps

1. Write the **5-line Unslop Direction** before touching code:
   - **Product:** What it does and for whom, in one plain sentence.
   - **Character:** 2–3 concrete words (never `clean`, `modern`, `sleek`, `minimal`, `premium`).
   - **World:** The physical material/environment (`data-ramp="graphite"` for apps/dashboards, `data-ramp="warm"` for paper/craft/human, `data-ramp="ink"` for night/technical/instruments).
   - **Moments:** 1–2 places that carry rich color and material detail while the chrome stays quiet.
   - **Signature:** One small product-specific detail used consistently.
2. Lock the visual style via `python -S studio.py styles recipe <style>` (see `.agents/skills/style-atlas/SKILL.md`).
3. Copy `templates/frame-tokens.css` and `templates/frame-starter.html` into the job's `source/`. Set `data-ramp="graphite|warm|ink"` on `<html>` and change only the brand block at the top of the tokens. Never hardcode colour, size or shadow in a scene: use the variables.
4. Build the scene from tokens in the **9-Pass Unslop Order**:
   `1. Spacing (4px grid)` → `2. Color (1 ramp, quiet chrome, 1 accent)` → `3. Icons (no emoji, 1 stroke)` → `4. Copy (no !!, no hype words, numbers always show comparison baseline)` → `5. Type (400-600 weights, tabular-nums)` → `6. Layout` → `7. Details (nested radius: inner = outer - padding >= 4)` → `8. Visuals (real preview or code treatment like drawGlyphs/drawHalftone)` → `9. Motion (window.seek(t), stepSpring, liquidSpan)`.
5. Gate each distinct scene in every output format, at a time that shows the finished layout:

```powershell
python -S studio.py polish output/jobs/ID/source/scene.html --format 9:16 --seek 4.2 --shot output/jobs/ID/previews/scene-916.png
```

   It fails on: text outside the frame, overlapping texts, text under the readable minimum, emoji, gradient text (`-webkit-background-clip: text`), and HIGH findings from `slop_tells` and `taste_audit`. Warnings (outside the safe area, weak hierarchy, clipped text, hype words/`!!`, excessive font-weight `>=800`, negative tracking on small text) need a decision, not silence.
6. Open the screenshot and look at it. Gates prove measurable correctness, not taste. Then run the adversarial checklist below and fix what a stern designer would reject.
7. Only then render. Record in the job's HANDOFF.md which scenes passed `polish` and at which seek time.

## House rules for video frames

1. **One thing leads.** Display type at least 2.5x the body size. Four equal cards read as generated; give one item more size or its own row.
2. **Real type scale** (tokens): label 2.1, body 2.8, lead 3.6, title 6.4, display 9, hero 17 (cqmin, 1 cqmin = 1% of the short side). Nothing under 2% of the short side. Numbers use `.num` (tabular).
3. **4 px rhythm** (`--sp-*`). Related items tighter than unrelated ones.
4. **Nested radii and layered shadows** (chip, panel, card, pill; `inner_radius = max(4px, outer_radius - padding)`; `--sh-1..3`, two layers each). Never one radius and one shadow everywhere.
5. **Full hairline borders or surface contrast.** Never a colour bar on one side of a card, alert or callout. Status = icon plus words.
6. **Quiet chrome, rich moments.** One tinted neutral ramp (`graphite`, `warm`, `ink`). One accent. No hardcoded indigo-to-purple gradient, no gradient text, no pure `#000` background.
7. **No emoji, no hype copy, no `!!`.** Use inline SVG icons (`currentColor`) or words. Changes always name their comparison baseline (e.g. `+12% vs last month`).
8. **Contrast:** body 4.5:1, large text 3:1. A caption over footage needs a scrim or pill (`.pill-caption`), never bare text.
9. **Safe areas.** 9:16 keeps the top 17% and bottom 30% of the width free of text (platform UI), sides 5.6%. 16:9 5.6% all round. Tokens set `--safe-*`; the gate checks it.
10. **Holds & pure `seek(t)`.** A text block stays at rest at least 0.5 s plus 0.3 s per word before leaving. Entrances 0.4 to 0.7 s, fast in and soft landing (`easeOut`, `stepSpring`, `liquidSpan`). Move `transform` and `opacity` only. Never put `will-change` on containers scaled by the camera.
11. **Extreme data:** long names, 0, 100%, many items. A scene must not break on them; test one extreme case.

## Adversarial checklist (before approving)

- Cover the headline: does the eye still land somewhere, or on nothing?
- Is there any element that is decoration only? Remove it.
- Squint: are there two competing focal points?
- Is any number shown without its unit, source or comparison?
- Would the scene look the same with another brand's name? Then it has no direction: lock a style via `studio.py styles recipe <style>` and push the 5-line Unslop Direction (`Moments` and `Signature`).

## Deeper references (load on demand)

| Need | File |
|---|---|
| 12 coded-video styles & 1100+ prompts | `.agents/skills/style-atlas/SKILL.md`, `studio.py styles` |
| Unslop 9-pass redline & story video | `tools/repos/unslop/skills/unslop/SKILL.md`, `studio.py unslop-story` |
| Anti-slop doctrine, banned defaults | `tools/repos/ux-ui-agent-skills/taste/design-taste.md` |
| Motion grammar (entrances, stagger, hover) | `tools/repos/ux-ui-agent-skills/taste/motion-choreography.md` |
| Charts and dense data screens | `tools/repos/ux-ui-agent-skills/components/data-viz.md` |
| Palettes, OKLCH scales, dark mode | `tools/repos/ux-ui-agent-skills/.claude/rules/tokens-and-color.md` |
| Review rubric with scoring | `tools/repos/ux-ui-agent-skills/workflows/design-review.md` |
