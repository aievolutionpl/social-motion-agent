---
name: creative-director
description: "Design and produce distinctive websites, motion videos and animated product interfaces. Use for a new creative direction, a substantial visual redesign, a social film or a design-to-motion showcase; combines a focused brief, art direction, selected specialist skills and visual review."
---

# Creative Director

Turn a real subject into a coherent visual experience, then verify the result in its actual medium. This is the portable creative entry point for Social Motion Agent, usable by Codex, Claude Code, Hermes and other agents that can read Markdown and work with files. A GitHub connection gives access to sources; it does not install a renderer or prove that a tool works.

## Select the work

| Request | Mode | Read next |
| --- | --- | --- |
| Reel, explainer, launch film, tutorial, edited footage | `video` | [Video direction](references/video-direction.md) |
| Landing page, product website, substantial website redesign | `website` | [Website design](references/website-design.md) |
| Animate a supplied Figma frame, screenshot or product mockup | `ui-motion` | [UI to motion](references/ui-to-motion.md) |

A site with a small animated feature remains a website; do not export a film unless requested. A film showing an app is not permission to redesign that app. For a small copy or component correction, reuse the current direction and read only the relevant module.

## Begin with context and a useful choice

1. Inspect the current project, its instructions, brand, existing components and supplied assets. Preserve working architecture and explicit visual choices. Record what imagery, footage and evidence actually exist.
2. Read [Brief and art direction](references/brief-and-direction.md). Reuse answers already supplied. Ask the missing material questions together, normally no more than five; do not run an interview again for revisions. Respect a request to choose autonomously or skip questions.
3. When the direction is open, present two or three distinct concepts with actual shot/section placements, asset needs and motion behavior. Recommend one. A compact styleboard or one representative frame is more useful than a list of adjectives. Wait for a requested choice; if the user delegated it, choose and explain in one sentence.
4. Fix the direction in a short working note: audience, intended action, central visual idea, layout/type/color roles, motion grammar, asset sources, output profile and review criteria. Treat it as the current decision record, not an extra deliverable the user must manage.

## Prepare only the capabilities this job uses

Read [Engines and setup](references/engines-and-setup.md). Locate the Social Motion Agent checkout by its `studio.py`, `config/routes.json` and `sources.lock.json`; do not derive it from an installed skill's location.

From that checkout, select a focused plan:

```bash
python -S studio.py skills plan --mode video
python -S studio.py skills setup --mode video
```

Replace `video` with `website` or `ui-motion` as appropriate. `plan` is read-only. If the selected files exist, use `skills check --mode MODE` to verify them; run `setup` only for missing sources. Preserve and report a modified checkout instead of overwriting it. Setup fetches pinned sources; it does not install every upstream application or activate provider accounts. Read selected upstream entry points on demand, not the whole catalogue.

For new film production, use the existing `studio.py new` records, stage checks and render adapters. For a website in another repository, use its existing stack and checks; these creative references work without the video workspace. If motion production needs a checkout, follow the setup reference without writing into an installed skill folder.

Hypermotion and HyperFrames are different products. If Hypermotion is requested, prepare its pinned sources and two skills, then verify its desktop/CLI and a small native export before committing to that engine. Do not silently switch to HyperFrames when Hypermotion is unavailable.

## Build one representative piece, then extend it

Make the hero/first screen, one key scene, or the supplied UI's accurate still first. Check hierarchy, crop and readability at the target size before building the whole sequence. Extend the same visual system through the remaining sections/scenes; change layout when the content requires it.

Use [Visual recipes](references/visual-recipes.md) to choose a starting composition and motion vocabulary. Recipes are options, not compulsory templates. Use the smallest specialist set that improves the result: one lead mode, one art direction, then audio, captions, data or capture guidance only when needed.

For words, captions and narration, read [Humanizer](references/humanizer.md). For generic composition or motion problems, read [Anti-slop review](references/anti-slop.md). These are editorial checks, not banned-font lists or a score that certifies quality.

## Review the actual output

Follow [Review and delivery](references/review-and-delivery.md). Inspect rendered frames or browser screenshots, test meaningful interactions, and listen to the actual mix when audio is present. Repair the most consequential problems and recheck what changed. If a required tool is unavailable, identify the missing check and preserve a reviewable draft.

Report what was built, where the user can view it, what was actually verified and what remains open. Do not claim virality, commercial rights, pixel fidelity, live recording, working accounts or human approval without evidence. Paid generation and publication require the user's authorization; the creative brief does not grant it automatically.

## Sources

This skill is an authored synthesis with selected upstream design methods, not a concatenation of upstream prompts. Read [Sources and adaptation](references/sources.md) when updating or redistributing it. Licenses for adapted MIT guidance travel in `licenses/`.
