# Optional integrations

The core does not require cloned upstream repositories.

- [HyperFrames](https://github.com/heygen-com/hyperframes): pinned npm dependency; primary motion renderer. Apache-2.0.
- [Hypermotion](https://github.com/psiddharthdesign/hypermotion): separate optional editor; not the same product as HyperFrames.
- [OpenScreen](https://github.com/getopenscreen/openscreen): optional screen recorder; set OPENSCREEN_EXECUTABLE after installing it yourself.
- [awesome-ai-motion](https://github.com/gongnyang/awesome-ai-motion): optional catalogue. Verify the upstream URL and license before installation; no automatic installation is performed.

`motion` expects an optional tools/repos/awesome-ai-motion/index.json. `edit` operations other than `fx` need your own video-studio adapter via VSTUDIO_SCRIPT. These extensions are not needed for the bundled demo or FFmpeg assembly.
