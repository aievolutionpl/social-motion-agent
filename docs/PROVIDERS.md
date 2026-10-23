# Optional providers and costs

The core orchestrates local files and renderers. Your coding agent supplies reasoning; this repository does not embed an LLM account or require a specific model.

| Capability | Integration | Default |
| --- | --- | --- |
| Motion rendering | Local pinned HyperFrames + GSAP | Ready after npm ci and required system tools |
| Footage assembly/effects | System FFmpeg | Local |
| Narration | scripts/voiceover.py, ElevenLabs REST API | Dry-run |
| Images | Generate in your agent's image tool, then asset-add | External/manual |
| AI video clips | Generate with your chosen provider, then asset-add | External/manual |
| Screen recording | Optional OpenScreen adapter | Uninstalled until configured |

## ElevenLabs

Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in your process environment. No secrets are read from a parent workspace; .env.example only documents variable names.

```bash
python -S scripts/voiceover.py --text-file narration.txt --output output/narration.mp3
# Only after reviewing the plan and approving the paid request:
python -S scripts/voiceover.py --text-file narration.txt --output output/narration.mp3 --execute
```

Default model: eleven_multilingual_v2. Your chosen voice ID is required. No private voice is bundled.
The adapter bounds text/response sizes, rejects existing outputs, uses a request timeout and reports sanitized errors. It intentionally does not retry paid calls automatically.
The adapter does not quote pricing; verify current provider pricing and get authorization before execution.

Protocol source: [ElevenLabs create speech](https://elevenlabs.io/docs/api-reference/text-to-speech/convert). Offline adapter tests cover dry-run and failure behavior. Live paid generation is not part of repository verification.

## Provider choice

Do not silently substitute a different provider or model. Record the choice and cost authorization in the job brief. Register outputs with source, rights, purpose and generation metadata. Never store credentials in job JSON, prompts, logs or Git.
