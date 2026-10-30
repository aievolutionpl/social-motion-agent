from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import kinetic_adapter as kinetic
import kinetic_platform
import studio_core as core
from test_studio import complete_plan


class KineticSourceTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "supplied"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("Synthetic source integrity fixture, not a real engine")
        self.pin = self.root / "pin.json"
        core.write(self.pin, {"tree_sha256": "fixture", "files": {"SKILL.md": core.sha(self.source / "SKILL.md")}})
        self.cache = self.root / "runtime/kinetic"
        self.addCleanup(patch.stopall)
        patch.object(kinetic, "PIN", self.pin).start()
        patch.object(kinetic, "CACHE", self.cache).start()

    def test_setup_is_verified_idempotent_and_does_not_overwrite_modified_cache(self):
        self.assertFalse(kinetic.setup(self.source)["already_present"])
        self.assertTrue(kinetic.setup(self.source)["already_present"])
        (self.cache / "SKILL.md").write_text("User edit")
        with self.assertRaisesRegex(ValueError, "changed"):
            kinetic.setup(self.source)
        self.assertEqual((self.cache / "SKILL.md").read_text(), "User edit")

    def test_modified_source_is_rejected_before_cache_is_written(self):
        (self.source / "SKILL.md").write_text("Different revision")
        with self.assertRaises(ValueError):
            kinetic.setup(self.source)
        self.assertFalse(self.cache.exists())

    def test_pinned_path_cannot_escape_source(self):
        core.write(self.pin, {"tree_sha256": "fixture", "files": {"../outside": "fixture"}})
        with self.assertRaisesRegex(ValueError, "Invalid path"):
            kinetic.verify_source(self.source)

    def test_prepare_copies_only_pinned_files_from_cache(self):
        files = core.read(self.pin)["files"]
        for relative in ("engine/index.html", "scripts/render.py"):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic preparation fixture, not executed")
            files[relative] = core.sha(path)
        core.write(self.pin, {"tree_sha256": "fixture", "files": files})
        kinetic.setup(self.source)
        (self.cache / "engine/unrelated.private").write_text("Unpinned fixture must not be copied")
        folder = core.create_job("prepare fixture", "kinetic-launch", "16:9", 30, "pl", self.root / "jobs")
        with patch.object(kinetic, "_adapt"):
            kinetic.prepare(folder)
        self.assertTrue((folder / "source/kinetic/index.html").is_file())
        self.assertFalse((folder / "source/kinetic/unrelated.private").exists())


class KineticRenderTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temporary.cleanup)
        self.folder = core.create_job("kinetic fixture", "kinetic-launch", "16:9", 2, "en", Path(temporary.name))
        complete_plan(self.folder)
        brief = core.read(self.folder / "brief.json")
        brief.update(engine="kinetic-film", audio_required=False)
        core.write(self.folder / "brief.json", brief)
        for relative in ("source/kinetic/spec.js", "source/kinetic-runtime/render.py"):
            path = self.folder / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic unit fixture; never executed")
        core.write(self.folder / "source/kinetic-settings.json", {"audio_asset_id": None})
        self.info = {"fps": 60, "dur": 2, "bpm": 128, "endCardStart": 1.5}

    def process_success(self, argv, **kwargs):
        if "--out" in argv:
            Path(argv[argv.index("--out") + 1]).write_bytes(b"synthetic picture")
        elif argv[0] == "ffmpeg":
            Path(argv[-1]).write_bytes(b"synthetic unit video, not media")
        return subprocess.CompletedProcess(argv, 0)

    def render_patches(self):
        return (patch.object(kinetic, "_run_json", return_value=self.info),
                patch.object(kinetic.subprocess, "run", side_effect=self.process_success),
                patch.object(kinetic, "quality", return_value={"passed": True}),
                patch.object(kinetic, "probe_job", return_value={"passed": True, "failures": []}))

    def test_success_records_actual_sources_and_uses_isolated_worker_directory(self):
        a, b, c, d = self.render_patches()
        with a, b as process, c, d:
            result = kinetic.render(self.folder, resolution="720", samples=2)
        self.assertTrue(result["probe_passed"])
        receipt = core.render_provenance(self.folder, result["render"])
        self.assertEqual(receipt["fingerprint"], core.fingerprint(self.folder))
        self.assertEqual(receipt["producer"], "kinetic-film")
        self.assertEqual((core.read(self.folder / "job.json")["width"], core.read(self.folder / "job.json")["fps"]), (1280, 60))
        argv = process.call_args_list[0].args[0]
        self.assertIn(".kinetic-", str(argv[argv.index("--out")+1]))
        self.assertFalse(process.call_args_list[0].kwargs["shell"])
        self.assertFalse((self.folder / "renders/kinetic.lock").exists())
        self.assertFalse(list((self.folder / "renders").glob(".kinetic-*")))

    def test_source_edit_during_render_prevents_receipt(self):
        def changed(argv, **kwargs):
            result = self.process_success(argv, **kwargs)
            if argv[0] == "ffmpeg":
                (self.folder / "source/kinetic/spec.js").write_text("Changed during render")
            return result
        with patch.object(kinetic, "_run_json", return_value=self.info), patch.object(
                kinetic.subprocess, "run", side_effect=changed), patch.object(kinetic, "quality", return_value={"passed": True}):
            with self.assertRaisesRegex(ValueError, "zmieni"):
                kinetic.render(self.folder)
        self.assertEqual(core.render_provenance(self.folder, "renders/kinetic.mp4"), {})

    def test_rejected_motion_has_no_receipt_or_passing_probe(self):
        a, b, _c, d = self.render_patches()
        with a, b, patch.object(kinetic, "quality", return_value={"passed": False}), d as probe:
            result = kinetic.render(self.folder)
        self.assertFalse(result["probe_passed"])
        self.assertFalse(result["receipt_recorded"])
        self.assertEqual(core.render_provenance(self.folder, result["render"]), {})
        probe.assert_not_called()

    def test_invalid_name_existing_output_and_lock_are_preserved(self):
        target = self.folder / "renders/kinetic.mp4"
        target.write_bytes(b"original")
        lock = self.folder / "renders/busy.lock"
        lock.write_text("Other render")
        with patch.object(kinetic.subprocess, "run") as process:
            for name in ("../escape", "kinetic", "busy"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    kinetic.render(self.folder, name)
        self.assertEqual(target.read_bytes(), b"original")
        self.assertEqual(lock.read_text(), "Other render")
        process.assert_not_called()

    def test_incomplete_intake_does_not_launch_renderer(self):
        data = core.read(self.folder / "intake.json")
        data["questions"][0]["answer"] = None
        core.write(self.folder / "intake.json", data)
        with patch.object(kinetic.subprocess, "run") as process, self.assertRaises(ValueError):
            kinetic.render(self.folder)
        process.assert_not_called()

    def test_audio_requires_registered_asset_and_engine_is_explicit(self):
        with patch.object(kinetic.subprocess, "run") as process:
            with self.assertRaisesRegex(ValueError, "asset ID"):
                kinetic.render(self.folder, audio="unregistered")
            brief = core.read(self.folder / "brief.json")
            brief["audio_required"] = True
            core.write(self.folder / "brief.json", brief)
            with self.assertRaisesRegex(ValueError, "premixed"):
                kinetic.render(self.folder)
            brief["engine"] = "hypermotion"
            core.write(self.folder / "brief.json", brief)
            with self.assertRaisesRegex(ValueError, "explicitly"):
                kinetic.render(self.folder)
        process.assert_not_called()

    def test_wrong_fps_is_rejected_and_lock_is_cleaned(self):
        with patch.object(kinetic, "_run_json", return_value={**self.info, "fps": 30}), self.assertRaisesRegex(ValueError, "60 FPS"):
            kinetic.render(self.folder)
        self.assertFalse((self.folder / "renders/kinetic.lock").exists())

    def test_prepare_preserves_existing_composition_and_rejects_portrait(self):
        with patch.object(kinetic, "verify_source") as verify:
            with self.assertRaisesRegex(ValueError, "exists"):
                kinetic.prepare(self.folder)
            job = core.read(self.folder / "job.json")
            job["format"] = "9:16"
            core.write(self.folder / "job.json", job)
            with self.assertRaisesRegex(ValueError, "16:9"):
                kinetic.prepare(self.folder)
        verify.assert_not_called()


class KineticPlatformTests(unittest.TestCase):
    def test_worker_limit_uses_available_memory_and_rejects_unsafe_resolution(self):
        with patch.object(kinetic_platform, "memory_gib", return_value=2), patch.object(kinetic_platform.os, "cpu_count", return_value=12):
            self.assertEqual(kinetic_platform.workers_for("720"), 1)
            self.assertEqual(kinetic_platform.workers_for("720", 10), 2)
            with self.assertRaisesRegex(ValueError, "lower --res"):
                kinetic_platform.workers_for("4k")

    def test_route_and_published_demo_are_consistent(self):
        route = core.routes()["kinetic-launch"]
        self.assertIn("skills/kinetic-launch/SKILL.md", route["skills"])
        for path in route["skills"]:
            self.assertTrue((core.ROOT / path).is_file())
        provenance = core.read(core.ROOT / "examples/kinetic-launch/provenance.json")
        self.assertEqual(core.sha(core.ROOT / "docs/media/kinetic-launch.mp4"), provenance["video_sha256"])
        readme = (core.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("kinetic-launch", readme.splitlines()[0])
        self.assertNotIn("docs/media/premium-intro.mp4", readme)

    def test_local_skill_is_searchable_with_actual_integrity(self):
        entry = kinetic.catalog_entry()
        self.assertEqual(entry["name"], "kinetic-launch")
        self.assertEqual(entry["sha256"], core.sha(core.ROOT / entry["path"]))


if __name__ == "__main__":
    unittest.main()
