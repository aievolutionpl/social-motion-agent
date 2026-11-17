"""Instantiate an editable ShotCraft scene with job-local media and a paused timeline."""
import html
import os
import re
import shutil
import tempfile
from pathlib import Path

import studio_core as core

RECIPES = ("flying-words", "carousel-3d", "before-after-slider-scrub")


def compose(folder, recipe, spec_path, overwrite=False):
    if recipe not in RECIPES:
        raise ValueError("Composable ShotCraft recipes: " + ", ".join(RECIPES))
    spec = core.read(core.local(folder, spec_path))
    job = core.read(folder / "job.json")
    target = core.local(folder, "source/index.html", exists=False)
    if target.exists() and not overwrite:
        raise ValueError("Composition exists. Use --overwrite to replace it.")
    gsap = core.ROOT / "node_modules/gsap/dist/gsap.min.js"
    if not gsap.is_file():
        raise ValueError("Run npm ci for the pinned GSAP runtime")
    colors = [spec.get(k, default) for k, default in (
        ("background", "#182221"), ("foreground", "#fbf8e9"), ("accent", "#e8aa66"))]
    if not all(isinstance(c, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in colors):
        raise ValueError("Palette values must be six-digit hex colors")
    assets = {a["id"]: a for a in core.read(folder / "assets.json")["items"]}
    copies = []
    def source_file(asset_id, extensions):
        item = assets.get(asset_id)
        if not item:
            raise ValueError("Unknown registered asset: " + str(asset_id))
        path = core.local(folder, item["path"])
        if path.suffix.lower() not in extensions or core.sha(path) != item["sha256"]:
            raise ValueError("Unexpected or modified media: " + asset_id)
        name = "shotcraft-" + item["sha256"] + path.suffix.lower()
        copies.append((path, name))
        return name

    if recipe == "flying-words":
        words = spec.get("words")
        if not isinstance(words, list) or not 1 <= len(words) <= 8 or not all(
                isinstance(w, str) and 0 < len(w.strip()) <= 48 for w in words):
            raise ValueError("Supply 1–8 short title words or phrases in words")
        layers = "".join("<span class='word'>" + html.escape(w) + "</span>" for w in words)
    else:
        ids = spec.get("assets")
        if not isinstance(ids, list) or not 2 <= len(ids) <= 6 or (recipe.startswith("before-") and len(ids) != 2):
            raise ValueError("Provide 2–6 product images or exactly two before/after images")
        images = [source_file(i, (".png", ".webp", ".jpg", ".jpeg")) for i in ids]
        layers = "".join(f'<div class="panel"><img src="{name}" alt=""></div>' for name in images)
        if recipe.startswith("before-"):
            layers += '<div class="divider"></div>'
    audio = ""
    if spec.get("audio"):
        name = source_file(spec["audio"], (".wav", ".mp3", ".m4a", ".aac", ".ogg"))
        audio = f'<audio id="score" src="{name}" data-start="0" data-duration="{job["duration_sec"]}" data-track-index="2"></audio>'
    template = (core.ROOT / "templates/shotcraft-scene.html").read_text(encoding="utf-8")
    settings = {"RECIPE": recipe, "WIDTH": job["width"], "HEIGHT": job["height"], "DURATION": job["duration_sec"],
                "FPS": job["fps"], "BACKGROUND": colors[0], "FOREGROUND": colors[1], "ACCENT": colors[2],
                "LAYERS": layers, "AUDIO": audio}
    page = re.sub(r"@@([A-Z]+)@@", lambda m: str(settings[m[1]]), template)
    for path, name in copies + [(gsap, "shotcraft-gsap.min.js")]:
        destination = core.local(folder, "source/" + name, exists=False)
        if not destination.exists():
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
                with path.open("rb") as stream:
                    shutil.copyfileobj(stream, tmp)
            os.replace(tmp.name, destination)
        elif core.sha(destination) != core.sha(path):
            raise ValueError("A scene dependency has been modified: " + name)
    with tempfile.NamedTemporaryFile(dir=target.parent, mode="w", encoding="utf-8", delete=False) as file:
        file.write(page)
    try:
        if overwrite:
            os.replace(file.name, target)
        else:
            os.link(file.name, target)
    finally:
        Path(file.name).unlink(missing_ok=True)
    return {"recipe": recipe, "source": "source/index.html", "duration": job["duration_sec"],
            "render_command": ["python", "-S", "studio.py", "render-html", str(folder), "--name", recipe]}
