import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import studio_core as core


def complete_plan(folder):
    """Synthetic fixture only; not a user-approved production brief."""
    intake = core.read(folder / "intake.json")
    for q in intake["questions"]:
        q["answer"] = "synthetic test fixture"
    core.write(folder / "intake.json", intake)
    brief = core.read(folder / "brief.json")
    brief.update(goal="test", audience="test", direction="test", engine="ffmpeg", engine_reason="synthetic fixture", audio_required=False)
    core.write(folder / "brief.json", brief)
    core.write(folder / "research.json", {"sources": [{"id": "s1", "title": "fixture",
               "url": "fixture:test", "accessed_at": core.now(), "used_for": "synthetic integration test"}],
               "claims": [], "conclusions": "No real-world claims in this fixture."})
    core.write(folder / "storyboard.json", {"scenes": [{"id": "s01", "visual": "test card",
               "duration_sec": core.read(folder / "job.json")["duration_sec"], "asset_ids": []}]})
    (folder / "source/script.md").write_text("# Scenariusz\n\nSynthetic fixture.\n", encoding="utf-8")


class ProductionTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.base = Path(self.temp.name).resolve()
        if not self.base.is_relative_to(base.resolve()):
            raise RuntimeError("Unexpected test directory")
        self.addCleanup(self.temp.cleanup)
        self.folder = core.create_job("test", "shorts", "9:16", 2, "pl", self.base)

    def test_intake_blocks_without_answers(self):
        errors = core.check_job(self.folder, "brief")
        self.assertTrue(any("5 pytań" in value for value in errors))

    def test_six_questions_are_rejected(self):
        complete_plan(self.folder)
        data = core.read(self.folder / "intake.json")
        data["questions"].append(dict(data["questions"][0]))
        core.write(self.folder / "intake.json", data)
        self.assertTrue(core.check_job(self.folder, "brief"))

    def test_research_is_required_before_assets(self):
        complete_plan(self.folder)
        self.assertEqual(core.check_job(self.folder, "assets"), [])
        core.write(self.folder / "research.json", {"sources": [], "claims": [], "conclusions": ""})
        self.assertTrue(core.check_job(self.folder, "assets"))

    def test_claims_need_a_known_source(self):
        complete_plan(self.folder)
        data = core.read(self.folder / "research.json")
        data["claims"] = [{"text": "A claim", "status": "confirmed", "source_ids": ["missing"]}]
        core.write(self.folder / "research.json", data)
        self.assertTrue(any("source_ids" in value for value in core.check_job(self.folder, "research")))

    def test_storyboard_duration_must_match(self):
        complete_plan(self.folder)
        data = core.read(self.folder / "storyboard.json")
        data["scenes"][0]["duration_sec"] = 12
        core.write(self.folder / "storyboard.json", data)
        self.assertTrue(any("Czas storyboardu" in value for value in core.check_job(self.folder, "storyboard")))

    def test_paths_cannot_escape_job(self):
        with self.assertRaises(ValueError):
            core.local(self.folder, "../../outside", exists=False)

    def test_asset_mutation_is_detected(self):
        complete_plan(self.folder)
        source = self.base / "test.txt"
        source.write_text("one", encoding="utf-8")
        asset = core.register_asset(self.folder, source, "fixture", "test-only", "test")
        self.assertEqual(core.check_job(self.folder, "assets"), [])
        (self.folder / asset["path"]).write_text("two", encoding="utf-8")
        self.assertTrue(any("zmienił" in value for value in core.check_job(self.folder, "assets")))

    def test_render_without_review_cannot_be_packaged(self):
        complete_plan(self.folder)
        with self.assertRaises(ValueError):
            core.package_job(self.folder)

    def test_profile_changes_invalidate_probe(self):
        complete_plan(self.folder)
        before = core.fingerprint(self.folder)
        job = core.read(self.folder / "job.json")
        job["width"] += 2
        core.write(self.folder / "job.json", job)
        self.assertNotEqual(before, core.fingerprint(self.folder))

    def test_reject_nonfinite_duration(self):
        for duration in (math.nan, math.inf, -1, 0):
            with self.assertRaises(ValueError):
                core.create_job("bad", "shorts", "9:16", duration, "pl", self.base)

    def test_route_skill_paths_exist(self):
        missing = [value for route in core.routes().values() for value in route["skills"] if not core.resolve_ref(value).is_file()]
        self.assertEqual(missing, [])

    def review_fixture(self):
        complete_plan(self.folder)
        render = self.folder / "renders/fixture.mp4"
        render.write_bytes(b"synthetic unit fixture; technical probe stub")
        preview = {"path": "renders/fixture.mp4", "sha256": core.sha(render), "reviewed": True,
                   "reviewer": "unit fixture", "notes": "synthetic unit fixture only"}
        core.write(self.folder / "preview.json", preview)
        job = core.read(self.folder / "job.json")
        job["render"] = "renders/fixture.mp4"
        core.write(self.folder / "job.json", job)
        core.write(self.folder / "technical.json", {"passed": True, "render_sha256": core.sha(render), "fingerprint": core.fingerprint(self.folder)})
        core.write(self.folder / "review.json", {"render_sha256": core.sha(render), "reviewer": "unit fixture",
                   "evidence": ["renders/fixture.mp4"],
                   "checks": {area: {"status": "pass", "notes": "unit fixture only"} for area in core.REVIEW_AREAS}})
        return render

    def test_review_is_invalid_after_render_changes(self):
        render = self.review_fixture()
        self.assertEqual(core.check_job(self.folder, "final"), [])
        render.write_bytes(b"a different render")
        self.assertTrue(core.check_job(self.folder, "final"))

    def test_package_copies_evidence_and_source(self):
        self.review_fixture()
        package = core.package_job(self.folder)
        self.assertTrue((package / "master.mp4").is_file())
        self.assertTrue((package / "source/script.md").is_file())
        self.assertTrue((package / "review.json").is_file())
        self.assertEqual(core.read(package / "job.json")["state"], "packaged")

    def test_generated_assets_require_provenance(self):
        source = self.base / "asset.bin"
        source.write_bytes(b"test")
        with self.assertRaises(ValueError):
            core.register_asset(self.folder, source, "fal", "test", "test", provider="fal")


if __name__ == "__main__":
    unittest.main()
