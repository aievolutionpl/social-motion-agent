# Built-in motion styles

Serve the repository root with `python3 -m http.server 8000` and open `/examples/motion-styles/`. Use the selector or a URL such as `?style=grainy-gradient&t=4.5`. The slider and `window.seek(seconds)` draw an absolute frame; `window.selectStyle(slug)` changes style. Configurable values are in `config/motion-presets.json`, shared by the CLI (`python -S studio.py motion presets [slug]`) and this example. No animation plays automatically. Every frame is a pure function of `t`: grain comes from a hash-baked tile whose offset jumps from `t`, there is no `Math.random()` or clock, and `tests/motion_pixels.cjs` checks repeatable, out-of-order seeking for every preset.

| Slug | Direction | What moves |
| --- | --- | --- |
| `riso-print` | Riso print | misregistered spot-color plates, breathing halftone |
| `decollage-time-layers` | Décollage | torn poster layers drifting in time |
| `optical-moire` | Optical moiré | two line fields interfering |
| `grainy-gradient` | Grainy gradient | glowing gradient rings the camera passes through, guide orb, living grain |
| `poster-color-block` | Poster color-block | solid fields slam in on the beat, giant words cropped by the frame edge, directional ghosting |
| `flat-pop` | Flat pop with photos | a sticker grows into the next brand field (visible trigger), photo cutout pops from below, stickers burst |
| `visual-journalism` | Visual journalism | photo with source tag, highlighter, dashed annotation drawn by arc length, slow push |
| `vintage-sketch` | Vintage sketch | engraving hatch drawn line by line, meridians, gold rule, rust route annotation |
| `cartoon-collage` | Cartoon collage | cutouts land with a settle and pills pop; camera close-up → glide → zoom out |
| `white-catalog` | White catalog | breathing grid, product cutouts slide in, highlighter, scribble arrow, product close-up |
| `brutalist-mono` | Brutalist mono | hard-cut grid blocks, typed command, blinking cursor |
| `luxury-dark` | Luxury dark | tracking opens slowly, one light sweep per segment, tilted gold rings in depth, rising dust |
| `continuous-action` | Continuous action explainer | hero never leaves, world flows by distance, numbers live on road signs, whip to a map view and back |

The ten direction presets illustrate menus from `config/motion-directions.json` and [Motion, not slides](../../skills/creative-director/references/motion-not-slides.md); placeholder words, products and data are synthetic. A real film takes palette, type and imagery from the brand brief. Full-frame color changes stay below three per second; the moiré pattern may cause visual discomfort, so avoid rapid movement or flashing in production.

These are original implementations inspired by ideas, not copied code or proof of a production renderer. Concept references: [Babel / Riso](https://lukekostohryz.com/babel), [Capitu title sequence](https://motionographer.com/2009/02/01/capitu-titles-2/), [Moiré](https://artiehinz.com/moire), and the style directions of [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) (MIT; notice in `skills/creative-director/licenses/bang-motion-MIT.txt`). The concise reference-priority and creative-handoff practice is independently written, inspired by [FrameCore Works Creative Studio](https://github.com/FrameCoreWorks/framecore-works-creative-studio/tree/ef54c252f294c4dd9e5ef0b4b203d955db49ad82) (Apache 2.0); no FrameCore text or code is included. Review asset rights separately.
