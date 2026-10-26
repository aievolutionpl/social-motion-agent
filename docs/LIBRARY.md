# Complete production library

This distribution includes the original sound library, backgrounds, fonts, local agent skills and the full original catalogue.

| Resource | Included |
| --- | ---: |
| Sound effects, original WAV/MP3 | 126 files |
| Backgrounds, original WebP | 9 files |
| Fonts, with OFL license texts | 3 files |
| Upstream repositories | 36 pinned Git submodules |
| Catalogue entries | 924 (916 upstream + 8 local) |

Catalogue entries include skills, recipes, templates and test fixtures. They are not 924 independently installed integrations.

## Focused preparation

Use `python -S studio.py skills plan --mode video` and `skills setup --mode video` for Hypermotion + Elaya. Mode `website` selects Elaya + Taste, and `ui-motion` selects all three. Full source download below remains optional. `skills check` verifies sources, never runtime or account readiness.

## Download everything

```bash
git clone --recurse-submodules https://github.com/aievolutionpl/social-motion-agent.git
cd social-motion-agent
npm ci
python -S scripts/bootstrap_library.py --check
```

Already cloned, or downloaded GitHub's ZIP?

```bash
python -S scripts/bootstrap_library.py
```

The bootstrap fetches the exact recorded commits from original GitHub repositories into tools/repos/. It works without a parent .git checkout. It does not run npm/pip installers, activate skills globally or connect accounts. It preserves modified checkouts and reports conflicts rather than resetting them. In a network failure, rerun it; completed sources are reused and failed staging directories remain under output/library-setup for inspection.

GitHub displays source folders as linked submodules, keeping original histories and license files. GitHub's standard ZIP does not contain submodule contents, so ZIP users must run the bootstrap. The source collection is approximately 650 MB before Git metadata/dependencies. The media files themselves are stored directly in this repository and are present in the ZIP.

Some upstreams use Git LFS. The original source collection did not include those remote payloads; bootstrap mirrors that behavior. If a particular example needs LFS media, install Git LFS and fetch it from that upstream after checking its rights and size.

## Find and use

```bash
python -S studio.py find typography --limit 8
python -S studio.py route shorts
python -S studio.py motion find reveal --limit 5
python -S studio.py sfx find whoosh --limit 5
python -S studio.py sfx check
```

Core local skills remain available before downloading the extended library. route reports optional_skills separately, including whether their files exist.
Read only the selected skill and its references. A downloaded repo is source code, not proof that its runtime, model account or external service is operational.

## Rights and scope

See MEDIA_RIGHTS.md and THIRD_PARTY_NOTICES.md. Tools retain original licenses. Audio redistribution is based on the owner's explicit confirmation; license evidence is pending and unrestricted reuse is not claimed.

Private portraits, avatars, customer campaigns, credentials, production output, dependency caches and machine-local application installations are deliberately excluded. Reproducible source code and shared production materials are included.

## Complete standalone ZIP

[Archived v1.1.1 bundle](https://github.com/aievolutionpl/social-motion-agent/releases/download/v1.1.1/social-motion-agent-v1.1.1-full.zip). It predates Creative Director and the current fixes; use the current checkout for the new workflow. All 34 pinned source trees are expanded into ordinary folders. No Git or library bootstrap is required. Run `python -S scripts/verify_bundle.py` for integrity verification; `library_check.py` checks Git checkouts and is intended for the clone workflow. Install runtime dependencies separately as described in README.
