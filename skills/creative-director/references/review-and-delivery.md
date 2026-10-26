# Review and delivery

Review evidence should answer what was inspected, at which version, and what remains uncertain. A command's successful exit is not visual approval. An attractive screenshot is not proof that a form or export works.

## Video and UI exports

Check the actual encoded output, not only the composition preview:

- Dimensions, aspect ratio, frame rate and expected duration; confirm the picture covers the whole intended timeline, not just the audio/container.
- Start/end, each scene's settled frame, frames around cuts, important actions and loop seams.
- Readability at intended viewing size; crop, safe areas, captions and word timing.
- Narration clarity, music balance, SFX placement, clipping and abrupt edits through actual listening when audio is present.
- Real claims, asset provenance, source licenses and the distinction between live footage, reconstruction and generated illustration.

Use the project's `check`, `sheet`, `probe` and `pack` commands as documented. Preserve render/source provenance from the actual renderer. After source changes, produce a new render and review that output; do not manufacture a provenance record or mark an old file current to pass a gate. An imported file with no trustworthy render history can be inspected, but its relationship to editable sources remains unverified.

The production record's approval fields must describe real review. A synthetic test fixture is never user approval. If the agent cannot listen or inspect the output, record the limitation and keep it a draft rather than inventing a pass.

## Websites and live motion

Inspect the running implementation at mobile and desktop widths. Exercise the primary journey, keyboard focus, navigation and modified form states. Test overflow, loading, empty and error states where relevant. For motion, check reduced-motion behavior and whether important content is still visible when animation startup fails. Use the project's available tests/build and report actual results.

If a source design was supplied, compare against that reference in the same viewport. Distinguish intended responsive adaptation from unintended fidelity changes. Do not use a taste inspector's result as a substitute for the brief or accessibility/functionality checks.

## Fix and finish

Prioritize defects by effect: false/missing content, broken behavior, illegibility, broken visual relationships, then cosmetic inconsistencies. Correct the most consequential issues and recheck changed areas. Avoid repeated full renders when a targeted frame can resolve the design question; render the final output when the composition is settled.

Deliver the requested editable sources and usable outputs with concise instructions. State the chosen direction, completed checks, important limitations and any user action needed. Do not create multiple formats or a large report merely to inflate the handoff. Publishing, sending to others and paid provider execution remain separate actions governed by the user's actual authorization.
