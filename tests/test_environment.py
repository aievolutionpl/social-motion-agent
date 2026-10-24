import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import environment
import studio_core as core


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        base = core.ROOT / "output/tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        core.write(self.root / "config/routes.json", {"routes": {"demo": {"skills": ["skills/demo.md"]}}})
        skill = self.root / "skills/demo.md"
        skill.parent.mkdir()
        skill.write_text("Synthetic test fixture", encoding="utf-8")
        core.write(self.root / "package.json", {"dependencies": {"hyperframes": "0.8.188", "gsap": "3.15.0"}})
        self.available = {"node", "npm", "ffmpeg", "ffprobe", "git"}
        self.versions = {"node": "v22.0.0", "npm": "10.9.2", "ffmpeg": "ffmpeg version 7.1",
                         "ffprobe": "ffprobe version 7.1"}
        self.commands = []
        self.npm_failure = None
        self.which = patch.object(environment.shutil, "which", side_effect=self.locate)
        self.run = patch.object(environment.subprocess, "run", side_effect=self.run_command)
        self.which.start()
        self.run.start()
        self.addCleanup(self.which.stop)
        self.addCleanup(self.run.stop)

    def locate(self, name):
        return str(self.root / "bin" / name) if name in self.available else None

    def install_fixture(self):
        for name, version, entry in (("hyperframes", "0.8.188", "bin/hyperframes.mjs"),
                                     ("gsap", "3.15.0", "dist/gsap.min.js")):
            folder = self.root / "node_modules" / name
            core.write(folder / "package.json", {"version": version})
            file = folder / entry
            file.parent.mkdir(parents=True)
            file.write_text("// synthetic fixture", encoding="utf-8")

    def run_command(self, command, **kwargs):
        self.commands.append(command)
        name = Path(command[0]).name
        if command[1:] in (["--version"], ["-version"]):
            return subprocess.CompletedProcess(command, 0, self.versions[name] + "\n", "")
        if name == "npm":
            if self.npm_failure == "timeout":
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])
            if self.npm_failure:
                return subprocess.CompletedProcess(command, self.npm_failure)
            self.install_fixture()
        return subprocess.CompletedProcess(command, 0)

    def test_missing_media_executable_prevents_readiness(self):
        self.install_fixture()
        for name in ("ffmpeg", "ffprobe"):
            with self.subTest(tool=name):
                self.available.remove(name)
                report = environment.inspect(self.root)
                self.assertFalse(report["ready"])
                self.assertFalse(report["local_assembly_ready"])
                self.assertTrue(any(name in issue for issue in report["issues"]))
                self.available.add(name)

    def test_version_boundaries_and_unrecognized_node_version(self):
        self.install_fixture()
        for version, expected in (("v21.99.0", False), ("v22.0.0", True),
                                  ("v24.1.0", True), ("unexpected output", False)):
            with self.subTest(node=version):
                self.versions["node"] = version
                self.assertEqual(environment.inspect(self.root)["ready"], expected)
        self.versions["node"] = "v22.0.0"
        for version, expected in (((3, 10, 19), False), ((3, 11, 0), True)):
            with self.subTest(python=version), patch.object(environment.sys, "version_info", version):
                self.assertEqual(environment.inspect(self.root)["ready"], expected)

    def test_uses_current_python_and_git_is_optional_for_demo(self):
        self.install_fixture()
        self.available.remove("git")
        report = environment.inspect(self.root)
        self.assertTrue(report["ready"])
        self.assertFalse(report["tools"]["git"])
        self.assertTrue(report["tools"]["python"])
        self.assertEqual(report["runtime_checks"]["python"]["path"], sys.executable)

    def test_missing_or_wrong_node_packages_are_actionable(self):
        report = environment.inspect(self.root)
        self.assertTrue(report["prerequisites_ready"])
        self.assertFalse(report["ready"])
        self.assertIn("setup", " ".join(report["next_steps"]))
        self.install_fixture()
        core.write(self.root / "node_modules/gsap/package.json", {"version": "0.0.0"})
        self.assertFalse(environment.inspect(self.root)["ready"])

    def test_setup_installs_locked_packages_without_library_by_default(self):
        report = environment.setup(self.root)
        self.assertTrue(report["ready"])
        self.assertTrue(report["setup"]["passed"])
        installs = [command for command in self.commands if "ci" in command]
        self.assertEqual(installs, [[self.locate("npm"), "ci", "--ignore-scripts"]])
        self.assertEqual([step["name"] for step in report["setup"]["steps"]], ["npm"])
        self.assertTrue((self.root / "output/system/setup.json").is_file())
        self.assertTrue((self.root / "output/system/setup-npm.log").is_file())

    def test_setup_requires_prerequisites_before_installing(self):
        self.available.remove("ffprobe")
        report = environment.setup(self.root)
        self.assertFalse(report["setup"]["passed"])
        self.assertEqual(report["setup"]["steps"], [])
        self.assertFalse(any("ci" in command for command in self.commands))

    def test_setup_failure_keeps_log_and_stops_before_library(self):
        for failure in (17, "timeout"):
            with self.subTest(failure=failure):
                self.npm_failure = failure
                report = environment.setup(self.root, with_library=True)
                self.assertFalse(report["ready"])
                self.assertFalse(report["setup"]["passed"])
                self.assertEqual(len(report["setup"]["steps"]), 1)
                self.assertIn("setup-npm.log", report["next"])
                self.assertTrue((self.root / report["setup"]["steps"][0]["log"]).is_file())

    def test_full_library_is_explicit_and_verified_after_bootstrap(self):
        report = environment.setup(self.root, with_library=True)
        self.assertTrue(report["setup"]["passed"])
        self.assertEqual([step["name"] for step in report["setup"]["steps"]],
                         ["npm", "library", "library-check"])
        self.assertEqual(report["setup"]["steps"][1]["command"],
                         [sys.executable, "-S", str(self.root / "scripts/bootstrap_library.py")])
        self.assertEqual(report["setup"]["steps"][2]["command"],
                         [sys.executable, "-S", str(self.root / "scripts/library_check.py")])

    def test_missing_git_blocks_requested_library_before_npm(self):
        self.available.remove("git")
        report = environment.setup(self.root, with_library=True)
        self.assertFalse(report["setup"]["passed"])
        self.assertEqual(report["setup"]["steps"], [])
        self.assertIn("Git", report["next"])

    def test_windows_npm_wrapper_uses_node_entry_point_without_shell(self):
        npm = self.root / "Node JS/npm.cmd"
        cli = npm.parent / "node_modules/npm/bin/npm-cli.js"
        cli.parent.mkdir(parents=True)
        cli.write_text("// synthetic fixture", encoding="utf-8")
        node = str(npm.parent / "node.exe")
        self.assertEqual(environment.npm_command(str(npm), node), [node, str(cli)])


class DoctorExitTests(unittest.TestCase):
    def test_cli_fails_when_runtime_is_missing_even_if_skills_exist(self):
        sys.path.insert(0, str(core.ROOT))
        import studio
        for ready in (False, True):
            with self.subTest(ready=ready), patch.object(studio, "doctor", return_value={"ready": ready, "missing_skill_paths": []}), \
                    patch.object(sys, "argv", ["studio.py", "doctor"]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(studio.main(), 0 if ready else 1)


if __name__ == "__main__":
    unittest.main()
