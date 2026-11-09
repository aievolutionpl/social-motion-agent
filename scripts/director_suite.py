"""Director Suite: local planning, upstream handoffs, timed cues and point feedback.

Patterns reimplemented from Explainroo (word cues), Argo (Playwright scene
manifests) and Huashu Motion (beat sheet / point-to-edit / editorial QA).
No upstream code or runtime is bundled, and nothing invokes paid APIs.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import studio_core as core

PROFILES = ("explainer", "demo", "launch")
LIMITS = {"explainer": 6.0, "demo": 6.0, "launch": 2.5}
UPSTREAM = {
    "explainer": "https://github.com/vincentsch/explainroo",
    "demo": "https://github.com/shreyaskarnik/argo",
    "launch": "https://github.com/alchaincyf/huashu-motion",
}
SCENE_ID = re.compile(r"^[a-z][a-z0-9_-]{0,39}$")


def _number(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{label}: expected a finite number")
    return float(value)


def _read_scenes(folder: Path) -> tuple[dict, list[dict]]:
    job = core.read(core.local(folder, "job.json"))
    duration = _number(job.get("duration_sec"), "duration_sec")
    if duration <= 0:
        raise ValueError("Job duration must be positive")
    raw = core.read(core.local(folder, "storyboard.json")).get("scenes", [])
    if not isinstance(raw, list) or not raw:
        raise ValueError("Complete storyboard.json scenes before using Director Suite")
    elapsed, ids, scenes = 0.0, set(), []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Scene {index + 1}: expected an object")
        name = item.get("id")
        if not isinstance(name, str) or not SCENE_ID.fullmatch(name) or name in ids:
            raise ValueError(f"Scene {index + 1}: ID must be unique and slug-safe (a-z, 0-9, _ or -)")
        ids.add(name)
        seconds = _number(item.get("duration_sec"), f"{name}.duration_sec")
        if seconds <= 0:
            raise ValueError(f"{name}: duration must be positive")
        visual = item.get("visual", "")
        narration = item.get("narration", "")
        if not isinstance(visual, str) or not isinstance(narration, str):
            raise ValueError(f"{name}: visual and narration must be strings")
        start = elapsed
        elapsed += seconds
        scenes.append({
            "id": name, "start_sec": round(start, 3), "end_sec": round(elapsed, 3),
            "duration_sec": seconds, "visual": visual.strip(),
            "narration": narration.strip(),
            "transition": item.get("transition", "cut") if isinstance(item.get("transition", "cut"), str) else "cut",
        })
    if abs(elapsed - duration) > max(0.05, 1 / int(job.get("fps", 30))):
        raise ValueError(f"Storyboard totals {elapsed:.3f}s, job requires {duration:.3f}s")
    return job, scenes


def _profile(value: str) -> str:
    if value not in PROFILES:
        raise ValueError("Choose profile: explainer, demo or launch")
    return value


def _write_files(folder: Path, files: dict[str, str], overwrite: bool) -> list[str]:
    paths = [(core.local(folder, name, exists=False), value) for name, value in files.items()]
    conflicts = [p for p, _ in paths if p.exists()]
    if conflicts and not overwrite:
        raise ValueError("Existing handoff files were not overwritten: " + ", ".join(str(p.relative_to(folder)) for p in conflicts))
    for path, value in paths:
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != folder and parent.is_relative_to(folder)):
            raise ValueError("Refusing to write through a symlink")
    for path, value in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    return [p.relative_to(folder).as_posix() for p, _ in paths]


def _markdown_beat_sheet(job: dict, scenes: list[dict], profile: str) -> str:
    lines = [
        f"# {job['title']} | Director beat sheet", "",
        f"Profile: {profile}. Duration: {job['duration_sec']:g}s. Format: {job['format']}.",
        "Timings come from storyboard.json, not a rendered timeline.", "",
        "| Start | End | Scene | Visual / action | Transition |",
        "| ---: | ---: | --- | --- | --- |",
    ]
    for scene in scenes:
        visual = scene["visual"].replace("|", "/").replace("\n", " ")
        lines.append(f"| {scene['start_sec']:.2f}s | {scene['end_sec']:.2f}s | {scene['id']} | {visual or 'TODO: real product shot'} | {scene['transition']} |")
    lines += [
        "", "## Editorial pass", "",
        "- Verify the first 3 seconds contain an actual hook, not only a title card.",
        "- Use genuine brand assets, screen recordings and claims; no fabricated proof.",
        "- Vary visual scale and camera language; avoid repetitive slide-like transitions.",
        "- Confirm the music accents and voice phrases against the final rendered audio.",
        "- Do not mark audio, visual or accessibility review as passed from a plan alone.",
    ]
    return "\n".join(lines) + "\n"


def plan(folder: Path, profile: str, *, overwrite: bool = False) -> dict:
    profile = _profile(profile)
    job, scenes = _read_scenes(folder)
    payload = {
        "schema_version": 1, "profile": profile, "job_id": job["id"],
        "duration_sec": job["duration_sec"], "format": job["format"],
        "source": "storyboard.json", "upstream_inspiration": UPSTREAM[profile],
        "rendered": False, "reviewed": False,
        "scenes": scenes,
    }
    names = _write_files(folder, {
        "source/director/beat-sheet.json": json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        "source/director/beat-sheet.md": _markdown_beat_sheet(job, scenes, profile),
    }, overwrite)
    return {"files": names, "profile": profile, "rendered": False, "qa": analyze(folder, profile)}


def analyze(folder: Path, profile: str) -> dict:
    profile = _profile(profile)
    job, scenes = _read_scenes(folder)
    warnings = []
    if profile == "launch" and scenes[0]["duration_sec"] > 3:
        warnings.append("First shot exceeds 3 s; verify the hook lands within the first 3 s")
    if len(scenes) < 3 and profile == "launch":
        warnings.append("Fewer than 3 shots in a launch film; assess movement and visual variety")
    overlong = [s["id"] for s in scenes if s["duration_sec"] > LIMITS[profile]]
    if overlong:
        warnings.append(f"Check shot movement/retention: duration over {LIMITS[profile]:g}s in " + ", ".join(overlong))
    if len(scenes) >= 4:
        durations = [s["duration_sec"] for s in scenes]
        if max(durations) - min(durations) < 0.15:
            warnings.append("Uniform shot durations; consider accents, contrast and varying pace")
    missing_visual = [s["id"] for s in scenes if not s["visual"]]
    if missing_visual:
        warnings.append("Missing scene visuals: " + ", ".join(missing_visual))
    if all(not s["narration"] for s in scenes):
        warnings.append("No scene narration registered; okay for music-led films, confirm intent")
    elif any(not s["narration"] for s in scenes):
        warnings.append("Some scenes lack narration; confirm intentional silent moments")
    return {
        "scope": "storyboard-only, not rendered-video quality certification",
        "profile": profile, "job_id": job["id"], "duration_sec": job["duration_sec"],
        "scene_count": len(scenes),
        "cut_points_sec": [s["end_sec"] for s in scenes[:-1]],
        "longest_scene_sec": max(s["duration_sec"] for s in scenes),
        "warnings": warnings, "rendered_review_required": True,
    }


def _argo(job: dict, scenes: list[dict]) -> dict[str, str]:
    prefix = "source/interchange/argo/"
    entries = []
    source = [
        "import { test, showOverlay } from '@argo-video/cli';", "",
        "test('social-motion', async ({ page, narration }) => {",
        "  // Configure baseURL, selectors and safe demo fixtures before recording.",
        "  await page.goto('/');",
        "  await narration.startRecording(page);",
    ]
    for scene in scenes:
        label = scene["visual"][:100] or scene["id"]
        entries.append({
            "scene": scene["id"], "text": scene["narration"],
            "overlay": {"type": "headline-card", "title": label,
                        "placement": "top-right", "motion": "fade-in"},
        })
        safe_id = json.dumps(scene["id"], ensure_ascii=False)
        source += [
            f"  narration.mark({safe_id});",
            f"  await showOverlay(page, {safe_id}, narration.durationFor({safe_id}));",
            "  // TODO: add real Playwright locators/actions for this scene.",
        ]
    source += ["});", ""]
    config = (
        "import { defineConfig } from '@argo-video/cli';\n"
        "export default defineConfig({\n"
        "  baseURL: 'http://localhost:3000', // Change to YOUR running test app\n"
        "  demosDir: 'demos', outputDir: 'videos',\n"
        f"  video: {{ width: {job['width']}, height: {job['height']}, fps: {job['fps']} }},\n"
        "});\n"
    )
    readme = (
        "# Argo handoff (scaffold, not a recording)\n\n"
        "Generated from storyboard.json. Replace placeholder overlays, configure baseURL, "
        "add Playwright actions/selectors, then verify narration and timing. "
        "Empty narration will not create a Polish TTS voice by itself.\n\n"
        "In a separate working copy with Argo installed, bring in the files, run "
        "`npx argo doctor`, `npx argo validate social-motion`, and only then "
        "`npx argo pipeline social-motion`. Recording can access the configured app; "
        "use test credentials and synthetic data, not live customer accounts.\n"
        "Source: https://github.com/shreyaskarnik/argo (MIT).\n"
    )
    return {
        prefix + "demos/social-motion.scenes.json": json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        prefix + "demos/social-motion.demo.ts": "\n".join(source),
        prefix + "argo.config.mjs": config,
        prefix + "README.md": readme,
    }


def _explainroo(job: dict, scenes: list[dict]) -> dict[str, str]:
    prefix = "source/interchange/explainroo/"
    script = ["# " + job["title"], ""]
    js = ["// Adapt labels and artwork to match each spoken paragraph.", "export default {"]
    for scene in scenes:
        script += ["## " + scene["id"], scene["narration"] or "[TODO: add spoken narration]", ""]
        label = scene["visual"][:110] or "Design a product-specific illustration"
        js += [
            f"  {scene['id']}(s) {{",
            f"    s.title({json.dumps(label, ensure_ascii=False)}, {{ at: 0 }});",
            "    // TODO: add images, icons and timed word/marker reveals.",
            "  },",
        ]
    js += ["};", ""]
    config = {
        "title": job["title"], "theme": "clean", "size": job["format"],
        "music": False, "captions": "auto",
    }
    if job["language"].casefold().startswith("en"):
        config["voice"] = "af_heart"
    readme = (
        "# Explainroo handoff (scaffold, not a rendered video)\n\n"
        "Edit script.md and scenes.js to tell a specific story. Scene and word "
        "timing is computed by Explainroo, not by this exporter.\n\n"
        "The bundled Kokoro voice list does not include Polish. For PL supply "
        "recorded or externally synthesized Polish narration and use an explicitly "
        "supported audio import path from Explainroo's current docs; do not "
        "assume an English default voice can pronounce Polish.\n"
        "Validate theme, voice and aspect ratio with the installed Explainroo version.\n"
        "Source: https://github.com/vincentsch/explainroo (MIT).\n"
    )
    return {
        prefix + "script.md": "\n".join(script),
        prefix + "scenes.js": "\n".join(js),
        prefix + "video.json": json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        prefix + "README.md": readme,
    }


def _huashu(job: dict, scenes: list[dict]) -> dict[str, str]:
    prefix = "source/interchange/huashu-motion/"
    lines = [
        "# Huashu Motion handoff",
        "",
        f"Title: {job['title']}",
        f"Aspect: {job['format']}, duration: {job['duration_sec']:g}s",
        "",
        "## Creative constraints",
        "- Read real product copy, images, screenshots and brand tokens before deciding motion language.",
        "- Present three distinct directions/keyframes before writing a full composition.",
        "- Motion must express a product change or user action; avoid PPT-like fades.",
        "- Align visual accents with a deliberate sound rhythm; check the mix by listening.",
        "- Run om check and om qa on the actual film; inspect individual frames.",
        "- Point-specific feedback is stored separately in notes/director-feedback.jsonl.",
        "",
        "## Scene intent (not executable om code)",
    ]
    for scene in scenes:
        lines.append(
            f"- {scene['start_sec']:.2f}–{scene['end_sec']:.2f}s [{scene['id']}]: "
            + (scene["visual"] or "TODO: product-specific shot")
        )
    lines += [
        "", "This is an editorial handoff, not an OM project or a tested render.",
        "Create and edit an OM index.html using the installed huashu-motion skill.",
        "Source: https://github.com/alchaincyf/huashu-motion (MIT; check third-party/character exclusions).",
        "",
    ]
    return {
        prefix + "DIRECTION.md": "\n".join(lines),
        prefix + "beat-sheet.json": json.dumps({"job": job["id"], "scenes": scenes}, indent=2, ensure_ascii=False) + "\n",
    }


def handoff(folder: Path, profile: str, *, overwrite: bool = False) -> dict:
    profile = _profile(profile)
    job, scenes = _read_scenes(folder)
    mapping = {"demo": _argo, "explainer": _explainroo, "launch": _huashu}
    files = _write_files(folder, mapping[profile](job, scenes), overwrite)
    return {"profile": profile, "upstream": UPSTREAM[profile], "files": files,
            "installed": False, "rendered": False, "requires_manual_completion": True}


def _aligned_words(data) -> list:
    if isinstance(data, dict) and isinstance(data.get("words"), list):
        return data["words"]
    if isinstance(data, dict) and isinstance(data.get("segments"), list):
        if any(not isinstance(seg, dict) or not isinstance(seg.get("words"), list) for seg in data["segments"]):
            raise ValueError("All segments need word arrays")
        return [word for seg in data["segments"] for word in seg["words"]]
    if isinstance(data, list):
        return data
    raise ValueError("Expected words array or Whisper-style segments[].words")


def _timestamp(value: float) -> str:
    ms = round(value * 1000)
    hh, ms = divmod(ms, 3600000)
    mm, ms = divmod(ms, 60000)
    ss, ms = divmod(ms, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def captions(folder: Path, alignment: str, *, overwrite: bool = False) -> dict:
    job, scenes = _read_scenes(folder)
    path = core.local(folder, alignment)
    words_in = _aligned_words(core.read(path))
    if not words_in or len(words_in) > 10000:
        raise ValueError("Alignment must contain between 1 and 10000 words")
    words = []
    previous_end = 0.0
    for i, raw in enumerate(words_in):
        if not isinstance(raw, dict):
            raise ValueError(f"Word {i}: expected object")
        content = raw.get("text", raw.get("word"))
        if not isinstance(content, str) or not content.strip() or len(content) > 100:
            raise ValueError(f"Word {i}: invalid text")
        start = _number(raw.get("start"), f"word {i} start")
        end = _number(raw.get("end"), f"word {i} end")
        if start < 0 or end <= start or start < previous_end - 0.001 or end > job["duration_sec"] + 0.05:
            raise ValueError(f"Word {i}: invalid order, timing or out-of-bounds")
        previous_end = end
        scene_id = next((s["id"] for s in scenes if start < s["end_sec"] - 0.0001), scenes[-1]["id"])
        words.append({"text": content.strip(), "start": start, "end": end, "scene_id": scene_id})
    groups = []
    group = []
    for word in words:
        if group and (len(group) >= 5 or word["start"] - group[-1]["end"] > 0.65
                      or word["end"] - group[0]["start"] > 2.6
                      or group[-1]["text"].endswith((".", "?", "!"))):
            groups.append(group)
            group = []
        group.append(word)
    if group:
        groups.append(group)
    srt = []
    for i, chunk in enumerate(groups, 1):
        text = " ".join(w["text"] for w in chunk)
        srt += [str(i), f"{_timestamp(chunk[0]['start'])} --> {_timestamp(chunk[-1]['end'])}", text, ""]
    files = _write_files(folder, {
        "source/director/word-cues.json": json.dumps({
            "source": alignment, "generated_from_measured_alignment": True,
            "language": job["language"], "words": words,
        }, ensure_ascii=False, indent=2) + "\n",
        "source/director/captions.srt": "\n".join(srt) + "\n",
    }, overwrite)
    return {"files": files, "word_count": len(words), "caption_count": len(groups),
            "timing_source": alignment, "audio_was_generated": False}


def point_feedback(folder: Path, at: float, x: float, y: float, comment: str) -> dict:
    job, scenes = _read_scenes(folder)
    at, x, y = _number(at, "at"), _number(x, "x"), _number(y, "y")
    if not 0 <= at <= job["duration_sec"] or not 0 <= x <= 1 or not 0 <= y <= 1:
        raise ValueError("at must be in film duration and x/y normalized to 0..1")
    if not isinstance(comment, str) or not comment.strip() or len(comment) > 2000:
        raise ValueError("Feedback must contain 1..2000 characters")
    scene = next((s for s in scenes if at < s["end_sec"]), scenes[-1])
    record = {
        "created_at": core.now(), "status": "open", "scene_id": scene["id"],
        "at_sec": at, "scene_time_sec": round(at - scene["start_sec"], 3),
        "x": x, "y": y, "comment": comment.strip(),
    }
    file = core.local(folder, "notes/director-feedback.jsonl", exists=False)
    if file.is_symlink():
        raise ValueError("Refusing to append to a symlink")
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"file": file.relative_to(folder).as_posix(), "feedback": record, "applied": False}


def list_feedback(folder: Path) -> dict:
    path = core.local(folder, "notes/director-feedback.jsonl", exists=False)
    if not path.exists():
        return {"feedback": []}
    if path.is_symlink():
        raise ValueError("Refusing to read feedback symlink")
    return {"feedback": [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]}
