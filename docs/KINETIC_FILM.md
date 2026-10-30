# Kinetic Film integration

`kinetic-launch` is a permanent route for short typography-led launches and teasers.
The adapter keeps Social Motion Agent job records, stage gates and source-bound receipts.
Scenario's actual HTML/CSS/JS engine renders the animation; its frame renderer averages temporal
subsamples for motion blur. It is separate from HyperFrames and native Hypermotion.

## Setup and first render

Get the [official skill package](https://www.scenario.com/explorations/kinetic-film/), inspect it,
then point setup to the extracted folder containing SKILL.md, engine/ and scripts/:

```bash
python -S studio.py kinetic setup --source /path/to/scenario-kinetic-film
python -m pip install -r requirements-kinetic.txt
python -S studio.py setup
python -S studio.py kinetic doctor
python -S studio.py kinetic demo --render --res 720 --samples 2
```

The first command verifies every expected file against `config/kinetic-source.json` and copies only
that allowlist into ignored `tools/runtime/scenario-kinetic-film`. A changed source/cache is reported
and preserved. No implicit downloads or account setup occur. Python NumPy/OpenCV are optional for
this engine; core commands still run with standard-library Python. Node Playwright is locked locally.
The browser must be installed separately if Chrome is unavailable (`npx playwright install chromium`).

## A real production

```bash
python -S studio.py route kinetic-launch
python -S studio.py new "Product launch" --kind kinetic-launch --format 16:9 --duration 30 --language pl
python -S studio.py kinetic prepare output/jobs/ID
# Complete intake/research/storyboard, register audio, and edit source/kinetic/spec.js.
python -S studio.py render-kinetic output/jobs/ID --name draft-v1 --res 1080 --samples 4 --audio ASSET_ID
python -S studio.py sheet output/jobs/ID --render renders/draft-v1.mp4
```

`prepare` preserves existing compositions and does not answer a new user's intake. It registers the
actual font assets and creates a source-local runtime with documented compatibility adjustments.
The example prepares the owner's supplied specification and premixed music/SFX without paid calls.

`render-kinetic` supports 720p, 1080p and 4K, 60 FPS, and 2/4/8 temporal samples. Higher settings cost
CPU time and memory. The default is 1080p with four samples; the reproduction demo defaults to 720p
with two. Worker count is conservative and based on available memory. 4K support is an adapter option,
not a claim that a complete 4K export was tested on every platform.

Frames must match the declared job duration. Numeric motion checks use the true Logo start, not a
fixed end-card duration. They retain the upstream thresholds: still share <=40%, holds <=0.6 s,
median flow >=2.5 px/frame. H.264 level <=5.2, file size <1 GB, full FFmpeg decode and -16 to -12 LUFS
for audible films are also checked. A rejected quality result has no valid production receipt.

## Compatibility and boundaries

- Windows RAM detection uses GlobalMemoryStatusEx. Unix paths use platform-native memory queries.
- Chromium reads file URLs with file-to-file access for local modules/fonts, avoiding a localhost dependency.
- Python child analysis is isolated so startup output cannot corrupt JSON.
- Encoder/browser exit failures propagate. Render names and locks are preserved; worker files are isolated per export.
- The upstream engine and source cache are not edited. Adaptations exist only inside the job's source tree.
- Current layouts are 16:9. Portrait conversion by padding is not a substitute for composing a portrait film.
- `studio.py polish` does not currently understand this engine's masks, 3D layers and `__seek` contract.
  Native motion QA and actual frame inspection are recorded separately; supporting UI plates can use normal polish.
- Scenario MCP is optional for new media. It is not connected by this integration. Model/schema discovery,
  current pricing and required user authorization still precede any paid generation.

## Publication and licenses

The README showcase was authorized by the owner on 2026-10-30. Its exact media hashes are in
`assets/media-manifest.json`; source and review limits are in `examples/kinetic-launch/provenance.json`.
Owner authorization does not independently establish every source asset's commercial terms.

The external engine is not included in the repository and is not labeled MIT. Its package did not
provide a separate engine license; upstream terms must be reviewed before redistribution.
Fonts retain their OFL notices. Supplied music and SFX have separate terms described in MEDIA_RIGHTS.md.
