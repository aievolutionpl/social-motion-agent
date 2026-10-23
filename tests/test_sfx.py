import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import backgrounds_catalog
import bg_video
import fx
import sfx_catalog as sfx
import studio_core as core

HAVE_SFX = sfx.INDEX.is_file()


class ClassifyTests(unittest.TestCase):
    def test_categories_from_names(self):
        cases = {"Cinematic Impact.WAV": "impact", "Punch Stop Riser.WAV": "riser", "Whoosh Cinematic.mp3": "transition",
                 "Camera Shutter.WAV": "camera", "Keyboard Typing.mp3": "typing", "click-3.mp3": "ui", "KeyGet.wav": "ui",
                 "Glitch 2.mp3": "glitch-tech", "Rain loud.wav": "ambience", "fart.mp3": "meme", "Glass break 01.wav": "foley",
                 "zzz unknown.wav": "other"}
        for name, expected in cases.items():
            self.assertEqual(sfx.classify(name)[0], expected, name)

    def test_gain_cap_is_half(self):
        self.assertEqual(sfx.GAIN_CAP, 0.5)
        self.assertEqual(fx.SFX_GAIN_CAP, 0.5)
        self.assertTrue(all(g <= 0.5 for g in sfx.BASE_GAIN.values()))


@unittest.skipUnless(HAVE_SFX, "brak SOUND EFFECTS/index.json")
class IndexTests(unittest.TestCase):
    def test_index_is_complete_and_consistent(self):
        self.assertEqual(sfx.check(), [], "uruchom: python -S scripts/sfx_catalog.py build")
        sounds = sfx.load()["sounds"]
        ids = [s["id"] for s in sounds]
        self.assertEqual(len(ids), len(set(ids)), "id muszą być unikalne")
        self.assertTrue(all(0 < s["default_gain"] <= 0.5 for s in sounds))
        self.assertTrue(all((sfx.FOLDER / s["file"]).is_file() for s in sounds))
        for s in sounds:
            if s.get("duplicate_of"):
                self.assertIn(s["duplicate_of"], ids)

    def test_agent_entry_files_exist(self):
        for name in ("README.md", "INDEX.md", "CLAUDE.md", "AGENTS.md", "index.json"):
            self.assertTrue((sfx.FOLDER / name).is_file(), name)
        self.assertIn("100%", (sfx.FOLDER / "README.md").read_text(encoding="utf-8"))

    def test_find_and_resolve(self):
        found = sfx.find("whoosh", category="transition", max_duration=3)
        self.assertGreater(found["total_matches"], 0)
        self.assertTrue(all(s["duration_sec"] <= 3 and not s.get("duplicate_of") for s in found["sounds"]))
        path, gain = sfx.resolve(found["sounds"][0]["id"])
        self.assertTrue(path.is_file())
        self.assertLessEqual(gain, 0.5)
        with self.assertRaises(ValueError):
            sfx.resolve("nie-ma-takiego-dzwieku")


@unittest.skipUnless(HAVE_SFX, "brak SOUND EFFECTS/index.json")
class MixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=base)
        cls.base = Path(cls.temp.name).resolve()
        cls.quiet = cls.base / "quiet.mp4"
        cls.silent = cls.base / "silent.mp4"
        common = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=540x960:r=30:d=3"]
        subprocess.run(common + ["-f", "lavfi", "-i", "sine=f=300:d=3", "-af", "volume=0.05", "-c:v", "libx264", "-preset", "ultrafast",
                                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.quiet)], check=True, timeout=120)
        subprocess.run(common + ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(cls.silent)], check=True, timeout=120)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def max_volume(path: Path) -> float:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                             capture_output=True, text=True, timeout=120)
        return float(out.stderr.split("max_volume:")[1].split("dB")[0])

    def test_sfx_is_mixed_into_existing_audio_with_same_duration(self):
        out = self.base / "mixed.mp4"
        fx.apply(self.quiet, out, [{"type": "sfx", "file": "cinematic-impact", "start": 1.0}])
        meta = fx.probe(out)
        self.assertTrue(meta["has_audio"])
        self.assertAlmostEqual(meta["duration"], 3.0, delta=0.15)
        self.assertGreater(self.max_volume(out), self.max_volume(self.quiet) + 10)

    def test_silent_source_gets_audio_track(self):
        out = self.base / "silent-out.mp4"
        fx.apply(self.silent, out, [{"type": "sfx", "file": "click-1", "start": 0.5}])
        self.assertTrue(fx.probe(out)["has_audio"])

    def test_gain_above_cap_and_bad_input_are_rejected(self):
        for bad in ({"type": "sfx", "file": "click-1", "start": 1, "gain": 0.8},
                    {"type": "sfx", "file": "click-1", "start": 1, "gain": 1.0},
                    {"type": "sfx", "start": 1},
                    {"type": "sfx", "file": "  ", "start": 1}):
            with self.assertRaises(fx.FxError, msg=bad):
                fx.normalize(bad, 3)
        with self.assertRaises(fx.FxError):
            fx.apply(self.quiet, self.base / "x.mp4", [{"type": "sfx", "file": "nie-ma", "start": 1}])

    def test_background_video_has_requested_format(self):
        image = core.ROOT / "assets/backgrounds/bg-02-navy-glow.webp"
        if not image.is_file():
            self.skipTest("brak tła testowego")
        out = self.base / "bg.mp4"
        bg_video.render(image, out, 1.0, "9:16", "push")
        meta = fx.probe(out)
        self.assertEqual((meta["width"], meta["height"]), (1080, 1920))
        self.assertAlmostEqual(meta["duration"], 1.0, delta=0.1)
        for bad in ({"duration": 0.1}, {"duration": 2000}, {"duration": 1, "amount": 0.9}):
            with self.assertRaises(ValueError, msg=bad):
                bg_video.render(image, self.base / "bad.mp4", **bad)
        with self.assertRaises(ValueError):
            bg_video.render(image, out, 1.0)


@unittest.skipUnless(backgrounds_catalog.INDEX.is_file(), "optional background library is not bundled")
class BackgroundsTests(unittest.TestCase):
    def test_index_and_entry_files(self):
        self.assertEqual(backgrounds_catalog.check(), [], "uruchom: python -I scripts/backgrounds_catalog.py build")
        for name in ("README.md", "INDEX.md", "CLAUDE.md", "AGENTS.md", "index.json"):
            self.assertTrue((backgrounds_catalog.FOLDER / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
