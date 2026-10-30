"""Kontrola dopracowania ramki HTML (scena wideo): pomiary w Chrome, reguły unslop (@heydamir, CC BY 4.0) plus bramki UX z ux-ui-agent-skills.

Uruchamiaj przez `python -I` (potrzebny Playwright z site-packages), np. z studio.py polish.
Mierzy tekst w docelowym formacie: poza kadrem, poza bezpiecznym polem platform, za mały,
nakładające się napisy, emoji, gradientowy tekst i sygnały slopu (hype copy, !!).
Potem odpala slop_tells i taste_audit z tools/repos/ux-ui-agent-skills.
Heurystyki upstreamu są sygnałem, nie wyrokiem; kod wyjścia 1 tylko dla błędów pomiarowych i wyników HIGH.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UX = ROOT / "tools/repos/ux-ui-agent-skills"
FORMATS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080)}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕✅❌✨]")
SLOP_COPY = re.compile(
    r"(?:!!|\b(?:supercharge|revolutionize|game-changing|seamless|unlock\s+the\s+magic|welcome\s+back,)\b)",
    re.IGNORECASE,
)

MEASURE = """() => {
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const text = walker.currentNode.textContent.trim();
    const el = walker.currentNode.parentElement;
    if (!text || !el || seen.has(el) || ['SCRIPT', 'STYLE', 'TITLE'].includes(el.tagName)) continue;
    seen.add(el);
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.display === 'none' || cs.visibility === 'hidden' || r.width === 0 || r.height === 0) continue;
    let opacity = 1;
    for (let n = el; n; n = n.parentElement) opacity *= parseFloat(getComputedStyle(n).opacity);
    const bgClip = (cs.webkitBackgroundClip || cs.backgroundClip || '').toLowerCase();
    const fillColor = (cs.webkitTextFillColor || '').toLowerCase();
    const gradientText = bgClip === 'text' && (fillColor === 'transparent' || fillColor === 'rgba(0, 0, 0, 0)');
    out.push({text: text.slice(0, 60), tag: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''),
      x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, size: parseFloat(cs.fontSize), opacity,
      weight: parseInt(cs.fontWeight, 10) || 400,
      tracking: parseFloat(cs.letterSpacing) || 0,
      gradient_text: gradientText,
      clipped: el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible', node: null});
  }
  return out;
}"""


def safe_insets(fmt: str, width: int, height: int) -> tuple[float, float, float]:
    """(boki, góra, dół) w px; zgodne z --safe-* w templates/frame-tokens.css."""
    short = min(width, height)
    side = 0.056 * short
    ratio = width / height
    if ratio <= 0.7:                       # pełnoekranowe Reels/Shorts/TikTok
        return side, 0.17 * short, 0.30 * short
    if ratio <= 0.8:                       # kadr 4:5 w feedzie
        return side, 0.08 * short, 0.10 * short
    return side, 0.056 * short, 0.056 * short


def overlap(a: dict, b: dict) -> float:
    w = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    h = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    if w <= 0 or h <= 0:
        return 0.0
    return w * h / min((a["x1"] - a["x0"]) * (a["y1"] - a["y0"]), (b["x1"] - b["x0"]) * (b["y1"] - b["y0"]))


def judge(items: list[dict], fmt: str, width: int, height: int) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    side, top, bottom = safe_insets(fmt, width, height)
    short = min(width, height)
    visible = [i for i in items if i["opacity"] > 0.05]
    if not visible:
        errors.append("Brak widocznego tekstu w ramce (zła chwila seek albo pusta scena)")
    for i in visible:
        label = f'"{i["text"][:28]}" ({i["tag"]})'
        if EMOJI.search(i["text"]):
            errors.append(f"Emoji w tekście {label}: użyj ikony SVG albo słów")
        if i.get("gradient_text"):
            errors.append(f"Gradientowy tekst (slop): {label} — użyj jednolitego koloru z rampy")
        if SLOP_COPY.search(i["text"]):
            warnings.append(f"Hasło z listy unslop (hype lub !!): {label}")
        if i.get("weight", 400) >= 800 and i["size"] < 0.08 * short:
            warnings.append(f"Zbyt gruby font ({i['weight']}) zamiast hierarchii rozmiarem: {label}")
        if i.get("tracking", 0) < -0.5 and i["size"] < 16:
            warnings.append(f"Ujemny tracking na małym tekście (<16px): {label}")
        if i["x0"] < -1 or i["y0"] < -1 or i["x1"] > width + 1 or i["y1"] > height + 1:
            errors.append(f"Tekst poza kadrem: {label}")
        elif i["x0"] < side - 1 or i["x1"] > width - side + 1 or i["y0"] < top - 1 or i["y1"] > height - bottom + 1:
            warnings.append(f"Tekst poza bezpiecznym polem platform ({fmt}): {label}")
        if i["size"] < 0.02 * short:
            errors.append(f'Za mały tekst {i["size"]:.0f}px (min {0.02 * short:.0f}px dla {fmt}): {label}')
        if i["clipped"]:
            warnings.append(f"Tekst ucięty przez overflow: {label}")
    for n, a in enumerate(visible):
        for b in visible[n + 1:]:
            share = overlap(a, b)
            if share > 0.08:
                errors.append(f'Nakładające się napisy ({share:.0%}): "{a["text"][:20]}" i "{b["text"][:20]}"')
    if visible:
        # rozmiar tekstu "zasadniczego": mediana ważona liczbą znaków (tam, gdzie leży większość treści)
        weighted = sorted((i["size"], len(i["text"])) for i in visible)
        half, running = sum(w for _, w in weighted) / 2, 0
        body = weighted[-1][0]
        for size, weight in weighted:
            running += weight
            if running >= half:
                body = size
                break
        largest = weighted[-1][0]
        if largest / body < 2.0:
            warnings.append(f"Słaba hierarchia: największy tekst {largest:.0f}px, tekst zasadniczy {body:.0f}px (cel co najmniej 2,5x)")
    return errors, warnings


def run_upstream(html: Path) -> dict:
    if not (UX / "node_modules/playwright").is_dir():
        return {"status": "skipped", "reason": "brak node_modules w tools/repos/ux-ui-agent-skills (npm install --ignore-scripts)"}
    findings = {}
    for gate in ("slop_tells", "taste_audit"):
        env = {**os.environ, "DS_REQUIRE_BROWSER": "1"}
        result = subprocess.run(["node", str(UX / "scripts" / f"{gate}.mjs"), str(html)], capture_output=True, text=True,
                                timeout=180, cwd=str(UX), env=env, encoding="utf-8", errors="replace")
        lines = [ln.strip() for ln in result.stdout.splitlines() if re.match(r"\s+(HIGH|MED|LOW)\s", ln)]
        findings[gate] = lines if result.returncode == 0 else [f"HIGH gate nie uruchomiła się: {(result.stderr or result.stdout)[-300:]}"]
    return {"status": "ran", "findings": findings}


def check(html: Path, fmt: str, seek: float | None, shot: Path | None, upstream: bool) -> dict:
    from playwright.sync_api import sync_playwright
    width, height = FORMATS[fmt]
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception:
            browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(html.resolve().as_uri())
        page.evaluate("() => window.__ready || Promise.resolve()")
        page.evaluate("() => document.fonts && document.fonts.ready")
        when = seek if seek is not None else page.evaluate("() => typeof window.DURATION === 'number' ? window.DURATION - 0.5 : null")
        if when is not None and page.evaluate("() => typeof window.seek === 'function'"):
            page.evaluate("(t) => window.seek(t)", when)
        page.wait_for_timeout(80)
        items = page.evaluate(MEASURE)
        if shot:
            shot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shot))
        snapshot = None
        if upstream:
            body = page.evaluate("() => document.documentElement.outerHTML")
            base = html.resolve().parent.as_uri() + "/"
            snapshot = Path(tempfile.mkdtemp(prefix="polish-")) / "frame.html"
            snapshot.write_text(re.sub(r"<head([^>]*)>", lambda m: m.group(0) + f'<base href="{base}">', body, count=1), encoding="utf-8")
        browser.close()
    errors, warnings = judge(items, fmt, width, height)
    report = {"file": str(html), "format": fmt, "viewport": [width, height], "seek_sec": when, "text_elements": len(items),
              "errors": errors, "warnings": warnings, "screenshot": str(shot) if shot else None}
    if snapshot:
        report["upstream"] = run_upstream(snapshot)
        findings = report["upstream"].get("findings", {})
        high = [f"{g}: {ln}" for g, lines in findings.items() for ln in lines if ln.startswith("HIGH")]
        report["upstream_high"] = high
    report["passed"] = not errors and not report.get("upstream_high")
    return report


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--format", choices=FORMATS, default="16:9")
    parser.add_argument("--seek", type=float, help="Sekunda sceny do zbadania; domyślnie koniec animacji")
    parser.add_argument("--shot", type=Path, help="Zapisz zrzut ekranu PNG")
    parser.add_argument("--no-upstream", action="store_true", help="Pomiń slop_tells i taste_audit")
    args = parser.parse_args(argv)
    if not args.html.is_file():
        print(f"Brak pliku: {args.html}", file=sys.stderr)
        return 1
    report = check(args.html, args.format, args.seek, args.shot, not args.no_upstream)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
