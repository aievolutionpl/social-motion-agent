# Agent operating map

Read AGENTS.md, START_HERE.md and skills/creative-director/SKILL.md. This repo is a production toolkit, not an autonomous quality guarantee. Reuse the existing checkout and preserve user edits.

## Inspect and resume

Check git status, studio.py doctor, job.json, brief.json, intake.json, preferences.json if present, timeline.json, storyboard.json and review notes. Use studio.py resume JOB for outstanding production stages. All customer assets and generated films stay in ignored output/jobs; do not commit them. Never re-interview for a narrow revision.

## Route the work

| Need | Entry point | Real result |
|---|---|---|
| First discussion | directions session --for SUBJECT --mode footage/product/explainer | Proposal packet, not approval |
| Inspect registered footage | editor inventory JOB | Metadata, sample images, scene/silence candidates |
| Compare visual approaches | editor directions JOB | Three initial SVG studies; customize before production |
| Recall real choices | editor preferences JOB | Job-local preferences and evidence |
| Montage | editor plan JOB --source source/plan.json, then render-assembly JOB | Validated canonical timeline and FFmpeg export |
| Custom motion | source/index.html, then render-html JOB --name VERSION | HyperFrames export with provenance |
| Explain a mechanism | styles recipe flat-vector or isometric-line-art | Art direction guidance; build actual scene |
| Review | editor qa JOB --render renders/VERSION.mp4 | Technical findings and explicit unchecked areas |
| Human feedback | editor review JOB --render ... --previous ... | Browser player, JSON comments bound to render SHA |
| Apply comments | editor feedback-import JOB --source source/feedback.json | Open requests; agent implements and verifies separately |

Read docs/EDITOR_WORKSPACE.md for exact JSON contracts. Use --help rather than inventing flags. Register sources with asset-add and real rights metadata. Plan requires actual registered IDs. Render naming preserves older versions. Changes to source require a new render; do not re-probe an old MP4 to claim it represents new sources.

## HyperFrames production contract

Use local GSAP and assets, a paused timeline, the repository's HyperFrames conventions and time-addressable scenes. No live random state, wall-clock animation or network-loaded fonts during capture. Keep the chosen format, readable holds and actual sound cues. Do not silently substitute a different engine or claim a native .hype application is installed.

Choose style from the brief, not from a starter's default colors. The 13 Canvas presets are deterministic examples, the 14 atlas styles are recipes, and optional upstream libraries are instructions rather than provider access. Show 2–3 useful choices before a substantial undecided production. Honor existing choices/delegation. Read references/editor-session.md and references/feedback-loop.md from Creative Director.

## Verify and hand off

Run relevant tests after code changes. Full suite: python -S -B -m unittest discover -s tests -v. Node browser pixel tests accept PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH for an installed Chromium, otherwise Playwright's managed browser is used. This overrides the executable only, never test assertions. Python browser suites need the virtual environment without -S.

For every delivered film: inspect representative and transition frames, watch timing, listen to encoded audio when available, run probe and QA, record limits. Technical QA does not establish typography or aesthetic quality. Browser comments stay local until exported/imported. Offer specific revisions; mark them implemented only after inspecting the new render. Paid requests and publication require authorization; do not infer them from a creative brief.

Local effect bank: `python -S studio.py prompts list/find/show` — 30 HyperFrames recipes, full text in `references/hyperframes-prompts.md`. Use `show ID` for the shared deterministic capture contract; these are not pre-rendered effects.
