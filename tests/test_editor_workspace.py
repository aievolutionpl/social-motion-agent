import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import studio_core as core
import editor_workspace as editor


class EditorWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = core.create_job('Test <script>', 'launch', '16:9', 2, 'pl', Path(self.tmp.name))
        job = core.read(self.folder / 'job.json')
        job.update(width=320, height=180)
        core.write(self.folder / 'job.json', job)
        self.media = self.folder / 'source/test.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=320x180:rate=30',
                        '-t','2','-c:v','libx264','-threads','1',str(self.media)],check=True)
        self.asset = core.register_asset(self.folder,self.media,'synthetic','test fixture','testing')

    def tearDown(self):
        self.tmp.cleanup()

    def test_inventory_frames_and_directions(self):
        report = editor.inventory(self.folder)
        item = report['report']['items'][0]
        self.assertNotIn('error', item)
        self.assertEqual(len(item['samples']), 3)
        self.assertFalse(item['has_audio'])
        self.assertEqual(item['width'],320)
        for sample in item['samples']:
            self.assertGreater((self.folder / sample['path']).stat().st_size, 100)
        result = editor.directions(self.folder)
        gallery = self.folder / result['gallery']
        self.assertEqual(len(list(gallery.parent.glob('*.svg'))),3)
        self.assertIn('&lt;script&gt;', (gallery.parent / '1.svg').read_text())
        self.assertFalse(result['approved'])

    def test_plan_validation_and_render(self):
        data = {'clips':[{'asset_id':self.asset['id'],'duration_sec':2,'in_sec':0,'fit':'contain'}], 'audio':{}}
        core.write(self.folder / 'source/plan.json',data)
        result = editor.plan(self.folder,'source/plan.json')
        self.assertEqual(core.read(self.folder / result['backup'])['clips'],[])
        from assembly import assemble
        rendered = assemble(self.folder)
        self.assertTrue(rendered.is_file())
        data['clips'][0]['in_sec']=1
        core.write(self.folder / 'source/plan.json',data)
        with self.assertRaises(ValueError):
            editor.plan(self.folder,'source/plan.json')
        self.assertEqual(editor.plan(self.folder)['clips'][0]['in_sec'],0)

    def test_preferences_keep_history_and_scope(self):
        core.write(self.folder / 'source/prefs.json',{'values':{'palette':['#ffffff','#123456']},'evidence':'Use my brand palette'})
        result = editor.preferences(self.folder,'source/prefs.json')
        self.assertEqual(result['scope'],'this_job')
        self.assertEqual(len(result['history']),1)
        core.write(self.folder / 'source/prefs.json',{'values':{'palette':['url(bad)']},'evidence':'test'})
        with self.assertRaises(ValueError):
            editor.preferences(self.folder,'source/prefs.json')
        self.assertEqual(editor.preferences(self.folder),result)

    def test_quality_and_feedback_identity(self):
        report = editor.quality(self.folder,'source/test.mp4')
        self.assertIn('Required audio missing', report['failures'])
        self.assertTrue(report['decode_passed'])
        page = editor.review(self.folder,'source/test.mp4','source/test.mp4')
        self.assertTrue((self.folder / page['page']).is_file())
        feedback = {'render':'source/test.mp4','sha256':report['sha256'], 'comments':[{'at':1,'x':.5,'y':.5,'text':'Cut here','status':'resolved'}]}
        core.write(self.folder / 'source/feedback.json',feedback)
        result=editor.import_feedback(self.folder,'source/feedback.json')
        self.assertEqual(core.read(self.folder / result['file'])['comments'][0]['status'],'open')
        feedback['sha256']='wrong'
        core.write(self.folder / 'source/feedback.json',feedback)
        with self.assertRaises(ValueError):
            editor.import_feedback(self.folder,'source/feedback.json')
        with self.assertRaises(ValueError):
            editor.review(self.folder,'../../outside.mp4')

    def test_finite_numbers(self):
        for n in (float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):
                editor.number(n)
