# Engines and setup

## Find the tools without assuming an installation path

The skill folder may live inside Social Motion Agent, in a host's skill directory, or in another project. Inspect the current task's directory and its explicit project context. A valid Social Motion Agent root contains `studio.py`, `config/routes.json`, `sources.lock.json` and the documented `scripts/` adapters. Do not search unrelated workspaces for credentials or customer assets.

If the task is a website, work in that website's repository; the creative modules do not require a video runtime. If video production needs the toolkit and no checkout is available, obtain the public repository in a task-local writable work directory, following the environment's normal network permissions:

```bash
git clone https://github.com/aievolutionpl/social-motion-agent.git work/social-motion-agent
```

Use a different unused destination when that path already exists. Inspect existing contents before reusing them. Read its `AGENTS.md` and `START_HERE.md`, and execute commands from that checkout. Do not overwrite an existing project or install tools into the skill package itself.

## Plan, fetch, inspect

```bash
python -S studio.py skills plan --mode video
python -S studio.py skills setup --mode video
```

Use `website` or `ui-motion` for those modes. The plan identifies selected upstream skills and missing sources. Run setup only for missing sources; if files exist, `skills check --mode MODE` verifies their revision/integrity. A modified checkout should be reported and preserved. Read selected skills only when relevant; inspect commands before execution and keep the user's request and project conventions authoritative.

For a focused Hypermotion source fetch, the existing bootstrap also supports:

```bash
python -S scripts/bootstrap_library.py --only hypermotion
```

This downloads sources and skills, not a working desktop application. Do not equate catalogue entries with active integrations.

## Choose the engine by the deliverable

| Engine or capability | Use | Readiness evidence |
| --- | --- | --- |
| HyperFrames + GSAP | Authored HTML motion and deterministic local film output | `studio.py doctor`, successful bundled demo render, inspected frames |
| Kinetic Film | Explicit typography-led teaser or launch on a musical beat grid | `studio.py kinetic setup --source PATH`, optional NumPy/OpenCV, `kinetic doctor`, actual `kinetic demo --render` and review; see `docs/KINETIC_FILM.md` |
| FFmpeg | Existing footage, trims, crop, concatenation, audio and effects | Local `ffmpeg`/`ffprobe`, a small representative assembly and probe |
| Hypermotion | Explicit native `.hype` scene/editor work | Pinned skills plus verified desktop/CLI, reopened scene and short inspected export |
| Browser app stack | Responsive sites and live UI motion | Existing project build/tests and actual browser interaction/screenshots |
| OpenScreen | Real window recording and tutorials | Installed runtime, chosen window, short actual capture and replay |
| Image, speech or video provider | New external media needed by the brief | Actual available tool/account, current parameters and required cost authorization |

For the default video runtime, `python -S studio.py setup` installs locked project dependencies after checking system tools. `python -S studio.py demo --render` is a local synthetic smoke test; initial browser downloads may require network access. It does not prove that Hypermotion, OpenScreen or paid providers work.

## Hypermotion preparation

After fetching, read `tools/repos/hypermotion/skills/hypermotion-brand-profile/SKILL.md` and `tools/repos/hypermotion/skills/hypermotion-explainer-director/SKILL.md`, then the pinned upstream setup and CLI documentation. Check `docs/HYPERMOTION.md` for known integration limits. Inspect the current supported platform/build and local executable before selecting commands; do not invent flags, endpoints or file formats.

The desktop app, CLI and MCP can have different versions and responsibilities. Source presence does not establish an executable renderer. Validate one minimal scene through create/open/export and inspect the resulting MP4 before extending the production. If a requested Hypermotion runtime cannot run, explain the exact blocker and the available alternative; obtain the user's direction before changing the named engine.

In the current toolkit, native jobs use `brief.engine = "hypermotion"` and a scene under `source/`. After the real brief, storyboard and asset checks, `python -S studio.py render-hype JOB --scene source/index.hype --name draft` validates the explicit scene and invokes the installed CLI. The adapter records source/render provenance and probes the MP4; review and package the same hash. It does not author a scene automatically. If using an older toolkit without this command, update deliberately or report the missing adapter rather than inventing a receipt.

## Cross-agent operation

The Markdown workflow and references are host-neutral. Use the host's actual tools for files, shell, browser, images and user questions. A read-only GitHub connector can inspect and plan; it cannot by itself install dependencies or create local media. Do not claim parity across hosts until the actual capability has been exercised. Avoid writing global configuration or requesting new credentials when a working authorized connection already exists.
