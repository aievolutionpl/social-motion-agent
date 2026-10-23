"""Optional ElevenLabs adapter. Dry-run by default; credentials only from environment."""
import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

def synthesize(text, voice, output, model="eleven_multilingual_v2", execute=False):
    if not text.strip() or len(text) > 10000:
        raise ValueError("Narration must contain 1-10000 characters; split long scripts into scenes.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", voice or ""):
        raise ValueError("Provide a valid voice ID via --voice or ELEVENLABS_VOICE_ID.")
    output = Path(output)
    if output.exists():
        raise ValueError("Output exists. Choose a new filename.")
    plan = {"provider": "elevenlabs", "model": model, "characters": len(text),
            "output": str(output), "executed": False}
    if not execute:
        return plan
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError("Set ELEVENLABS_API_KEY in your environment. Never paste it into chat.")
    request = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": model}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST")
    # No automatic retries: an ambiguous paid request must not be silently repeated.
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            if not response.headers.get("Content-Type", "").startswith("audio/"):
                raise ValueError("Provider returned a non-audio response.")
            audio = response.read(32 * 1024 * 1024 + 1)
            if not audio or len(audio) > 32 * 1024 * 1024:
                raise ValueError("Provider response is empty or exceeds the 32 MB limit.")
    except urllib.error.HTTPError as exc:
        raise ValueError(f"ElevenLabs returned HTTP {exc.code}; inspect account permissions or quota. No retry made.") from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError("ElevenLabs connection failed. Check account history before retrying a paid request.") from None
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(audio)
    return {**plan, "executed": True, "bytes": len(audio)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--voice", default=os.environ.get("ELEVENLABS_VOICE_ID"))
    parser.add_argument("--model", default="eleven_multilingual_v2")
    parser.add_argument("--execute", action="store_true", help="Explicitly make a paid API request.")
    args = parser.parse_args()
    try:
        print(json.dumps(synthesize(args.text_file.read_text(encoding="utf-8-sig"), args.voice,
                                    args.output, args.model, args.execute), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    raise SystemExit(main())
