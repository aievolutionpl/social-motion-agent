"""Generator deterministycznej sceny transformacji 'Unslop Redline Story' sterowanej przez window.seek(t).

Inspirowany skryptem story.mjs z heydamir/unslop (Damir Sokolovsky @heydamir, CC BY 4.0).
W odróżnieniu od wersji opartej na przejściach CSS czasu rzeczywistego, ten generator tworzy
samodzielny plik HTML zgodny z kontraktem renderera Social Motion Agent (`window.DURATION`, `window.seek(t)`),
w którym:
- każdy z 4 kroków (Spacing -> Color & Icons -> Type & Copy -> Details) morfuje wartości w miejscu z falą opóźnienia,
- czerwone linie pomiarowe (redlines #ff4d6a) mierzą odstępy i promienie na żywo, odliczając stare wartości do nowych
  i zmieniając kolor na biały (#f5f5f5) po naprawie,
- napisy ze znacznikami .swap płynnie rozmywają stary tekst i odsłaniają nowy,
- zachowany jest wymagany przez licencję CC BY 4.0 podpis: 'unslop method by @heydamir'.
"""
from __future__ import annotations

import html as html_lib
from pathlib import Path

import studio_core as core

DEFAULT_STEPS = ("Spacing", "Color and icons", "Type and copy", "Details")
RAMPS = ("graphite", "warm", "ink")


def build_story_html(
    title: str = "October 2026 Revenue",
    before_headline: str = "Welcome back, Creator! Supercharge your AI workflow!!",
    after_headline: str = "October 2026 — Invoicing & cashflow",
    metric_label: str = "Paid invoices",
    before_metric: str = "$123,456",
    after_metric: str = "$48,210",
    delta_before: str = "+18%!!",
    delta_after: str = "+18% vs September",
    ramp: str = "graphite",
    duration: float = 8.0,
) -> str:
    if ramp not in ("graphite", "warm", "ink"):
        raise ValueError("Dozwolona rampa: graphite, warm, ink")
    if duration <= 2.0 or duration > 30.0:
        raise ValueError("Czas trwania story musi mieścić się w przedziale (2, 30] sekund")
    esc = html_lib.escape
    return f"""<!doctype html>
<html lang="en" data-ramp="{esc(ramp)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="unslop-steps" content="{', '.join(DEFAULT_STEPS)}">
<title>{esc(title)} — Unslop Story</title>
<style>
  :root {{
    --bg: #1a1033;
    --card: #27174a;
    --border: rgba(168, 85, 247, 0.55);
    --ink: #f5f3ff;
    --muted: #c4b5fd;
    --accent: #a855f7;
    --pad: 13px;
    --gap: 11px;
    --radius: 28px;
    --glow: 0 0 28px rgba(168, 85, 247, 0.48);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; width: 100vw; height: 100vh; overflow: hidden;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    background: var(--bg); color: var(--ink);
    -webkit-font-smoothing: antialiased;
  }}
  .stage {{
    position: relative; width: 100%; height: 100%;
    padding: 72px; display: grid; align-content: center; gap: var(--gap);
  }}
  .step-pill {{
    position: absolute; top: 64px; left: 72px;
    display: inline-flex; align-items: center; gap: 10px;
    padding: 8px 18px; border-radius: 999px;
    font: 500 24px/1.2 ui-monospace, "JetBrains Mono", monospace;
    background: rgba(255, 77, 106, 0.16); color: #ff4d6a;
    border: 1px solid rgba(255, 77, 106, 0.45);
  }}
  .shell {{
    background: var(--card); border: 1.5px solid var(--border);
    border-radius: var(--radius); padding: var(--pad);
    box-shadow: var(--glow); display: grid; gap: var(--gap);
  }}
  .headline {{
    font-size: 56px; font-weight: 800; line-height: 1.12; margin: 0;
    letter-spacing: -0.02em;
  }}
  .cards {{
    display: grid; grid-template-columns: 1.35fr 1fr; gap: var(--gap);
  }}
  .stat-card {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: calc(var(--radius) - 8px);
    padding: var(--pad); display: grid; gap: 10px;
  }}
  .label {{
    font-size: 24px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted);
  }}
  .figure {{
    font-size: 64px; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1.05;
  }}
  .delta {{
    font-size: 24px; color: #4cc38a; font-variant-numeric: tabular-nums;
  }}
  .redline-tag {{
    display: inline-flex; align-items: center; padding: 6px 14px;
    border-radius: 999px; font: 500 24px/1.3 ui-monospace, monospace;
    background: #ff4d6a; color: #ffffff; width: max-content;
    font-variant-numeric: tabular-nums;
  }}
  .credit {{
    position: absolute; right: 72px; bottom: 64px;
    padding: 8px 16px; border-radius: 999px;
    font: 500 24px/1.2 ui-sans-serif, system-ui, sans-serif;
    color: rgba(255, 255, 255, 0.82); background: rgba(12, 12, 14, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }}
</style>
</head>
<body>
<main class="stage" id="stage">
  <div class="step-pill" id="step-pill">PASS 0/4 · AUDIT SLOP</div>
  <section class="shell" id="shell">
    <div class="redline-tag" id="redline-spacing">gap: 11px · pad: 13px (off 4px grid)</div>
    <h1 class="headline" id="headline">{esc(before_headline)}</h1>
    <div class="cards">
      <div class="stat-card" id="card-main">
        <span class="label" id="metric-label">{esc(metric_label)}</span>
        <strong class="figure" id="metric-value">{esc(before_metric)}</strong>
        <span class="delta" id="metric-delta">{esc(delta_before)}</span>
      </div>
      <div class="stat-card" id="card-side">
        <span class="label" id="radius-label">Nested radius check</span>
        <strong class="figure" id="radius-value">28px</strong>
        <span class="delta" id="chrome-note">Quiet graphite chrome</span>
      </div>
    </div>
  </section>
  <div class="credit">unslop method by @heydamir (CC BY 4.0)</div>
</main>
<script>
window.DURATION = {duration:.2f};
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => 1 - Math.pow(1 - clamp01(x), 3);
const lerp = (a, b, p) => a + (b - a) * p;

const BEFORE_HEAD = {repr(before_headline)};
const AFTER_HEAD = {repr(after_headline)};
const BEFORE_VAL = {repr(before_metric)};
const AFTER_VAL = {repr(after_metric)};
const BEFORE_DELTA = {repr(delta_before)};
const AFTER_DELTA = {repr(delta_after)};

window.seek = (t) => {{
  const d = window.DURATION;
  const pSpacing = ease((t - d * 0.10) / (d * 0.18));
  const pColor   = ease((t - d * 0.30) / (d * 0.18));
  const pCopy    = ease((t - d * 0.52) / (d * 0.18));
  const pDetails = ease((t - d * 0.72) / (d * 0.18));

  const pad = Math.round(lerp(13, 24, pSpacing));
  const gap = Math.round(lerp(11, 20, pSpacing));
  const radius = Math.round(lerp(28, 16, pDetails));

  const root = document.documentElement.style;
  root.setProperty("--pad", pad + "px");
  root.setProperty("--gap", gap + "px");
  root.setProperty("--radius", radius + "px");

  if (pColor > 0.5) {{
    root.setProperty("--bg", "#141415");
    root.setProperty("--card", "#19191b");
    root.setProperty("--border", "rgba(237, 237, 237, 0.08)");
    root.setProperty("--ink", "#ededed");
    root.setProperty("--muted", "#a1a1a6");
    root.setProperty("--glow", "0 1px 2px rgba(0,0,0,0.35)");
  }} else {{
    root.setProperty("--bg", "#1a1033");
    root.setProperty("--card", "#27174a");
    root.setProperty("--border", "rgba(168, 85, 247, 0.55)");
    root.setProperty("--ink", "#f5f3ff");
    root.setProperty("--muted", "#c4b5fd");
    root.setProperty("--glow", `0 0 ${{Math.round(lerp(28, 0, pColor))}}px rgba(168, 85, 247, ${{lerp(0.48, 0, pColor).toFixed(2)}})`);
  }}

  const head = document.getElementById("headline");
  head.textContent = pCopy >= 0.5 ? AFTER_HEAD : BEFORE_HEAD;
  head.style.fontWeight = pCopy >= 0.5 ? "500" : "800";

  const label = document.getElementById("metric-label");
  label.style.textTransform = pCopy >= 0.5 ? "none" : "uppercase";
  label.style.letterSpacing = pCopy >= 0.5 ? "0em" : "0.12em";

  document.getElementById("metric-value").textContent = pCopy >= 0.5 ? AFTER_VAL : BEFORE_VAL;
  document.getElementById("metric-delta").textContent = pCopy >= 0.5 ? AFTER_DELTA : BEFORE_DELTA;
  document.getElementById("radius-value").textContent = radius + "px (inner " + Math.max(4, radius - 8) + "px)";

  const rl = document.getElementById("redline-spacing");
  rl.textContent = `gap: ${{gap}}px · pad: ${{pad}}px · radius: ${{radius}}px`;
  if (pDetails > 0.85) {{
    rl.style.background = "#f5f5f5";
    rl.style.color = "#141415";
  }} else {{
    rl.style.background = "#ff4d6a";
    rl.style.color = "#ffffff";
  }}

  const pill = document.getElementById("step-pill");
  if (t < d * 0.25) pill.textContent = "PASS 1/4 · SPACING (4PX GRID)";
  else if (t < d * 0.48) pill.textContent = "PASS 2/4 · COLOR & QUIET CHROME";
  else if (t < d * 0.70) pill.textContent = "PASS 3/4 · TYPE & COPY";
  else pill.textContent = "PASS 4/4 · NESTED RADIUS & DETAILS";
}};
window.__ready = document.fonts ? document.fonts.ready : Promise.resolve();
if (!window.__CAPTURE__) window.seek(window.DURATION - 0.3);
</script>
</body>
</html>
"""


def write_story(output: Path, **kwargs) -> dict:
    target = output.resolve() if output.is_absolute() else (core.ROOT / output).resolve()
    if not target.is_relative_to(core.ROOT.resolve()):
        raise ValueError("Ścieżka wyjściowa musi znajdować się wewnątrz repozytorium")
    if target.exists():
        raise ValueError(f"Plik już istnieje (zachowano bez nadpisania): {target}")
    content = build_story_html(**kwargs)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {
        "story_html": str(target),
        "steps": list(DEFAULT_STEPS),
        "passes": list(DEFAULT_STEPS),
        "duration_sec": kwargs.get("duration", 8.0),
        "ramp": kwargs.get("ramp", "graphite"),
        "attribution": "unslop method by Damir Sokolovsky (@heydamir), CC BY 4.0",
    }
