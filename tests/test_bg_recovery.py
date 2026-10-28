import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bg_video


class BackgroundRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(__file__).resolve().parents[1] / "output/tests/bg-recovery"
        self.base.mkdir(parents=True, exist_ok=True)

    def test_timeout_removes_partial_output_and_allows_retry(self):
        with tempfile.TemporaryDirectory(dir=self.base) as directory:
            image = Path(directory) / "input.png"
            image.write_bytes(b"fixture")
            output = Path(directory) / "background.mp4"

            def timed_out(*args, **kwargs):
                output.write_bytes(b"unfinished video")
                raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

            with patch.object(bg_video.subprocess, "run", side_effect=timed_out):
                with self.assertRaises(subprocess.TimeoutExpired):
                    bg_video.render(image, output, 1.0)
            self.assertFalse(output.exists())

            def succeeded(*args, **kwargs):
                output.write_bytes(b"finished video")
                return subprocess.CompletedProcess(args[0], 0, "", "")

            with patch.object(bg_video.subprocess, "run", side_effect=succeeded) as process:
                result = bg_video.render(image, output, 1.0)
            process.assert_called_once()
            self.assertEqual(result["output"], str(output))
            self.assertEqual(output.read_bytes(), b"finished video")

    def test_existing_output_is_preserved_without_launching_ffmpeg(self):
        with tempfile.TemporaryDirectory(dir=self.base) as directory:
            image = Path(directory) / "input.png"
            image.write_bytes(b"fixture")
            output = Path(directory) / "background.mp4"
            output.write_bytes(b"original video")
            with patch.object(bg_video.subprocess, "run") as process:
                with self.assertRaises(ValueError):
                    bg_video.render(image, output, 1.0)
            process.assert_not_called()
            self.assertEqual(output.read_bytes(), b"original video")


if __name__ == "__main__":
    unittest.main()
