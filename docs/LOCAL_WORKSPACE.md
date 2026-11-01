# One local production workspace

Keep one active checkout for production. Its current `START_HERE.md`, `studio.py` and
Creative Director instructions define the workflow. Earlier source snapshots are historical
references, not alternate instructions to run automatically.

Keep films in `output/jobs/<id>/`. Start a continuation by reading that production's
`job.json` and `HANDOFF.md`, then use `studio.py resume`. A `FINAL` filename is not
evidence of review or publication approval.

## Preserve before consolidating

Before retiring another checkout, compare its production IDs, source changes, media,
runtime requirements and local settings. Preserve collisions under distinct names. Verify
the preserved bytes with SHA-256; retain a recovery checkpoint until it is no longer needed.
Do not replace a newer source tree with an older one merely because the older copy has more files.

Private portraits, client footage, production history, credentials and runtime caches stay
local. They are not part of a source-code synchronization. The repository's existing ignore
rules exclude `output/` and runtime folders; separately ignore any additional private paths.

## Optional preservation ledger

`scripts/check_local_workspace.py` checks a local ledger at
`output/workspace-state/local-workspace.json`. It reads files without modifying them or
contacting providers. It verifies recorded SHA-256 values, required production identities
and the existence of renders referenced by those cards. It permits new production folders.

The ledger is private and is not shipped with this repository. A fresh clone reports that
no local ledger exists; this does not mean its public source installation is incomplete.
Use `studio.py doctor` and the project tests for installation checks.

Create a ledger only after verifying your consolidation. For example, run a local Python
script like the following from the project root, replacing `important` and `productions`
with the files and production IDs you actually verified:

```python
from pathlib import Path
import hashlib
import json

root = Path.cwd()
important = ["assets/media-manifest.json"]
productions = []
records = [
    {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
    for name in important
]
ledger = root / "output/workspace-state/local-workspace.json"
ledger.parent.mkdir(parents=True, exist_ok=True)
with ledger.open("x", encoding="utf-8") as stream:
    json.dump({"schema_version": 1, "role": "canonical-local-workspace",
               "preserved_files": records, "required_jobs": productions},
              stream, ensure_ascii=False, indent=2)
```

Then run:

```bash
python -S -B scripts/check_local_workspace.py
```

The ledger detects differences from its recorded baseline. It is not a backup, a creative
review or proof that every historical dependency is installed. Preserve previous bytes
before deliberately updating a recorded file, and update the ledger explicitly rather
than dismissing a missing-file report.
