import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import motion_catalog as catalog
import polish_check as polish
import studio_core as core

HAVE_CATALOG = catalog.INDEX.is_file()


def text(label, x0, y0, x1, y1, size=40, opacity=1.0, clipped=False):
    return {"text": label, "tag": "p", "x0": x0, "y0": y0, "x1": x1, "y1": y1, "size": size, "opacity": opacity, "clipped": clipped}


class JudgeTests(unittest.TestCase):
    def test_clean_layout_passes(self):
        errors, warnings = polish.judge([text("Tytul", 120, 300, 900, 380, 90), text("opis sceny w kilku slowach", 120, 400, 700, 440, 36)], "16:9", 1920, 1080)
        self.assertEqual((errors, warnings), ([], []))

    def test_flags_offscreen_small_overlap_and_emoji(self):
        items = [text("poza", 1800, 300, 2100, 340), text("mikro", 200, 300, 400, 320, size=12),
                 text("A", 300, 500, 700, 560), text("B", 320, 520, 720, 580), text("ok \U0001F680", 200, 700, 500, 740)]
        errors, _ = polish.judge(items, "16:9", 1920, 1080)
        joined = "\n".join(errors)
        for needle in ("poza kadrem", "Za mały", "Nakładające", "Emoji"):
            self.assertIn(needle, joined)

    def test_vertical_safe_area_warns_for_bottom_text(self):
        _, warnings = polish.judge([text("dol", 100, 1700, 900, 1760, 60), text("g", 100, 400, 800, 520, 120)], "9:16", 1080, 1920)
        self.assertTrue(any("bezpiecznym" in w for w in warnings))

    def test_invisible_text_is_ignored_and_empty_frame_fails(self):
        errors, _ = polish.judge([text("duch", 100, 100, 400, 160, opacity=0.0)], "16:9", 1920, 1080)
        self.assertTrue(any("Brak widocznego tekstu" in e for e in errors))


@unittest.skipUnless(HAVE_CATALOG, "brak tools/repos/awesome-ai-motion")
class CatalogTests(unittest.TestCase):
    def test_find_filters_and_ranks(self):
        result = catalog.find("reveal", purpose="attention", medium="shorts", rendered=True, limit=5)
        self.assertGreater(result["total_matches"], 0)
        self.assertTrue(all(e["rendered"] and "attention" in e["purposes"] for e in result["effects"]))
        self.assertLessEqual(len(result["effects"]), 5)

    def test_unknown_filter_and_slug_fail_clearly(self):
        with self.assertRaises(ValueError):
            catalog.find("x", purpose="bogus")
        with self.assertRaises(ValueError):
            catalog.show("nie-ma-takiego")
        with self.assertRaises(ValueError):
            catalog.recipe("nie-ma")

    def test_show_returns_usable_card(self):
        card = catalog.show("mask-reveal")
        self.assertEqual(card["ease"], "power3.out")
        self.assertTrue(Path(card["html_template"]).is_file())
        self.assertTrue(catalog.recipe("edu-hook")["steps"])

    def test_catalog_matches_published_counts(self):
        data = catalog.load()
        self.assertEqual(len(data["effects"]), data["counts"]["effects"])
        self.assertEqual(len(data["recipes"]), data["counts"]["recipes"])


class StarterTests(unittest.TestCase):
    @staticmethod
    def require_playwright(case):
        try:
            import playwright  # noqa: F401
        except ImportError:
            case.skipTest("Playwright niedostępny")

    def test_starter_passes_gate_in_every_format(self):
        self.require_playwright(self)
        starter = core.ROOT / "templates/frame-starter.html"
        for fmt in ("16:9", "9:16", "4:5", "1:1"):
            report = polish.check(starter, fmt, None, None, upstream=False)
            self.assertEqual(report["errors"], [], fmt)
            self.assertGreater(report["text_elements"], 5, fmt)

    def test_bad_page_is_rejected(self):
        self.require_playwright(self)
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            page = Path(folder) / "bad.html"
            page.write_text("<body style='margin:0;background:#fff'><p style='font-size:11px;position:absolute;left:1900px;top:50px'>"
                            "maly tekst \U0001F680</p></body>", encoding="utf-8")
            report = polish.check(page, "16:9", None, None, upstream=False)
            self.assertFalse(report["passed"])
            self.assertTrue(any("Emoji" in e for e in report["errors"]))


class RoutesTests(unittest.TestCase):
    def test_new_routes_point_to_existing_files(self):
        routes = core.routes()
        for key in ("polish", "motion"):
            self.assertIn(key, routes)
            for ref in routes[key]["skills"]:
                self.assertTrue(core.resolve_ref(ref).is_file(), ref)
        self.assertTrue((core.ROOT / "templates/frame-tokens.css").is_file())
        self.assertTrue((core.ROOT / "templates/motion-helpers.js").is_file())


if __name__ == "__main__":
    unittest.main()
