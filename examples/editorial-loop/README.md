# Editorial loop

An 8-second silent, synthetic illustration of editing, motion and refinement. Ivory, ink and coral; three persistent clip objects, a moving playhead and deliberate type hierarchy. Not a recording of a running editor. No generated footage, customer assets, provider calls or paid generation.

Reproduce from the repository root:

```bash
npm ci --prefix examples/editorial-loop --ignore-scripts
node examples/editorial-loop/render.mjs
```

The deterministic Canvas source exposes `window.seek(seconds)`. Renderer: pinned @napi-rs/canvas (same Canvas scene, without browser), 960×540, 30 fps H.264 MP4; README derivative: 720×405, 20 fps looping GIF. Intermediate frames stay in ignored `output/editorial-loop/`. System DejaVu Sans/sans-serif may vary across platforms. The source is MIT, using original geometric graphics and system text, without bundled font files or audio.

This showcase renderer is separate from production job adapters and does not issue production approvals or replace their evidence gates.

The showcase uses a separate pinned Canvas renderer because browser startup is unavailable in the build environment. It does not establish HyperFrames or browser runtime readiness. Requires Node.js and FFmpeg; install the example dependencies with the command above.

## Verification

Encoded MP4 probed at 960×540, 30 fps, 240 frames, 8 seconds. Contact sheet inspected at one-second intervals: title, clip labels and footer remain in frame. Silent by design. User taste approval is pending; this is a repository showcase, not a packaged client film.
