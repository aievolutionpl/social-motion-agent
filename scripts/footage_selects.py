"""Find editable source ranges from measured local transcripts."""
import json
import math
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

import studio_core as core
from editor_workspace import probe


def media(folder, asset_id):
    item = next((a for a in core.read(folder / "assets.json")["items"] if a["id"] == asset_id), None)
    if not item or not re.fullmatch(r"[A-Za-z0-9_-]+", asset_id):
        raise ValueError("Unknown registered asset")
    path = core.local(folder, item["path"])
    if core.sha(path) != item["sha256"]:
        raise ValueError("Registered media changed. Register the new file.")
    return item, path


def phrases(data, duration):
    """Accept native Whisper segments, whisper.cpp JSON or measured words."""
    if not isinstance(data, dict):
        raise ValueError("Expected an alignment object")
    rows = data.get("segments", data.get("transcription", data.get("words")))
    if not isinstance(rows, list) or not rows:
        raise ValueError("Expected measured segments or words")
    previous = 0.0
    result = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid transcript row")
        if "offsets" in row:
            start = float(row["offsets"]["from"]) / 1000
            end = float(row["offsets"]["to"]) / 1000
        else:
            start, end = float(row["start"]), float(row["end"])
        words = row.get("text", row.get("word"))
        if not isinstance(words, str) or not words.strip():
            raise ValueError("Empty transcript phrase")
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < min(end, duration)
                and start >= previous - .03 and end <= duration + .1):
            raise ValueError("Transcript times outside source or out of order")
        previous = end
        result.append({"in_sec": start, "out_sec": min(end, duration), "quote": words.strip()})
    if "words" in data and "segments" not in data and "transcription" not in data:
        grouped = []
        for word in result:
            if (grouped and word["in_sec"] - grouped[-1]["out_sec"] < .65
                    and word["out_sec"] - grouped[-1]["in_sec"] < 10
                    and not grouped[-1]["quote"].endswith((".", "?", "!"))):
                grouped[-1]["quote"] += " " + word["quote"]
                grouped[-1]["out_sec"] = word["out_sec"]
            else:
                grouped.append(dict(word))
        return grouped
    return result


def index(folder, asset_id, *, transcript=None, model=None, executable="whisper-cli"):
    if bool(transcript) == bool(model):
        raise ValueError("Choose a measured transcript or a local whisper.cpp model")
    item, path = media(folder, asset_id)
    info = probe(path)
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        raise ValueError("Source has no audio to transcribe")
    duration = float(info["format"]["duration"])
    if transcript:
        data = core.read(core.local(folder, transcript))
        origin = "imported"
    else:
        binary = shutil.which(executable)
        if not binary or not Path(model).is_file():
            raise ValueError("Install whisper-cli and supply a local model, or import a measured transcript")
        with tempfile.TemporaryDirectory() as temp:
            wav = Path(temp) / "speech.wav"
            prefix = Path(temp) / "speech"
            subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vn", "-ar", "16000",
                            "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True, timeout=1800)
            language = core.read(folder / "job.json")["language"]
            subprocess.run([binary, "-m", str(Path(model).resolve()), "-f", str(wav), "-l", language,
                            "-oj", "-of", str(prefix)], check=True, timeout=3600, stdout=subprocess.DEVNULL)
            data = json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8-sig"))
        origin = "whisper.cpp"
    ranges = phrases(data, duration)
    core.write(core.local(folder, f"notes/transcripts/{asset_id}.json", exists=False),
               {"asset_id": asset_id, "sha256": item["sha256"], "source": origin, "ranges": ranges})
    return len(ranges)


def tokens(text):
    text = unicodedata.normalize("NFKD", text.casefold().replace("ł", "l"))
    return set(re.findall(r"[a-z0-9]{3,}", "".join(c for c in text if not unicodedata.combining(c))))


def shortlist(folder, query="", asset_id=None):
    wanted = tokens(query) - {"jak", "jest", "mnie", "sie", "the", "and", "for", "dla"}
    ranked = []
    missing = []
    for asset in core.read(folder / "assets.json")["items"]:
        if asset_id and asset["id"] != asset_id:
            continue
        path = core.local(folder, f"notes/transcripts/{asset['id']}.json", exists=False)
        if not path.is_file():
            missing.append(asset["id"])
            continue
        record = core.read(path)
        if record["sha256"] != asset["sha256"] or core.sha(core.local(folder, asset["path"])) != record["sha256"]:
            raise ValueError("Stale transcript for " + asset["id"])
        for row in record["ranges"]:
            quote = row["quote"]
            content = tokens(quote)
            matches = sorted(term for term in wanted if any(w == term or
                             (len(term) >= 4 and w.startswith(term[:4])) for w in content))
            question = quote.endswith("?")
            concrete = bool(re.search(r"\d", quote))
            score = 4 * len(matches) + 2 * question + concrete
            reasons = []
            if matches:
                reasons.append("zgodność z tematem: " + ", ".join(matches))
            if question:
                reasons.append("pytanie na otwarcie")
            if concrete:
                reasons.append("konkretna liczba")
            entry = {**row, "asset_id": asset["id"], "reason": ", ".join(reasons) or "wypowiedź z nagrania",
                     "clip": {"asset_id": asset["id"], "in_sec": row["in_sec"],
                              "duration_sec": round(row["out_sec"] - row["in_sec"], 6),
                              "fit": "cover", "keep_audio": True}}
            ranked.append((score, entry))
    ranked.sort(key=lambda it: -it[0])
    choices = []
    seen = set()
    for _, entry in ranked:
        key = " ".join(entry["quote"].casefold().split())
        if key not in seen:
            choices.append(entry)
            seen.add(key)
        if len(choices) == 3:
            break
    return {"candidates": choices, "without_transcript": missing}
