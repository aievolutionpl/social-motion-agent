# Style choice and revision loop

Apply this contract to every new film. Reuse answers from this conversation, but never silently pick an unrequested style. Ask about style before rendering; offer 2–3 concrete directions and recommend one. A user's explicit “choose for me” delegates this decision. Narrow revisions retain the approved style unless the user asks to change it.

## First response

Ask missing essentials together: audience/action, duration/format, preferred style/reference, audio and assets. Present choices as a compact table:

| Direction | First frame | Motion and rhythm | Tradeoff |
| --- | --- | --- | --- |
| Editorial timeline | Ivory background, ink type, coral edit marker | Clips split, reorganize and resolve into one output | Best for explaining this editor; quiet rather than cinematic |
| Kinetic typography | Large words on graphite | Word masks, camera pushes, beat-driven cuts | Strong launch hook; requires careful reading holds |
| Product close-up | Real supplied product UI | Cursor actions, zoom to result | Needs approved screenshots or recording |

Tailor choices to the subject. Show a representative frame or styleboard where rendering tools are available. Label concepts as concepts. Do not generate the whole film while awaiting a decision. Record the chosen direction and its actual source in the job's direction.md and existing intake.json; never invent approval fields.

## Setup without making the user operate the terminal

Inspect the checkout and run `python -S scripts/quickstart.py --browser` yourself when local film production is requested. This restores locked Node packages and the capture browser. If prerequisites are missing, report exactly which runtime is missing. Install system runtimes only through the environment's supported package manager and existing authorization; do not run arbitrary remote installation scripts or claim success without rechecking. Prepare focused upstream skills only when the job needs them. Optional Kinetic/Hypermotion runtimes and paid accounts remain separate.

## Every preview ends with useful feedback

Deliver the actual preview with a short self-review: strongest moment, weakest moment and a proposed correction. Ask:

- What should we keep?
- What should change? Give a timestamp if possible.
- How would you rate style, pacing and clarity from 1–5? “Skip rating” is valid.

Offer 2–3 specific next moves, for example “shorten the opener by 0.5 s”, “replace the second text scene with product footage” or “compare an editorial variant”. Explain the benefit and likely cost. Do not automatically render all alternatives.

Append the real answer to `feedback.md` in the existing job folder with version, output SHA, likes, dislikes, optional ratings and agreed changes. Do not infer ratings from silence. If feedback concerns a point in the frame, use the existing `studio.py director feedback` queue too. Preferences belong to this project unless the user explicitly wants them reused elsewhere.

Implement agreed changes, render a new version, inspect it, and report what changed and what remains. Never mark a queue item complete just because a plan exists. Preserve earlier notes and the approved direction. After delivery, ask whether the user accepts this version or wants another iteration; do not imply a perfect score or approval. Existing probe/review/package gates still apply.
