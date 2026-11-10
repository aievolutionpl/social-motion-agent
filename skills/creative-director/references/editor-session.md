# Editing partner: from choices to a reviewed film

Use for editing existing footage, product demos and original motion films. Keep the existing job records and evidence gates. The user is the creative decision maker; the agent does the technical work.

## Offer a decision, not an interview

Reuse known answers. Ask only material gaps in audience, goal, destination, duration, footage, brand and sound. Run `python -S studio.py directions session --for "subject" --mode footage|product|explainer` for a discussion scaffold. It is an offline menu, not media analysis. Inspect supplied media before recommending one direction. Tailor three choices to the actual subject: opening image, editing rhythm, design language, example transition, sound, asset requirements and tradeoff. Explain why your recommendation fits. Different choices must change storytelling, not just colors.

An explicit reference or existing approved direction may already resolve the choice. A delegated choice is sufficient: record its source and proceed. Otherwise wait for the requested selection; do useful media inventory while waiting. Never interpret silence as approval. Do not repeatedly ask for approval of routine edits already authorized.

## Select and assemble before decorating

Create a real inventory using metadata and visual/audio inspection: duration, dimensions, FPS, speech, quality, usable ranges, rights/source and missing material. Separate observations from suggestions. Preserve originals. Do not invent transcripts, word timings or in/out points. Use measured alignment for word captions.

Keep `edit-plan.md` beside the existing storyboard: timeline in/out, asset ID, source in/out, purpose, action/result, transition, audio cue and acceptance criterion. Check source ranges and timeline coverage. For interview/reel editing, establish the dialogue spine first; use J/L cuts when speech should bridge pictures, B-roll when it adds evidence or covers a necessary cut, and room tone across joins. Speed ramps must serve action and remain intelligible. Do not remove pauses that communicate emotion merely to maximize pace.

Save `direction.md`: real selection/delegation, palette and source, typography roles, texture, camera grammar, signature move, reference roles and prohibited clichés specific to this job. Match style to subject: a documentary may need quiet cuts; a launch may earn expressive motion. Neither novelty quotas nor a mandatory moving background override the brief.

## Make one scene prove the direction

Before expanding an uncertain design, build a representative scene at delivery size, including its most difficult transition and a short sound sample if sound is available. Clearly label a styleframe, animatic or placeholder. A beautiful still does not validate motion. Extend the approved visual system after feedback, then show a rough cut of the full story before expensive finishing.

For product scenes, keep one recognizable focal object. Make the action cause the visible result. Preserve the object's identity across transitions; open space before landing a moving item. Keep readable text separate from scaling/deforming surfaces. Measure cursor targets from layout; a cursor must reach its target before the result appears. Label authored mockups as illustrations. Never present them as recorded working functionality. Recompose portrait layouts instead of shrinking a desktop screen.

Animate attention and relationships: establish context, reveal action, hold the payoff. Use overlap deliberately, but keep the reading interval. Inspect departure, midpoint, landing and settled state for snaps, text shimmer, clipping and discontinuous data. A loop reset needs a visible cause or an unobtrusive seam. These principles work in the existing deterministic renderer; do not import a live React animation loop into frame capture without a tested time adapter.

## Sound and assets are production work

Maintain `audio-cues.md`: timeline cue, purpose, registered source, in/out, gain/fades, speech priority and actual verification status. Choose voice, ambience, music and SFX as separate layers. Use a real measured beat grid when syncing; do not invent BPM or timestamps. Place SFX on meaningful events, not every entrance. Preserve speech, duck music where needed, smooth audio joins and listen for masking, clicks, distortion and excessive peaks. Measure loudness against the agreed destination; no universal loudness target is an artistic guarantee. Recheck the encoded MP4, not just the source audio.

Use supplied/licensed assets first; record missing shots and rights honestly. Explain a stock, illustration or generation alternative before replacing a requested kind of material. Available generation tools, paid authorization and output quality must be checked separately. No available audio means an explicitly silent preview or cue plan, never a claim of completed sound design.

## Feedback that leads to a specific revision

Deliver the actual version with a short self-review and two or three concrete next moves: what changes, why it helps and its scope. Ask what to keep/change; invite timestamps and optional style/pacing/clarity ratings. Tie `feedback.md` to the rendered SHA and version. Record request, affected shot, proposed change, status and verification evidence. Preserve previous versions. Use the existing `director feedback` queue for frame coordinates.

Change only the agreed scope; a local timing fix does not reopen the style interview. Re-render after source changes, inspect the affected scene and neighboring transitions, then inspect the full export for continuity and audio. Mark an item resolved only after verifying the new output. A changed style may require a new representative scene. Final acceptance belongs to an identified version; technical probe and human creative acceptance remain distinct.

See `docs/EDITOR_UPGRADE_RESEARCH.md` for the source assessment. This workflow is authored guidance, not a vendored upstream runtime.

## Execute with the editor workspace

Read `docs/EDITOR_WORKSPACE.md` from the checkout. Run `editor inventory JOB` after registering supplied assets; inspect its actual samples, scene ranges and silence events. Read `editor preferences JOB` before choosing or revising designs. Run `editor directions JOB` for three initial visual studies, then customize the chosen study to the brief (the SVG generator does not design the final scene). Store real user preferences with evidence through `editor preferences --source`.

Use `editor plan --source` to validate and apply assembly changes with a backup; this edits the renderer's canonical timeline. For renders run `editor qa`, inspect reported events, and create `editor review --render ... --previous ...`. Import exported comments with `editor feedback-import`; read the resulting notes, never treat them as implemented changes or approval. Existing technical provenance and packaging checks remain required.
