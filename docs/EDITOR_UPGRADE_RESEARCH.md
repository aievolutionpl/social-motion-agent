# Editing partner upgrade: source assessment and implementation

Analysis date: 2026-11-10. Scope: source inspection, not a claim that upstream demos or renderers were executed.

## Sources inspected

- [benjitaylor/skills](https://github.com/benjitaylor/skills/tree/299140fafd08df55a9c234e610c3f64af3f45531), Stageshow: entrypoint, choreography, motion and review references, kit and example inventory.
- [aievolutionpl/motion-designer-studio](https://github.com/aievolutionpl/motion-designer-studio/tree/af5ab42cbe4028cb9010362d6567b12a224d906d): README, style engine, storyboard, audio design, photo/footage guidance, schema/tool inventory.
- Existing Social Motion Agent: Creative Director, feedback loop, direction CLI, production gates and renderer adapter.

## What is actually valuable

| Source | Strength | Application here | Boundary |
|---|---|---|---|
| Stageshow planning | Place, focal object, action and payoff precede implementation | Product choices explicitly describe first frame, causal action and outcome | Its miniature UI is a specialty, not a universal film format |
| Stageshow framing | Recognizable context with meaningful words at the focus; portrait recomposition | Representative scene at destination size, product fidelity and readable result | Do not copy another product's identity or impose neutral grays on every brand |
| Stageshow choreography | Stable objects, measured targets, overlap, landing continuity, separate geometry/text | Review departure, transit, landing and hold; preserve object identity | Live React/state choreography is not automatically deterministic video capture |
| Stageshow review | Findings grounded in actual frames, ranked by visible impact | Revision evidence tied to export version, frame and timestamp | A still/contact sheet cannot establish audio or normal-speed playback quality |
| Motion Designer style engine | Explain palette sources, visual language, reference roles and signature motion | Job-local direction note connected to real selection | Avoid importing novelty quotas, mandatory background movement or arbitrary aesthetic bans |
| Motion Designer storyboard | Purpose, camera, transitions, timing, sound and acceptance per scene | Editing plan extends existing storyboard with source ranges | Do not introduce a competing Motion Project record alongside established job truth |
| Motion Designer audio | Measured cue timing, speech-first rhythm and deterministic audio | Separate cue plan, actual asset, mix and verified encoded audio | A cue sheet or hypothetical provider is not produced sound |
| Motion Designer footage | Asset preparation, crop, compositing and timeline-based video | Inventory first, honest missing-shot list, suitable source ranges | Do not force parallax or cutouts onto documentary footage |

## Gaps in the original project

The project already offered style choice, deterministic motion helpers, a feedback loop and strong technical render provenance. Adding another general director skill would duplicate those capabilities. The missing connection was editorial: choosing a path from actual material, explaining tradeoffs, building dialogue/rough cut before decoration, proving the difficult scene and sound, then tracking revisions against the precise export.

## Implemented now

1. `directions session`: read-only JSON discussion packets for footage, product and explainer work, each with three distinct options, sound strategy and tradeoffs. No false approvals or fabricated media analysis.
2. An editing-partner reference integrated into the portable skill, repository instructions and onboarding entrypoint.
3. A unified production sequence: inspect → choose/delegate → representative scene → rough cut → motion/mix → verified revision → acceptance and existing packaging gates.
4. Job-local edit plan, audio cues and feedback conventions, without changing existing job schema or pretending these notes are enforced runtime gates.
5. README copy explaining the collaborator experience and concrete limitations.

## Deliberately separate follow-up work

- Automatic source inventory and waveform/shot selection can reduce manual work, but need codec fixtures, measured timings and review of selection accuracy.
- A machine-enforced approval ledger would need integration with intake, resume and packaging plus migration tests. The new packet is explicitly a proposal, not such a ledger.
- A Stageshow adapter would need verified licensing, deterministic seek, font/layout stabilization, capture tests and a real exported sample before support is advertised.
- More style profiles should be added only with representative tested scenes; catalog size is not a quality metric.

## Attribution and reuse

The additions are original prose and Python orchestration. No upstream code, templates, assets or examples were copied or installed into the project. Motion Designer Studio identifies its license as MIT. Stageshow declares MIT in its package.json, although no root LICENSE file was found in the inspected checkout; preserve and verify the applicable notice before vendoring its kit. Source links above record inspiration and exact inspected revisions. Existing third-party notices remain applicable.
