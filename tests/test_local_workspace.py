"""Preservation checks use only synthetic temporary production files."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_local_workspace


class LocalPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'original.txt'
        self.source.write_text('important original', encoding='utf-8')
        folder = self.root / 'output/jobs/example'
        folder.mkdir(parents=True)
        (folder / 'job.json').write_text(json.dumps({'id': 'example', 'render': 'film.mp4'}), encoding='utf-8')
        (folder / 'film.mp4').write_bytes(b'synthetic render fixture')
        self.manifest = {'schema_version': 1, 'role': 'canonical-local-workspace',
                         'preserved_files': [{'path': 'original.txt', 'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}],
                         'required_jobs': ['example']}

    def test_valid_ledger_and_changed_original(self):
        self.assertTrue(check_local_workspace.check(self.root, self.manifest)['passed'])
        self.source.write_text('overwritten', encoding='utf-8')
        result = check_local_workspace.check(self.root, self.manifest)
        self.assertFalse(result['passed'])
        self.assertIn('SHA-256', result['errors'][0])

    def test_missing_render_is_reported_without_changing_production(self):
        (self.root / 'output/jobs/example/film.mp4').unlink()  # synthetic fixture only
        result = check_local_workspace.check(self.root, self.manifest)
        self.assertFalse(result['passed'])
        self.assertIn('Render', result['errors'][0])
        self.assertTrue((self.root / 'output/jobs/example/job.json').is_file())

    def test_foreign_paths_and_invalid_schema_are_rejected(self):
        self.manifest['preserved_files'][0]['path'] = '../outside.txt'
        self.assertFalse(check_local_workspace.check(self.root, self.manifest)['passed'])
        for path in ['C:\\secret.txt', '/etc/passwd', '../outside', '']:
            with self.assertRaises(ValueError):
                check_local_workspace.local(self.root, path)
        with self.assertRaises(ValueError):
            check_local_workspace.check(self.root, {'schema_version': 2})
