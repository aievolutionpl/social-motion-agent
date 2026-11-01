# Two explainer directions

These are independent Social Motion art directions synthesized from two user-supplied briefs. Learn their visual and motion grammar; create new compositions for each subject. They extend the 12 upstream styles, without replacing `explainer`, `lowpoly` or `cartoon`. Choose one as the lead direction for a film. Combine directions only when the brief calls for it and the handoff preserves comprehension.

| Choose | Best fit | The image teaches through |
| --- | --- | --- |
| `isometric-line-art` — cinematic isometric line-art | Components, infrastructure, layered systems, mechanisms, material/energy/data flows | Drawing, assembly, cutaway, exploded view and a visible route to a consequence |
| `flat-vector` — premium flat-vector editorial explainer | Concepts, processes, choices, comparisons, service or product education | Illustrated interaction, changing state, meaningful shape morphs, masks and connected diagrams |

```bash
python -S studio.py styles recipe isometric-line-art
python -S studio.py styles recipe flat-vector
python -S studio.py styles find "" --style isometric-line-art --category explainer
python -S studio.py styles find "" --style flat-vector --category explainer
```

The CLI returns a style lock, suggested palette, implementation contract and an offline planning example. The examples are writing guidance, not rendered or approved films. Read this reference before composing either direction.

## Production settings come from the job

Keep one resolved brief in the existing job records: topic/question/comparison, audience and takeaway, selected style, storyboard decision, narration source/transcript, captions, fixed duration when silent, aspect ratio, native dimensions, output FPS/container, music and SFX. Resolve these before scene code; do not add a second contradictory configuration to a renderer. Suggested 30 fps and palettes are starting points, not overrides of the brief.

- Derive objects, claims, labels, beats and diagrams from the actual subject. The source briefs' example topic, 30 seconds and 9:16 are not defaults for every film.
- With narration, decode the actual recording duration and use it as the master timeline. Do not trim, stretch or synthesize replacement speech to fit a silent-duration setting. Mark estimated alignment honestly. With narration disabled, use the configured duration and make the visuals understandable without speech.
- With captions enabled, align to final speech; without speech, use requested explanatory captions. With captions disabled, omit subtitle work; concise object labels remain useful.
- Music and SFX are independent opt-ins. Use authorized assets/providers, record provenance and include enabled tracks in the final mix. Missing assets are an open requirement, not permission for paid generation.
- With a storyboard approval checkpoint, show a beat table plus genuine rendered representative frames and wait for the requested approval. Reuse approved geometry. If that checkpoint is explicitly waived, plan internally and continue through the existing production evidence gates; never fabricate approval. Style selection alone does not waive a checkpoint.
- Use authentic assets and accurate interfaces for real brands. Research material claims; label illustrative quantities. Do not invent benchmarks, percentages or product capabilities.

The pasted briefs' Claude-only Artifact environment and bans on local tools are not requirements of these styles. Reuse Social Motion's existing engine, job records and render/export adapters. An HTML preview is a preview; a requested MP4 requires an actual decoded video with all visible layers and enabled audio. Report a missing exporter rather than renaming WebM to MP4. Style availability does not establish renderer or provider availability.

## Isometric line-art: the construction is the explanation

**Composition.** Create a coherent orthographic world with stable axes and believable relative scale. Objects need identifiable silhouettes, openings, joints, supports and meaningful internal construction. An abstract topic may use a spatial relationship diagram; do not force every idea into a machine. Use a dominant mechanism, concise takeaway and a few attached callouts. Reframe for each aspect ratio.

**Line system.** Separate strong silhouette, medium structural edges, fine internal detail and colored active routes. Optional construction guides fade as the object resolves. Reveal by path arc length with staged timing: principal contour, structure, detail, then the active relationship. Use a consistent dark technical canvas or a deliberate light-paper variant. The CLI's ink/turquoise palette is optional; orange can distinguish a second semantic flow. Resting structures stay quiet. Avoid heavy glow and excessive drafting clutter.

**Depth.** Hide rear edges using deliberate layer ordering, depth testing or sparse face fills. Reveal internals in an explicit cutaway/X-ray moment. Exploded parts retain alignment guides and return to coherent positions. Crossing paths must not imply a false connection. Do not expose every triangulation edge. If WebGL is useful, verify thick-line support and viewport sizing; SVG or Canvas can express the same grammar.

**Choreography.** Assemble parts along meaningful axes and around correct pivots. Follow a packet, material or energy from source along a visible route to its destination, then show the change it causes. Coordinate dependent motions; components remain connected unless separation is the explanation. Use small precise settles, not repeated bounce. Transition by extending a structural edge, tracking a route, entering a cutaway or rearranging related components. Keep orientation legible during pans and zooms.

**Beat planning.** Start with a recognizable subject in action. A possible sequence is assembly → reveal → flow → consequence → wider relationship, but select order and representations by the subject. Each major composition contains several informative changes, with time to read. Roughly 12–18 developments can suit a short film; this is a planning hint, not a quota or fixed scene count. Avoid an inert completed drawing held between unrelated resets.

**Copy-ready direction.** “Explain the configured topic as one connected isometric technical world. Make the subject recognizable before labeling it. Stage contour, structure, internal mechanism and a source-to-result flow; preserve axes, occlusion and mechanical connections. Let the camera and shared geometry carry the explanation. Use changing geometry to teach why the result occurs.”

## Flat-vector: the transformation carries the idea

**Composition.** Build original layered Bézier illustrations with confident silhouettes, purposeful internal details and mostly solid fills. Use a hero demonstration, supporting interaction and readable short labels. Keep curves, corners, contour weights and proportions consistent. Negative space and clear overlaps establish 2D depth. Subtle shadow or shallow parallax can clarify separation; full perspective rendering, glossy surfaces and clip-art packs change the direction.

**Color.** Start from ivory/ink with cobalt as the active accent, adding a secondary teal, coral or amber only when it distinguishes information. Recolor for a verified brand or subject. Keep color roles stable as objects morph. Use masks and layered fills rather than ornamental gradients or particles. Do not use color alone to communicate a critical difference.

**Morph grammar.** Carry an identifiable part into the next idea: a line unfolds into a route, an illustration separates into its components, a filled region becomes a comparison, or a shared silhouette reveals a new state. Morph only when the relationship makes sense. Match path topology, point order and endpoints; precompute samples/interpolators. For incompatible shapes, transform corresponding parts separately or use a motivated occlusion mask. Check intermediate frames for twisting, self-crossing and unreadable blobs. Keep labels stable during recognition moments.

**Choreography.** Use anticipation, decisive eased action, a slight follow-through and delayed connected motion. Stage quick structural changes, slower comprehension and overlapping handoffs. A virtual 2D camera can follow an object or pull back to show relationships, then settle for reading. Characters belong only where their gestures participate in the explanation. Avoid equal scene durations, endless elastic wobble, repeated icon entrances and transformation for its own sake.

**Beat planning.** Start with the subject or concrete problem, show an interaction and observable state change, transform a related shape into the next relationship, and end with a visible takeaway. Use comparison, cutaway, flow or typography only where it explains the topic. Do not force every subject into an identical five-step flow or a generic sales end card.

**Copy-ready direction.** “Explain the configured topic through original flat-vector editorial illustration. Show the causal interaction in the shapes themselves; carry a meaningful component through split/recombine morphs or tailored masks into the next idea. Preserve a coherent 2D drawing system, stable morph endpoints and readable pauses. Let the audience learn from the changing image.”

## Build and review either direction

1. Write the takeaway and causal beats, choose one style, then build one representative composition. Check recognition and phone-size readability before extending it.
2. Derive every visual state from `window.seek(t)` or the engine's equivalent pure-time contract. Cache geometry, labels, path lengths and interpolation. Preview can use an elapsed-time clock; capture cannot accumulate frame state or depend on fresh randomness. Keep native export resolution even if preview density is reduced.
3. Test direct and out-of-order seeking, state transitions and the ending. Inspect intermediate morph/cutaway frames as well as endpoints. Check label collisions, line visibility, hidden-edge ordering, path connections, mechanical pivots and changing quantities.
4. Render with the existing adapter, probe actual dimensions/duration/FPS/container and audio, and inspect frames across the whole film at realistic display size. Listen to the final mix when audio is present. Verify the muted visual explanation too.
5. Preserve source/render provenance and use the existing review/package gates. Automated checks do not establish educational clarity, listening approval or publication approval. Record any unresolved check; never claim a style recipe is a completed film.

## Source boundary

Synthesized from the two creative direction texts supplied by the workspace owner for integration into Social Motion. These profiles describe reusable composition and motion principles; they do not reproduce the full prompts, topic-specific scene sequences, another creator's template or source code. They are local Social Motion additions, separate from upstream Opus style attribution. No third-party media rights are granted by this guidance.
