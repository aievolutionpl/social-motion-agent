"""Offline contract tests for Director Suite. No upstream binaries or API keys."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import director_suite as director
import studio_core as core


class DirectorSuiteTests(unittest.TestCase):
    def setUp(self):
        temp_root = core.ROOT / "output/tests"
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_root)
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.job = core.create_job("Szkolenie AI", "shorts", "9:16", 5, "pl", base)
        core.write(self.job / "storyboard.json", {"scenes": [
            {"id": "hook", "duration_sec": 1.2,
             "visual": "Prawdziwy ekran: logo aplikacji",
             "narration": "Zobacz, jak działa AI."},
            {"id": "click", "duration_sec": 1.8,
             "visual": "Kliknięcie w dashboard",
             "narration": "Kliknij tutaj."},
            {"id": "result", "duration_sec": 2,
             "visual": "Wynik na ekranie", "narration": ""},
        ]})

    def test_plan_and_fingerprint(self):
        before = core.fingerprint(self.job)
        result = director.plan(self.job, "launch")
        self.assertEqual(len(result["files"]), 2)
        self.assertFalse(result["rendered"])
        path = self.job / "source/director/beat-sheet.json"
        sheet = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual([s["start_sec"] for s in sheet["scenes"]], [0, 1.2, 3])
        self.assertEqual(sheet["scenes"][-1]["end_sec"], 5)
        self.assertNotEqual(before, core.fingerprint(self.job))
        self.assertIn("storyboard-only", result["qa"]["scope"])

    def test_plan_preserves_user_edits_unless_overwrite(self):
        director.plan(self.job, "launch")
        sheet = self.job / "source/director/beat-sheet.md"
        sheet.write_text("hand edited", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not overwritten"):
            director.plan(self.job, "launch")
        self.assertEqual(sheet.read_text(encoding="utf-8"), "hand edited")
        director.plan(self.job, "launch", overwrite=True)
        self.assertIn("Director beat sheet", sheet.read_text(encoding="utf-8"))

    def test_qa_is_advisory_not_fake_render_certification(self):
        result = director.analyze(self.job, "launch")
        self.assertEqual(result["cut_points_sec"], [1.2, 3.0])
        self.assertTrue(result["rendered_review_required"])
        self.assertTrue(any("lack narration" in s for s in result["warnings"]))
        self.assertNotIn("score", result)

    def test_qa_checks_pacing(self):
        core.write(self.job / "storyboard.json", {"scenes": [
            {"id": "long", "duration_sec": 4, "visual": "one"},
            {"id": "short", "duration_sec": 1, "visual": "two"},
        ]})
        report = director.analyze(self.job, "launch")
        self.assertTrue(any("First shot" in w for w in report["warnings"]))
        self.assertTrue(any("duration over" in w for w in report["warnings"]))

    def test_bad_scene_ids_or_timing_refused(self):
        scenarios = [
            [{"id": "hello/world", "duration_sec": 5}],
            [{"id": "a", "duration_sec": 2}, {"id": "a", "duration_sec": 3}],
            [{"id": "a", "duration_sec": math.nan}],
            [{"id": "a", "duration_sec": 6}],
            [{"id": "a", "duration_sec": 0}],
        ]
        for scenes in scenarios:
            with self.subTest(scenes=str(scenes)):
                core.write(self.job / "storyboard.json", {"scenes": scenes})
                with self.assertRaises(ValueError):
                    director.plan(self.job, "launch")

    def test_argo_exports_scaffold_not_fake_recording(self):
        result = director.handoff(self.job, "demo")
        self.assertFalse(result["installed"])
        self.assertTrue(result["requires_manual_completion"])
        demo = self.job / "source/interchange/argo/demos/social-motion.demo.ts"
        self.assertIn("narration.startRecording(page)", demo.read_text(encoding="utf-8"))
        manifest = json.loads((self.job / "source/interchange/argo/demos/social-motion.scenes.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["scene"] for entry in manifest], ["hook", "click", "result"])
        self.assertEqual(manifest[0]["text"], "Zobacz, jak działa AI.")
        self.assertIn("http://localhost:3000", (self.job / "source/interchange/argo/argo.config.mjs").read_text(encoding="utf-8"))

    def test_explainroo_polish_needs_external_voice(self):
        director.handoff(self.job, "explainer")
        path = self.job / "source/interchange/explainroo"
        config = json.loads((path / "video.json").read_text(encoding="utf-8"))
        self.assertNotIn("voice", config)
        self.assertIn("[TODO: add spoken narration]", (path / "script.md").read_text(encoding="utf-8"))
        self.assertIn("external", (path / "README.md").read_text(encoding="utf-8").lower())
        self.assertIn("s.title", (path / "scenes.js").read_text(encoding="utf-8"))

    def test_huashu_handoff_does_not_claim_to_render(self):
        result = director.handoff(self.job, "launch")
        self.assertFalse(result["rendered"])
        self.assertFalse((self.job / "source/interchange/huashu-motion/index.html").exists())
        self.assertIn("not executable", (self.job / "source/interchange/huashu-motion/DIRECTION.md").read_text(encoding="utf-8"))

    def test_exports_cannot_clobber_files(self):
        director.handoff(self.job, "demo")
        path = self.job / "source/interchange/argo/demos/social-motion.demo.ts"
        path.write_text("my changes", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not overwritten"):
            director.handoff(self.job, "demo")
        self.assertEqual(path.read_text(encoding="utf-8"), "my changes")

    def test_polish_alignment_produces_real_srt_and_scene_cues(self):
        core.write(self.job / "source/alignment.json", {"segments": [
            {"words": [
                {"word": "Zażółć", "start": 0.1, "end": 0.4},
                {"word": "gęślą.", "start": 0.45, "end": 1},
            ]},
            {"words": [{"word": "Kliknij", "start": 1.3, "end": 1.65},
                       {"word": "tu!", "start": 1.7, "end": 2.1}]},
        ]})
        result = director.captions(self.job, "source/alignment.json")
        self.assertEqual(result["word_count"], 4)
        self.assertFalse(result["audio_was_generated"])
        cues = json.loads((self.job / "source/director/word-cues.json").read_text(encoding="utf-8"))
        self.assertEqual([w["scene_id"] for w in cues["words"]], ["hook", "hook", "click", "click"])
        text = (self.job / "source/director/captions.srt").read_text(encoding="utf-8")
        self.assertIn("00:00:00,100 --> 00:00:01,000", text)
        self.assertIn("Zażółć gęślą.", text)
        self.assertEqual(result["caption_count"], 2)

    def test_rejects_unmeasured_or_unsafe_alignment(self):
        invalid = [
            [{"text": "a", "start": 0.3, "end": 0.6}, {"text": "b", "start": 0.1, "end": 0.2}],
            [{"text": "a", "start": 0.3, "end": 7}],
            [{"text": "a", "start": math.inf, "end": 0.5}],
            [{"text": "", "start": 0, "end": 0.5}],
            [],
        ]
        for words in invalid:
            core.write(self.job / "source/alignment.json", {"words": words})
            with self.subTest(words=str(words)), self.assertRaises(ValueError):
                director.captions(self.job, "source/alignment.json")
        with self.assertRaises(ValueError):
            director.captions(self.job, "../../../etc/passwd")
        self.assertFalse((self.job / "source/director/captions.srt").exists())

    def test_point_feedback_maps_to_scene_and_does_not_fake_fix(self):
        saved = director.point_feedback(self.job, 1.5, 0.33, 0.67, "Przesuń CTA")
        self.assertEqual(saved["feedback"]["scene_id"], "click")
        self.assertFalse(saved["applied"])
        saved = director.point_feedback(self.job, 5, 1, 1, "Sprawdź ostatnią klatkę")
        self.assertEqual(saved["feedback"]["scene_id"], "result")
        self.assertEqual(len(director.list_feedback(self.job)["feedback"]), 2)
        self.assertFalse((self.job / "source/director/beat-sheet.json").exists())

    def test_feedback_rejects_bad_coordinates(self):
        for at, x, y in [(-0.1, .5, .5), (10, .5, .5), (0, -1, .5), (0, 1.01, .5),
                         (0, .5, math.nan), (math.inf, .5, .5)]:
            with self.subTest(at=at, x=x, y=y), self.assertRaises(ValueError):
                director.point_feedback(self.job, at, x, y, "Move")
        with self.assertRaises(ValueError):
            director.point_feedback(self.job, 1, .5, .5, "")
        self.assertEqual(director.list_feedback(self.job), {"feedback": []})


if __name__ == "__main__":
    unittest.main()
