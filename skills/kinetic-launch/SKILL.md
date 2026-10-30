---
name: kinetic-launch
description: Create short beat-synced product launch films and teasers with the optional pinned Scenario Kinetic Film engine, oversized typography, CSS 3D camera moves and temporal motion blur. Uses Social Motion Agent production records, source receipts and numeric motion gates.
---

# Kinetic launch films

Use `studio.py route kinetic-launch`. The `creative-director` skill continues to own the
brief, direction, story and review. This skill selects a specific local renderer, not a provider account.
Preserve an explicitly selected engine. Reuse actual user answers; do not restart intake for a revision.

## Prepare the optional runtime once

The upstream package is not redistributed or relicensed by this repository. Download the official
skill ZIP from [Scenario Kinetic Film](https://www.scenario.com/explorations/kinetic-film/), extract it,
and inspect its SKILL.md. Its files must match `config/kinetic-source.json`.

```bash
python -S studio.py kinetic setup --source /path/to/scenario-kinetic-film
python -m pip install -r requirements-kinetic.txt
python -S studio.py setup
python -S studio.py kinetic doctor
```

Setup verifies and caches only pinned files under ignored `tools/runtime/`. It does not overwrite a
modified cache, download media, connect Scenario MCP or run paid generation. Doctor is an offline
dependency check; verify the actual browser export with the bundled demo.

## Reproduce the published example

```bash
python -S studio.py kinetic demo --render --res 720 --samples 2
```

This uses the supplied score and original blocks; a new job has fresh render receipts and pending
human review. It is an animated workflow illustration, not a screen recording of an agent run.

## Make a new film

```bash
python -S studio.py new "Product launch" --kind kinetic-launch --format 16:9 --duration 30 --language pl
python -S studio.py kinetic prepare output/jobs/ID
```

Fill the existing intake, brief, research, storyboard and `source/script.md`. Edit
`source/kinetic/spec.js`: palette, BPM, beat count, words, scene blocks, logo and image assets.
At 128 BPM, 64 beats equal 30 seconds. Every scene and camera state must be a pure function of time.
Choose a concrete visual grammar; the Style Atlas typography recipe is optional guidance,
not a reason to replace this renderer or fetch unrelated tools.

Use one or two words per hit. Keep text readable during motion and preview representative frames.
The Kinetic engine uses `window.__seek(t)` and layered 3D type. Its numeric motion gate is separate
from the UI-oriented `studio.py polish`; do not fabricate a polish pass. The static frame tokens and
Unslop guidance still apply to supporting UI plates when they are authored separately.

Register a premixed score using `asset-add`, then pass its asset ID:

```bash
python -S studio.py render-kinetic output/jobs/ID --name draft-v1 --res 1080 --samples 4 --audio ASSET_ID
python -S studio.py sheet output/jobs/ID --render renders/draft-v1.mp4
```

Respect existing audio gain limits and document music/SFX provenance. No provider generation is
implicit. A silent composition must explicitly set `brief.audio_required=false`.
Only 16:9 is currently supported; a full-screen portrait needs a separately authored composition.

## Verify the actual result

The adapter checks 60 FPS, job duration, exact frame count, H.264 level, size, full decode,
loudness when audio exists, and motion before the actual Logo block: no more than 40% still frames,
no hold longer than 0.6 s, median optical flow at least 2.5 px/frame. These thresholds describe this
high-energy style, not all films. Keep them while improving a failed composition.

Only a successful render and motion check creates a source-bound receipt. Changed source invalidates
the result; probing an imported video does not create such evidence. Existing render names and locks
are preserved. Failed quality output stays unapproved and cannot be packaged without valid provenance.

Inspect frames and play the actual file with audio. Record the exact hash, evidence and limitations in
review.json and HANDOFF.md. Technical success does not imply listening, device playback, commercial
rights or publication approval. Package through the normal workflow after the applicable review.
