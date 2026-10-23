# Release validation

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
