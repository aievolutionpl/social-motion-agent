"""Create an explicitly synthetic, editable film. Never fabricate human approval."""
import shutil
from studio_core import ROOT, create_job, now, read, write

def resize_template(html, width, height):
    html = html.replace("1920", "__WIDTH__").replace("1080", "__HEIGHT__")
    return html.replace("__WIDTH__", str(width)).replace("__HEIGHT__", str(height))

def create_demo(aspect="16:9"):
    gsap = ROOT / "node_modules/gsap/dist/gsap.min.js"
    if not gsap.is_file():
        raise ValueError("Run npm ci first to install the pinned local GSAP and HyperFrames dependencies.")
    folder = create_job("Social Motion Agent demo", "launch", aspect, 8, "en")
    job = read(folder / "job.json")
    job["synthetic_demo"] = True
    write(folder / "job.json", job)
    intake = read(folder / "intake.json")
    for question in intake["questions"]:
        question["answer"] = "Bundled synthetic example; not a user or client answer."
    write(folder / "intake.json", intake)
    brief = read(folder / "brief.json")
    brief.update(goal="Demonstrate the local production workflow", audience="Developers and creators",
                 direction="Editorial typography and precise motion", cta="Create your first film",
                 audio_required=False, engine="hyperframes", engine_reason="Local editable HTML composition")
    write(folder / "brief.json", brief)
    write(folder / "research.json", {"sources": [{"id": "local-demo", "title": "Bundled synthetic example",
          "url": "fixture:bundled-demo", "accessed_at": now(), "used_for": "No external factual claims"}],
          "claims": [], "conclusions": "Synthetic typography demo. No customer data, endorsements or performance claims."})
    write(folder / "storyboard.json", {"scenes": [
        {"id": "idea", "visual": "A strong idea becomes a film", "duration_sec": 2.6, "asset_ids": []},
        {"id": "workflow", "visual": "Brief, compose and review", "duration_sec": 2.6, "asset_ids": []},
        {"id": "result", "visual": "Editable films, ready for review", "duration_sec": 2.8, "asset_ids": []}]})
    html = (ROOT / "examples/launch/index.html").read_text(encoding="utf-8")
    html = resize_template(html, job["width"], job["height"])
    (folder / "source/index.html").write_text(html, encoding="utf-8")
    shutil.copy2(gsap, folder / "source/gsap.min.js")
    (folder / "source/script.md").write_text(
        "# Script\n\nSynthetic silent demo: From a clear idea. To a film worth watching. Brief. Compose. Review. Make it move.\n", encoding="utf-8")
    (folder / "HANDOFF.md").write_text("# Handoff\n\nSynthetic demo only. Run render-html, inspect the film, record actual review. No paid calls.\n", encoding="utf-8")
    return folder
