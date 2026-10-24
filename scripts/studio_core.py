"""Local production records, routing and evidence gates. No network calls."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT  # Standalone distribution; never search parent workspaces.
STAGES = ("brief", "research", "storyboard", "assets", "preview", "final")
FORMATS = {"16:9": (1920, 1080), "9:16": (1080, 1920),
           "4:5": (1080, 1350), "1:1": (1080, 1080)}
REVIEW_AREAS = ("visual", "audio", "captions", "facts", "rights", "platform")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def local(base: Path, value: str, *, exists: bool = True) -> Path:
    if not value or not isinstance(value, str):
        raise ValueError("Wymagana lokalna ścieżka")
    path = (base / value).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Ścieżka wychodzi poza katalog produkcji: {value}")
    if exists and not path.is_file():
        raise ValueError(f"Brak pliku: {value}")
    return path


def resolve_ref(value: str) -> Path:
    return local(ROOT, value, exists=False)


def routes() -> dict:
    return read(ROOT / "config/routes.json")["routes"]


def create_job(title: str, kind: str, aspect: str, duration: float, language: str,
               base: Path | None = None) -> Path:
    if kind not in routes() or aspect not in FORMATS:
        raise ValueError("Nieznana ścieżka produkcji lub proporcje")
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Czas filmu musi być dodatnią, skończoną liczbą")
    slug = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")[:55] or "video"
    identifier = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + slug + "-" + uuid.uuid4().hex[:6]
    folder = (base or ROOT / "output/jobs") / identifier
    folder.mkdir(parents=True, exist_ok=False)
    for name in ("assets", "source", "previews", "renders", "final", "notes"):
        (folder / name).mkdir()
    width, height = FORMATS[aspect]
    write(folder / "job.json", {"schema_version": 1, "id": identifier, "title": title,
          "kind": kind, "format": aspect, "width": width, "height": height,
          "fps": 30, "duration_sec": duration, "language": language,
          "state": "intake", "created_at": now(), "history": [], "render": None})
    questions = [
        ("Jaki jeden efekt ma wywołać film?", ["Wyjaśnić temat", "Zainteresować ofertą", "Pokazać rezultat", "Opowiedzieć historię"]),
        ("Do kogo konkretnie mówimy?", ["Nowi odbiorcy bez wiedzy", "Obecni klienci lub widzowie", "Specjaliści", "Osoby gotowe do zakupu"]),
        ("Jaki kierunek wizualny wybieramy?", ["Filmowy i oparty na obrazie", "Czytelny explainer motion", "Dynamiczny montaż nagrań", "Konkretny styl z referencji"]),
        ("Jak prowadzimy dźwięk?", ["Lektor i subtelna muzyka", "Głos z nagrania", "Muzyka i tekst na ekranie", "Bez dźwięku"]),
        ("Jaki jest najważniejszy priorytet produkcji?", ["Jakość i dopracowanie", "Tempo realizacji", "Mały koszt generacji", "Kilka wersji do porównania"]),
    ]
    write(folder / "intake.json", {"skill": "5-pytan", "instruction":
          "Dostosuj dokładnie 5 pytań do briefu. Nie pytaj ponownie o znane decyzje. Każde ma 3–5 opcji i odpowiedź własną. Zapisz rzeczywiste odpowiedzi użytkownika.",
          "questions": [{"id": i + 1, "question": q, "options": options,
                         "allow_free_text": True, "answer": None} for i, (q, options) in enumerate(questions)],
          "user_waiver": None})
    write(folder / "brief.json", {"goal": "", "audience": "", "direction": "", "cta": "",
          "brand_config": "", "audio_required": True, "captions_required": False,
          "budget": {"currency": "USD", "limit": None, "authorization_evidence": ""},
          "engine": "", "engine_reason": "", "language": language})
    write(folder / "research.json", {"sources": [], "claims": [], "conclusions": ""})
    write(folder / "storyboard.json", {"scenes": []})
    write(folder / "assets.json", {"items": []})
    write(folder / "timeline.json", {"clips": [], "audio": {"voice": None, "music": None, "music_gain": 0.12}})
    write(folder / "preview.json", {"path": "", "sha256": "", "reviewed": False, "reviewer": "", "notes": ""})
    write(folder / "review.json", {"render_sha256": "", "reviewer": "", "evidence": [],
          "checks": {area: {"status": "pending", "notes": ""} for area in REVIEW_AREAS}})
    (folder / "source/script.md").write_text("# Scenariusz\n\n", encoding="utf-8")
    (folder / "HANDOFF.md").write_text("# Stan produkcji\n\nIntake: oczekuje na 5 pytań i odpowiedzi.\n", encoding="utf-8")
    return folder


def fingerprint(folder: Path) -> str:
    job = read(folder / "job.json")
    spec = {key: job[key] for key in ("kind", "format", "width", "height", "fps", "duration_sec", "language")}
    parts = [json.dumps(spec, sort_keys=True).encode("utf-8")]
    parts += [(folder / name).read_bytes() for name in
              ("intake.json", "brief.json", "research.json", "storyboard.json", "assets.json", "timeline.json", "source/script.md")]
    # Composition changes must invalidate earlier technical evidence.
    for path in sorted((folder / "source").rglob("*")):
        if path.is_file() and not any(p in {"node_modules", ".git", ".hyperframes", "__pycache__"} for p in path.parts):
            local(folder, path.relative_to(folder).as_posix())
            parts.append(path.relative_to(folder).as_posix().encode("utf-8"))
            parts.append(sha(path).encode("ascii"))
    return hashlib.sha256(b"".join(parts)).hexdigest()


def check_job(folder: Path, stage: str) -> list[str]:
    """Validate recorded evidence; this does not certify the truth of human review."""
    errors = []
    if stage not in STAGES:
        return ["Nieznany etap"]
    level = STAGES.index(stage)
    try:
        job, intake, brief = (read(folder / name) for name in ("job.json", "intake.json", "brief.json"))
        questions = intake.get("questions", [])
        waiver = str(intake.get("user_waiver") or "").casefold()
        waived = any(phrase in waiver for phrase in ("pomiń pytania", "bez pytań", "start od razu"))
        if not waived and (len(questions) != 5 or any(not str(q.get("answer") or "").strip() for q in questions)):
            errors.append("Najpierw dokładnie 5 pytań i rzeczywiste odpowiedzi użytkownika (intake.json)")
        for key in ("goal", "audience", "direction"):
            if not str(brief.get(key, "")).strip():
                errors.append("Uzupełnij brief." + key)
        if level >= 1:
            research = read(folder / "research.json")
            sources = research.get("sources", [])
            if not sources or not research.get("conclusions", "").strip():
                errors.append("Research wymaga źródeł i wniosków przed produkcją")
            ids = set()
            for source in sources:
                if not all(source.get(key) for key in ("id", "title", "url", "accessed_at", "used_for")):
                    errors.append("Źródło researchu wymaga id, title, url, accessed_at, used_for")
                if source.get("id") in ids:
                    errors.append("Powtórzone ID źródła researchu")
                ids.add(source.get("id"))
            for claim in research.get("claims", []):
                if claim.get("status") != "confirmed" or not claim.get("text") or not claim.get("source_ids") or not set(claim["source_ids"]).issubset(ids):
                    errors.append("Fakty na ekranie wymagają confirmed i istniejących source_ids; usuń lub oznacz niepotwierdzony claim poza listą faktów")
        if level >= 2:
            scenes = read(folder / "storyboard.json").get("scenes", [])
            duration = sum(float(scene.get("duration_sec", 0)) for scene in scenes)
            if not scenes or any(not scene.get("id") or not scene.get("visual") or not math.isfinite(float(scene.get("duration_sec", 0))) or float(scene.get("duration_sec", 0)) <= 0 for scene in scenes):
                errors.append("Storyboard wymaga scen z id, visual i dodatnim duration_sec")
            if not math.isfinite(duration) or abs(duration - job["duration_sec"]) > 1 / job["fps"]:
                errors.append("Czas storyboardu nie odpowiada docelowemu czasowi filmu")
            if len({s.get("id") for s in scenes}) != len(scenes):
                errors.append("Powtórzone ID sceny")
            if not brief.get("engine") or not brief.get("engine_reason"):
                errors.append("Wybierz engine i zapisz engine_reason")
            if not (folder / "source/script.md").read_text(encoding="utf-8").replace("# Scenariusz", "").strip():
                errors.append("Uzupełnij scenariusz w source/script.md")
        if level >= 3:
            assets = read(folder / "assets.json").get("items", [])
            asset_ids = set()
            for asset in assets:
                if not all(asset.get(key) for key in ("id", "path", "sha256", "source", "rights", "purpose")):
                    errors.append("Asset wymaga id, path, sha256, source, rights, purpose")
                    continue
                if asset["id"] in asset_ids:
                    errors.append("Powtórzone ID assetu")
                asset_ids.add(asset["id"])
                if sha(local(folder, asset["path"])) != asset["sha256"]:
                    errors.append("Asset zmienił się po zarejestrowaniu: " + asset["id"])
                if asset.get("provider") == "fal" and not all(asset.get(k) for k in ("endpoint", "request_id", "prompt")):
                    errors.append("Asset fal wymaga endpoint, request_id i prompt")
                if asset.get("provider") == "imagegen" and not asset.get("prompt"):
                    errors.append("Asset imagegen wymaga promptu")
            for scene in read(folder / "storyboard.json").get("scenes", []):
                if not set(scene.get("asset_ids", [])).issubset(asset_ids):
                    errors.append("Scena odwołuje się do nieznanego assetu: " + scene["id"])
        if level >= 4:
            preview = read(folder / "preview.json")
            if not preview.get("reviewed") or not preview.get("reviewer") or not preview.get("notes"):
                errors.append("Preview wymaga oględzin, reviewer i notes")
            if sha(local(folder, preview.get("path", ""))) != preview.get("sha256"):
                errors.append("Preview jest inny niż obejrzany plik")
        if level >= 5:
            render = local(folder, job.get("render", ""))
            technical, review = read(folder / "technical.json"), read(folder / "review.json")
            checksum = sha(render)
            if not technical.get("passed") or technical.get("render_sha256") != checksum or technical.get("fingerprint") != fingerprint(folder):
                errors.append("Brak aktualnej pozytywnej kontroli technicznej tego renderu i dokumentów")
            if review.get("render_sha256") != checksum or not review.get("reviewer") or not review.get("evidence"):
                errors.append("Review wymaga SHA renderu, recenzenta oraz lokalnych dowodów oględzin")
            for value in review.get("evidence", []):
                local(folder, value)
            for area in REVIEW_AREAS:
                item = review.get("checks", {}).get(area, {})
                if item.get("status") not in ("pass", "na") or not item.get("notes"):
                    errors.append("Review niekompletny: " + area)
                if area == "audio" and brief.get("audio_required") and item.get("status") == "na":
                    errors.append("Audio jest wymagane w briefie")
                if area == "captions" and brief.get("captions_required") and item.get("status") == "na":
                    errors.append("Napisy są wymagane w briefie")
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        errors.append(str(exc))
    return errors


def register_asset(folder: Path, source_file: Path, source: str, rights: str, purpose: str, **metadata) -> dict:
    if not source_file.is_file() or not all(x.strip() for x in (source, rights, purpose)):
        raise ValueError("Potrzebny plik, źródło, warunki użycia i cel assetu")
    if metadata.get("provider") == "fal" and not all(metadata.get(k) for k in ("endpoint", "request_id", "prompt")):
        raise ValueError("Asset fal wymaga endpoint, request_id i prompt")
    if metadata.get("provider") == "imagegen" and not metadata.get("prompt"):
        raise ValueError("Asset imagegen wymaga promptu")
    identifier = "a-" + uuid.uuid4().hex[:10]
    target = folder / "assets" / (identifier + source_file.suffix.lower())
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(source_file, target)
    item = {"id": identifier, "path": target.relative_to(folder).as_posix(), "sha256": sha(target),
            "source": source, "rights": rights, "purpose": purpose, "added_at": now(), **metadata}
    manifest = read(folder / "assets.json")
    manifest["items"].append(item)
    write(folder / "assets.json", manifest)
    return item


def probe_job(folder: Path, render_path: str) -> dict:
    render = local(folder, render_path)
    job, brief = read(folder / "job.json"), read(folder / "brief.json")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(render)],
                            capture_output=True, text=True, check=True, timeout=60)
    info = json.loads(result.stdout)
    video = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    audio = [s for s in info["streams"] if s.get("codec_type") == "audio"]
    duration = float(info.get("format", {}).get("duration", 0))
    num, den = video.get("avg_frame_rate", "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0
    failures = []
    if video.get("width") != job["width"] or video.get("height") != job["height"]:
        failures.append("Nieprawidłowe wymiary")
    if abs(duration - job["duration_sec"]) > max(0.15, 2 / job["fps"]):
        failures.append("Nieprawidłowy czas filmu")
    if abs(fps - job["fps"]) > 0.1:
        failures.append("Nieprawidłowy FPS")
    if brief.get("audio_required") and not audio:
        failures.append("Brak wymaganej ścieżki audio")
    payload = {"checked_at": now(), "render": render_path, "render_sha256": sha(render),
               "fingerprint": fingerprint(folder), "passed": not failures, "failures": failures,
               "width": video.get("width"), "height": video.get("height"), "fps": fps,
               "duration_sec": duration, "audio_streams": len(audio), "ffprobe": info}
    write(folder / "technical.json", payload)
    job["render"] = render_path
    write(folder / "job.json", job)
    return payload


def contact_sheet(folder: Path, render_path: str) -> Path:
    job = read(folder / "job.json")
    target = folder / "previews" / ("sheet-" + uuid.uuid4().hex[:8] + ".jpg")
    source = local(folder, render_path)
    vf = f"fps=6/{job['duration_sec']},scale=360:-2,tile=3x2:padding=8:margin=8"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(source),
                    "-vf", vf, "-frames:v", "1", str(target)], check=True, timeout=120)
    if not target.is_file():
        raise ValueError("Nie powstał contact sheet")
    return target


def package_job(folder: Path) -> Path:
    errors = check_job(folder, "final")
    if errors:
        raise ValueError("\n".join(errors))
    job = read(folder / "job.json")
    package = folder / "final" / ("delivery-" + uuid.uuid4().hex[:8])
    package.mkdir(exist_ok=False)
    render = local(folder, job["render"])
    master = "master" + render.suffix
    excluded = {"node_modules", ".git", ".venv", ".hyperframes", "__pycache__"}
    rewritten = {"job.json", "technical.json", "preview.json", "review.json", "README.md"}

    def omitted(path: Path) -> bool:
        return any(part in excluded or part == ".env" or part.startswith(".env.") for part in path.parts)

    def checked_reference(value: str) -> tuple[Path, Path]:
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            raise ValueError("Pakiet wymaga ścieżek względnych: " + str(value))
        relative = Path(os.path.normpath(value))
        source = local(folder, relative.as_posix())
        if omitted(relative) or omitted(source.relative_to(folder.resolve())):
            raise ValueError("Pakiet nie zawiera sekretów ani cache: " + value)
        return relative, source

    def copy_file(value: str, destination: str | None = None) -> str:
        relative, source = checked_reference(value)
        name = destination or relative.as_posix()
        target = local(package, name, exists=False)
        if target.exists():
            if not target.is_file() or sha(target) != sha(source):
                raise ValueError("Kolizja plików w pakiecie: " + name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return name

    def copy_evidence(value: str) -> str:
        relative, source = checked_reference(value)
        if source == render:
            return master
        if relative.as_posix() in rewritten:
            raise ValueError("Dowód wskazuje metadane zmieniane przy eksporcie: " + value)
        return copy_file(value)

    event = {"at": now(), "event": "packaged", "path": package.relative_to(folder).as_posix()}
    try:
        copy_file(job["render"], master)
        for name in ("brief.json", "intake.json", "research.json", "storyboard.json", "timeline.json", "assets.json", "HANDOFF.md"):
            copy_file(name)
        # Copy only inspected source files; never follow directory symlinks.
        for source in sorted((folder / "source").rglob("*")):
            relative = source.relative_to(folder)
            if omitted(relative):
                continue
            if source.is_symlink() and source.is_dir():
                raise ValueError("Katalog źródeł zawiera dowiązanie katalogu: " + relative.as_posix())
            if source.is_file():
                copy_file(relative.as_posix())
        # Retain asset paths used by the timeline and local composition.
        for asset in read(folder / "assets.json")["items"]:
            copy_file(asset["path"])
        preview, review = read(folder / "preview.json"), read(folder / "review.json")
        preview["path"] = copy_evidence(preview["path"])
        review["evidence"] = [copy_evidence(value) for value in review["evidence"]]
        write(package / "preview.json", preview)
        write(package / "review.json", review)
        write(package / "job.json", {**job, "render": master, "state": "packaged", "history": [*job["history"], event]})
        technical = read(folder / "technical.json")
        technical["render"] = master
        delivery_fingerprint = fingerprint(package)
        if delivery_fingerprint != technical["fingerprint"]:
            technical.setdefault("source_fingerprint", technical["fingerprint"])
            technical["fingerprint"] = delivery_fingerprint
        write(package / "technical.json", technical)
        (package / "README.md").write_text("# Pakiet filmu\n\nMaster jest powiązany z technical.json i review.json. Podgląd, dowody recenzji, źródła oraz assety mają lokalne ścieżki w pakiecie. Sekrety i cache są pominięte; source_fingerprint, jeśli obecny, zachowuje fingerprint oryginalnej produkcji. Wymagania wybranego silnika sprawdź w brief.engine i HANDOFF.md. Publikacja wymaga osobnej zgody.\n", encoding="utf-8")
        errors = check_job(package, "final")
        if errors:
            raise ValueError("Niekompletny pakiet: " + "\n".join(errors))
    except Exception:
        shutil.rmtree(package, ignore_errors=True)
        raise
    job["state"] = "packaged"
    job["history"].append(event)
    write(folder / "job.json", job)
    return package
