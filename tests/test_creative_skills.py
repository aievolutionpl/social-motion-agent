import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import creative_skills
import install_skill
import studio_core as core


class CreativeRoutingTests(unittest.TestCase):
    def test_plan_uses_small_pinned_selection_without_executing(self):
        with patch.object(creative_skills.subprocess, "run") as run:
            video = creative_skills.plan("video")
            website = creative_skills.plan("website")
        run.assert_not_called()
        self.assertIn("hypermotion", {s["id"] for s in video["sources"]})
        self.assertEqual({s["id"] for s in website["sources"]}, {"ai-design-skills", "taste-skill"})
        for report in (video, website):
            self.assertFalse(report["runtime_verified"])
            self.assertLessEqual(len(report["read_on_demand"]), 4)
            for entry in report["sources"]:
                self.assertRegex(entry["commit"], r"^[a-f0-9]{40}$")

    def test_setup_only_fetches_selected_sources_and_check_is_offline(self):
        fake = subprocess.CompletedProcess([], 0, "checked", "")
        with patch.object(creative_skills.subprocess, "run", return_value=fake) as run:
            creative_skills.prepare("website", check=True)
        command = run.call_args.args[0]
        self.assertIn("--check", command)
        self.assertEqual([command[i + 1] for i, arg in enumerate(command) if arg == "--only"],
                         ["ai-design-skills", "taste-skill"])
        self.assertNotIn("npm", command)

    def test_bootstrap_failure_never_reports_success(self):
        fake = subprocess.CompletedProcess([], 1, "", "modified checkout")
        with patch.object(creative_skills.subprocess, "run", return_value=fake):
            report = creative_skills.prepare("video")
        self.assertFalse(report["passed"])
        self.assertIn("modified checkout", report["error"])

    def test_unknown_mode_fails_without_side_effects(self):
        with self.assertRaises(ValueError):
            creative_skills.plan("publish")


class FullBundleRoutingTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = core.read(core.ROOT / "config/creative-skills.json")
        self.lock = core.read(core.ROOT / "sources.lock.json")
        core.write(self.root / "config/creative-skills.json", self.config)
        core.write(self.root / "sources.lock.json", self.lock)
        names = [self.config["entrypoint"], *self.config["modes"]["website"]["upstream"],
                 "skills/creative-director/references/guide.md", "tools/repos/taste-skill/LICENSE"]
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic archive fixture", encoding="utf-8")
        self.manifest = {"schema_version": 1, "sources": self.lock["sources"], "files": [
            {"path": file.relative_to(self.root).as_posix(), "bytes": file.stat().st_size, "sha256": core.sha(file)}
            for file in self.root.rglob("*") if file.is_file()]}
        core.write(self.root / "bundle-manifest.json", self.manifest)

    def prepare_without_git(self, *, check=False):
        with patch.object(creative_skills.subprocess, "run", side_effect=AssertionError("Bundle must not invoke Git or fetch")):
            return creative_skills.prepare("website", check=check, root=self.root)

    def test_full_bundle_setup_and_check_work_without_git_or_runtime_claim(self):
        for check in (False, True):
            with self.subTest(check=check):
                report = self.prepare_without_git(check=check)
                self.assertTrue(report["passed"], report["error"])
                self.assertEqual(report["source_distribution"], "full-bundle")
                self.assertEqual(report["bundle_files_checked"], len(self.manifest["files"]))
                self.assertTrue(report["source_setup_only"])
                self.assertFalse(report["runtime_verified"])

    def test_bundle_commit_mismatch_fails_without_overwriting_or_fetching(self):
        source = next(s for s in self.manifest["sources"] if s["id"] == "taste-skill")
        source["commit"] = "0" * 40
        core.write(self.root / "bundle-manifest.json", self.manifest)
        before = (self.root / "bundle-manifest.json").read_bytes()
        report = self.prepare_without_git()
        self.assertFalse(report["passed"])
        self.assertIn("does not match sources.lock.json: taste-skill", report["error"])
        self.assertEqual((self.root / "bundle-manifest.json").read_bytes(), before)

    def test_changed_selected_file_is_rejected_even_outside_entrypoints(self):
        path = self.root / "tools/repos/taste-skill/LICENSE"
        original = path.read_bytes()
        for changed in (b"x" * len(original), original + b"user change"):
            with self.subTest(bytes=len(changed)):
                path.write_bytes(changed)
                report = self.prepare_without_git()
                self.assertFalse(report["passed"])
                self.assertIn("Bundle file changed: tools/repos/taste-skill/LICENSE", report["error"])
                self.assertEqual(path.read_bytes(), changed)

    def test_present_but_unlisted_entrypoint_is_not_trusted(self):
        missing = self.config["modes"]["website"]["upstream"][0]
        self.manifest["files"] = [f for f in self.manifest["files"] if f["path"] != missing]
        core.write(self.root / "bundle-manifest.json", self.manifest)
        report = self.prepare_without_git(check=True)
        self.assertTrue(report["files_present"])
        self.assertFalse(report["passed"])
        self.assertIn("Required file missing from bundle manifest: " + missing, report["error"])

    def test_unsafe_or_invalid_manifest_fails_without_bootstrap(self):
        for content in ("{", json.dumps({**self.manifest, "files": [
                {"path": "tools/repos/taste-skill/../../../outside", "bytes": 1, "sha256": "0" * 64}]})):
            with self.subTest(content=content[:20]):
                (self.root / "bundle-manifest.json").write_text(content, encoding="utf-8")
                report = self.prepare_without_git()
                self.assertFalse(report["passed"])
                self.assertIn("Invalid full-bundle manifest", report["error"])

    def test_source_zip_without_manifest_uses_normal_bootstrap(self):
        (self.root / "bundle-manifest.json").unlink()
        result = subprocess.CompletedProcess([], 0, "selected pinned sources ready", "")
        with patch.object(creative_skills.subprocess, "run", return_value=result) as run:
            report = creative_skills.prepare("website", root=self.root)
        self.assertTrue(report["passed"])
        command = run.call_args.args[0]
        self.assertEqual(command[2], str(self.root / "scripts/bootstrap_library.py"))
        self.assertEqual([command[i + 1] for i, value in enumerate(command) if value == "--only"],
                         ["ai-design-skills", "taste-skill"])


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        (self.source / "references").mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: creative-director\ndescription: Design films\n---\n", encoding="utf-8")
        (self.source / "references/guide.md").write_text("Reusable guide", encoding="utf-8")
        self.destination = self.root / "profile/skills"

    def test_dry_run_does_not_create_profile(self):
        report = install_skill.install(self.destination, source=self.source)
        self.assertEqual(report["status"], "planned")
        self.assertFalse(self.destination.exists())

    def test_install_is_complete_idempotent_and_preserves_user_edits(self):
        report = install_skill.install(self.destination, execute=True, source=self.source)
        target = self.destination / "creative-director"
        self.assertEqual(report["status"], "installed")
        self.assertEqual(install_skill.inventory(target), install_skill.inventory(self.source))
        self.assertEqual(install_skill.install(self.destination, execute=True, source=self.source)["status"], "already-current")
        (target / "references/guide.md").write_text("user content", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "preserve"):
            install_skill.install(self.destination, execute=True, source=self.source)
        self.assertEqual((target / "references/guide.md").read_text(encoding="utf-8"), "user content")

    def test_active_profile_environment_is_respected(self):
        for agent, variable in (("codex", "CODEX_HOME"), ("claude", "CLAUDE_CONFIG_DIR"), ("hermes", "HERMES_HOME")):
            with patch.dict(os.environ, {variable: str(self.root / agent)}):
                self.assertEqual(install_skill.default_destination(agent), self.root / agent / "skills")

    def test_failed_staging_does_not_expose_partial_skill(self):
        with patch.object(install_skill.shutil, "copytree", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                install_skill.install(self.destination, execute=True, source=self.source)
        self.assertFalse((self.destination / "creative-director").exists())
        self.assertEqual(list(self.destination.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
