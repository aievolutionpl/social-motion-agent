import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import polish_check as polish
import studio_core as core
import style_atlas
import unslop_story


class StyleAtlasTests(unittest.TestCase):
    def test_list_styles_returns_all_twelve_canonical_styles(self):
        report = style_atlas.list_styles()
        self.assertEqual(report["total_styles"], 12)
        slugs = {item["slug"] for item in report["styles"]}
        self.assertEqual(
            slugs,
            {
                "typography",
                "productui",
                "cinematic3d",
                "explainer",
                "generative",
                "handdrawn",
                "cartoon",
                "collage",
                "lowpoly",
                "photoreal",
                "pixel",
                "retro",
            },
        )
        self.assertIn("subagent_blueprint", report)
        self.assertEqual(len(report["attributions"]), 3)

    def test_recipe_returns_tokens_contract_and_subagent_blueprint(self):
        for slug in style_atlas.STYLES:
            with self.subTest(slug=slug):
                rec = style_atlas.recipe(slug)
                self.assertEqual(rec["slug"], slug)
                self.assertTrue(rec["style_recipe"])
                self.assertIn("--bg-0", rec["tokens"])
                self.assertIn("build_contract", rec)
                sections = rec["subagent_blueprint"]["prompt_to_code_sections"]
                self.assertIn("inputs", sections)
                self.assertIn("gotchas", sections)
        all_recipes = style_atlas.recipe()
        self.assertEqual(len(all_recipes["styles"]), 12)
        with self.assertRaises(ValueError):
            style_atlas.recipe("unknown-style")

    def test_find_and_show_work_with_offline_fallback_and_filters(self):
        found = style_atlas.find("spring", style="productui", limit=5)
        self.assertGreaterEqual(found["total_matches"], 1)
        first_slug = found["results"][0]["slug"]
        shown = style_atlas.show(first_slug, remake=True)
        self.assertEqual(shown["slug"], first_slug)
        self.assertIn("subagent_blueprint", shown)
        for tag in ("inputs", "direction", "structure", "build", "gotchas"):
            self.assertIn(tag, shown["subagent_blueprint"]["prompt_to_code_sections"])

    def test_find_and_show_reject_invalid_filters_and_unknown_ids(self):
        with self.assertRaises(ValueError):
            style_atlas.find("ui", style="not-a-style")
        with self.assertRaises(ValueError):
            style_atlas.find("ui", category="not-a-category")
        with self.assertRaises(ValueError):
            style_atlas.find("ui", tech="flash-player")
        with self.assertRaises(ValueError):
            style_atlas.show("missing:999")

    def test_live_upstream_parsing_combines_markdown_and_json_sources(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            root = Path(folder)
            styles_dir = root / "styles"
            styles_dir.mkdir(parents=True)
            (styles_dir / "typography.md").write_text(
                '<a id="c1"></a>\n'
                "### 1. Spring Baseline Lockup\n"
                "Author: @tester · Remake: [skillry.dev](https://skillry.dev/test)\n\n"
                "```text\n"
                "Create a 60fps HTML/CSS kinetic typography title card with spring physics.\n"
                "```\n",
                encoding="utf-8",
            )
            videos_json = root / "videos.json"
            videos_json.write_text(
                json.dumps(
                    [
                        {
                            "slug": "saas-launch-42",
                            "author": "@tester",
                            "category": "motion",
                            "tech_tags": ["css", "svg"],
                            "has_remake": True,
                            "prompt": "Build an interactive SaaS dashboard launch animation in HTML and CSS.",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            style_atlas._load_style_markdown_entries.cache_clear()
            style_atlas._load_videos_json.cache_clear()
            try:
                with patch.object(style_atlas, "STYLES_REPO", root), patch.object(style_atlas, "VIDEOS_JSON", videos_json):
                    found = style_atlas.find("SaaS", limit=10)
                    self.assertGreaterEqual(found["total_matches"], 1)
                    card = style_atlas.show("saas-launch-42", remake=True)
                    self.assertEqual(card["style"], "productui")
                    md_card = style_atlas.show("typography-c1", remake=True)
                    self.assertEqual(md_card["style"], "typography")
                    self.assertTrue(md_card["has_remake"])
            finally:
                style_atlas._load_style_markdown_entries.cache_clear()
                style_atlas._load_videos_json.cache_clear()


class UnslopStoryTests(unittest.TestCase):
    def test_write_story_creates_valid_deterministic_html_and_preserves_existing(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            target = Path(folder) / "story.html"
            result = unslop_story.write_story(target, title="Audit Demo", ramp="graphite", duration=12.0)
            self.assertTrue(target.is_file())
            self.assertEqual(result["passes"], ["Spacing", "Color and icons", "Type and copy", "Details"])
            content = target.read_text(encoding="utf-8")
            self.assertIn("window.DURATION = 12.00;", content)
            self.assertIn("window.seek =", content)
            self.assertIn("@heydamir", content)
            with self.assertRaises(ValueError):
                unslop_story.write_story(target, title="Overwrite Attempt")

    def test_write_story_rejects_unsafe_paths_and_invalid_parameters(self):
        with self.assertRaises(ValueError):
            unslop_story.write_story(Path("../../outside.html"))
        with self.assertRaises(ValueError):
            unslop_story.write_story(core.ROOT / "output/tests/bad-ramp.html", ramp="neon")
        with self.assertRaises(ValueError):
            unslop_story.write_story(core.ROOT / "output/tests/bad-dur.html", duration=2.0)

    def test_generated_story_passes_polish_check_across_passes(self):
        try:
            import playwright  # noqa: F401
        except ImportError:
            self.skipTest("Playwright niedostępny")
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            target = Path(folder) / "story.html"
            unslop_story.write_story(target, title="Audit Story", ramp="graphite", duration=12.0)
            for seek_t in (0.8, 3.0, 7.5, 11.2):
                report = polish.check(target, "16:9", seek_t, None, upstream=False)
                self.assertEqual(report["errors"], [], f"seek={seek_t}: {report['errors']}")


if __name__ == "__main__":
    unittest.main()
