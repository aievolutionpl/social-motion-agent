---
name: social-motion-studio
description: Create or edit YouTube videos, social shorts, screen tutorials, app showcases, explainers and motion films using this workspace's production records, researched brief and skill routing.
---

# Social Motion Studio

Use the project root three levels above this skill folder. Read START_HERE.md, AGENTS.md and docs/PRODUCTION.md there.

For a new film read **skills/creative-director/SKILL.md**, then its video guidance and local **skills/intake/SKILL.md**. Reuse actual supplied answers across the five brief categories and ask only missing material questions with options. Respect an explicit request to skip; small revisions reuse the current brief. Run `studio.py skills plan --mode video`, then `skills setup --mode video` if the selected sources are missing.

Research before production. Record read sources and verified on-screen facts. Select only relevant instructions through studio.py route/find. Read the user-provided brand brief when applicable. Keep each production under output/jobs/ with a current HANDOFF.md.

Read docs/PROVIDERS.md for ElevenLabs narration, built-in imagegen and fal H3 Max b-roll. Check actual tools and existing authorization; instructions do not prove connectivity. Keep prompts/request IDs with local assets. Do not silently replace named providers.

Use the working local HTML renderer for motion or FFmpeg assembly for footage. HyperFrames is the primary HTML motion renderer; Hypermotion is a separate optional upstream tool. Inspect a draft before master, then probe, review and package the same hash. State any missing visual/audio checks. Publication requires explicit user approval.

For real website/application recordings use routes `showcase` or `tutorial`, then `.agents/skills/screen-tutorials/SKILL.md` and `docs/OPENSCREEN.md`. Install OpenScreen separately and set OPENSCREEN_EXECUTABLE. Adapter tests do not prove live desktop capture. Reuse the existing five-question intake for a new lesson.
