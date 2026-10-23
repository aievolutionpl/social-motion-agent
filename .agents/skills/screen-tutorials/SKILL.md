---
name: screen-tutorials
description: Record real websites or desktop apps and turn their workflows into product showcases or step-by-step tutorials, including Polish AI-tool lessons, using this workspace's OpenScreen setup.
---

# Nagrania, pokazy i tutoriale narzędzi AI

Project root: three directory levels above this skill folder. Read `START_HERE.md`, then `workflows/SCREEN_TUTORIALS.md`. Runtime, comparison and limits: `docs/OPENSCREEN.md`; current verification: the current job HANDOFF.md.

## Route the request

- A short product/feature demonstration → `python -S studio.py route showcase`.
- An educational lesson with reproducible steps → `python -S studio.py route tutorial`.
- A raw recording is the capture step of either route, without adding an unrequested voice, camera or publication.

Use the existing five-question intake for a new film; tailor its questions to the tool, learner, outcome, duration/platform and narration. Reuse known answers and existing brand decisions. Adding this integration or running a technical fixture is not a new creative film and does not require an intake round.

Research the demonstrated tool's current official documentation and actual UI before writing instructions. Record its URL/version/date, prerequisites, account tier and limitations relevant to the lesson. Show genuine actions and results. A simulated interface must not be presented as footage of the real application.

## Capture and edit

OpenScreen is the selected recorder and demo editor. Use `scripts/openscreen.py` with your separately installed runtime configured through `config/openscreen.json`. The upstream skill is `tools/repos/openscreen/plugin/skills/openscreen-demo/SKILL.md`; its MCP workflows are available only when those tools are actually connected. The existing CLI works without a global MCP registration or a new agent session. Do not stop a CLI-capable task merely because MCP is absent.

Record one uniquely named, prepared application window with a finite duration. The wrapper checks that the selector matches exactly one window and never falls back to the desktop. Use a clean profile/demo data, keep secrets and notifications outside the take, and enable mic, system audio or camera only when they serve the requested film. Save raw footage, `.cursor.json`, webcam/audio sidecars and project together in the job. `pack` currently handles legacy v2 projects; editor/caption-generated documents need their assets collected separately.

Browser automation does not move the physical pointer. Preserve real action timestamps and coordinates; if MCP is connected, supply them through `setPointerTrack` with the mapping described by its current schema. Otherwise use intentional manual zooms and callouts. Do not claim auto-zoom has click data when telemetry is missing. Keep the actual UI readable in a vertical adaptation; reframe or crop deliberately.

For Polish narration use scripts/voiceover.py with your own voice ID and keep the chosen voice stable. OpenScreen `--audio` mixes voiceover during export, while its `captions` command reads the recording's audio: voiceover added at export will not automatically receive captions. Generate/align captions from the real VO with our existing caption workflow, or use a recording with the narration already mixed in before captioning. Do not download an unneeded Whisper model for a silent capture.

## Review and deliver

Inspect a draft for the correct window, actual feature behavior, readable controls, coherent cursor/zoom and narration timing. Run full export, ffprobe/decode, inspect final frames, and verify names/pronunciation. Retain the original recording and editable project; register the selected MP4 in the normal job asset/timeline/probe/review/pack workflow.

Report tested capabilities separately from untested desktop capture, microphone/webcam, MCP connection and account access. Never infer a successful recording from an existing filename or from CLI help. Native Electron commands on this host require execution outside the restricted sandbox; do not disable Chromium security to work around it. Publication follows the existing explicit-approval rule.
