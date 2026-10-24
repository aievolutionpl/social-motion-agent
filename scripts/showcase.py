"""Reproduce the 36-second portrait showcase using local assets, without AI API calls."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import shutil
import subprocess
from studio_core import ROOT, create_job, now, read, register_asset, write, probe_job

SCENES = [
    ("product", 5, "Photographic citrus concept and mask reveal"),
    ("dimension", 5, "48-face CSS cylinder with perspective and orbit"),
    ("kinetic", 4, "Staggered kinetic typography on lime"),
    ("retro", 4, "Pixel can and stepped motion"),
    ("process", 7, "Actual storyboard fields from this job"),
    ("workshop", 5, "Photo asset and kinetic graphic together"),
    ("close", 6, "Social Motion Agent and repository call to action"),
]
PROMPT = "Premium photographic advertising still for a fictional unbranded sparkling citrus drink. Vertical 9:16. Blank cobalt blue aluminum slim can with condensation, tilted 15 degrees, floating above orange slices and clear sparkling water. Tangerine seamless studio background, hard directional light, detailed metal and fruit. Upper 28 percent clean for typography. No letters, logos, watermark or border."

def prepare(folder: Path):
    source = folder / "source"
    if (source / "index.html").exists():
        raise ValueError("Composition exists; preserve it and create a new job.")
    gsap = ROOT / "node_modules/gsap/dist/gsap.min.js"
    if not gsap.is_file():
        raise ValueError("Run npm ci first.")
    job = read(folder / "job.json")
    if (job["width"], job["height"], job["duration_sec"]) != (1080, 1920, 36):
        raise ValueError("Showcase requires 1080x1920 and 36 seconds.")
    brief = read(folder / "brief.json")
    brief.update(goal="Demonstrate varied editable video styles and the real production files",
                 audience="Creators and entrepreneurs using Codex on Windows",
                 direction="Editorial product photography, geometric 3D, kinetic type and retro pixel art",
                 cta="Download and open in Codex", audio_required=True, engine="hyperframes",
                 engine_reason="Pinned local renderer supports reproducible HTML and paused GSAP without paid API calls")
    write(folder / "brief.json", brief)
    intake = read(folder / "intake.json")
    if any(not q.get("answer") for q in intake["questions"]):
        for q in intake["questions"]:
            q["answer"] = "Bundled showcase creative specification; not a new user answer. See brief.json."
        write(folder / "intake.json", intake)
    write(folder / "research.json", {"sources":[
        {"id":"project", "title":"Project source and production workflow", "url":"https://github.com/aievolutionpl/social-motion-agent", "accessed_at":now(), "used_for":"Editable HTML, JSON workflow and local rendering"},
        {"id":"motion", "title":"Pinned awesome-ai-motion: mask-reveal and flip-reveal", "url":"https://github.com/gongnyang/awesome-ai-motion", "accessed_at":now(), "used_for":"Local effect cards inspected; stagger, perspective and timing"},
        {"id":"rights", "title":"Media rights", "url":"repo:docs/MEDIA_RIGHTS.md", "accessed_at":now(), "used_for":"Owner-supplied sound library and its documented limitations"}],
        "claims":[], "conclusions":"Fictional product, no client results or performance claims. Product image generated once and bundled. 3D is actual CSS geometry, not a generated video. Process panel displays fields from the actual storyboard. Sound licensing documents remain pending; no commercial publication approval implied."})
    asset = register_asset(folder, ROOT / "examples/showcase/citrus.png", "Built-in imagegen, 2026-10-24", "AI-generated fictional unbranded demo product", "Product opening and workshop gallery", provider="imagegen", prompt=PROMPT)
    scenes=[{"id":key,"duration_sec":duration,"visual":visual,"audio":"Local SFX at scene boundaries", "asset_ids":[asset["id"]] if key in ("product","workshop") else []} for key,duration,visual in SCENES]
    write(folder / "storyboard.json", {"scenes":scenes})
    source.mkdir(exist_ok=True)
    for name in ("frame-tokens.css", "frame-starter.html"):
        shutil.copy2(ROOT / "templates" / name, source / name)
    shutil.copy2(gsap, source / "gsap.min.js")
    shutil.copy2(ROOT / "assets/fonts/PressStart2P-Regular.ttf", source / "pixel.ttf")
    shutil.copy2(ROOT / "examples/showcase/citrus.png", source / "citrus.png")
    plan=json.dumps({"format":"9:16", "duration_sec":job["duration_sec"], "scenes":[s["id"] for s in scenes[:4]]},ensure_ascii=False,indent=2)
    composition=(ROOT / "examples/showcase/index.html").read_text(encoding="utf-8").replace("__PLAN__",html.escape(plan))
    (source / "index.html").write_text(composition,encoding="utf-8")
    (source / "image-prompt.txt").write_text(PROMPT,encoding="utf-8")
    (source / "script.md").write_text("# Showcase script\n\n"+"\n".join(f"{key}: {duration}s. {visual}." for key,duration,visual in SCENES)+"\n\nSound-led, no narration. Local SFX only; no paid calls.\n",encoding="utf-8")
    (folder / "HANDOFF.md").write_text("# Showcase\n\n36s portrait. Inspect every scene with polish, render, inspect transitions and listen to audio. Do not fabricate approval. Generated image provenance is in assets.json. Public media license documents remain pending.\n",encoding="utf-8")
    return folder

def mix(folder: Path, silent: Path):
    """Bounded local mix: two uses maximum per sound, gains <= .35, no normalization boost."""
    cues=[("Cinematic Impact.WAV",0,.28), ("Camera Clicks.WAV",2.5,.3),
          ("sfx_whoosh.mp3",4.9,.3), ("Echo impact.mp3",10,.3),
          ("Click - Sound Effect (HD).mp3",12,.3), ("fast-whoosh-118248.mp3",13.9,.35),
          ("Camera Clicks.WAV",16,.3), ("sfx_whoosh.mp3",17.9,.3),
          ("Click - Sound Effect (HD).mp3",21,.3), ("fast-whoosh-118248.mp3",24.9,.35),
          ("Echo impact.mp3",27,.3), ("Cinematic Impact.WAV",30,.28)]
    output=folder / "renders/showcase.mp4"
    if output.exists():
        raise ValueError("Master exists; preserve it and create a new job.")
    command=["ffmpeg","-hide_banner","-nostdin","-n","-i",str(silent)]
    filters=[]
    for i,(name,start,gain) in enumerate(cues,1):
        item=register_asset(folder, ROOT / "SOUND EFFECTS" / name, "Bundled owner-supplied SFX", "See docs/MEDIA_RIGHTS.md; supporting license documents pending", f"Sound cue at {start}s, gain {gain}")
        command += ["-i",str(folder / item["path"])]
        filters.append(f"[{i}:a]atrim=0:2.3,asetpts=PTS-STARTPTS,volume={gain},afade=t=out:st=2.1:d=0.2,adelay={round(start*1000)}:all=1[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(1,len(cues)+1))+f"amix=inputs={len(cues)}:normalize=0,apad,atrim=0:36,alimiter=limit=0.89:level=0[mix]")
    command += ["-filter_complex",";".join(filters),"-map","0:v:0","-map","[mix]","-c:v","copy","-c:a","aac","-b:a","192k","-t","36","-movflags","+faststart",str(output)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=180)
    (folder / "notes/audio-mix.log").write_text(result.stderr,encoding="utf-8")
    result.check_returncode()
    write(folder / "notes/audio-cues.json", {"cues":[{"file":n,"time":t,"gain":g} for n,t,g in cues], "listened":False})
    return probe_job(folder,"renders/showcase.mp4")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render",action="store_true")
    parser.add_argument("--job",type=Path,help="Prepare an existing blank 36-second portrait job")
    args=parser.parse_args()
    folder=args.job.resolve() if args.job else create_job("Social Motion Agent showcase", "shorts", "9:16", 36, "pl")
    prepare(folder)
    result={"job":str(folder),"reviewed":False}
    if args.render:
        from hyperframes_adapter import render
        # The intermediate composition is intentionally silent; master receives the local mix.
        render(folder,"showcase-picture","high")
        result["technical"]=mix(folder,folder / "renders/showcase-picture.mp4")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
