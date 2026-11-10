# Editor workspace

Six local tools support the editing conversation. They use existing jobs, registered assets and renderers. Python standard library + FFmpeg/ffprobe are required; HTML review needs a browser. No account or paid provider is required.

Use `JOB` below as the existing `output/jobs/<id>` path. Register files first with `studio.py asset-add --help`; originals are copied into the job and source/rights remain in assets.json.

## 1. Media inventory

```bash
python -S studio.py editor inventory JOB
```

Produces a versioned HTML contact gallery and JSON with dimensions, duration, FPS, audio presence, SHA, sampled frames, detected visual scene boundaries and silence events. Invalid media are reported individually. Scene boundaries are candidate edit ranges, not a claim that a shot is good, sharp or semantically relevant. The agent inspects samples and listens to footage before making selections. Audio presence does not imply speech. Long media may exceed the five-minute per-command timeout; split or inspect selected assets separately rather than claiming analysis completed.

## 2. Three visual directions

```bash
python -S studio.py editor directions JOB
```

Creates three SVG styleframes and a comparison gallery at job aspect ratio: editorial, kinetic and diagram. Uses the job title and saved palette where present. These are initial composition studies, not generated product imagery or finished scene designs. The agent adapts imagery, font and story to the brief and shows the user the alternatives. No automatic selection or approval occurs. Build the chosen motion sample through the normal renderer.

## 3. Project preference memory

Write `JOB/source/preferences-update.json`:

```json
{"values":{"palette":["#fff8ee","#182a35","#d54b31"],"font":"brand font","pace":"calm opening, fast middle","keep":"large product details","avoid":"glitch transitions","style":"editorial"},"evidence":"Actual user instruction or feedback"}
```

```bash
python -S studio.py editor preferences JOB --source source/preferences-update.json
python -S studio.py editor preferences JOB
```

Values merge, previous values and evidence remain in history. Scope is this job only; no global client memory is read. The agent reads these preferences before later scenes and revisions. The gallery applies palette automatically; the remaining preferences are creative guidance, not automatic font installation or pacing implementation.

## 5. Editable plan connected to rendering

```bash
python -S studio.py editor plan JOB
python -S studio.py editor plan JOB --source source/proposed-timeline.json
python -S studio.py render-assembly JOB
```

The plan is the existing timeline.json, not a second competing timeline. Example:

```json
{"clips":[{"asset_id":"REGISTERED_ID","in_sec":1,"duration_sec":4,"fit":"cover","keep_audio":true}],"audio":{"voice":null,"music":null,"music_gain":0.12}}
```

Use real IDs and enough clips to match job.duration_sec. Application validates finite values, registered sources, available picture, source ranges, fit and total duration, then backs up the old timeline. Changing duration is explicit in job.json; no hidden retiming of narration. Existing renderer supports cuts, contain/cover and voice/music; this command does not add arbitrary layered effects or caption tracks. Render evidence becomes stale when timeline changes, through the existing fingerprint mechanism.

## 8. Version-specific review

```bash
python -S studio.py editor review JOB --render renders/current.mp4 --previous renders/older.mp4
```

Open the returned page using a local HTTP server scoped to JOB, e.g. `python -m http.server 8765 --bind 127.0.0.1 --directory JOB`. The page shows both videos, supports frame-position/time comments and saves them to browser storage keyed by render SHA. Export JSON for durable transfer. Place the downloaded file inside JOB, then:

```bash
python -S studio.py editor feedback-import JOB --source source/feedback.json
```

Import validates the render hash, duration and normalized coordinates. Imported comments are open requests, never automatically applied edits or human acceptance. The agent reads the saved notes, implements agreed changes and renders a new version. Comparison uses separate player controls. Local storage is not a server database; export before switching devices. The review page has no remote dependencies or write API.

## 9. Export QA

```bash
python -S studio.py editor qa JOB --render renders/current.mp4
```

Decodes the full export, compares dimensions/duration with the job, checks required audio and reports black/frozen intervals and volume statistics. Exit 1 means a technical mismatch; decode errors also fail. Report is bound to SHA. Black/freeze events are review candidates: deliberate holds and black transitions may be correct. This does not establish text clipping, caption readability, true-peak compliance or subjective quality; those remain explicit visual/audio checks. Existing probe/review/pack gates still apply.
