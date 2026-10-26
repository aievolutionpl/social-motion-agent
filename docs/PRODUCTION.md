# Production workflow

## Create and plan

Run `python -S studio.py new "Film title" --kind launch --format 16:9 --duration 20`.
The returned job contains intake, brief, research, storyboard, asset registry, timeline and review records.

Fill in intake answers from the actual user, reusing supplied decisions. In brief.json set goal, audience, direction, engine, engine_reason, audio_required and captions_required. Select "hyperframes" for authored HTML motion, "hypermotion" for native .hype scenes with a verified desktop runtime, or "ffmpeg" for footage.
Research entries need id, title, url, accessed_at and used_for. Claims need text, status "confirmed" and known source_ids. Record conclusions even when the film makes no factual claims.
Storyboard scenes need unique id, visual, positive duration_sec and asset_ids. Scene durations must total the job duration. Write the script in source/script.md.

Use `check JOB --stage storyboard` and `resume JOB` to find missing fields. Synthetic demo records are labelled fixtures and are not suitable for client approval.

## Materials

```bash
python -S studio.py asset-add output/jobs/JOB_ID --file image.png --source "Your source URL or description" --rights "Your usage rights" --purpose "Opening scene"
```

Generated images also need --provider imagegen --prompt-file prompt.txt.
Generated fal assets need --provider fal --endpoint MODEL_ENDPOINT --request-id REQUEST_ID --prompt-file prompt.txt.
These fields record provenance; they do not call an image or video generation API.

## Motion film

Create source/index.html using the composition contract in HYPERFRAMES.md. Copy your local dependencies beside it and register any media you use. Run:

```bash
python -S studio.py check output/jobs/JOB_ID --stage assets
python -S studio.py render-html output/jobs/JOB_ID --name draft
python -S studio.py sheet output/jobs/JOB_ID --render renders/draft.mp4
```

Render names cannot overwrite earlier files. A lock prevents two renders using the same name. A failed render keeps its log; retry with a fresh name after inspecting the failure. An interrupted process may leave a lock: inspect its PID before removing it.

## Native Hypermotion

For a native Hypermotion scene, follow [HYPERMOTION.md](HYPERMOTION.md) and author `source/index.hype` using the pinned upstream tools. `studio.py render-hype JOB --scene source/index.hype --name draft` invokes the installed CLI, validates the scene, records a render receipt and probes the MP4. It requires a separately installed desktop/CLI; it does not convert HTML to .hype or silently fall back to HyperFrames. Scene dependencies belong inside the job, not in unrelated machine folders.

## Footage assembly

Set timeline.json clips to objects with asset_id, duration_sec, in_sec and fit (contain or cover). Audio accepts voice/music asset IDs and music_gain. Then run render-assembly JOB, probe JOB --render RELATIVE_MP4 and sheet JOB --render RELATIVE_MP4.
The existing fx command supports local effects; see `python -S scripts/fx.py --help`.
Original footage is preserved.

## Review and delivery

1. Inspect the actual file and contact sheet. Listen when audio is present. Check captions, factual claims, media rights and platform framing.
2. Fill preview.json with path, SHA-256, reviewed true, reviewer and actual notes.
3. Fill review.json with render_sha256, reviewer, local evidence paths and checks for visual, audio, captions, facts, rights and platform. Each check needs status pass/na and meaningful notes. Required audio/captions cannot be na.
4. After source changes, render again, then probe the new file. Render adapters save `<render>.mp4.provenance.json`, binding the exact MP4 to the source fingerprint captured before rendering. `probe` only checks that receipt; it cannot certify an old MP4 against new sources. Legacy files without a receipt must be re-rendered. Do not manufacture receipts for historical files.
5. Run `check JOB --stage final`, then `pack JOB`.

Pack creates a local delivery folder with the master and source/evidence files. The exported `job.json` and `technical.json` point to the packaged master. `preview.json`, the reviewed preview and files listed in `review.evidence` travel with the package, preserving usable relative paths. The original production keeps its render paths. The delivery folder can be moved as a whole without relying on the original job directory.

Pack does not upload or publish anything. Review packages for private content before sharing them. The delivery includes the render receipt alongside the master.

## Adding a render adapter

Capture `source_fingerprint = studio_core.fingerprint(folder)` immediately before rendering. After the renderer successfully writes a new file, call `studio_core.record_render(folder, relative_mp4, source_fingerprint, producer_name)`, then `studio_core.probe_job(folder, relative_mp4)`. The receipt rejects source or registered-asset changes during rendering. Keep the receipt with the MP4. Import external footage using `asset-add`, then assemble it through a tracked render; measuring an arbitrary external MP4 alone does not prove how it was built.
