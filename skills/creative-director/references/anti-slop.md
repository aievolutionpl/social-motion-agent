# Anti-slop review & Unslop 9-Pass Craft System

Look for unmade decisions, not a forbidden aesthetic. A deliberate gradient in an established brand is different from a generic glow used to fill space. Keep useful detail: removing ornaments without adding a stronger composition can leave an empty, unhelpful result.

Adapted in part from **unslop** by Damir Sokolovsky (`@heydamir`, `https://github.com/heydamir/unslop`, CC BY 4.0).

## The core principle: One bright element, quiet chrome

The difference between AI slop and craft is **where the richness goes**:
- **Slop** spreads color and effects over the chrome: purple-to-blue backgrounds, glowing borders, gradient text, neon pills, emoji labels and pulsing badges.
- **Craft** keeps the chrome quiet (one tinted neutral ramp, three text roles, hairlines at 8% opacity, one accent used sparingly) and puts the richness into **one or two Moments** of content that people remember: a rendered object from the product's world, a carefully drawn main chart, or a concrete product preview.

## Write the 5-Line Direction before editing

Derive five short lines from what the product actually does and who it is for — never from generic trends:

1. **Product:** What it does and for whom, in one plain sentence.
2. **Character:** Two or three concrete words (`calm, exact, a little warm` or `fast, technical, playful`). Words like `clean`, `modern`, `sleek`, `minimal` and `premium` are banned because they describe every template.
3. **World:** The physical place or material the product belongs to (paper and ink → `warm` ramp; instruments and night shifts → `ink` ramp; neutral workspace → `graphite` ramp).
4. **Moments:** One or two places where the screen or film gets rich color, material and detail.
5. **Signature:** One small detail only this product would have (keycaps, live status dot, route line, domain glyph matrix), used consistently.

## The 9-Pass Redline Order

When cleaning up or building a coded screen or video frame, apply passes in this order:

1. **Spacing (4px grid):** Margins, paddings, gaps and heights sit on multiples of 4px (`--sp-*`). Space inside a group is smaller than space between groups. Equal items share one height and padding. Icons, labels and right-aligned numbers each sit in a strict column.
2. **Color (1 tinted ramp + 1 accent):** Pick `data-ramp="graphite|warm|ink"` in `templates/frame-tokens.css`. Three text roles (`--ink`, `--ink-2`, `--ink-3`), hairlines at 8% opacity, depth from surface steps (`--bg-0`, `--bg-1`, `--surface`, `--surface-hi`) instead of colored glows. Remove hue gradients on surfaces and gradient text.
3. **Icons:** Replace every emoji (`🚀 ✨ 💰 🔥`) with a consistent 1.5px stroke SVG line icon in the muted/secondary text color, or remove it if it adds no meaning.
4. **Copy:** Plain statements that fit only this product. No exclamation marks (`!`, `!!`), no greeting headlines (`Welcome back, X! 👋`), no hype words (`supercharge`, `seamless`, `unlock`, `magic`, `revolutionize`, `game-changing`, `AI-powered`). Every delta names its comparison (`+12% vs last month`, never `+12%!!`).
5. **Type:** Hierarchy from size and color, not weight 800–900. Use weights 400–600, sentence case instead of wide-tracked uppercase labels, `tabular-nums` (`.num`) in one consistent format, and zero or slightly positive tracking on small text (`<16px`).
6. **Layout:** Never shrink an app preview into a narrow centered column. For landing heroes, use an edge-to-edge world scene with text on calm empty space and the product rising from below, or an asymmetric split. Compose the frame with no dead empty band.
7. **Details (Nested radius & chart hierarchy):** Inner radius = outer radius minus padding, never below 4px. One main chart clearly leads; secondary data uses a compact list or table, never a second equal chart. Stat cards hold numbers, labels and comparison deltas — no decorative mini-sparklines.
8. **Visuals & Code Treatments:** Remove glossy blobs, orbs, nebulas and stock robots. Use real product UI previews, studio-lit world objects, or deterministic code treatments from `templates/motion-helpers.js`:
   - **Domain Glyphs (`bakeGlyphAtlas` + `drawGlyphs`):** Draw an image as a grid of characters from the product's own material (finance `. : 1 7 4 0 8 $ %`, code `. : / { } < > = #`, data `. · : | + ▪`). Bake the pixel sample once outside `seek(t)`.
   - **Halftone Dots (`drawHalftone`)** or **Duotone** mapped to the ramp and accent.
9. **Motion:** Remove looping `animate-pulse`/`animate-ping`, `transition-all`, bouncy hover scaling, and layout property animation (`width`, `height`, `top`, `left`). Move `transform` and `opacity` only, driven by `window.seek(t)` in video or one consistent easing curve on web.

## Diagnose and replace

| Symptom | Ask | Useful correction |
| --- | --- | --- |
| Every section is a row of equal cards | Does the content really have equal roles? | Give one main chart or item 2/3 width and keep supporting stats compact |
| Hero could advertise any competitor | What specific behavior, place, object or proof belongs here? | Make that the central visual, headline and `Signature` detail |
| Chrome glows while content is empty | Where should the eye land first? | Quiet the chrome to the neutral ramp and put color into 1–2 `Moments` |
| Constant movement with no focus | Where should the eye be at this instant? | Let support elements rest; move only the cause, action or result |
| Tiny annotation and crowded captions | Can someone read this at the final viewing size? | Enforce `>= 2.1cqmin`, recompose and run `studio.py polish` |

## Review in priority order

1. Truth and purpose: recognizable subject, supported claims, useful content.
2. Hierarchy and readability: one primary focus, clear grouping, legible words (`studio.py polish`).
3. Rhythm: enough variation to guide attention, enough repetition to feel coherent.
4. Craft: nested radii, column alignment, tabular figures, motion easing, audio edits and loop seams.
