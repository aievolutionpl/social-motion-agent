---
name: director-suite
description: Plan, QA and hand off explainers, Playwright product demos and launch motion using Explainroo, Argo and Huashu-inspired patterns.
---

# Director Suite

Use `python -S studio.py director ...` inside an actual Social Motion Agent video job. Read [docs/DIRECTOR_SUITE.md](../../docs/DIRECTOR_SUITE.md) before using a profile.

1. Read `AGENTS.md` and the job's approved brief, claims, assets and storyboard. Do not invent brands, product proof, narrations or customer screenshots.
2. Choose `explainer` (educational voice and illustrations), `demo` (real UI through Playwright), or `launch` (product-first motion and sound).
3. Run `director plan JOB --profile PROFILE`, inspect editable beat sheet and run `director qa`. Treat findings as **advice**. It cannot inspect a rendered MP4.
4. Run `director handoff JOB --profile PROFILE` only when an upstream project is needed. Output is a **scaffold** and needs its real runtime and tested configuration. Never state it was installed or rendered just because files exist.
5. If actual measured word timestamps exist, run `director captions JOB --alignment JOB_RELATIVE_PATH`. For Polish, use recorded or externally synthesized Polish speech with a supported upstream audio path.
6. Accept point revisions with `director feedback JOB --at TIME --x FRACTION --y FRACTION --comment TEXT`. Read queue with `feedback-list`. Implement edits in the source, rerender and redo checks. A recorded comment is not an applied fix.
7. Use existing `probe`, `sheet`, manual preview/audio checks, and `pack` review gates. Nothing auto-publishes or incurs paid usage.

The reference projects are separate open-source tools with their own installation and licensing. We adopt general patterns using original local code; never silently vendor them into this repository.
