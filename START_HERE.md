# Start here

For the consolidated local production workspace, read `LOCAL_WORKSPACE.md` when present.
It identifies the active production folders and preservation checks. Historical files under
`output/legacy-workbench/` are references and never override the current instructions or code.
See `docs/LOCAL_WORKSPACE.md` for the portable consolidation and preservation-ledger workflow.

1. Read `AGENTS.md` and `skills/creative-director/SKILL.md`. Choose video, website or ui-motion. Narrow revisions reuse the existing brief and tools.
2. Inspect the project and supplied references. Reuse known answers; ask missing material questions. Show two or three distinct directions with concrete scene/section placements when undecided. Do not treat silence as approval.
3. Run `python -S studio.py skills plan --mode MODE`. Prepare missing sources with `skills setup --mode MODE`, then `skills check --mode MODE`. Source preparation does not install or test upstream runtimes.
4. For websites, preserve the target project's stack. Read website, anti-slop and humanizer modules. Check the actual page and existing project tests; no video job or renderer is needed.
5. For films, install Python 3.11+, Node 22+ with npm, FFmpeg/ffprobe. Run `python -S studio.py setup`, then `python -S studio.py doctor`. Setup installs locked Node dependencies, not system runtimes. Doctor is offline and does not inspect accounts.
6. Try `python -S studio.py demo --format 9:16 --render` for HyperFrames. For the current README film, prepare the optional engine as in `docs/KINETIC_FILM.md`, then run `python -S studio.py kinetic demo --render --res 720 --samples 2`. Both use supplied materials, not paid generation. First render may need Chromium.
7. For original films, use `studio.py new`, fill real intake/research/storyboard and follow `docs/PRODUCTION.md`. HyperFrames is the local HTML renderer. Native Hypermotion requires verified desktop/CLI and a short export test; see `docs/HYPERMOTION.md`. Never silently substitute a requested engine.
8. For an existing storyboard, consider `python -S studio.py director plan JOB --profile explainer|demo|launch` and `director qa`. Read `docs/DIRECTOR_SUITE.md`: optional Argo/Explainroo/Huashu handoffs are not themselves renders. Measured word cues can produce SRT, and point feedback is a pending change request, not a finished edit.
9. Review actual frames and audio or the running website. New video sources require a new render receipt. Probe, review and package the same file. A successful encoder is not creative approval.

Typography-led launch or teaser: `studio.py route kinetic-launch`, `skills/kinetic-launch/SKILL.md`.
Use `kinetic prepare JOB` and `render-kinetic JOB`; the optional engine has its own motion checks and
16:9 composition contract. Do not silently substitute HyperFrames or claim UI polish covers its 3D layers.

Walking presenter, kinetic captions and text behind the subject: `studio.py route kinetic-walk-talk`,
`skills/kinetic-walk-talk/SKILL.md` and `docs/KINETIC_WALK_TALK.md`. Create a 9:16 job with
`--kind kinetic-walk-talk`, then use `walk-talk prepare JOB --mode footage|recording|ai`.
`walk-talk compose JOB` builds HyperFrames sources from registered footage and real text timings.

Use `studio.py resume JOB` for incomplete film stages. Films stay in `output/jobs/<id>/`; websites stay in their target project. Never fabricate answers, rights, connectivity or review.

Portable installation: `docs/AGENT_SETUP.md`. All 38 upstream sources: `scripts/bootstrap_library.py`; the full collection is optional for the first render and focused skill paths. Use `python -S studio.py styles list` and `python -S studio.py unslop-story` for Opus 5.5 video styles and Before->After UI transformation stories.

Openers, promos and coded explainers: read `skills/creative-director/references/motion-not-slides.md`, draft the style brief with `python -S studio.py directions brief --for "..."` and run `python -S studio.py motion lint FILE.html` before `polish`.

Built-in motion presets (13): `python -S studio.py motion presets` or `python -S studio.py motion presets grainy-gradient`. From the repository root run `python3 -m http.server 8000` and open `http://localhost:8000/examples/motion-styles/`. Select a style and seek with the slider or `window.seek(seconds)`; these are canvas examples, not HyperFrames compositions or approved productions. See `examples/motion-styles/README.md`.
