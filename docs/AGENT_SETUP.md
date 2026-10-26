# Agent setup

The portable package is `skills/creative-director/`: `SKILL.md`, conditional references and license notices. It contains no credentials, account connections or machine-specific paths. Instructions work with agents that can read Markdown, inspect a project and run tools; the package does not supply these capabilities itself.

## In this repository

Agents using `.agents/skills/` can discover the Creative Director bridge there. `CLAUDE.md` directs Claude Code to the same workflow. For Hermes project discovery, follow its current trust mechanism; do not silently change trust settings. Every host can explicitly read `AGENTS.md`, `START_HERE.md` and `skills/creative-director/SKILL.md`.

A GitHub connector may expose only reads. It does not provide a terminal, renderer, image generator, browser or local write access. Without execution, prepare the brief/direction/storyboard and identify the missing execution environment; do not claim a rendered deliverable.

## Portable installation

```bash
python -S scripts/install_skill.py --agent codex
python -S scripts/install_skill.py --agent codex --execute

# Choose the host you use
python -S scripts/install_skill.py --agent claude --execute
python -S scripts/install_skill.py --agent hermes --execute

# Custom/project skill parent directory
python -S scripts/install_skill.py --dest .claude/skills --execute
```

| Host | Default skill parent | Profile override |
| --- | --- | --- |
| Codex | `~/.codex/skills` | `CODEX_HOME` |
| Claude Code | `~/.claude/skills` | `CLAUDE_CONFIG_DIR` |
| Hermes | `~/.hermes/skills` | `HERMES_HOME` |

`--dest` overrides the parent. Identical packages are reused; differing packages are preserved and never overwritten. Compare changes and choose a separate destination or manage the existing installation. A staged copy prevents partial references becoming visible.

Use `$creative-director` in Codex or the named skill in your host's interface. Hermes exposes it as `/creative-director`. Start a new session or use the host's supported refresh if its index is cached. An installation test verifies files, not every version of every agent product.

Official references: [Claude Code skills](https://code.claude.com/docs/en/skills), [Hermes skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills/), [Hermes project discovery](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md).

## Sources and runtimes

`studio.py skills plan --mode video|website|ui-motion` is read-only. Setup downloads selected pinned repositories. Check verifies source integrity offline. No upstream code, provider requests or account connections are started. Full bundles with a manifest are checked by their pinned source metadata and file hashes without Git; source ZIPs without a manifest can use the bootstrap.

For video, `studio.py setup` separately installs locked HyperFrames/GSAP dependencies. Hypermotion source download provides specialist instructions; `.hype` export needs verified desktop/CLI and a short export test. See [HYPERMOTION.md](HYPERMOTION.md).

For websites, preserve the framework and use available browser tools. Taste's optional scripts have their own Node/browser prerequisites. If running its direction script, set `TASTE_SKILL_HISTORY` to a project-local file. Image acquisition/generation is a separate scoped action; supplied assets take priority.

## Verification scope

Tests cover mode routing, pinned sources, installer completeness/idempotency, preservation of edits and failure cleanup. Behavioral evaluations exercise realistic briefs. These do not certify live Codex, Claude Code, Hermes, Hypermotion desktop or paid provider sessions. Report actual checks in each production.
