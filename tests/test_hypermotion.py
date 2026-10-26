import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import hypermotion_adapter as hm
import studio_core as core
from test_studio import complete_plan


class HyperMotionTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.folder = core.create_job("native fixture", "explainer", "16:9", 2, "en", self.base)
        complete_plan(self.folder)
        self.scene = self.folder / "source/index.hype"
        self.scene.write_bytes(b"mock native scene; not a real Hyper Motion project")

    def process_success(self, argv, **kwargs):
        if "render" in argv:
            Path(argv[argv.index("-o") + 1]).write_bytes(b"mock video")
        return subprocess.CompletedProcess(argv, 0)

    def test_success_uses_explicit_scene_and_records_source_provenance(self):
        before = core.fingerprint(self.folder)
        with patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(
                hm.subprocess, "run", side_effect=self.process_success) as process, patch.object(
                hm, "probe_job", return_value={"passed": True, "failures": []}) as probe:
            result = hm.render(self.folder)
        self.assertEqual(process.call_count, 2)
        argv = process.call_args_list[1].args[0]
        self.assertEqual(argv[argv.index("--scene") + 1], str(self.scene))
        self.assertEqual(argv[argv.index("--fps") + 1], "30")
        self.assertFalse(process.call_args.kwargs["shell"])
        receipt = core.render_provenance(self.folder, result["render"])
        self.assertEqual(receipt["fingerprint"], before)
        self.assertEqual(receipt["producer"], "hypermotion")
        self.assertTrue(result["probe_passed"])
        self.assertFalse(result["reviewed"])
        probe.assert_called_once_with(self.folder, "renders/hypermotion.mp4")

    def test_validation_failure_does_not_render(self):
        with patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(
                hm.subprocess, "run", return_value=Mock(returncode=1)) as process:
            with self.assertRaisesRegex(ValueError, "Hyper Motion failed"):
                hm.render(self.folder)
        process.assert_called_once()
        self.assertEqual(list((self.folder / "renders").iterdir()), [])
        self.assertTrue((self.folder / "notes/hypermotion-hypermotion.log").is_file())

    def test_timeout_cleans_partial_sentinels_and_lock(self):
        def timeout(argv, **kwargs):
            if "render" in argv:
                output = Path(argv[argv.index("-o") + 1])
                output.write_bytes(b"partial")
                Path(str(output) + ".error").write_text("partial failure")
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
            return subprocess.CompletedProcess(argv, 0)
        with patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(
                hm.subprocess, "run", side_effect=timeout):
            with self.assertRaisesRegex(ValueError, "timed out"):
                hm.render(self.folder)
        self.assertEqual(list((self.folder / "renders").iterdir()), [])

    def test_success_exit_without_nonempty_video_is_rejected(self):
        for empty_file in (False, True):
            def empty(argv, **kwargs):
                if empty_file and "render" in argv:
                    Path(argv[argv.index("-o") + 1]).touch()
                return subprocess.CompletedProcess(argv, 0)
            with self.subTest(empty_file=empty_file), patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(
                    hm.subprocess, "run", side_effect=empty), patch.object(hm, "probe_job") as probe:
                with self.assertRaisesRegex(ValueError, "non-empty video"):
                    hm.render(self.folder)
            probe.assert_not_called()
            self.assertEqual(list((self.folder / "renders").iterdir()), [])

    def test_source_change_during_render_has_no_valid_receipt(self):
        def changed(argv, **kwargs):
            result = self.process_success(argv, **kwargs)
            if "render" in argv:
                self.scene.write_bytes(b"changed during render")
            return result
        with patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(
                hm.subprocess, "run", side_effect=changed), patch.object(hm, "probe_job") as probe:
            with self.assertRaises(ValueError):
                hm.render(self.folder)
        self.assertEqual(core.render_provenance(self.folder, "renders/hypermotion.mp4"), {})
        probe.assert_not_called()

    def test_invalid_name_scene_and_incomplete_plan_do_not_launch(self):
        outside_source = self.folder / "assets/scene.hype"
        outside_source.write_bytes(b"fixture")
        with patch.object(hm.subprocess, "run") as process:
            for kwargs in ({"name": "../escape"}, {"scene": "assets/scene.hype"}, {"scene": "../escape.hype"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    hm.render(self.folder, **kwargs)
            core.write(self.folder / "research.json", {})
            with self.assertRaises(ValueError):
                hm.render(self.folder)
        process.assert_not_called()

    def test_existing_output_and_lock_are_preserved(self):
        target = self.folder / "renders/hypermotion.mp4"
        target.write_bytes(b"original")
        with patch.object(hm, "command", return_value=["fixture-cli"]), patch.object(hm.subprocess, "run") as process:
            with self.assertRaises(ValueError):
                hm.render(self.folder)
            self.assertEqual(target.read_bytes(), b"original")
            lock = self.folder / "renders/busy.lock"
            lock.write_text("other render")
            with self.assertRaises(ValueError):
                hm.render(self.folder, name="busy")
            self.assertEqual(lock.read_text(), "other render")
        process.assert_not_called()

    def test_cli_missing_is_actionable_and_does_not_fallback(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(hm.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "HYPERMOTION_CLI"):
                hm.command()

    def test_mjs_and_npm_windows_wrapper_use_node_without_shell(self):
        npm = self.base / "npm with spaces & symbol"
        entry = npm / "node_modules/@psiddharthdesign/hypermotion/bin/hypermotion.mjs"
        entry.parent.mkdir(parents=True)
        entry.write_text("// mock entry")
        wrapper = npm / "hypermotion.cmd"
        wrapper.write_text("@echo mock")
        for path in (entry, wrapper):
            with self.subTest(path=path), patch.dict(os.environ, {"HYPERMOTION_CLI": str(path)}), patch.object(
                    hm.shutil, "which", return_value="node-fixture"):
                self.assertEqual(hm.command("validate", "a & b.hype"),
                                 ["node-fixture", str(entry), "validate", "a & b.hype"])


if __name__ == "__main__":
    unittest.main()
