import copy
import functools
import http.server
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import studio_core as core
import install_skill
import walk_talk as wt


def png(path, foreground=False):
    """Authored synthetic RGBA fixture, no user footage or third-party media."""
    width, height = 64, 114
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            pixel = (220, 225, 230, 255)
            if foreground:
                pixel = (255, 60, 50, 255) if 25 < x < 39 and 25 < y < 90 else (0, 0, 0, 0)
            row.extend(pixel)
        rows.append(bytes(row))
    def chunk(tag, data):
        return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b''))


class WalkTalkTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.folder = core.create_job("Synthetic walk test", wt.NAME, "9:16", 3, "pl", self.base)
        wt.prepare(self.folder)

    def spec(self):
        data = core.read(self.folder / "source/walk-talk.json")
        data.update(background_asset="base", foreground_asset="front",
                    captions=[{"start": 0, "end": 1, "text": "Zażółć gęślą jaźń"},
                              {"start": 1, "end": 2, "text": "Druga fraza"}],
                    accents=[{"start": 0.1, "end": 2.5, "text": "POKAŻ\nPROCES", "behind_subject": True}],
                    punches=[{"start": 1, "end": 1.6, "zoom": 1.12}])
        return data

    def fixture(self):
        if not shutil.which("ffprobe") or not (ROOT / "node_modules/gsap/dist/gsap.min.js").is_file():
            self.skipTest("FFprobe and pinned GSAP required for composition integration")
        spec = self.spec()
        for role, foreground in (("background", False), ("foreground", True)):
            path = self.base / (role + ".png")
            png(path, foreground)
            item = core.register_asset(self.folder, path, "Synthetic test fixture", "Authored test fixture", role)
            spec[role + "_asset"] = item["id"]
        core.write(self.folder / "source/walk-talk.json", spec)
        return wt.compose(self.folder)

    def test_prepare_preserves_pending_brief_and_refuses_overwrite(self):
        self.assertTrue(core.check_job(self.folder, "brief"))
        self.assertEqual(core.read(self.folder / "job.json")["state"], "intake")
        original = (self.folder / "source/walk-talk.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "already exist"):
            wt.prepare(self.folder, "ai")
        self.assertEqual((self.folder / "source/walk-talk.json").read_bytes(), original)

    def test_prepare_all_modes_and_rejects_landscape(self):
        for mode in wt.MODES:
            folder = core.create_job("Synthetic mode", wt.NAME, "9:16", 3, "pl", self.base)
            self.assertEqual(wt.prepare(folder, mode)["mode"], mode)
        folder = core.create_job("Wrong format", wt.NAME, "16:9", 3, "pl", self.base)
        with self.assertRaisesRegex(ValueError, "9:16"):
            wt.prepare(folder)
        self.assertFalse((folder / "source/walk-talk.json").exists())

    def test_validation_rejects_unusable_timing_and_missing_matte(self):
        mutations = [lambda s: s.update(foreground_asset=None),
                     lambda s: s["captions"][0].update(start=float("nan")),
                     lambda s: s["accents"][0].update(end=4),
                     lambda s: s["punches"][0].update(zoom=True),
                     lambda s: s["captions"][1].update(start=0.8),
                     lambda s: s["punches"].append({"start": 1.5, "end": 2, "zoom": 1.1}),
                     lambda s: s["accents"][0].update(color="red;position:fixed"),
                     lambda s: s["accents"][0].update(behind_subject="yes")]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                spec = self.spec()
                mutate(spec)
                with self.assertRaises(ValueError):
                    wt.validate(spec, 3)
        wt.validate(self.spec(), 3)

    def test_behind_subject_is_optional_for_plain_captions(self):
        spec = self.spec()
        spec["foreground_asset"] = None
        spec["accents"][0]["behind_subject"] = False
        wt.validate(spec, 3)

    def test_video_cannot_borrow_duration_from_longer_audio(self):
        path = self.base / "short.mp4"
        path.write_bytes(b"Synthetic metadata fixture, not playable")
        asset = core.register_asset(self.folder, path, "Fixture", "Authored fixture", "Metadata test")
        info = {"streams": [{"codec_type": "video", "duration": "1"},
                            {"codec_type": "audio", "duration": "10"}], "format": {"duration": "10"}}
        with patch.object(wt.subprocess, "run", return_value=Mock(stdout=json.dumps(info).encode())):
            with self.assertRaisesRegex(ValueError, "full job duration"):
                wt.media(self.folder, asset["id"], "background", 3, 30)

    def test_webm_stream_duration_tag_is_supported(self):
        path = self.base / "matte.webm"
        path.write_bytes(b"Synthetic WebM metadata fixture")
        asset = core.register_asset(self.folder, path, "Fixture", "Authored fixture", "Metadata test")
        info = {"streams": [{"codec_type": "video", "width": 64, "height": 114,
                             "tags": {"DURATION": "00:00:03.000000000"}}]}
        with patch.object(wt.subprocess, "run", return_value=Mock(stdout=json.dumps(info).encode())):
            self.assertEqual(wt.media(self.folder, asset["id"], "foreground", 3, 30)["id"], asset["id"])

    def test_real_composition_copies_dependencies_and_preserves_existing_source(self):
        report = self.fixture()
        self.assertFalse(report["reviewed"])
        self.assertFalse(report["foreground_alpha_verified"])
        self.assertTrue((self.folder / "source/media/walk-talk-font-OFL.txt").is_file())
        target = self.folder / "source/index.html"
        original = target.read_bytes()
        with self.assertRaisesRegex(ValueError, "Composition exists"):
            wt.compose(self.folder)
        self.assertEqual(target.read_bytes(), original)

    def test_changed_asset_is_rejected_before_creating_composition(self):
        self.fixture()
        target = self.folder / "source/index.html"
        target.unlink()
        registry = core.read(self.folder / "assets.json")
        (self.folder / registry["items"][0]["path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Changed registered asset"):
            wt.compose(self.folder)
        self.assertFalse(target.exists())

    def test_text_is_escaped_and_cannot_rewrite_template_slots(self):
        self.fixture()
        target = self.folder / "source/index.html"
        target.unlink()
        spec = core.read(self.folder / "source/walk-talk.json")
        spec["captions"][0]["text"] = '</script><script>window.injected=true</script> @@ANIMATION@@'
        core.write(self.folder / "source/walk-talk.json", spec)
        wt.compose(self.folder)
        content = target.read_text(encoding="utf-8")
        self.assertNotIn('<script>window.injected', content)
        self.assertIn('&lt;script&gt;window.injected', content)
        self.assertIn('@@ANIMATION@@', content)

    def test_audio_replacement_mutes_both_visual_tracks(self):
        self.fixture()
        (self.folder / "source/index.html").unlink()
        spec = core.read(self.folder / "source/walk-talk.json")
        spec["audio_asset"] = "mix"
        core.write(self.folder / "source/walk-talk.json", spec)
        video = self.base / "base.mp4"
        audio = self.base / "mix.wav"
        video.write_bytes(b"Synthetic input")
        audio.write_bytes(b"Synthetic mix")
        loaded = {"background": {"path": video, "image": False, "stream": {"width": 64, "height": 114}, "has_audio": True},
                  "foreground": {"path": video, "image": False, "stream": {"width": 64, "height": 114}, "has_audio": False},
                  "audio": {"path": audio, "image": False, "stream": {}, "has_audio": True}}
        # Preserve the existing PNG dependencies; use distinct video destinations.
        with patch.object(wt, "media", side_effect=lambda folder, identity, role, *args: copy.deepcopy(loaded[role])):
            report = wt.compose(self.folder)
        content = (self.folder / "source/index.html").read_text(encoding="utf-8")
        self.assertEqual(content.count('muted data-volume="0"'), 2)
        self.assertEqual(content.count('<audio '), 1)
        self.assertEqual(report["audio"], "replacement-premix")

    def test_portable_installer_includes_all_references_and_preserves_user_edits(self):
        destination = self.base / "skills"
        report = install_skill.install(destination, name=wt.NAME, execute=True)
        self.assertEqual(report["status"], "installed")
        target = destination / wt.NAME
        self.assertEqual(install_skill.inventory(target), install_skill.inventory(ROOT / "skills" / wt.NAME))
        self.assertEqual(install_skill.install(destination, name=wt.NAME)["status"], "already-current")
        guide = target / "references/style-bible.md"
        guide.write_text("User revision", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "preserve"):
            install_skill.install(destination, name=wt.NAME, execute=True)
        self.assertEqual(guide.read_text(encoding="utf-8"), "User revision")

    def test_composition_seeks_deterministically_in_browser(self):
        self.fixture()
        if not shutil.which("node"):
            self.skipTest("Node required for browser test")
        probe = subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, capture_output=True)
        if probe.returncode:
            self.skipTest("Pinned Playwright unavailable")
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}/' + (self.folder / "source/index.html").relative_to(ROOT).as_posix()
            try:
                result = subprocess.run(["node", str(ROOT / "tests/walk_talk_pixels.cjs"), url], cwd=ROOT,
                                        capture_output=True, text=True, encoding="utf-8", timeout=60)
            except subprocess.TimeoutExpired as exc:
                self.fail("Browser check timed out: " + str(exc.stdout) + " " + str(exc.stderr))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
