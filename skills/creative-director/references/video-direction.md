# Video direction

## Plan what changes in the viewer's understanding

Write the film as a sequence of observable beats, not a sequence of transitions. Each scene needs a purpose, a focal element, readable text, duration, asset source and exit into the next scene. A shot can introduce a question, demonstrate an action, reveal a mechanism, compare states or deliver a result.

For a short social film, a useful starting structure is:

1. **Opening:** immediately show the subject, result or concrete problem. Choose the opening frame intentionally; a logo animation is rarely enough by itself.
2. **Development:** show how or why, using specific actions and evidence. Each cut adds information rather than restating the opening.
3. **Payoff:** resolve the opening with a visible result or clear explanation.
4. **Next action:** give one useful action when the brief calls for it. Do not add a sales CTA to a purely educational piece by default.

These are story functions, not fixed percentages of duration. An explanation may need a long hold; a product tease may need a concise reveal. Time the script aloud and against the actual narration before finalizing cuts.

## Pick a visual grammar

Use one of the [visual recipes](visual-recipes.md), or define an equivalent grammar from the brand. Record framing, typography roles, image treatment, color relationships and movement. Establish repeated elements that orient the viewer, then vary scale, viewpoint or composition for new information.

Use movement by meaning:

| Meaning | Candidate motion | Check |
| --- | --- | --- |
| New information joins a group | Short stagger in reading order | All items settle before reading begins |
| One object becomes another state | Match cut or shared-element transition | Identity remains recognizable |
| Mechanism or causality | Reveal one relationship at a time | Cause is visible before the result |
| Compare two states | Stable framing, deliberate wipe or cut | Labels and scale remain comparable |
| Emphasize a small detail | Controlled crop or camera move | Context survives and UI text stays readable |
| End a thought | Reading hold, then clean cut | The exit does not race the final word |

Avoid every scene entering from the same direction. Do not assign a different effect to every object. Movement, silence and stillness should have a pattern the viewer can follow.

## Compose for the actual frame

- Recompose each aspect ratio; do not assume a centered crop preserves the story.
- For vertical social delivery, start from the repo's safe-area tokens and check current platform overlays when the placement matters. Keep captions and key actions away from UI-covered edges.
- Judge readability at a realistic phone display size. A text minimum passing a script is not proof that the scene is comfortable to read.
- Keep the important subject visually distinct from supporting annotation. Avoid paragraph-sized title cards and competing text layers.
- Use real footage for observed actions, code for legible diagrams/UI, and generated imagery for shots whose role is explicitly illustrative. Label reconstructions where their status changes interpretation.

## Audio and captions

Make a cue sheet for narration, music changes and purposeful SFX. Build cuts around spoken phrases; avoid cutting off breath or the final syllable. Reduce background energy under speech and measure the mix against the chosen delivery requirements. Listen for clipping, masking, abrupt edits and inconsistent loudness.

Generate captions from the final voice track, then correct names, punctuation and timing. Keep line breaks at phrases, avoid covering the demonstration, and verify an audio-muted viewing pass. A missing audio review must remain an explicit limitation.

## Reproducible production

From the Social Motion Agent checkout, create the job and follow `docs/PRODUCTION.md`; use the actual engine's local skill and composition contract. For HyperFrames, use a paused GSAP timeline and local assets as documented in `docs/HYPERFRAMES.md`. Control time from the renderer: no wall-clock behavior, uncontrolled randomness or network-loaded fonts during capture.

The existing render adapters record source/render provenance. After source edits, render again; running a technical probe on an old MP4 does not establish that it matches the edited composition. Review and package the exact output hash.

## Retention experiments

When the user wants stronger reach, propose two or three opening hypotheses: result first, problem demonstration, or unexpected mechanism. Keep the rest of the piece comparable so the opening can be evaluated. Record the intended audience, changed variable and measurement, such as early retention or completed views, only if actual analytics are available. Do not promise virality or invent engagement numbers.
