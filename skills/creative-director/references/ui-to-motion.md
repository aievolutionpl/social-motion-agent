# UI to motion & Opus 5.5 / Unslop Animation Patterns

## Decide whether this is an embedded interaction, a product film or an Unslop Story

For an existing website, animate only the requested area and keep its live text and controls accessible. For a standalone showcase or social reel, agree the output size, duration and whether it loops. Do not automatically deliver multiple GIF formats or turn a small motion request into a full film.

Read the supplied design through the available Figma connector, local file or image. If the input is a live URL that needs to be captured and redesigned/animated, save or inspect its structure first. If the input is a flat screenshot, state which elements can be isolated or reconstructed; do not promise layer-perfect fidelity from information that does not exist.

## Establish an accurate still first

Identify fixed surfaces, content groups, overlays and elements that will actually change. Preserve relative geometry, clipping, type, images and hierarchy. Compare the reconstructed final frame to the supplied reference at the same viewport and scale. Check crop, alignment, shadows, masks and font loading.

## Animate behavior, not just arrival

A good sequence demonstrates a real state transition:

| UI element | Story | Required consistency |
| --- | --- | --- |
| List or inbox | An item arrives, is selected, then handled | Selection, count and resulting state agree |
| Calendar | Choose a valid slot and confirm the event | Dates and availability remain coherent |
| Chart | Reveal the data, then highlight one finding | Values, labels and axes retain their meaning |
| Editor / Cmd+K | Type to filter, select and show the result | Input and preview describe the same change |
| Continuous morph | Button → loader → check → player → slider → toggle → tabs → chart → toast | Same container morphs size/radius/color via `springTimeline` |

## Coded-video physics & architecture (from `awesome-opus5-5-videos`)

When coding UI motion for video export (`window.seek(t)`):

1. **Closed-form step-response springs (`stepSpring`, `springTimeline` in `templates/motion-helpers.js`):**
   Every style is computed purely from time `t` inside `window.seek(t)` with zero state carried between frames. A property that changes target multiple times across a beat grid is the sum of one step-response spring per target change:
   `v(t) = v0 + sum_i (v_i - v_{i-1}) * stepSpring(t, t_i, zeta, omega)`.
2. **Dual-spring liquid morphs (`liquidSpan` in `templates/motion-helpers.js`):**
   For tab indicators, toggle knobs and selection pills, drive the leading edge with a faster spring (`omega = 18`) and the trailing edge with a slower spring (`omega = 11`). The element naturally stretches during motion and settles cleanly at rest.
3. **Direct-manipulation cursor drags:**
   While the cursor is held down (`t_grab <= t <= t_release`), compute the slider or card position directly from the cursor's coordinates; on `t > t_release`, spring back from the release position.
4. **Critical rendering gotchas:**
   - **Never put `will-change: transform` on an element that the camera scales up**, or Chromium caches the layer at 1x and renders blurry text.
   - **Separate exit and enter windows for swapped text:** inside a morphing container, fade/blur the old text out before the new text rises in so they never overlap.
   - **Seamless loops:** make the last frame (`seek(DURATION)`) identical to the first frame (`seek(0)`), including cursor coordinates, counters, active tabs and velocity.

## Unslop Redline Story Video (`studio.py unslop-story`)

Adapted from `heydamir/unslop` (Damir Sokolovsky `@heydamir`, CC BY 4.0). When the user wants a viral "Before → After" UI transformation video showing a vibecoded screen unslopping itself step by step:

1. Generate the deterministic `window.seek(t)` story template:
   ```bash
   python -S studio.py unslop-story output/jobs/ID/source/story.html --ramp graphite --duration 8
   ```
2. **How the transformation works:**
   - **Nothing is swapped, everything morphs in place:** 4 sequential passes (`Spacing` → `Color and icons` → `Type and copy` → `Details`) interpolate padding, gaps, radii, surface colors and typography inside `window.seek(t)`.
   - **Live redlines (`#ff4d6a` → `#f5f5f5`):** red measurement tags display the off-grid gaps/paddings/radii, count live toward the 4px-grid target values as the elements move, and turn white (`#f5f5f5`) once fixed.
   - **Attribution:** every Unslop story video retains the credit `unslop method by @heydamir (CC BY 4.0)`.

Inspect start, each pass transition, settled state and seam at the intended output size (`studio.py polish`), then render and probe the final MP4.
