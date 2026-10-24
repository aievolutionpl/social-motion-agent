# Release validation

## Fresh Windows download audit, 2026-10-24

Independently cloned GitHub commit `d4cdd31f84492e6c79e99e3f2fe9b356932dd12b` into a new directory, without reusing the workshop's node_modules or tool checkouts.

- `npm ci --ignore-scripts`: 74 packages installed, audit reported zero vulnerabilities.
- `bootstrap_library.py`: all 34 pinned public upstream sources fetched successfully.
- `library_check.py`: all 920 catalogue entries and 138 media hashes passed.
- Existing suite: 63 tests, 61 passed, two optional Playwright skips.
- All five FFmpeg assembly smoke scenarios passed, including original audio and ducking. Packaging without review remained blocked.
- Fresh-clone portrait demo: 1080 × 1920, 30 FPS, eight seconds; technical probe passed.
- GitHub CI for that exact commit completed successfully: https://github.com/aievolutionpl/social-motion-agent/actions/runs/40110001381.
- Release v1.0.0 has the full 545,361,718-byte ZIP and checksum attached; GitHub reports SHA-256 `e24ac90c450939878c6f72499be2d3f37a34bff7b39584d2821aa0b03897ca3c`. This is the old release, not the new showcase.
- The retained local ZIP matched that remote digest. All 23,200 files in its extracted copy passed `verify_bundle.py` with all 34 sources. The archive was not downloaded a second time.

On this machine, the first sandboxed render failed with `EACCES` on Chromium's loopback connection. Retrying outside the restricted Windows sandbox succeeded. This is an execution-permission requirement, not evidence that every Windows installation is identical. Paid accounts, private voice IDs, live desktop capture and optional upstream runtimes were not tested.

New showcase changes: 65 tests, 63 passed, two optional skips. Tests additionally verify a complete reproducible job, preservation of supplied intake answers, local assets, absence of unresolved template markers and refusal to overwrite an existing composition or accept the wrong format. Visual and audio approval are separate from these checks.

All seven portrait scene layouts passed `studio.py polish`, including the installed upstream taste/slop checks, at 2.5, 7.5, 12.5, 16, 23.5, 27.5 and 33 seconds. Screenshots were inspected; a contact sheet from the rendered draft was also inspected. The README montage is captured from the composition, not a generated interface mockup. A human listening review is still required before final delivery approval.

Checked 2026-10-23 on Windows, Python 3.13, HyperFrames 0.8.188, GSAP 3.15.0 and system FFmpeg.

- Initial core suite: 60 tests, 46 passed, 14 skipped before the extended library was included. The current complete-library result is recorded below.
- FFmpeg smoke: five successful modes (voice, music, ducked mix, original audio, original audio with music and a still). Unreviewed packaging rejected.
- HyperFrames landscape: 1920 × 1080, 30 FPS, 8 seconds; technical probe passed.
- HyperFrames portrait: 1080 × 1920, 30 FPS, 8 seconds; technical probe passed.
- Actual frames and a portrait contact sheet inspected. Demo is intentionally silent; no narration quality is claimed.
- README GIF is taken from the landscape render, not a generated product mockup.
- Offline tests cover narration dry-run, missing credentials and sanitized HTTP failures. No paid provider requests were made.
- Source audit excludes personal media, local account state, runtime caches, private upstream modifications and production outputs. Public upstream sources are now included as pinned submodules.

HyperFrames lint reports zero errors and three advisory warnings about grouping nested content into sub-compositions. The compact teaching example deliberately keeps its three scenes in one file; renders were checked. For larger films use separate sub-compositions.

CI tests Python 3.11 and 3.13 on Linux, performs FFmpeg smoke tests and renders the bundled demo. See the Actions badge for the current remote result. OpenScreen live capture, optional video-studio, paid services are not part of this release's end-to-end verification.

## Complete-library expansion

All 34 exact commits were fetched successfully from their public upstream sources. The original 126 audio files, nine backgrounds and three fonts were copied without modification; SHA-256 values are recorded in assets/media-manifest.json. Seven local skills and 913 upstream catalogue entries are included. Media rights are documented separately.

Complete-library verification: 63 tests, 61 passed and 2 optional Playwright skips. All 920 catalogue files and 138 media hashes validated; all 34 source commits matched. Original audio index check and motion catalogue search passed.
