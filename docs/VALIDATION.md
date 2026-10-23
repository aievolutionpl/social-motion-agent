# Release validation

Checked 2026-10-23 on Windows, Python 3.13, HyperFrames 0.8.188, GSAP 3.15.0 and system FFmpeg.

- Unit/integration suite: 60 tests, 46 passed, 14 skipped for optional media catalogues or Playwright.
- FFmpeg smoke: five successful modes (voice, music, ducked mix, original audio, original audio with music and a still). Unreviewed packaging rejected.
- HyperFrames landscape: 1920 × 1080, 30 FPS, 8 seconds; technical probe passed.
- HyperFrames portrait: 1080 × 1920, 30 FPS, 8 seconds; technical probe passed.
- Actual frames and a portrait contact sheet inspected. Demo is intentionally silent; no narration quality is claimed.
- README GIF is taken from the landscape render, not a generated product mockup.
- Offline tests cover narration dry-run, missing credentials and sanitized HTTP failures. No paid provider requests were made.
- Source audit excludes personal media, local account state, runtime caches, cloned upstream repositories and production outputs.

HyperFrames lint reports zero errors and three advisory warnings about grouping nested content into sub-compositions. The compact teaching example deliberately keeps its three scenes in one file; renders were checked. For larger films use separate sub-compositions.

CI tests Python 3.11 and 3.13 on Linux, performs FFmpeg smoke tests and renders the bundled demo. See the Actions badge for the current remote result. OpenScreen live capture, optional video-studio, external motion libraries and paid services are not part of this release's end-to-end verification.
