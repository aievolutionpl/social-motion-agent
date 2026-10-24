# Start here

Start with the bundled demo. The complete upstream source library is optional for this first render.

1. Install Python 3.11+, Node 22+ with npm, and FFmpeg/ffprobe on your system.
2. Run `python -S studio.py setup`. It checks these prerequisites, installs pinned Node dependencies with `npm ci --ignore-scripts`, and reports any remaining blockers. It does not install system tools or call paid services. Run `python -S studio.py doctor` for an offline readiness check; a nonzero exit means the default render workflow is not ready.
3. Run `python -S scripts/premium_intro.py --render` for the published 30-second landscape intro, including Polish voice, captions, music and actual Codex screenshots. No generation API credentials required. See `examples/premium-intro/README.md`.
   Run `python -S studio.py demo --render` for a synthetic 8-second film. No paid AI APIs are used; the first render may download Chrome.
   For the 36-second portrait showcase with product photography, CSS 3D, kinetic type and local SFX, run `python -S scripts/showcase.py --render`. Read `examples/showcase/README.md` for provenance and review requirements.
4. For your own film, read `skills/intake/SKILL.md` and create a job using `studio.py new`.
5. Edit its JSON planning files and `source/index.html`; read `docs/PRODUCTION.md` and `docs/HYPERFRAMES.md`.
6. Review the actual render, then record evidence and package it. A successful encoder exit is not creative approval.

Use `studio.py resume <job>` to find missing evidence and continue a job. Outputs are local and ignored by Git.

For the complete workshop, install Git and run `python -S studio.py setup --with-library`, then `python -S scripts/library_check.py`. This also downloads the 34 pinned upstream source repositories without installing or running their runtimes. Read docs/LIBRARY.md.
