---
name: creative-director
description: "Design and produce distinctive websites, motion videos and animated product interfaces, or act as a specialized Motion & UI Subagent. Combines a 5-line Unslop direction, 12 canonical Opus 5.5 style recipes, 1100+ coded-video prompt patterns, 9-pass redline review and verified output."
---

# Creative Director & Motion Subagent

Turn a real subject into a coherent visual experience, then verify the result in its actual medium. This is the portable creative entry point and **subagent orchestrator** for Social Motion Agent, usable by Codex, Claude Code, Antigravity, Hermes and other agents that can read Markdown and work with files. A GitHub connection gives access to sources; it does not install a renderer or prove that a tool works.

## Select the work

| Request | Mode | Read next |
| --- | --- | --- |
| Reel, explainer, launch film, tutorial, edited footage | `video` | [Video direction](references/video-direction.md) |
| Landing page, product website, substantial website redesign / unslopping | `website` | [Website design](references/website-design.md) |
| Animate a supplied Figma frame, screenshot, product mockup or unslop redline story | `ui-motion` | [UI to motion](references/ui-to-motion.md) |

A site with a small animated feature remains a website; do not export a film unless requested. A film showing an app is not permission to redesign that app. For a small copy or component correction, reuse the current direction and read only the relevant module.

## Subagent Delegation Protocol

When invoked as a specialized **Motion / Design Subagent** by a parent orchestrator (or when dividing a film across subagents), follow this 4-stage contract:

1. **Stage 1 — Style Scout & 5-Line Direction:**
   - Query `python -S studio.py styles list`, `studio.py styles recipe <style>` and `studio.py styles find <query>` to lock one of the **12 canonical coded-video styles** (`typography`, `productui`, `explainer`, `cinematic3d`, `handdrawn`, `collage`, `pixel`, `cartoon`, `lowpoly`, `generative`, `retro`, `photoreal`).
   - Write the **5-line Unslop Direction**: `Product`, `Character` (no template words like *clean/modern/sleek*), `World` (determines `data-ramp="graphite|warm|ink"`), `Moments` (1–2 rich elements while chrome stays quiet), and `Signature` (1 unique product detail).
2. **Stage 2 — Deterministic Scene Coding (`window.seek(t)`):**
   - Implement scenes using `templates/frame-tokens.css` and `templates/motion-helpers.js` (`stepSpring`, `springTimeline`, `liquidSpan`, `bakeGlyphAtlas`, `drawGlyphs`, `drawHalftone`).
   - Every visual state must be a pure function of time `t` inside `window.seek(t)`: no CSS transitions during capture, no timers, no `Math.random()` in the frame loop, and no `will-change` on containers scaled by the camera.
3. **Stage 3 — 9-Pass Unslop Redline & Polish Gate:**
   - Audit and fix in strict order: `1. Spacing (4px grid)` → `2. Color (1 ramp, quiet chrome, 1 accent)` → `3. Icons (no emoji)` → `4. Copy (no !!, no hype, numbers with comparison baseline)` → `5. Type (400-600 weights, tabular-nums)` → `6. Layout` → `7. Details (nested radius: inner = outer - padding >= 4)` → `8. Visuals` → `9. Motion`.
   - Run `python -S studio.py polish <scene.html> --format <fmt> --seek <sec> --shot <png>` and inspect the actual screenshot.
4. **Stage 4 — Render, Probe & Evidence Handoff:**
   - Render via `studio.py render-html` or `render-assembly`, run `probe` and `sheet`, and return a structured JSON/Markdown summary with the output path, SHA-256, verified checks and any open limitations.

## Begin with context and a useful choice

1. Inspect the current project, its instructions, brand, existing components and supplied assets. Preserve working architecture and explicit visual choices. Record what imagery, footage and evidence actually exist.
2. Read [Brief and art direction](references/brief-and-direction.md). Reuse answers already supplied. Ask the missing material questions together, normally no more than five; do not run an interview again for revisions. Respect a request to choose autonomously or skip questions.
3. When the direction is open, present two or three distinct concepts with actual shot/section placements, asset needs and motion behavior. Recommend one. A compact styleboard or one representative frame is more useful than a list of adjectives. Wait for a requested choice; if the user delegated it, choose and explain in one sentence.
4. Fix the direction in a short working note: 5-line Unslop Direction (`Product`, `Character`, `World`, `Moments`, `Signature`), selected Style Lock recipe, layout/type/color roles, motion grammar, asset sources, output profile and review criteria.

## Prepare only the capabilities this job uses

Read [Engines and setup](references/engines-and-setup.md). Locate the Social Motion Agent checkout by its `studio.py`, `config/routes.json` and `sources.lock.json`; do not derive it from an installed skill's location.

From that checkout, select a focused plan:

```bash
python -S studio.py skills plan --mode video
python -S studio.py skills setup --mode video
```

Replace `video` with `website` or `ui-motion` as appropriate. `plan` is read-only. If the selected files exist, use `skills check --mode MODE` to verify them; run `setup` only for missing sources. Preserve and report a modified checkout instead of overwriting it. Setup fetches pinned sources; it does not install every upstream application or activate provider accounts. Read selected upstream entry points on demand, not the whole catalogue.

For new film production, use the existing `studio.py new` records, stage checks and render adapters. For a website in another repository, use its existing stack and checks; these creative references work without the video workspace.

Hypermotion and HyperFrames are different products. If Hypermotion is requested, prepare its pinned sources and two skills, then verify its desktop/CLI and a small native export before committing to that engine. Do not silently switch to HyperFrames when Hypermotion is unavailable.

## Build one representative piece, then extend it

Make the hero/first screen, one key scene, or the supplied UI's accurate still first. Check hierarchy, crop and readability at the target size before building the whole sequence. Extend the same visual system through the remaining sections/scenes; change layout when the content requires it.

Use [Visual recipes](references/visual-recipes.md) and `python -S studio.py styles` to choose a starting composition, Style Lock recipe and motion vocabulary. Use the smallest specialist set that improves the result: one lead mode, one art direction, then audio, captions, data or capture guidance only when needed.

For words, captions and narration, read [Humanizer](references/humanizer.md). For generic composition, UI slop or motion problems, read [Anti-slop review](references/anti-slop.md).

## Review the actual output

Follow [Review and delivery](references/review-and-delivery.md). Inspect rendered frames or browser screenshots, test meaningful interactions, and listen to the actual mix when audio is present. Repair the most consequential problems and recheck what changed. If a required tool is unavailable, identify the missing check and preserve a reviewable draft.

Report what was built, where the user can view it, what was actually verified and what remains open. Do not claim virality, commercial rights, pixel fidelity, live recording, working accounts or human approval without evidence. Paid generation and publication require the user's authorization; the creative brief does not grant it automatically.

## Sources

This skill is an authored synthesis with selected upstream design methods, not a concatenation of upstream prompts. Read [Sources and adaptation](references/sources.md) when updating or redistributing it. Licenses for adapted MIT and CC BY 4.0 guidance travel in `licenses/`.
