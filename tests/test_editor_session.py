import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import motion_directions


class EditorSessionTests(unittest.TestCase):
    def test_modes_offer_distinct_unapproved_choices(self):
        packets = [motion_directions.session('Film o produkcie', mode)
                   for mode in ('footage', 'product', 'explainer')]
        for packet in packets:
            self.assertEqual(packet['status'], 'proposal')
            self.assertIsNone(packet['approval'])
            self.assertEqual(len({o['name'] for o in packet['options']}), 3)
            self.assertTrue(all(o['audio'] and o['tradeoff'] for o in packet['options']))
        self.assertNotEqual(packets[0]['options'], packets[1]['options'])

    def test_invalid_inputs(self):
        for subject, mode in [(' ', 'footage'), ('Film', 'unknown')]:
            with self.assertRaises(ValueError):
                motion_directions.session(subject, mode)

    def test_cli_produces_json(self):
        result = subprocess.run([sys.executable, '-S', 'studio.py', 'directions', 'session',
                                 '--for', 'Demo aplikacji', '--mode', 'product'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['mode'], 'product')
