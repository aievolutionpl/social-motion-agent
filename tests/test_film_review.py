import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import assembly
import editor_workspace as editor
import film_plan
import film_review_server
import film_variants
import footage_selects
import shotcraft_compose
import studio_core as core
import style_feedback


class FilmWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.job = core.create_job("Rolka <test>", "shorts", "16:9", 4, "pl", self.base / "jobs", style_profile="tester")
        job = core.read(self.job / "job.json")
        job.update(width=192, height=108, fps=15)
        core.write(self.job / "job.json", job)

    def footage(self):
        path = self.base / "take.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=192x108:r=15",
                        "-f", "lavfi", "-i", "sine=frequency=370:sample_rate=48000",
                        "-af", "volume=0:enable='gte(t,2)'", "-t", "4", "-c:v", "libx264", "-threads", "1",
                        "-c:a", "aac", str(path)], check=True)
        return core.register_asset(self.job, path, "synthetic", "test", "review")

    def test_brief_and_real_source_selects(self):
        plan = film_plan.plan("20-sekundowa rolka z idącym prezenterem i tekstem za sylwetką")
        self.assertEqual(plan["route"], "kinetic-walk-talk")
        self.assertEqual(plan["format"], "9:16")
        self.assertTrue(any("Maska" in gap for gap in plan["missing"]))
        self.assertIn("--duration", plan["next_commands"][0])
        asset = self.footage()
        rows = [{"text": text, "start": i, "end": i + .8}
                for i, text in enumerate(("Co to jest?", "Cena to 20 złotych.", "Przykład."))]
        core.write(self.job / "notes/decode.json", {"segments": rows})
        footage_selects.index(self.job, asset["id"], transcript="notes/decode.json")
        choice = footage_selects.shortlist(self.job, "cena")["candidates"][0]
        self.assertEqual((choice["quote"],choice["clip"]["in_sec"]), ("Cena to 20 złotych.", 1))
        result = film_variants.render_set(self.job, openings=True, query="cena")
        _, manifest = style_feedback.collection(self.job, result["collection"])
        self.assertEqual(len(manifest["variants"]), 3)
        self.assertEqual(manifest["variants"][0]["source"]["start"], 1)
        self.assertTrue(all(v["duration"] <= 3.15 for v in manifest["variants"]))

    def test_three_full_films_and_shared_ratings(self):
        asset = self.footage()
        master = self.job / "renders/test.mp4"
        shutil.copyfile(self.job / asset["path"], master)
        core.record_render(self.job, "renders/test.mp4", core.fingerprint(self.job), "test-fixture")
        batch = film_variants.after_render(self.job, {"render":"renders/test.mp4", "probe_passed":True})["variants"]
        self.assertEqual(film_variants.render_set(self.job,"renders/test.mp4")["collection"], batch["collection"])
        directory, manifest = style_feedback.collection(self.job, batch["collection"])
        page = (directory / "index.html").read_text(encoding="utf-8")
        self.assertIn("Rolka &lt;test&gt;", page)
        self.assertNotIn("/*FILMS*/", page)
        frames = []
        for variant in manifest["variants"]:
            path = directory / variant["file"]
            streams = editor.probe(path)["streams"]
            self.assertTrue(any(s["codec_type"] == "audio" for s in streams))
            frame = subprocess.check_output(["ffmpeg","-v","error","-ss","1","-i",str(path),"-frames:v","1",
                                             "-f","rawvideo","-pix_fmt","rgb24","-threads","1","-"])
            frames.append(hashlib.sha256(frame).digest())
            self.assertAlmostEqual(variant["duration"], 4, places=1)
        self.assertEqual(len(set(frames)), 3)
        item = next(v for v in manifest["variants"] if v["style"] == "studio")
        vote = {"style":"studio", "sha256":item["sha256"], "stars":5}
        with film_review_server.make_server(self.job, batch["collection"]) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}"
                with urlopen(Request(url + "/studio.mp4", headers={"Range":"bytes=0-15"})) as response:
                    self.assertEqual((response.status,len(response.read())), (206,16))
                req = Request(url+"/feedback", data=json.dumps({"ratings":[vote]}).encode(),
                              headers={"Content-Type":"application/json","Origin":url})
                with urlopen(req) as response:
                    self.assertEqual(json.load(response)["saved"], 1)
                style_feedback.save(self.job, batch["collection"], [dict(vote, stars=None, note="Zachowaj tempo")], "chat")
                with urlopen(url+"/feedback") as response:
                    saved = json.load(response)["ratings"]
                self.assertEqual([(v["stars"], v["note"]) for v in saved], [(5, "Zachowaj tempo")])
            finally:
                server.shutdown()
                thread.join()
        new = core.create_job("Kolejny", "shorts", "9:16", 5, "pl", self.job.parent, style_profile="tester")
        prefs = film_plan.plan("Rolka",new)["preferences"]
        self.assertEqual(prefs["style_order"][0], "studio")
        self.assertEqual(prefs["comments"][0]["note"], "Zachowaj tempo")
        self.assertEqual(style_feedback.summary(self.job.parent,"someone-else")["comments"], [])
        with self.assertRaises(ValueError):
            style_feedback.save(self.job, batch["collection"], [dict(vote,sha256="old")], "chat")

    def test_camera_dialogue_ducks_the_bed_in_encoded_audio(self):
        import array
        import math
        asset = self.footage()
        music = self.base / "music.wav"
        subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i","sine=frequency=1900:sample_rate=48000",
                        "-t","4",str(music)],check=True)
        bed = core.register_asset(self.job,music,"synthetic","test","bed")
        core.write(self.job/"timeline.json",{"clips":[{"asset_id":asset["id"],"in_sec":0,"duration_sec":4,"fit":"contain"}],
                                            "audio":{"music":bed["id"],"music_gain":.7}})
        output = assembly.assemble(self.job)
        def level(at):
            pcm = subprocess.check_output(["ffmpeg","-v","error","-ss",str(at),"-i",str(output),"-t","0.5",
                "-vn","-af","bandpass=f=1900:t=h:w=30","-ar","12000","-ac","1","-f","f32le","-"])
            samples = array.array("f")
            samples.frombytes(pcm)
            return math.sqrt(sum(x*x for x in samples)/len(samples))
        self.assertLess(level(1), level(3)*.9)
        report = editor.quality(self.job,output.relative_to(self.job).as_posix())
        self.assertIsNotNone(report["encoded_loudness"]["integrated_lufs"])
        self.assertIsNotNone(report["encoded_loudness"]["true_peak_dbtp"])

    def test_three_editable_shotcraft_scenes(self):
        gsap = core.ROOT/"node_modules/gsap/dist/gsap.min.js"
        if not gsap.is_file():
            self.skipTest("Pinned GSAP required")
        ids = []
        for color in ("red","blue"):
            path = self.base/(color+".png")
            subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i","color="+color+":s=96x64",
                            "-frames:v","1","-threads","1",str(path)],check=True)
            ids.append(core.register_asset(self.job,path,"synthetic","test","product")["id"])
        spec = "source/scene.json"
        core.write(self.job/spec,{"words":["Ruch","i","światło"],"assets":ids})
        for recipe in shotcraft_compose.RECIPES:
            with self.subTest(recipe=recipe):
                result = shotcraft_compose.compose(self.job,recipe,spec,overwrite=True)
                rendered_source = (self.job/result["source"]).read_text(encoding="utf-8")
                self.assertIn('class="'+recipe+'"',rendered_source)
                self.assertNotIn("@@DURATION@@",rendered_source)
                self.assertIn("window.__timelines",rendered_source)
        with self.assertRaises(ValueError):
            shotcraft_compose.compose(self.job,"flying-words",spec)


if __name__ == "__main__":
    unittest.main()
