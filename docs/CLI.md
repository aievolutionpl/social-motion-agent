# CLI reference

Run `python -S studio.py --help` for the complete parser and subcommand help.

| Command | Purpose |
| --- | --- |
| setup [--with-library] | Check prerequisites and install pinned Node dependencies; optionally restore the full source library |
| skills plan --mode video\|website\|ui-motion | Read-only selection of relevant pinned instructions and actual missing paths |
| skills setup --mode MODE | Fetch only the selected source repositories; never run their code or install runtimes |
| skills check --mode MODE | Offline source integrity check, including manifest-based full bundles |
| doctor | Offline readiness and version checks; nonzero exit when required render dependencies are missing |
| demo [--format 9:16] [--render] | New synthetic editable HyperFrames example |
| new TITLE --kind KIND --duration SECONDS | Create a job; no generation |
| map / route KIND / find QUERY | Select production guidance |
| resume JOB | Show the earliest incomplete stage |
| check JOB --stage STAGE | Evidence checks for brief/research/storyboard/assets/preview/final |
| asset-add JOB --file FILE --source SOURCE --rights RIGHTS --purpose PURPOSE | Copy and hash an asset |
| render-html JOB --name NAME | Lint, render with HyperFrames and probe |
| render-hype JOB --scene source/index.hype --name NAME | Validate and render with the installed Hypermotion desktop/CLI, record provenance and probe |
| kinetic setup --source PATH / doctor | Verify and cache the separately obtained pinned Kinetic Film package; inspect optional local dependencies |
| kinetic prepare JOB [--example social-motion-agent] | Create source/kinetic/spec.js and an adapted job-local runtime without overwriting a composition |
| kinetic demo [--render] [--res 720] [--samples 2] | New job reproducing the owner's current README film with supplied audio |
| render-kinetic JOB --name NAME --res 1080 --samples 4 [--audio ASSET_ID] | Render Kinetic Film, enforce motion gates, record matching source/render receipt and probe |
| render-assembly JOB | Assemble registered footage/stills with FFmpeg |
| edit JOB fx --asset ID --name NAME --effect SPEC | Apply local FFmpeg effects |
| probe JOB --render PATH | Check dimensions, duration, FPS and audio |
| sheet JOB --render PATH | Generate a contact sheet |
| pack JOB | Create delivery only when evidence passes |
| background IMAGE OUTPUT --duration SECONDS | Animate an image into a clip |
| sfx build/find/check | Index and search your own licensed audio |
| motion find/show/recipe | Extended catalogue, fetched as a pinned source or expanded in a full bundle |
| styles list/recipe/find/show | 12 canonical Opus 5.5 video styles, 1,128 prompt exemplars and subagent `<inputs>/<direction>/<structure>/<build>/<gotchas>` blueprints |
| unslop-story OUTPUT [--title TITLE] [--ramp graphite\|warm\|ink] | Generate a deterministic 4-pass Before->After Redline Transformation Story HTML (`window.seek(t)`) |
| polish HTML | Optional Playwright layout measurements and 4-pass Unslop DOM checks |

JOB must be inside output/jobs. --render paths are relative to that job. Paid narration is separate:
`python -S scripts/voiceover.py --help`.

Optional video-studio edit operations require VSTUDIO_SCRIPT. Optional browser measurements require Playwright and its Chromium installation; upstream heuristic gates require their separate source installation. No optional dependency is reported as connected just because its instructions exist.

## First run

Run `python -S studio.py setup`, then `python -S studio.py demo --render`. Setup uses `npm ci --ignore-scripts` inside this repository. Python 3.11+, Node 22+ with npm, FFmpeg and ffprobe must already be installed; missing prerequisites produce actionable diagnostics and a nonzero exit. Git is needed only when restoring the optional source library with `--with-library`.

`doctor` checks local executables, versions, required skill paths and the bundled Node runtime dependencies without reading credentials or contacting external accounts. Its JSON report includes `ready`, `prerequisites_ready`, `issues` and `next_steps`. Read `ready` or the process exit code before attempting a render. Browser download availability and paid provider accounts are not checked.
