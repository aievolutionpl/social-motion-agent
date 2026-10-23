# Start here

1. Run `python -S studio.py doctor`. Python 3.11+, Node 22+ and FFmpeg/ffprobe are required for the full workflow.
2. Install pinned Node dependencies with `npm ci`.
3. Run `python -S studio.py demo --render` for a synthetic 8-second film. No paid AI APIs are used; the first render may download Chrome.
4. For your own film, read `skills/intake/SKILL.md` and create a job using `studio.py new`.
5. Edit its JSON planning files and `source/index.html`; read `docs/PRODUCTION.md` and `docs/HYPERFRAMES.md`.
6. Review the actual render, then record evidence and package it. A successful encoder exit is not creative approval.

Use `studio.py resume <job>` to find missing evidence and continue a job. Outputs are local and ignored by Git.
