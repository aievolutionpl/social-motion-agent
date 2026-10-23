---
name: motion-ui-polish
description: Make code-built video frames look designed instead of generated. Use whenever a film scene, title, dashboard, caption, lower third, chart, UI mock or any HTML/CSS/React frame is written in code for social-motion-agent. Gives starter tokens, anti-slop rules, safe areas, minimum sizes, and a measured gate (studio.py polish) built on the UX/UI Agent Skills kit.
---

# Motion UI Polish

Problem: frames coded by a model share tells that read as machine-made at once: indigo gradient, four equal cards, one radius and one flat shadow everywhere, tiny grey text, emoji as icons, a coloured bar on one side of a card. This skill removes them before render, and measures what can be measured.

Project root is three levels above this folder. Doctrine source: `tools/repos/ux-ui-agent-skills` (MIT, snapshot in `sources.lock.json`). Read only the parts a scene needs.

## Steps

1. Copy `templates/frame-tokens.css` and `templates/frame-starter.html` into the job's `source/`. Change only the brand block at the top of the tokens (accent, surfaces; take colours from the production brand brief). Never hardcode colour, size or shadow in a scene: use the variables.
2. Build the scene from tokens. Motion is a pure function of time (`window.seek(t)`, no timers, no `Math.random`), the contract `vstudio` and the HTML renderers expect. Choose effects with the `motion-effect-picker` skill, not by guessing.
3. Gate each distinct scene in every output format, at a time that shows the finished layout:

```powershell
python -S studio.py polish output/jobs/ID/source/scene.html --format 9:16 --seek 4.2 --shot output/jobs/ID/previews/scene-916.png
```

   It fails on: text outside the frame, overlapping texts, text under the readable minimum, emoji, and HIGH findings from `slop_tells` and `taste_audit`. Warnings (outside the safe area, weak hierarchy, clipped text) need a decision, not silence.
4. Open the screenshot and look at it. Gates prove measurable correctness, not taste. Then run the adversarial checklist below and fix what a stern designer would reject.
5. Only then render. Record in the job's HANDOFF.md which scenes passed `polish` and at which seek time.

## House rules for video frames

1. **One thing leads.** Display type at least 2.5x the body size. Four equal cards read as generated; give one item more size or its own row.
2. **Real type scale** (tokens): label 2.1, body 2.8, lead 3.6, title 6.4, display 9, hero 17 (cqmin, 1 cqmin = 1% of the short side). Nothing under 2% of the short side. Numbers use `.num` (tabular).
3. **4 px rhythm** (`--sp-*`). Related items tighter than unrelated ones.
4. **Several radii and shadows, each with a role** (chip, panel, card, pill; `--sh-1..3`, two layers each). Never one radius and one shadow everywhere.
5. **Full hairline borders or surface contrast.** Never a colour bar on one side of a card, alert or callout. Status = icon plus words.
6. **Colour by meaning.** One accent. Danger only for destructive or negative. No hardcoded indigo-to-purple gradient, no pure `#000` text or background (tokens use a tinted near-black).
7. **No emoji and no decorative pictographs.** Use inline SVG icons (`currentColor`) or words. No dash characters in on-screen text (workspace rule).
8. **Contrast:** body 4.5:1, large text 3:1. A caption over footage needs a scrim or pill (`.pill-caption`), never bare text.
9. **Safe areas.** 9:16 keeps the top 17% and bottom 30% of the width free of text (platform UI), sides 5.6%. 16:9 5.6% all round. Tokens set `--safe-*`; the gate checks it.
10. **Holds.** A text block stays at rest at least 0.5 s plus 0.3 s per word before leaving. Entrances 0.4 to 0.7 s, fast in and soft landing (ease-out). Move `transform` and `opacity` only.
11. **Extreme data:** long names, 0, 100%, many items. A scene must not break on them; test one extreme case.

## Adversarial checklist (before approving)

- Cover the headline: does the eye still land somewhere, or on nothing?
- Is there any element that is decoration only? Remove it.
- Squint: are there two competing focal points?
- Is any number shown without its unit, source or comparison?
- Would the scene look the same with another brand's name? Then it has no direction: take an aesthetic from `tools/repos/ux-ui-agent-skills/taste/aesthetic-systems.md` or a spec in `design-systems/library/<name>/DESIGN.md` (138 of them) and resolve it into the token block.

## Deeper references (load on demand)

| Need | File under `tools/repos/ux-ui-agent-skills/` |
|---|---|
| Anti-slop doctrine, banned defaults | `taste/design-taste.md` |
| Motion grammar (entrances, stagger, hover) | `taste/motion-choreography.md` |
| Charts and dense data screens | `components/data-viz.md`, `tokens/data-viz.json`, `examples/terminal/` |
| Palettes, OKLCH scales, dark mode | `.claude/rules/tokens-and-color.md` |
| UI copy, labels, empty states | `content/voice-tone.md` |
| Review rubric with scoring | `workflows/design-review.md`, `.claude/agents/design-critic.md` |
| A named look (Stripe, Linear, Apple...) | `design-systems/library/` + `taste/aesthetic-systems.md` |

Run upstream gates directly only when needed (from that folder, `DS_REQUIRE_BROWSER=1`, system Chrome): `node scripts/slop_tells.mjs <file>`, `node scripts/taste_audit.mjs <file>`, `node scripts/measure_render.mjs <file>` (WCAG contrast on the real render). Their results are heuristics: a strong signal, not a verdict. Do not edit the upstream checkout.
