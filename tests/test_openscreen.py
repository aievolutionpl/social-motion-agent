import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import openscreen


class CaptureAdapterTests(unittest.TestCase):
    def test_ambiguous_and_missing_windows_never_select_desktop(self):
        available={"windows":[{"name":"Demo - one"},{"name":"Demo - two"}],"displays":[{"name":"Desktop"}]}
        for selector in ("demo","missing"):
            with self.assertRaises(ValueError):
                openscreen.require_window(available,selector)
        self.assertEqual(openscreen.require_window(available,"DEMO - ONE")["name"],"Demo - one")

    def test_empty_or_failed_event_stream_is_not_completion(self):
        for stream in ([],[{"event":"done","success":False}],[{"event":"progress","percentage":100}]):
            with self.assertRaises(RuntimeError):
                openscreen.done(stream)

    def test_mixed_logs_keep_actual_completion(self):
        parsed=openscreen.events('diagnostic\n{"event":"progress","percentage":50}\n{"event":"done","success":true,"outputPath":"demo.mp4"}\n')
        self.assertEqual(openscreen.done(parsed)["outputPath"],"demo.mp4")

    def test_existing_output_is_preserved(self):
        base=openscreen.ROOT/"output/system/openscreen/test-temp"
        base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(base.resolve()))
            path=Path(folder)/"take.openscreen";path.write_text("original",encoding="utf-8")
            with self.assertRaises(FileExistsError):
                openscreen.output_path(path)
            self.assertEqual(path.read_text(encoding="utf-8"),"original")

    def test_error_event_fails_even_when_process_exit_is_zero(self):
        result=subprocess.CompletedProcess([],0,'{"event":"error","message":"capture failed"}\n','')
        with patch.object(openscreen,"executable",return_value=Path("test.exe")),patch.object(openscreen.subprocess,"run",return_value=result):
            with self.assertRaises(RuntimeError):
                openscreen.invoke(["record"])


if __name__=="__main__":
    unittest.main()
