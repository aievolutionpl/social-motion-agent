"""Offline regression tests for the curated ShotCraft pack."""
from __future__ import annotations

import functools
import http.server
import json
import shutil
import subprocess
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shotcraft_pack


class ShotCraftTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-S", str(ROOT / "studio.py"), "shotcraft", *map(str, args)],
            cwd=ROOT, text=True, capture_output=True, encoding="utf-8")

    def test_registry_references_and_preview_contract(self):
        report = shotcraft_pack.validate()
        self.assertTrue(report["passed"])
        self.assertEqual(report["shot_count"], 10)
        self.assertEqual(report["browser_previews"], 5)
        self.assertEqual(report["sequence_count"], 4)
        available = {s["id"] for s in shotcraft_pack.list_shots()["shots"]}
        for id_ in ("carousel-3d", "card-flock-tumble", "flying-words",
                    "before-after-slider-scrub", "value-stagger-gradient"):
            self.assertIn(id_, available)
            self.assertTrue(shotcraft_pack.show(id_)["preview"])
        gallery = (ROOT / "examples/shotcraft-motion/index.html").read_text(encoding="utf-8")
        for id_ in available:
            if shotcraft_pack.show(id_)["preview"]:
                self.assertIn('"' + id_ + '":', gallery)

    def test_frame_accurate_plans(self):
        for sequence in ("product-reel", "app-launch", "education-explainer", "kinetic-teaser"):
            for fps in (24, 25, 30, 50, 60):
                plan = shotcraft_pack.plan(sequence, 15, fps, "Test Brand", "Visit")
                self.assertEqual(plan["total_frames"], 15 * fps)
                self.assertEqual(plan["shots"][0]["start_frame"], 0)
                self.assertEqual(plan["shots"][-1]["end_frame_exclusive"], plan["total_frames"])
                for a, b in zip(plan["shots"], plan["shots"][1:]):
                    self.assertEqual(a["end_frame_exclusive"], b["start_frame"])
                for shot in plan["shots"]:
                    self.assertGreater(shot["duration_frames"], 0)
                self.assertEqual(plan, shotcraft_pack.plan(sequence, 15, fps, "Test Brand", "Visit"))

    def test_explicit_missing_assets_and_invalid_requests(self):
        report = shotcraft_pack.plan("product-reel")
        self.assertTrue(any("verified data" in x for x in report["needs_confirmation_or_assets"]))
        self.assertTrue(any("brand" in x for x in report["needs_confirmation_or_assets"]))
        app = shotcraft_pack.plan("app-launch")
        self.assertTrue(any("anonymized" in x for x in app["needs_confirmation_or_assets"]))
        for args in (("missing",), ("product-reel", 3), ("product-reel", 15, 17)):
            with self.assertRaises(ValueError):
                shotcraft_pack.plan(*args)

    def test_cli(self):
        for args in (("list",), ("show", "carousel-3d"), ("validate",),
                     ("plan", "product-reel", "--duration", "15", "--fps", "30",
                      "--brand", "Example", "--cta", "Visit")):
            result = self.cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout))
        self.assertNotEqual(self.cli("plan", "not-a-sequence").returncode, 0)
        self.assertNotEqual(self.cli("show", "not-an-effect").returncode, 0)

    def test_hyperframes_film_lint_optional(self):
        cli = ROOT / "node_modules/hyperframes/bin/hyperframes.mjs"
        if not shutil.which("node") or not cli.is_file():
            self.skipTest("HyperFrames runtime is not installed")
        prepare = subprocess.run(["node", str(ROOT / "scripts/prepare-example.mjs")],
                                 cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(prepare.returncode, 0, prepare.stdout + "\n" + prepare.stderr)
        result = subprocess.run(["node", str(cli), "lint", str(ROOT / "examples/shotcraft-motion/film")],
                                cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)

    def test_gallery_pixels_optional(self):
        if not shutil.which("node"):
            self.skipTest("Node is not installed")
        if subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, capture_output=True).returncode:
            self.skipTest("Playwright is not installed")
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/examples/shotcraft-motion/"
            result = subprocess.run(["node", str(ROOT / "tests/shotcraft_pixels.cjs"), url],
                                    cwd=ROOT, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
