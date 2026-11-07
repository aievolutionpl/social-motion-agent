import functools
import http.server
import json
import shutil
import subprocess
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MotionPresetTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable,'-S',str(ROOT/'studio.py'),'motion','presets',*args], cwd=ROOT, text=True, capture_output=True, encoding='utf-8')

    def test_registry_and_selection(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        styles = json.loads(result.stdout)['styles']
        expected = {'riso-print','decollage-time-layers','optical-moire','grainy-gradient','poster-color-block','flat-pop',
                    'visual-journalism','vintage-sketch','cartoon-collage','white-catalog','brutalist-mono','luxury-dark','continuous-action'}
        self.assertEqual({s['slug'] for s in styles}, expected)
        directions = json.loads((ROOT/'config/motion-directions.json').read_text(encoding='utf-8'))
        known = {d['slug'] for menu in ('style_directions','explainer_modes') for d in directions[menu]}
        for style in styles:
            if 'direction' in style:
                self.assertIn(style['direction'], known, style['slug'])
                self.assertTrue(style['idea_source'].startswith('https://'))
        for style in styles:
            selected = self.cli(style['slug'])
            self.assertEqual(selected.returncode, 0, selected.stderr)
            self.assertEqual(json.loads(selected.stdout)['parameters'], style['parameters'])
        self.assertNotEqual(self.cli('missing').returncode, 0)

    def test_rendered_pixels_in_browser(self):
        if not shutil.which('node'):
            self.skipTest('Node unavailable; browser pixel test not run')
        probe = subprocess.run(['node','-e',"require('playwright')"],cwd=ROOT,capture_output=True)
        if probe.returncode:
            self.skipTest('Playwright unavailable; browser pixel test not run')
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        server = http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            url = 'http://127.0.0.1:%d/examples/motion-styles/' % server.server_port
            result = subprocess.run(['node',str(ROOT/'tests/motion_pixels.cjs'),url],cwd=ROOT,text=True,capture_output=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
