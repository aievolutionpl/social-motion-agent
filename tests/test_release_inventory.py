import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import release_check


class ReleaseInventoryTests(unittest.TestCase):
    def test_only_generated_root_inventory_is_excluded(self):
        base = release_check.ROOT / 'output/tests'
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            (root / 'bundle-manifest.json').write_text('{}')
            (root / 'docs').mkdir()
            nested = root / 'docs/bundle-manifest.json'
            nested.write_text('{}')
            source = root / 'source.py'
            source.write_text('print(1)')
            with patch.object(release_check, 'ROOT', root):
                self.assertEqual(set(release_check.source_files()), {nested, source})

    def test_inventory_is_not_exempt_from_git_index_inspection(self):
        path = release_check.ROOT / 'bundle-manifest.json'
        self.assertIn('unexpected large non-image file', release_check.inspect(path, b'x' * 2_000_001))
