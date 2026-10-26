# Hypermotion: source skills and native rendering

Hypermotion is a separate desktop application, CLI and MCP server for editable `.hype` scenes. It is not HyperFrames. This repository pins [psiddharthdesign/hypermotion](https://github.com/psiddharthdesign/hypermotion) at `e510cd60c0d2632863b5a3f78dba71b905c75ff2` in `sources.lock.json`.

## 1. Prepare instructions

```bash
python -S studio.py skills plan --mode video
python -S studio.py skills setup --mode video
python -S studio.py skills check --mode video
```

Source paths exist only after preparation or in an expanded full bundle. Read:

- `tools/repos/hypermotion/skills/hypermotion-brand-profile/SKILL.md`
- `tools/repos/hypermotion/skills/hypermotion-explainer-director/SKILL.md`
- The selected skill's reference files, upstream `AGENTS.md` and `cli/README.md`.

## 2. Verify the actual runtime

Fetching sources does not install the app, build the CLI or register an MCP server. The pinned documentation is inconsistent about Windows releases: its main README describes a Windows installer while `cli/README.md` describes public desktop releases as macOS-only and Windows/Linux paths as best-effort/development. Inspect current official releases and the actual local build before promising a Windows export.

The CLI package is `@psiddharthdesign/hypermotion`; it requires Node 20+ and the desktop app. Follow the pinned installation documentation for the user's platform. Prefer a scoped installation and existing available tools; do not silently change global MCP configuration. A connected MCP server should expose `doctor` and `get_capabilities`; inspect actual returned capabilities. The CLI provides `hypermotion doctor` and help. The desktop override is `HYPERMOTION_APP_PATH`.

Validate a minimal native scene, reopen it and export a short MP4. Inspect the frames and ffprobe result. CLI discovery/help alone does not prove the desktop renderer works. If a requested native engine is unavailable, retain the brief/storyboard and report the exact blocker; ask before switching engines.

## 3. Produce a tracked native film

Create a normal film job, complete its real brief/research/storyboard and register materials. Set `brief.engine` to `hypermotion` and explain the choice. Author `source/index.hype` using the pinned schema/tools; keep scene media in the job. Use explicit scene paths rather than rendering whichever unrelated scene happens to be open.

```bash
python -S studio.py render-hype output/jobs/JOB_ID --scene source/index.hype --name draft
python -S studio.py sheet output/jobs/JOB_ID --render renders/draft.mp4
```

The local adapter invokes the installed CLI, keeps a log and records source/render provenance. It does not create a scene for you or install a runtime. Review and package the same hash following [PRODUCTION.md](PRODUCTION.md). After changes, render again; never manufacture a receipt for an old file.

`HYPERMOTION_CLI` can specify a CLI executable or its JavaScript `.mjs` entrypoint; otherwise the adapter checks PATH. The CLI still needs the desktop app. Missing prerequisites fail clearly and do not trigger an automatic fallback.

## Verification boundary

Adapter tests simulate process outcomes, timeout/partial-output handling and provenance registration. They do not establish a working installed Hypermotion desktop, MCP connection, platform build or live native render. Confirm these separately for each execution environment. HyperFrames demo success is not a Hypermotion test.
