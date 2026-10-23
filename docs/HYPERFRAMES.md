# HyperFrames integration

HyperFrames is the primary HTML-to-video engine in this distribution. Hypermotion is a separate optional project.

The adapter runs the locally installed, pinned CLI directly through Node. It does not resolve the newest package through npx on each render. Dependencies are pinned by package-lock.json.

## Composition contract

Use examples/launch/index.html as a complete example:

- A root with data-composition-id, data-width, data-height, data-duration and data-fps.
- Timed clips with data-start, data-duration and data-track-index.
- A paused GSAP timeline registered under window.__timelines[compositionId].
- Local scripts, fonts and media. No browser timers or random animation.
- Dimensions and duration matching job.json.

`studio.py demo` copies the bundled composition and installed GSAP into a new job. For your own production, create the job, edit the plan, then write the composition. Rendering runs lint first and writes a per-render log. A technical probe validates the resulting MP4 and records its SHA.

## Commands

```bash
npm ci
npm run lint:video
npm run preview
python -S studio.py demo --render
python -S studio.py render-html output/jobs/JOB_ID --name master --quality high
```

HyperFrames may download Chrome on its first render. Node 22+, FFmpeg and ffprobe are required. The wrapper uses one worker and software browser rendering for predictable resource usage. Rendering is local, but dependency/browser downloads require network access.

For Docker and upstream-specific options, use the official CLI directly. Re-probe the final file through studio.py to associate it with the job. Only render trusted HTML; compositions execute JavaScript.

Sources: [official CLI](https://hyperframes.app/docs/5-packages/cli), [rendering](https://hyperframes.app/docs/3-guides/4-rendering), [upstream repository](https://github.com/heygen-com/hyperframes). Installed CLI help and bundled docs were checked against 0.8.188.
