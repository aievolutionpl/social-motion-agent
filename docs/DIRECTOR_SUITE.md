# Director Suite: Explainroo + Argo + Huashu Motion patterns

> **Scope:** native, offline production planning and adapters in Social Motion Agent. No upstream runtime is installed or embedded by these commands. This is **not** a promise that an MP4 was generated or reviewed. All existing job evidence gates and authorizations remain in force.

## Why these three references?

| Source | Pattern adopted | Our implementation |
| --- | --- | --- |
| [Explainroo](https://github.com/vincentsch/explainroo) | Scene narration + precise word cues + agent-readable storyboards | Alignment JSON to `word-cues.json` + Unicode SRT; explainer project scaffold |
| [Argo CLI](https://github.com/shreyaskarnik/argo) | Playwright browser demos, scene manifest, narration marks, overlays | Argo `.scenes.json`, `.demo.ts`, `argo.config.mjs` handoff |
| [Huashu Motion](https://github.com/alchaincyf/huashu-motion) | Director rhythm sheet, product-first language, point-to-edit and visual QA | Beat sheet, pacing warnings, timestamp + normalized XY feedback queue, editorial handoff |

Code and text here are original implementations of broadly applicable patterns, not copied engines. Respect upstream licenses for any later runtime installations, sample content or assets (including Huashu's separate character exclusions).

## Quick start

Create a normal Social Motion Agent job:

```bash
python -S studio.py new "Demo CRM" --kind launch --format 9:16 --duration 15 --language pl
```

Copy the returned job path. Fill `storyboard.json` with real creative intent and durations summing to the job duration:

```json
{
  "scenes": [
    {
      "id": "hook",
      "duration_sec": 2,
      "visual": "Prawdziwy ekran produktu: leady trafiają do CRM",
      "narration": "Ile leadów gubisz w skrzynce?"
    },
    {
      "id": "action",
      "duration_sec": 7,
      "visual": "Użytkownik otwiera inbox i przypisuje kontakt",
      "narration": "Zobacz, jak działa automatyczna kwalifikacja."
    },
    {
      "id": "payoff",
      "duration_sec": 6,
      "visual": "Gotowy pipeline i czytelne CTA",
      "narration": "Wszystko w jednym miejscu."
    }
  ]
}
```

The `narration` field is optional. IDs must be unique slugs starting with a lowercase ASCII letter and containing only lowercase letters, digits, hyphens and underscores.

### Rhythm and QA (Huashu-inspired)

```bash
python -S studio.py director plan output/jobs/ID --profile launch
python -S studio.py director qa output/jobs/ID --profile launch
```

This produces editable `source/director/beat-sheet.json` and `source/director/beat-sheet.md` with computed scene offsets. `qa` checks for opening shots over three seconds (launch), unusually long shots, lack of visual intent, missing narration and repetitive cut lengths. **Warnings are editorial prompts, not scores**, and they do not certify what a rendered film looks or sounds like.

Profiles:
- `launch`: product launch and high-energy motion, default alert at shots longer than 2.5 seconds.
- `demo`: real interface / product walkthrough, alert at longer than 6 seconds.
- `explainer`: teaching and illustrations, alert at longer than 6 seconds.

Edit `storyboard.json` and rerun `plan --overwrite` if desired. Without `--overwrite`, generated files are never replaced silently.

### Upstream handoffs

```bash
python -S studio.py director handoff output/jobs/ID --profile demo
python -S studio.py director handoff output/jobs/ID --profile explainer
python -S studio.py director handoff output/jobs/ID --profile launch
```

All output lives under `source/interchange/`.

**Demo -> Argo:** The generated `argo/` subtree contains editable TypeScript and scenes JSON with matching narration markers, plus a local `argo.config.mjs`. Copy into a separate Argo workspace, edit selectors/actions, set `baseURL` to a dedicated test app, configure a supported Polish voice or import a recording, run `npx argo doctor` then `npx argo validate social-motion` and only then `npx argo pipeline social-motion`. No screen recording happens from the exporter. The generated placeholder script starts recording but has no app-specific Playwright clicks; it must be completed.

**Explainer -> Explainroo:** The `explainroo/` subtree includes `script.md`, `scenes.js`, `video.json` and instructions. Finish actual narration and drawings. Explainroo's bundled Kokoro voices do **not** offer Polish; bring in an actual Polish narration through a supported external audio workflow. Do not silently switch to English.

**Launch -> Huashu Motion:** The `huashu-motion/` subtree contains a director's brief and beat JSON, **not** a pretend `om`-compatible `index.html`. Install/run the original skill separately (`npx skills add alchaincyf/huashu-motion`) and let the agent create a product-specific composition. Use `om check`, `om qa`, and human viewing/listening on the final render.

### Word-aligned captions (Explainroo-inspired)

Use a measured word alignment exported by Whisper or another speech aligner. **Never** invent timings from word count.

`source/alignment.json` may be `{"words":[{"text":"Dzień","start":0.1,"end":0.4}, ...]}`, or Whisper-style `{"segments":[{"words":[{"word":"Dzień","start":0.1,"end":0.4}]}]}`.

```bash
python -S studio.py director captions output/jobs/ID --alignment source/alignment.json
```

Output: `source/director/word-cues.json` (each word linked to a storyboard scene) and UTF-8 `source/director/captions.srt`. Validates ordering, overlap, finite timestamps and duration. It does not synthesize voice, analyze a recording or prove that words were pronounced correctly.

### Point-to-edit feedback (Huashu-inspired)

Use fractions of the video frame: `x=0` left, `x=1` right, `y=0` top, `y=1` bottom.

```bash
python -S studio.py director feedback output/jobs/ID --at 6.8 --x 0.65 --y 0.35 --comment "Zwiększ rozmiar CTA"
python -S studio.py director feedback-list output/jobs/ID
```

Feedback appends to `notes/director-feedback.jsonl` with a matched scene ID and relative scene time. The queue **does not edit the source automatically** and its items default to `status=open`. The agent should inspect the correct frame, implement each requested change, rerender, and seek user approval before considering it resolved.

## Safety and evidence

- Existing `output/jobs/` boundary checks are used. Alignment is a job-local file, not an arbitrary external path. None of the above invokes a remote provider, downloads packages or publishes.
- Generated handoffs under `source/` participate in Social Motion Agent's source fingerprint. Changes invalidate earlier render receipts, so a new render and review are needed.
- Feedback is in `notes/`; it is a work queue, not proof of a completed edit.
- Use real product interfaces with test data and a dedicated testing account. Do not automate customer billing, destructive actions or live production without separate authorization.
- Retain the existing `check`, `probe`, `sheet` and `pack` gates. Rendered-video checks (glitches, captions, audio, rights, factual claims, legibility) cannot be replaced by these storyboard checks.
- If adapting actual upstream code or media beyond these self-authored patterns, audit and keep notices, pinned versions, and source-specific license requirements.

## Tests

```bash
python -S -B -m unittest tests/test_director_suite.py -v
python -S -B -m unittest discover -s tests -v
python -S scripts/release_check.py
```

Current support is intentionally **scaffolding and offline planning**, not verified runtime compatibility with all future versions of external tools.
