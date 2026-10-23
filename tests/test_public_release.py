import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import studio_core as core
import hyperframes_adapter as hf
import voiceover
from demo import resize_template
from test_studio import complete_plan

class PortableReleaseTests(unittest.TestCase):
    def test_portrait_resize_does_not_replace_width_twice(self):
        source = '<main data-width="1920" data-height="1080">'
        self.assertEqual(resize_template(source, 1080, 1920), '<main data-width="1080" data-height="1920">')

    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.folder = core.create_job("fixture", "launch", "16:9", 8, "en", Path(self.temp.name))
        complete_plan(self.folder)
        (self.folder / "source/index.html").write_text("<html>fixture</html>", encoding="utf-8")

    def test_source_change_invalidates_fingerprint(self):
        before = core.fingerprint(self.folder)
        (self.folder / "source/index.html").write_text("<html>changed</html>", encoding="utf-8")
        self.assertNotEqual(before, core.fingerprint(self.folder))

    def test_refs_cannot_escape_repository(self):
        with self.assertRaises(ValueError):
            core.resolve_ref("../outside")

    def test_render_cannot_escape_output(self):
        with self.assertRaises(ValueError):
            hf.render(self.folder, "../../outside")

    def test_existing_render_is_preserved(self):
        target = self.folder / "renders/existing.mp4"
        target.write_bytes(b"original")
        with self.assertRaises(ValueError):
            hf.render(self.folder, "existing")
        self.assertEqual(target.read_bytes(), b"original")

    def test_pending_intake_blocks_renderer(self):
        intake = core.read(self.folder / "intake.json")
        intake["questions"][0]["answer"] = None
        core.write(self.folder / "intake.json", intake)
        with patch.object(hf.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                hf.render(self.folder)
            run.assert_not_called()

    def test_failure_removes_partial_and_lock_but_keeps_log(self):
        with patch.object(hf, "command", return_value=["fake"]), patch.object(
                hf.subprocess, "run", return_value=Mock(returncode=1)):
            with self.assertRaises(ValueError):
                hf.render(self.folder, "failed")
        self.assertFalse((self.folder / "renders/failed.mp4").exists())
        self.assertFalse((self.folder / "renders/failed.lock").exists())
        self.assertTrue((self.folder / "notes/hyperframes-failed.log").exists())

    def test_concurrent_render_lock_is_respected(self):
        lock = self.folder / "renders/busy.lock"
        lock.write_text("other process")
        with self.assertRaises(ValueError):
            hf.render(self.folder, "busy")
        self.assertTrue(lock.exists())

    def test_voice_dry_run_needs_no_key_or_network(self):
        with patch.dict("os.environ", {}, clear=True), patch.object(voiceover.urllib.request, "urlopen") as request:
            result = voiceover.synthesize("Sample", "synthetic-voice", self.folder / "sample.mp3")
        request.assert_not_called()
        self.assertFalse(result["executed"])

    def test_voice_execute_requires_key(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
            voiceover.synthesize("Sample", "synthetic-voice", self.folder / "sample.mp3", execute=True)

    def test_voice_http_errors_do_not_leak_body_or_retry(self):
        from urllib.error import HTTPError
        error = HTTPError("https://api.elevenlabs.io", 429, "sensitive provider body", {}, None)
        with patch.dict("os.environ", {"ELEVENLABS_API_KEY": "unit-test-placeholder"}):
            with patch.object(voiceover.urllib.request, "urlopen", side_effect=error) as call:
                with self.assertRaisesRegex(ValueError, "HTTP 429") as caught:
                    voiceover.synthesize("Sample", "synthetic-voice", self.folder / "sample.mp3", execute=True)
        self.assertNotIn("sensitive", str(caught.exception))
        self.assertEqual(call.call_count, 1)

if __name__ == "__main__":
    unittest.main()
