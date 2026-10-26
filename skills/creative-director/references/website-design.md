# Website design

## Start with the page's job

Separate a page people read from an interface people operate. A marketing page needs an understandable offer and a path to action. An app screen needs a clear task, honest state and usable controls. Do not force an editorial landing-page composition onto a dense working interface.

Inspect the existing stack, navigation, components and tokens. Keep them when they serve the task. Before styling, write one line per proposed section: what the visitor learns, what supports it, and what action follows. Remove sections that merely repeat a claim. Do not automatically add logos, testimonials, pricing tiers, guarantees or an FAQ without real content.

## Build a subject-specific first screen

The first screen should identify the offer or subject, give a concrete reason to continue and show the primary action where one is needed. Choose a visual that proves or explains something: actual product behavior, a relevant photograph, a useful diagram or an original illustration tied to the idea.

Use the chosen art direction to set roles for type, spacing, surface, accent and imagery. Prefer a small coherent system; reuse the brand's existing values. A particular font, gradient, border or layout is not inherently wrong. Judge whether it supports the content and remains consistent.

When Taste is selected, read the installed `design-taste-frontend` entry point and use its page/app distinction and direction library as alternatives. Its house-style inspector is opinionated: check findings against the actual brand and brief. Do not remove intentional branded elements merely to reach a tool score.

## Give sections different jobs and appropriate forms

| Content | Useful form | Avoid |
| --- | --- | --- |
| A visible product capability | Real UI crop with nearby explanation | Decorative grey bars pretending to be a product |
| A process | Ordered steps with a result at each step | Three unrelated icon cards |
| A comparison | Shared criteria and consistent scale | Invented competitor weaknesses |
| Evidence | Quote, result or demonstration beside the claim | Unsupported customer logos or numerical proof |
| A rich collection | Browsable list, gallery or table | Flattening everything into identical tiles |
| A decision | Plain options, costs and consequences | Decorative controls that do nothing |

Useful interaction can make a page memorable: a real material selector, product demonstration or grounded calculator. Add it only if it helps this visitor decide or understand. Implement loading, empty, error and success states when the interaction needs them.

## Motion has a location and a reason

Specify the element, trigger, behavior, duration/reading hold and fallback. A restrained hero entrance, a product state demonstration and a section transition are different tasks; they should not share one repeated effect.

Keep primary content visible without successful animation startup. Do not show an empty page while waiting for a timeline. Use reduced-motion preferences, pause offscreen decorative loops, preserve semantic text and keyboard operation, and avoid scroll hijacking. Web motion is not permission to export videos or add a new animation library.

## Verify before handoff

Use the project's tests/build and inspect the real browser at desktop and a narrow mobile width, plus an intermediate layout if the composition changes there. Check wrapping, horizontal overflow, image crop, focus visibility, touch targets, menu behavior, links/forms and console errors. Test long content and empty/error states for components changed by the work.

Choose metadata, indexability and structured data from the actual publication intent. Do not automatically noindex every campaign page or invent schema facts. If browser access is unavailable, explain that visual verification is pending; source inspection alone is not equivalent.
