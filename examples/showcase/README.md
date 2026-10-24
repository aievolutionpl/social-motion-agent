# Social Motion Agent showcase

36 seconds, 1080 × 1920, 30 FPS. An editable, fictional demonstration for creators and entrepreneurs: product photography, CSS cylinder geometry, kinetic typography, pixel art, actual job data and a closing call to action.

From the repository root, with Node 22+, Python 3.11+, FFmpeg and ffprobe installed:

```powershell
npm ci
python -S scripts/showcase.py --render
```

Each invocation creates a separate production under `output/jobs/`. It copies local assets and pinned GSAP, generates the process panel from that job's actual fields, renders through HyperFrames, mixes the bundled sound effects and probes the resulting `renders/showcase.mp4`. No AI account or paid generation is needed to reproduce it. The intermediate picture render intentionally has no audio; the final probe includes the mix.

To edit before rendering, omit `--render`, edit the new job's `source/index.html`, then use the normal `render-html` workflow. `window.seek(seconds)` and a paused GSAP timeline provide deterministic scene inspection. Start frames, midpoints, cuts and final holds need visual review; successful rendering does not confer approval.

The layout began with `templates/frame-starter.html` and `frame-tokens.css`. Effect references: the pinned `awesome-ai-motion` mask-reveal and flip-reveal cards. HTML, CSS and the 48-face cylinder are editable source. The pixel illustration is code geometry. This is not a capture of a separate SaaS application.

`citrus.png` was generated with built-in imagegen on 2026-10-24 for this fictional demo, not downloaded from a brand campaign. The prompt is retained in `scripts/showcase.py` and each generated job. It is not a real product endorsement. The font is the existing OFL Press Start 2P asset; its original license remains in `assets/fonts/licenses/`.

Audio uses only `SOUND EFFECTS/`, gains 0.28–0.35, at most two uses per effect, no normalization boost. Supporting audio license documents remain pending as documented in `docs/MEDIA_RIGHTS.md`; commercial publication is not approved by this example. No fabricated listening or final review is recorded. Review and packaging remain explicit workflow steps.
