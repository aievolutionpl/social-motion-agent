import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import edit_bridge
import fx
import studio_core as core


class EffectSpecTests(unittest.TestCase):
    def test_rejects_unknown_effect_and_parameters(self):
        with self.assertRaises(fx.FxError):
            fx.normalize({"type": "explode"}, 5)
        with self.assertRaises(fx.FxError):
            fx.normalize({"type": "grade", "preset": "punchy", "amount": 1}, 5)

    def test_requires_window_inside_clip(self):
        with self.assertRaises(fx.FxError):
            fx.normalize({"type": "punch_in", "start": 1}, 5)
        with self.assertRaises(fx.FxError):
            fx.normalize({"type": "glitch", "start": 4, "end": 9}, 5)
        with self.assertRaises(fx.FxError):
            fx.normalize({"type": "glitch", "start": 3, "end": 2}, 5)

    def test_rejects_non_numeric_and_out_of_range(self):
        for bad in ({"type": "punch_in", "start": "a", "end": 2}, {"type": "punch_in", "start": 0, "end": 2, "zoom": 9},
                    {"type": "speed_ramp", "start": 0, "end": 1, "factor": 0.01},
                    {"type": "grade", "preset": "neon"}, {"type": "flash", "start": 1, "alpha": "nan"}):
            with self.assertRaises(fx.FxError, msg=bad):
                fx.normalize(bad, 5)

    def test_ramp_segments_cover_clip_and_reject_overlap(self):
        ramps = [fx.normalize({"type": "speed_ramp", "start": 1, "end": 3, "factor": 0.5}, 6)]
        segments = fx.ramp_segments(ramps, 6)
        self.assertEqual(segments, [(0.0, 1, 1.0), (1, 3, 0.5), (3, 6, 1.0)])
        self.assertAlmostEqual(sum((b - a) / f for a, b, f in segments), 8.0)
        overlap = ramps + [fx.normalize({"type": "speed_ramp", "start": 2, "end": 4, "factor": 2}, 6)]
        with self.assertRaises(fx.FxError):
            fx.ramp_segments(overlap, 6)

    def test_inline_syntax(self):
        self.assertEqual(fx.parse_inline("punch_in:start=1,end=2.2,zoom=1.3"),
                         {"type": "punch_in", "start": "1", "end": "2.2", "zoom": "1.3"})
        with self.assertRaises(fx.FxError):
            fx.parse_inline("glitch:start")


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=base)
        cls.base = Path(cls.temp.name).resolve()
        cls.src = cls.base / "src.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=2",
                        "-f", "lavfi", "-i", "sine=f=440:d=2", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-shortest", str(cls.src)], check=True, timeout=120)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_full_chain_keeps_size_audio_and_expected_duration(self):
        out = self.base / "chain.mp4"
        effects = [{"type": "grade", "preset": "warm"}, {"type": "vignette"},
                   {"type": "punch_in", "start": 0.2, "end": 1.0, "zoom": 1.25}, {"type": "shake", "start": 1.0, "end": 1.4},
                   {"type": "glitch", "start": 1.4, "end": 1.6}, {"type": "flash", "start": 1.7},
                   {"type": "fade", "in": 0.2, "out": 0.2}]
        report = fx.apply(self.src, out, effects)
        meta = fx.probe(out)
        self.assertEqual((meta["width"], meta["height"]), (1080, 1920))
        self.assertTrue(meta["has_audio"])
        self.assertAlmostEqual(meta["duration"], report["expected_duration_sec"], delta=0.15)

    def test_speed_ramp_changes_duration_and_keeps_audio(self):
        out = self.base / "ramp.mp4"
        report = fx.apply(self.src, out, [{"type": "speed_ramp", "start": 0.5, "end": 1.5, "factor": 0.5}])
        self.assertAlmostEqual(report["expected_duration_sec"], 3.0)
        meta = fx.probe(out)
        self.assertAlmostEqual(meta["duration"], 3.0, delta=0.2)
        self.assertTrue(meta["has_audio"])

    def test_refuses_to_overwrite_existing_render(self):
        out = self.base / "exists.mp4"
        out.write_bytes(b"x")
        with self.assertRaises(fx.FxError):
            fx.apply(self.src, out, [{"type": "grade"}])

    def test_bridge_registers_probe_and_log(self):
        folder = core.create_job("fx bridge", "shorts", "9:16", 2, "pl", self.base)
        asset = core.register_asset(folder, self.src, "synthetic fixture", "test only", "bridge test")
        (folder / "source/effects.json").write_text(json.dumps({"effects": [{"type": "grade", "preset": "cool"}]}), encoding="utf-8")
        result = edit_bridge.edit(folder, "fx", [asset["id"]], "fx-v1", spec="source/effects.json")
        self.assertTrue(result["probe_passed"], result["probe_failures"])
        self.assertTrue((folder / "renders/fx-v1.mp4").is_file())
        log = core.read(folder / "notes/edit-fx-v1.json")
        self.assertEqual(log["render_sha256"], core.sha(folder / "renders/fx-v1.mp4"))
        with self.assertRaises(ValueError):
            edit_bridge.edit(folder, "fx", [asset["id"]], "fx-v1", spec="source/effects.json")
        with self.assertRaises(ValueError):
            edit_bridge.edit(folder, "fx", ["a-missing"], "fx-v2", spec="source/effects.json")
        with self.assertRaises(ValueError):
            edit_bridge.edit(folder, "fx", [asset["id"]], "../escape", spec="source/effects.json")
        with self.assertRaises(ValueError):
            edit_bridge.edit(folder, "fx", [asset["id"]], "fx-v3", spec="../../escape.json")


if __name__ == "__main__":
    unittest.main()
