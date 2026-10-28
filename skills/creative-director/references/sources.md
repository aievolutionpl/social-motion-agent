# Sources and adaptation

Reviewed on 2026-10-26. This package contains original instructions written for Social Motion Agent, informed by the following primary sources. It is not an official release or endorsement from those projects. Upstream text is design input, not an instruction to override the user's brief or run arbitrary commands.

## Selected upstream methods

| Source and pinned revision | Read paths | What informs this skill |
| --- | --- | --- |
| [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills/tree/eabf86665588de0eb4c9e2fbf5fc9d3ae807e9f1), MIT, copyright 2026 Elaya | `skills/landing-page-design/SKILL.md`; `skills/design-to-motion/SKILL.md` | Purpose-driven page structure, targeted intake, faithful UI reconstruction, state-based motion, deterministic capture and loop review |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/12af471f627f866411b4bd785b19646d3672784c), MIT, copyright 2026 Leonxlnx | `skills/taste-skill/SKILL.md` (`design-taste-frontend`, titled tasteskill v2); its linked page/app guidance | Subject-specific art direction, multiple composition choices, distinction between pages and working app screens, screenshot-led iteration |
| [psiddharthdesign/hypermotion](https://github.com/psiddharthdesign/hypermotion/tree/e510cd60c0d2632863b5a3f78dba71b905c75ff2), Apache-2.0 | `skills/hypermotion-brand-profile/SKILL.md`; `skills/hypermotion-explainer-director/SKILL.md`; setup documentation | Existing optional native scene workflow and the need to distinguish its source skills, CLI and desktop runtime |

The full pinned sources are managed by the repository's `sources.lock.json` and bootstrap workflow. Their licenses remain their own. The standalone Creative Director package does not include Hypermotion implementation code or replace its Apache notices. It retains the MIT notices for the two adapted design sources in `../licenses/`.

## Deliberate adaptation choices

- Preserve existing brand, stack and user choices ahead of a source's house style. Do not impose blanket font, gradient, punctuation or layout bans.
- Ask a few material questions when needed, reuse supplied answers and respect delegated decisions. A source's no-questions default or mandatory full questionnaire is not universal.
- Require evidence for proof, prices, guarantees, customer logos and metrics. Do not add fabricated specificity to make copy sound persuasive.
- Keep website motion separate from film export; no compulsory GIF bundle, full-page animation or additional runtime for a small change.
- Prefer existing authorized connectors and the host's actual capabilities. Do not require a new Figma token or a particular browser-control API by default.
- Integrate with Social Motion Agent's render contract instead of combining incompatible clocks or relabelling HyperFrames as Hypermotion.
- Treat visual heuristics and retention ideas as proposals to validate, not guarantees of quality, safety, accessibility or virality.

The humanizer, recipe selection and cross-agent orchestration notes are authored local guidance. They do not rely on an unprovided proprietary writing skill. Update these source records when adopting a new upstream revision, and recheck the affected workflow rather than silently following upstream HEAD.
