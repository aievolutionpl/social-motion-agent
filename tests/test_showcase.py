import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import studio_core as core
import showcase


class ShowcaseTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temp.cleanup)
        self.folder = core.create_job("showcase fixture", "shorts", "9:16", 36, "pl", Path(temp.name))

    @unittest.skipUnless((core.ROOT / "node_modules/gsap/dist/gsap.min.js").is_file(), "npm ci required")
    def test_prepared_job_is_complete_portable_and_preserves_user_answers(self):
        intake = core.read(self.folder / "intake.json")
        for q in intake["questions"]:
            q["answer"] = "User supplied choice"
        core.write(self.folder / "intake.json", intake)
        showcase.prepare(self.folder)
        self.assertEqual(core.check_job(self.folder, "assets"), [])
        self.assertEqual(core.read(self.folder / "intake.json"), intake)
        source = (self.folder / "source/index.html").read_text(encoding="utf-8")
        self.assertNotIn("__PLAN__", source)
        self.assertNotIn(str(core.ROOT), source)
        for file in ("citrus.png", "pixel.ttf", "gsap.min.js", "frame-tokens.css"):
            self.assertTrue((self.folder / "source" / file).is_file())
        self.assertIn("dimension", source)
        self.assertFalse(core.read(self.folder / "preview.json").get("reviewed"))
        with self.assertRaisesRegex(ValueError, "Composition exists"):
            showcase.prepare(self.folder)

    @unittest.skipUnless((core.ROOT / "node_modules/gsap/dist/gsap.min.js").is_file(), "npm ci required")
    def test_wrong_format_rejected_before_modifying_brief(self):
        job = core.read(self.folder / "job.json")
        job["width"] = 1920
        core.write(self.folder / "job.json", job)
        before = (self.folder / "brief.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "1080x1920"):
            showcase.prepare(self.folder)
        self.assertEqual(before, (self.folder / "brief.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
