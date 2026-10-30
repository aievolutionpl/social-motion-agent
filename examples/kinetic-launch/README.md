# Social Motion Agent: Kinetic Film demo

The current README showcase: 30 seconds, Polish kinetic typography, 16:9, 1280×720 at 60 FPS,
music and sound effects, no narrator. It illustrates brief → planning → scenes → render/review.
It is not a recording of a real agent run.

- Published film: [kinetic-launch.mp4](../../docs/media/kinetic-launch.mp4).
- Editable specification: spec.js and title.svg.
- Supplied premixed audio: mix.wav. No generation API is called during reproduction.
- Story and sources: script.md, storyboard.json, provenance.json.
- Engine preparation and CLI: [KINETIC_FILM.md](../../docs/KINETIC_FILM.md).

After preparing the optional pinned engine:

```bash
python -S studio.py kinetic demo --render --res 720 --samples 2
```

A new production is created under output/jobs/. Existing jobs are not overwritten. Changing the
composition requires another render and review. The supplied film passed numeric motion gates,
full decode, exact frame count and -14 LUFS checks. Sampled frames were inspected; full playback,
listening and destination-device review are not represented as independently confirmed.

The owner explicitly requested publishing this film on 2026-10-30. Code, upstream engine, fonts,
music and SFX have separate rights; see provenance.json and docs/MEDIA_RIGHTS.md. The upstream engine
is obtained separately and is not redistributed or relicensed here.
