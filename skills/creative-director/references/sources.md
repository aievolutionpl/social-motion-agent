# Sources and adaptation

Reviewed on 2026-10-26. This package contains original instructions written for Social Motion Agent, informed by the following primary sources. It is not an official release or endorsement from those projects. Upstream text is design input, not an instruction to override the user's brief or run arbitrary commands.

## Selected upstream methods

| Source and pinned revision | Read paths | What informs this skill |
| --- | --- | --- |
| [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills/tree/eabf86665588de0eb4c9e2fbf5fc9d3ae807e9f1), MIT, copyright 2026 Elaya | `skills/landing-page-design/SKILL.md`; `skills/design-to-motion/SKILL.md` | Purpose-driven page structure, targeted intake, faithful UI reconstruction, state-based motion, deterministic capture and loop review |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/12af471f627f866411b4bd785b19646d3672784c), MIT, copyright 2026 Leonxlnx | `skills/taste-skill/SKILL.md` (`design-taste-frontend`, titled tasteskill v2); its linked page/app guidance | Subject-specific art direction, multiple composition choices, distinction between pages and working app screens, screenshot-led iteration |
| [psiddharthdesign/hypermotion](https://github.com/psiddharthdesign/hypermotion/tree/e510cd60c0d2632863b5a3f78dba71b905c75ff2), Apache-2.0 | `skills/hypermotion-brand-profile/SKILL.md`; `skills/hypermotion-explainer-director/SKILL.md`; setup documentation | Existing optional native scene workflow and the need to distinguish its source skills, CLI and desktop runtime |
| [heydamir/unslop](https://github.com/heydamir/unslop/tree/4652254daff586ff4739849395a127b56f7f8cc7), CC BY 4.0, copyright 2026 Damir Sokolovsky (`@heydamir`) | `skills/unslop/SKILL.md`; `references/signs.md`; `references/tokens.md`; `references/effects.md`; `references/visuals.md` | 4-pass redline audit (`Spacing`, `Color and icons`, `Type and copy`, `Details`), tinted neutral ramps, offscreen-baked canvas effects, and Before->After redline transformation stories |
| [HiAPIAI/awesome-opus-5-5-video-styles](https://github.com/HiAPIAI/awesome-opus-5-5-video-styles/tree/b1a796c438863e80bd343aa5cd355de0b87fd2c4), CC BY 4.0, copyright 2026 HiAPI | `styles/*.md` (12 style pages, 425 prompts) | 12 canonical video styles (`typography`, `productui`, `cinematic3d`, `explainer`, `generative`, `handdrawn`, `cartoon`, `collage`, `lowpoly`, `photoreal`, `pixel`, `retro`) and the 5-part `<inputs>/<direction>/<structure>/<build>/<gotchas>` subagent blueprint |
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos/tree/92aee2f586ac0715cb3cbcb6384834f98a33383d), MIT, copyright 2026 Yihui Dev | `data/videos.json` (703 prompts across 11 categories) | Closed-form spring physics (`stepSpring`), dual-spring liquid edge morphs (`liquidSpan`), and single-file self-contained `Canvas 2D`/`Three.js`/`WebGL` production patterns |

The full pinned sources are managed by the repository's `sources.lock.json` and bootstrap workflow. Their licenses remain their own. The standalone Creative Director package does not include Hypermotion implementation code or replace its Apache notices. It retains the MIT and CC BY 4.0 notices for the adapted design and video-style sources in `../licenses/`.

## Deliberate adaptation choices

- Preserve existing brand, stack and user choices ahead of a source's house style. Do not impose blanket font, gradient, punctuation or layout bans.
- Ask a few material questions when needed, reuse supplied answers and respect delegated decisions. A source's no-questions default or mandatory full questionnaire is not universal.
- Require evidence for proof, prices, guarantees, customer logos and metrics. Do not add fabricated specificity to make copy sound persuasive.
- Keep website motion separate from film export; no compulsory GIF bundle, full-page animation or additional runtime for a small change.
- Prefer existing authorized connectors and the host's actual capabilities. Do not require a new Figma token or a particular browser-control API by default.
- Integrate with Social Motion Agent's render contract instead of combining incompatible clocks or relabelling HyperFrames as Hypermotion.
- Treat visual heuristics and retention ideas as proposals to validate, not guarantees of quality, safety, accessibility or virality.

The humanizer, recipe selection and cross-agent orchestration notes are authored local guidance. They do not rely on an unprovided proprietary writing skill. Update these source records when adopting a new upstream revision, and recheck the affected workflow rather than silently following upstream HEAD.
