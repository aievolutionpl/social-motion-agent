---
name: motion-design
description: Motion design for agent-assisted video production.
---

# Motion design

Read templates/frame-tokens.css and docs/HYPERFRAMES.md. Use one dominant visual idea per scene, strong typography, sufficient reading holds and format-specific safe margins. Prefer movement that explains hierarchy: staggered reveals, precise transforms and restrained transitions. Use paused GSAP timelines registered as window.__timelines[compositionId]. Do not use timers, random animation or autoplay. Keep all dependencies local. Lint and render, inspect snapshots at beginning/middle/end and around cuts. No invented performance claims. Do not mark a technical render as visually approved.
