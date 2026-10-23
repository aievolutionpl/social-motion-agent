import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bootstrap_library as bootstrap
import library_check

class LibraryTests(unittest.TestCase):
    def test_text_integrity_accepts_only_line_ending_changes(self):
        original = b"first\r\nsecond\r\n"
        expected = hashlib.sha256(original).hexdigest()
        self.assertTrue(library_check.digest_matches(b"first\nsecond\n", expected))
        self.assertFalse(library_check.digest_matches(b"changed\nsecond\n", expected))

    def test_manifest_rejects_unsafe_url_and_path(self):
        base = bootstrap.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            fixture = {"id":"example", "path":"tools/repos/example", "url":"https://github.com/example/repo.git", "commit":"a"*40}
            with patch.object(bootstrap, "ROOT", root):
                for key, value in (("url","file:///private/repo"), ("path","../../outside"), ("commit","main")):
                    entry = dict(fixture, **{key:value})
                    (root / "sources.lock.json").write_text(json.dumps({"sources":[entry]}), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        bootstrap.sources()

    def test_existing_modified_checkout_is_preserved(self):
        entry = {"id":"example", "path":"tools/repos/example", "commit":"a"*40}
        base = bootstrap.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            target = root / entry["path"]
            target.mkdir(parents=True)
            (target / "important.txt").write_text("keep")
            with patch.object(bootstrap, "ROOT", root), patch.object(
                bootstrap, "run", side_effect=[str(target.resolve()), "a"*40, " M important.txt"]):
                with self.assertRaisesRegex(ValueError, "modifications"):
                    bootstrap.install(entry)
            self.assertEqual((target / "important.txt").read_text(), "keep")

if __name__ == "__main__":
    unittest.main()
