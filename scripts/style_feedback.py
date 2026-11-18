"""User-supplied style judgments, shared by the local HTML and chat interfaces."""
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

import studio_core as core

STYLES = {"editorial": "Reportaż", "kinetic": "Kinetyczny", "studio": "Studio"}
# Only apply unambiguous, entire requests automatically. Every other note is
# returned verbatim to the editing agent together with the current brief.
TREATMENT_REQUESTS = {
    "mniej zbliżeń": ("kinetic", "gentle"), "less zoom": ("kinetic", "gentle"),
    "więcej zbliżeń": ("kinetic", "energetic"), "more zoom": ("kinetic", "energetic"),
    "większy kadr": ("studio", "large"), "larger frame": ("studio", "large"),
    "mniejszy kadr": ("studio", "small"), "smaller frame": ("studio", "small"),
}


def profile_name(name):
    if not isinstance(name, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name):
        raise ValueError("Use a profile name of 1–64 letters, digits, hyphens or underscores")
    return name


def database(jobs_dir):
    return jobs_dir / ".style-feedback.sqlite3"


def connect(jobs_dir):
    db = sqlite3.connect(database(jobs_dir), timeout=20)
    db.execute("""CREATE TABLE IF NOT EXISTS ratings (
        profile TEXT, job TEXT, gallery TEXT, style TEXT, sha TEXT, stars INTEGER,
        note TEXT, channel TEXT, updated TEXT,
        PRIMARY KEY(profile,job,gallery,style))""")
    return db


def collection(folder, key):
    if not isinstance(key, str) or not re.fullmatch(r"(?:films|openings)-[a-f0-9]{20}", key):
        raise ValueError("Invalid gallery ID")
    path = core.local(folder, "previews/" + key + "/manifest.json")
    directory = path.parent
    data = core.read(path)
    if data["id"] != key or data["job_id"] != core.read(folder / "job.json")["id"]:
        raise ValueError("Feedback belongs to a different film")
    return directory, data


def save(folder, key, entries, source, *, general_note=None):
    directory, manifest = collection(folder, key)
    if not isinstance(entries, list) or len(entries) > len(STYLES) or (not entries and general_note is None):
        raise ValueError("Provide a rating or a comment about the whole film")
    if general_note is not None and (not isinstance(general_note, str) or len(general_note) > 2000):
        raise ValueError("General comment must be at most 2000 characters")
    variants = {item["style"]: item for item in manifest["variants"]}
    checked = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid rating")
        style = entry.get("style")
        variant = variants.get(style)
        if not variant or style in [item[0] for item in checked]:
            raise ValueError("Unknown or duplicate style")
        if entry.get("sha256") != variant["sha256"] or core.sha(core.local(directory, variant["file"])) != variant["sha256"]:
            raise ValueError("Film version does not match feedback")
        stars, note = entry.get("stars"), entry.get("note")
        if stars is not None and (type(stars) is not int or not 1 <= stars <= 5):
            raise ValueError("Stars must be an integer from 1 to 5")
        if note is not None and (not isinstance(note, str) or len(note) > 2000):
            raise ValueError("Comment must be at most 2000 characters")
        if stars is None and not (note and note.strip()):
            raise ValueError("Rate the film or add a comment")
        checked.append((style, variant["sha256"], stars, note.strip() if note is not None else None))
    if general_note is not None:
        checked.append(("all", key, None, general_note.strip()))
    profile = profile_name(manifest["profile"])
    with closing(connect(folder.parent)) as db, db:
        for style, sha, stars, note in checked:
            db.execute("""INSERT INTO ratings VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(profile,job,gallery,style) DO UPDATE SET
                stars=COALESCE(excluded.stars,ratings.stars), note=COALESCE(excluded.note,ratings.note),
                channel=excluded.channel, updated=excluded.updated""",
                       (profile, manifest["job_id"], key, style, sha, stars, note, source,
                        datetime.now(timezone.utc).isoformat(timespec="microseconds")))
    return {"saved": len(checked), "profile": profile}


def summary(jobs_dir, profile, *, exclude_job=None):
    profile_name(profile)
    ranked = dict.fromkeys(STYLES, 3.0)
    notes = []
    if database(jobs_dir).is_file():
        with closing(connect(jobs_dir)) as db:
            params = (profile, exclude_job or "")
            for style, total, count in db.execute(
                    "SELECT style,SUM(stars),COUNT(stars) FROM ratings WHERE profile=? AND job<>? AND stars IS NOT NULL GROUP BY style", params):
                if style in ranked:
                    ranked[style] = (total + 6) / (count + 2)
            notes = [{"style": row[0], "note": row[1]} for row in db.execute(
                "SELECT style,note FROM ratings WHERE profile=? AND job<>? AND LENGTH(note)>0 ORDER BY updated DESC LIMIT 12", params)]
    treatments = {}
    for entry in notes:
        phrase = entry["note"].strip().casefold().rstrip(".!?").strip()
        request = TREATMENT_REQUESTS.get(phrase)
        if request and entry["style"] in ("all", request[0]):
            treatments.setdefault(*request)
    return {"profile": profile, "style_order": sorted(STYLES, key=lambda k: -ranked[k]),
            "comments": notes, "treatments": treatments}


def current(folder, manifest):
    feedback = {"gallery": manifest["id"], "ratings": [], "general_note": ""}
    if database(folder.parent).is_file():
        with closing(connect(folder.parent)) as db:
            for style, sha, stars, note in db.execute(
                    "SELECT style,sha,stars,note FROM ratings WHERE profile=? AND job=? AND gallery=?",
                    (manifest["profile"], manifest["job_id"], manifest["id"])):
                if style == "all":
                    feedback["general_note"] = note
                else:
                    feedback["ratings"].append({"style": style, "sha256": sha, "stars": stars, "note": note})
    return feedback


def import_file(folder, key, path):
    data = core.read(core.local(folder, path))
    if data.get("gallery") != key or data.get("job_id") != core.read(folder / "job.json")["id"]:
        raise ValueError("Rating export belongs to another gallery")
    return save(folder, key, data["ratings"], "html", general_note=data.get("general_note"))
