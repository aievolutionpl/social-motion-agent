import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import studio_core as core
import premium_intro
import release_check


class PremiumIntroTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / 'output/tests'
        base.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temp.cleanup)
        self.folder = core.create_job('premium fixture', 'showcase', '16:9', 30, 'pl', Path(temp.name))

    @unittest.skipUnless((core.ROOT / 'node_modules/gsap/dist/gsap.min.js').is_file(), 'npm ci required')
    def test_reproduction_preserves_answers_and_requires_review(self):
        intake = core.read(self.folder / 'intake.json')
        for question in intake['questions']:
            question['answer'] = 'Actual user choice'
        core.write(self.folder / 'intake.json', intake)
        premium_intro.prepare(self.folder)
        self.assertEqual(core.check_job(self.folder, 'assets'), [])
        self.assertEqual(core.read(self.folder / 'intake.json'), intake)
        for file in ('source/index.html', 'source/gsap.min.js', 'source/media/hero.png',
                     'source/media/codex-clean.jpg', 'audio/mix.wav', 'captions.srt'):
            self.assertTrue((self.folder / file).is_file(), file)
        self.assertFalse(core.read(self.folder / 'preview.json').get('reviewed'))
        with self.assertRaisesRegex(ValueError, 'Composition exists'):
            premium_intro.prepare(self.folder)

    def test_wrong_format_does_not_change_brief(self):
        job = core.read(self.folder / 'job.json')
        job['duration_sec'] = 20
        core.write(self.folder / 'job.json', job)
        before = (self.folder / 'brief.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '1920x1080'):
            premium_intro.prepare(self.folder)
        self.assertEqual(before, (self.folder / 'brief.json').read_bytes())

    def test_published_video_must_match_integrity_manifest(self):
        path = core.ROOT / 'docs/media/kinetic-launch.mp4'
        raw = path.read_bytes()
        self.assertEqual(release_check.inspect(path, raw), [])
        self.assertIn('media missing or different from integrity manifest',
                      release_check.inspect(path, raw[:-1]))


if __name__ == '__main__':
    unittest.main()
