---
name: motion-effect-picker
description: Choose the right motion for a scene from a catalogue of 637 effects and 11 recipes (awesome-ai-motion) instead of improvising, then implement it as a pure function of time. Use when planning or building any animated scene, title reveal, transition, chart build, hook or caption in social-motion-agent.
---

# Motion Effect Picker

Source: `tools/repos/awesome-ai-motion` (MIT; GSAP bundled under its no-charge licence, see its ATTRIBUTIONS.md). 637 effect cards, 128 of them with a rendered clip and HTML template, 11 recipes, decision tables. Never read the whole index; query it.

## Steps

1. State the scene intent and medium in one sentence ("the question that opens the video, shorts").
2. Query:

```powershell
python -S studio.py motion find reveal --purpose attention --medium shorts --rendered --limit 8
python -S studio.py motion show mask-reveal
python -S studio.py motion recipe            # lista receptur
python -S studio.py motion recipe edu-hook   # kroki z czasem i parametrami
```

   Purposes: attention, explanation, comparison, sequence, emphasis, transition, data, feedback, atmosphere, branding. Media: explainer, shorts, scrolldeck, presentation, product-demo, data-story, web-ui. Also `--family`, `--level`.
3. Choose 2 or 3 candidates, read each card's `use_when`, `avoid`, `params`, `ease`, `pairs_with`. Take the card defaults first, then adjust.
4. Compose with the shared rules: one focus per scene, one main action plus one or two supporting, the finished state held long enough to read, `transform` and `opacity` only.
5. Implement as a pure function of time. The card `snippet` is GSAP; translate it, do not import it:
   - seconds to progress: `p = clamp((t - start) / duration)`; stagger = `start + i * gap`
   - easing from `templates/motion-helpers.js` (`easeOut`, `easeIn`, `easeInOut`, `backOut`, `elasticOut`, `spring`): `power3.out` is `easeOut(3)`
   - `yPercent: 110 -> 0` is `translateY(110% -> 0%)` on the line inside an `overflow: hidden` window
6. Build with `motion-ui-polish` (tokens and gate), view the frames at start, main action and end state, compare with the card's `good_example`.

## When a template exists

If `show` prints `html_template`, open it to see structure and timing, copy it into the job's `source/`, and replace text or data. Keep the timeline. Do not run the catalogue's `render.mjs` without installing its Playwright dependency; our pipeline renders through `vstudio` or the HTML renderer.

## First five seconds (educational and explainer videos)

0 to 1 s a question or surprising result; 1 to 3 s a clue to the mechanism or comparison; 3 to 5 s the learning promise with a readable hold. One claim per screen. Large camera moves only to reveal the question or the result. Start from `motion recipe edu-hook`, then `mask-reveal`, `split-compare`, `count-up`, `annotation-callout`.

## Limits

- Card parameter names are partly Korean; values, ranges, `ease` and `snippet` are language neutral. Descriptions and prompts come back in English.
- A `planned` card has no clip or template; use its parameters and prompt only.
- Overused effects look generated. Do not repeat one effect on more than one element per scene, and do not stack three effects on the same moment.
