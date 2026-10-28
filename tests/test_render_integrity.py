"""Regression coverage for stale source approval and audio-masked short video."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import assembly
import studio_core as core
from test_studio import complete_plan


class RenderIntegrityTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.folder = core.create_job("integrity fixture", "launch", "16:9", 2, "en", Path(self.temp.name))
        job = core.read(self.folder / "job.json")
        job.update(width=160, height=90)
        core.write(self.folder / "job.json", job)
        complete_plan(self.folder)
        self.render_path = "renders/fixture.mp4"
        self.render = self.folder / self.render_path
        self.render.write_bytes(b"synthetic fixture; ffprobe mocked")
        self.info = {"streams": [{"codec_type": "video", "width": 160, "height": 90,
                                   "avg_frame_rate": "30/1", "duration": "2.0"}],
                     "format": {"duration": "2.0"}}

    def record(self):
        return core.record_render(self.folder, self.render_path, core.fingerprint(self.folder), "synthetic-unit-fixture")

    def probe(self, folder=None, path=None):
        with patch.object(core.subprocess, "run", return_value=Mock(stdout=json.dumps(self.info))):
            return core.probe_job(folder or self.folder, path or self.render_path)

    def review(self):
        core.write(self.folder / "preview.json", {"path": self.render_path, "sha256": core.sha(self.render),
                   "reviewed": True, "reviewer": "synthetic fixture", "notes": "Test only, not production approval"})
        core.write(self.folder / "review.json", {"render_sha256": core.sha(self.render),
                   "reviewer": "synthetic fixture", "evidence": [self.render_path],
                   "checks": {area: {"status": "pass", "notes": "Synthetic fixture"} for area in core.REVIEW_AREAS}})

    def test_reprobe_cannot_approve_old_video_after_source_change(self):
        receipt = self.record()
        self.assertTrue(self.probe()["passed"])
        self.review()
        self.assertEqual(core.check_job(self.folder, "final"), [])
        (self.folder / "source/index.html").write_text("Changed composition", encoding="utf-8")
        report = self.probe()
        self.assertFalse(report["passed"])
        self.assertEqual(report["fingerprint"], receipt["fingerprint"])
        self.assertEqual(core.render_provenance(self.folder, self.render_path), receipt)
        self.assertTrue(core.check_job(self.folder, "final"))
        with self.assertRaises(ValueError):
            core.package_job(self.folder)

    def test_unregistered_external_video_is_measured_without_fabricating_provenance(self):
        report = self.probe()
        self.assertFalse(report["passed"])
        self.assertIsNone(report["fingerprint"])
        self.assertEqual(report["video_duration_sec"], 2)
        self.assertEqual(core.render_provenance(self.folder, self.render_path), {})

    def test_changed_render_does_not_reuse_receipt(self):
        self.record()
        self.render.write_bytes(b"modified render")
        self.assertFalse(self.probe()["passed"])

    def test_source_change_during_render_prevents_receipt(self):
        before = core.fingerprint(self.folder)
        (self.folder / "source/index.html").write_text("Concurrent edit", encoding="utf-8")
        with self.assertRaises(ValueError):
            core.record_render(self.folder, self.render_path, before, "synthetic-unit-fixture")
        self.assertEqual(core.render_provenance(self.folder, self.render_path), {})

    def test_audio_duration_cannot_mask_missing_video_frames(self):
        self.record()
        self.info["streams"][0]["duration"] = "1.0"
        self.info["streams"].append({"codec_type": "audio", "duration": "2.0"})
        report = self.probe()
        self.assertFalse(report["passed"])
        self.assertTrue(any("strumienia wideo" in failure for failure in report["failures"]))

    def test_moved_delivery_keeps_reprobeable_render_receipt(self):
        self.record()
        self.probe()
        self.review()
        package = core.package_job(self.folder)
        delivery = Path(self.temp.name) / "moved-delivery"
        shutil.move(package, delivery)
        self.assertTrue(self.probe(delivery, "master.mp4")["passed"])
        self.assertEqual(core.check_job(delivery, "final"), [])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg is required")
    def test_short_source_is_rejected_and_valid_assembly_has_receipt(self):
        source = Path(self.temp.name) / "one-second.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                        "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30:duration=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=1",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(source)],
                       check=True, capture_output=True, timeout=60)
        asset = core.register_asset(self.folder, source, "lavfi synthetic fixture", "test-only", "regression test")
        timeline = {"clips": [{"asset_id": asset["id"], "duration_sec": 2, "in_sec": 0, "fit": "contain"}], "audio": {}}
        core.write(self.folder / "timeline.json", timeline)
        with self.assertRaisesRegex(ValueError, "wykracza"):
            assembly.assemble(self.folder)
        self.assertEqual(list((self.folder / "renders").glob("work-*")), [])
        # Two valid one-second excerpts cover the two-second output.
        timeline["clips"][0]["duration_sec"] = 1
        timeline["clips"].append(dict(timeline["clips"][0]))
        core.write(self.folder / "timeline.json", timeline)
        target = assembly.assemble(self.folder)
        report = core.probe_job(self.folder, target.relative_to(self.folder).as_posix())
        self.assertTrue(report["passed"], report["failures"])
        self.assertAlmostEqual(report["video_duration_sec"], 2, delta=0.15)


if __name__ == "__main__":
    unittest.main()
