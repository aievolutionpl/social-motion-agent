# ShotCraft Motion Lab

[![Social Motion Agent](https://img.shields.io/badge/Social%20Motion%20Agent-ShotCraft%20Motion%20Lab-9db1ef)](../../README.md)

Five original, deterministic Canvas motion studies inspired by [Video ShotCraft](https://github.com/Vincentwei1021/video-shotcraft). These are **working browser demonstrations** to compare movement, not an MP4 exporter or copied Remotion components.

## Open
From the root of the repository:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/examples/shotcraft-motion/`. Select a shot, press Play, or drag the time slider. Use deep links such as `?shot=carousel-3d&t=2.3`.

## Available visual studies
- `carousel-3d`: overlapping product cards with parallax, scaling and readable holds.
- `card-flock-tumble`: scattered cards converge into a clean matrix.
- `flying-words`: dynamic typography settles into a readable statement.
- `value-stagger-gradient`: graduated process bars. **Numbers are indices, not fictional KPIs.**
- `before-after-slider-scrub`: concept-only UI comparison with a draggable-time reveal.

All visual output is a pure function of selected time; automatic play uses the clock solely to advance the seek cursor. No network requests except the local registry, no remote media, no account or client assets. `window.seek(seconds)` and `window.selectShot(slug)` support automated browser checks.

## Agent workflow

```bash
python -S studio.py shotcraft list
python -S studio.py shotcraft show flying-words
python -S studio.py shotcraft plan product-reel --duration 15 --fps 30 --brand "Brand" --cta "See details"
```

See [ShotCraft Motion Pack](../../docs/SHOTCRAFT_MOTION_PACK.md) for shot source links, mappings and constraints. The Python storyboard is a safe planning artifact: it does **not** automatically generate a usable HyperFrames scene or import videos. Use the existing Creative Director, production route and final QA for delivery.

## Testing

```bash
python -S -B -m unittest discover -s tests -p "test_shotcraft_pack.py" -v
```

With installed Playwright and Chromium, the test also checks five previews for nonblank frames, visible motion and repeatable reverse seeks. If Playwright is unavailable, the browser portion is skipped; other offline tests still run.

### Attribution

All Canvas drawing logic is original to this repo. The shot-selection **ideas** reference upstream Video ShotCraft (Apache-2.0); linked upstream recipes, code and assets retain their own terms. No upstream code or artwork is bundled in this lab. Some scenes intentionally use synthetic UI for learning; do not represent them as customer demos or factual performance data.
