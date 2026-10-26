# UI to motion

## Decide whether this is an embedded interaction or a film

For an existing website, animate only the requested area and keep its live text and controls accessible. For a standalone showcase, agree the output size, duration and whether it loops. Do not automatically deliver multiple GIF formats or turn a small motion request into a full film.

Read the supplied design through the available Figma connector, local file or image. Prefer an existing authorized integration over requiring a new personal token. If the input is a flat screenshot, state which elements can be isolated or reconstructed; do not promise layer-perfect fidelity from information that does not exist.

## Establish an accurate still first

Identify fixed surfaces, content groups, overlays and elements that will actually change. Preserve relative geometry, clipping, type, images and hierarchy. Export assets only when needed for fidelity; retain semantic live text in the web result where practical.

Compare the reconstructed final frame to the supplied reference at the same viewport and scale. Check crop, alignment, shadows, masks and font loading. Inspect difference images when useful, but judge intentional implementation differences separately. Never report pixel accuracy solely because the dimensions match.

## Animate behavior, not just arrival

A good sequence demonstrates a real state transition:

| UI element | Story | Required consistency |
| --- | --- | --- |
| List or inbox | An item arrives, is selected, then handled | Selection, count and resulting state agree |
| Calendar | Choose a valid slot and confirm the event | Dates and availability remain coherent |
| Chart | Reveal the data, then highlight one finding | Values, labels and axes retain their meaning |
| Editor | Make a small edit and show its result | Input and preview describe the same change |
| Workflow | A known input passes through actual stages | Do not imply unsupported automation |

Use motion to connect action and result. For joined app surfaces, keep the frame stable while content changes. For independent cards, a short group entrance can establish hierarchy. Avoid animating every region continuously; let the demonstration direct attention.

## Make the clock reproducible

Use the chosen engine's timeline contract. In HyperFrames, use its paused GSAP timeline instead of importing a second capture-clock framework from another skill. Load local assets and wait for fonts before a reference capture. Avoid random data, wall-clock timing and network-dependent states during export.

For a requested loop, explicitly model intro, action, reading hold, exit and reset. Reset both visual styles and logical values: typed text, counters, selected items, masks and cursors. Compare the beginning and end, inspect frames around the seam, and check that no hidden layer appears during reset. A live website demonstration may stop in a useful final state rather than dissolving endlessly.

Inspect start, action peak, settled state and seam at the intended output size. Test reduced-motion and offscreen behavior on web. Encode only the requested formats, then inspect the encoded file as well as the source preview. Do not describe animated screenshots as a live recording of the application.
