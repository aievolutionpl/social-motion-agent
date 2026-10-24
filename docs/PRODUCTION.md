# Production workflow

## Create and plan

Run `python -S studio.py new "Film title" --kind launch --format 16:9 --duration 20`.
The returned job contains intake, brief, research, storyboard, asset registry, timeline and review records.

Fill in intake answers from the actual user. In brief.json set goal, audience, direction, engine, engine_reason, audio_required and captions_required. Select "hyperframes" for authored motion or "ffmpeg" for footage.
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

## Footage assembly

Set timeline.json clips to objects with asset_id, duration_sec, in_sec and fit (contain or cover). Audio accepts voice/music asset IDs and music_gain. Then run render-assembly JOB, probe JOB --render RELATIVE_MP4 and sheet JOB --render RELATIVE_MP4.
The existing fx command supports local effects; see `python -S scripts/fx.py --help`.
Original footage is preserved.

## Review and delivery

1. Inspect the actual file and contact sheet. Listen when audio is present. Check captions, factual claims, media rights and platform framing.
2. Fill preview.json with path, SHA-256, reviewed true, reviewer and actual notes.
3. Fill review.json with render_sha256, reviewer, local evidence paths and checks for visual, audio, captions, facts, rights and platform. Each check needs status pass/na and meaningful notes. Required audio/captions cannot be na.
4. Run probe again after changes. Source changes invalidate earlier technical evidence.
5. Run `check JOB --stage final`, then `pack JOB`.

Pack creates a local delivery folder with the master and source/evidence files. The exported `job.json` and `technical.json` point to the packaged master. `preview.json`, the reviewed preview and files listed in `review.evidence` travel with the package, preserving usable relative paths. The original production keeps its render paths. The delivery folder can be moved as a whole without relying on the original job directory.

Pack does not upload or publish anything. Review packages for private content before sharing them.
