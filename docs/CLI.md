# CLI reference

Run `python -S studio.py --help` for the complete parser and subcommand help.

| Command | Purpose |
| --- | --- |
| doctor | Local dependency detection; no credentials or account requests |
| demo [--format 9:16] [--render] | New synthetic editable HyperFrames example |
| new TITLE --kind KIND --duration SECONDS | Create a job; no generation |
| map / route KIND / find QUERY | Select production guidance |
| resume JOB | Show the earliest incomplete stage |
| check JOB --stage STAGE | Evidence checks for brief/research/storyboard/assets/preview/final |
| asset-add JOB --file FILE --source SOURCE --rights RIGHTS --purpose PURPOSE | Copy and hash an asset |
| render-html JOB --name NAME | Lint, render with HyperFrames and probe |
| render-assembly JOB | Assemble registered footage/stills with FFmpeg |
| edit JOB fx --asset ID --name NAME --effect SPEC | Apply local FFmpeg effects |
| probe JOB --render PATH | Check dimensions, duration, FPS and audio |
| sheet JOB --render PATH | Generate a contact sheet |
| pack JOB | Create delivery only when evidence passes |
| background IMAGE OUTPUT --duration SECONDS | Animate an image into a clip |
| sfx build/find/check | Index and search your own licensed audio |
| motion find/show/recipe | Optional external catalogue, not bundled |
| polish HTML | Optional Playwright layout measurements |

JOB must be inside output/jobs. --render paths are relative to that job. Paid narration is separate:
`python -S scripts/voiceover.py --help`.

Optional video-studio edit operations require VSTUDIO_SCRIPT. Optional browser measurements require Playwright and its Chromium installation; upstream heuristic gates require their separate source installation. No optional dependency is reported as connected just because its instructions exist.
