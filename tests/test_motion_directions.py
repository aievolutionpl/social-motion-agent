import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLIDES = """<!doctype html><html><body>
<section class="scene"><span class="kicker">01 - feature</span><h2>Title</h2><p>Body copy</p></section>
<section class="scene"><h2>Two</h2></section>
<section class="scene"><h2>Three</h2></section>
<video src="clip.mp4" autoplay loop></video>
<style>.scene{transition: opacity .4s}</style>
<script>
const tl = gsap.timeline();
document.querySelectorAll('.scene').forEach((s, i) => tl.to(s, {autoAlpha: 1}));
const jitter = Math.random();
const started = Date.now();
</script></body></html>"""

FILM = """<!doctype html><html><body>
<div id="world"><div class="title">One world</div></div>
<style>.title{transition: none}</style>
<script>
// a comment mentioning Math.random() must not count
const hash = i => ((i * 2654435761) >>> 0) / 4294967295;
window.seek = t => { document.querySelector('#world').style.transform = `scale(${1 + .04 * Math.sin(t)})`; };
</script></body></html>"""


class MotionDirectionsTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, '-S', str(ROOT / 'studio.py'), *args], cwd=ROOT, text=True,
                              capture_output=True, encoding='utf-8')

    def test_menus_are_complete_and_presets_resolve(self):
        data = json.loads((ROOT / 'config/motion-directions.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['style_directions']), 10)
        self.assertEqual(len(data['opener_concepts']), 19)
        self.assertEqual([c['id'] for c in data['opener_concepts']], list(range(1, 20)))
        self.assertEqual(len(data['explainer_modes']), 6)
        presets = {s['slug'] for s in json.loads((ROOT / 'config/motion-presets.json').read_text(encoding='utf-8'))['styles']}
        for menu in ('style_directions', 'explainer_modes'):
            for item in data[menu]:
                if item['preset']:
                    self.assertIn(item['preset'], presets, item['slug'])
        self.assertTrue((ROOT / data['source']['license_file']).is_file())
        listed = json.loads(self.cli('directions', 'list').stdout)
        self.assertEqual(listed['menus']['opener_concepts'], 19)
        self.assertNotEqual(self.cli('directions', 'list', 'missing').returncode, 0)

    def test_show_by_slug_and_concept_number(self):
        shown = json.loads(self.cli('directions', 'show', 'grainy-gradient').stdout)
        self.assertEqual(shown['menu'], 'style_directions')
        self.assertIn('?style=grainy-gradient', shown['example'])
        concept = json.loads(self.cli('directions', 'show', '15').stdout)
        self.assertEqual(concept['slug'], 'claim-how-result')
        self.assertNotEqual(self.cli('directions', 'show', 'nope').returncode, 0)

    def test_brief_ranks_candidates_deterministically(self):
        first = self.cli('directions', 'brief', '--for', 'AI fintech launch')
        self.assertEqual(first.returncode, 0, first.stderr)
        brief = json.loads(first.stdout)
        self.assertEqual(len(brief['concept_candidates']), 3)
        self.assertEqual(brief['concept_candidates'][0]['slug'], 'through-gradient-shapes')
        self.assertEqual(len(brief['direction_candidates']), 3)
        self.assertIn('concept · scenes · objects · opening · ending', brief['fingerprint_template'])
        self.assertEqual(first.stdout, self.cli('directions', 'brief', '--for', 'AI fintech launch').stdout)
        explainer = json.loads(self.cli('directions', 'brief', '--kind', 'explainer', '--for', 'history biography').stdout)
        self.assertEqual(explainer['explainer_modes'][0]['slug'], 'vintage-sketch')
        self.assertNotEqual(self.cli('directions', 'brief').returncode, 0)

    def test_fingerprint_compare(self):
        a = 'problem gone · 4 · notifications / finger / clean screen · notifications falling · logo from clean screen'
        same = json.loads(self.cli('directions', 'compare', a, a).stdout)
        self.assertFalse(same['distinct'])
        self.assertEqual(same['different_count'], 0)
        other = json.loads(self.cli('directions', 'compare', a, 'living number · 6 · counter / city / map · dark to light · decisive stop').stdout)
        self.assertTrue(other['distinct'])
        self.assertTrue(other['concept_changed'])
        self.assertNotEqual(self.cli('directions', 'compare', 'too · short', a).returncode, 0)

    def test_lint_flags_slideshow_and_passes_film(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad, good = Path(tmp) / 'bad.html', Path(tmp) / 'good.html'
            bad.write_text(SLIDES, encoding='utf-8')
            good.write_text(FILM, encoding='utf-8')
            result = self.cli('motion', 'lint', str(bad))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual({e['check'] for e in report['errors']}, {'random', 'seek-contract'})
            self.assertTrue({'slide-deck', 'text-tiers', 'video-clock', 'css-clock', 'system-clock'} <= {w['check'] for w in report['warnings']})
            result = self.cli('motion', 'lint', str(good))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(json.loads(result.stdout)['warnings'], [])
        self.assertEqual(self.cli('motion', 'lint', 'examples/motion-styles/index.html').returncode, 0)
        self.assertNotEqual(self.cli('motion', 'lint').returncode, 0)

    def test_camera_and_rhythm_helpers(self):
        if not shutil.which('node'):
            self.skipTest('Node unavailable; helper test not run')
        script = r"""
const fs=require('fs'); const src=fs.readFileSync(process.argv[1],'utf8');
const h=new Function(src+';return {shotCamera,cameraTransform,frameOn,grainOffset,enterExit,directionalBlur}')();
const keys=[{t:0,s:1,x:400,y:250},{t:1,s:2,x:200,y:100}];
const out={mid:h.shotCamera(.5,keys),end:h.shotCamera(3,keys),edge:h.cameraTransform({s:2,x:0,y:0},800,500),
  frame:h.frameOn({x:100,y:100,w:200,h:100},.6,800,500),g1:h.grainOffset(1.3),g2:h.grainOffset(1.3),
  enter:h.enterExit(0,0,2),held:h.enterExit(1.5,0,2),gone:h.enterExit(3,0,2),blur:h.directionalBlur(.5)};
console.log(JSON.stringify(out));"""
        result = subprocess.run(['node', '-e', script, str(ROOT / 'templates/motion-helpers.js')], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out['mid'], {'s': 1.5, 'x': 300, 'y': 175})
        self.assertEqual(out['end'], {'s': 2, 'x': 200, 'y': 100})
        self.assertEqual((out['edge']['tx'], out['edge']['ty']), (0, 0))
        self.assertEqual(out['frame']['s'], 2.4)
        self.assertEqual(out['g1'], out['g2'])
        self.assertEqual(out['enter'], 0)
        self.assertEqual(out['held'], 1)
        self.assertEqual(out['gone'], 0)
        self.assertEqual(out['blur'], '15.00 1.20')


if __name__ == '__main__':
    unittest.main()
