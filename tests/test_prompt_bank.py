import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import prompt_bank
from studio_core import ROOT


class PromptBankTests(unittest.TestCase):
    def test_all_recipes_have_full_contract_and_correct_timing(self):
        items=prompt_bank.query('list')['items']
        self.assertEqual(len(items),30)
        self.assertEqual(len({i['id'] for i in items}),30)
        for item in items:
            full=prompt_bank.query('show',item['id'])
            self.assertEqual(full['frames'],full['duration_sec']*full['fps'])
            self.assertIn('window.__timelines.main',full['ready_to_use_prompt'])
            self.assertIn('window.seek(t)',full['ready_to_use_prompt'])
            self.assertNotIn('React Three Fiber',full['prompt'])
            self.assertNotIn('propsy',full['prompt'])
            self.assertEqual(full['status'],'recipe_not_rendered')

    def test_search_and_filters(self):
        self.assertEqual(prompt_bank.query('list',category='3d')['count'],14)
        self.assertEqual(prompt_bank.query('list',category='paper')['count'],7)
        self.assertEqual(prompt_bank.query('find','paragon')['items'][0]['id'],'hf-05')
        self.assertEqual(prompt_bank.query('find','slowo z pylu')['items'][0]['id'],'hf-29')
        self.assertEqual(prompt_bank.query('show','2')['id'],'hf-02')
        self.assertEqual(prompt_bank.query('find','no-such-effect')['count'],0)
        with self.assertRaises(ValueError):prompt_bank.query('show','../../private')
        with self.assertRaises(ValueError):prompt_bank.query('find','')

    def test_cli_and_document_completeness(self):
        run=subprocess.run([sys.executable,'-S','studio.py','prompts','show','hf-30'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn('HyperFrames',json.loads(run.stdout)['ready_to_use_prompt'])
        doc=(ROOT/'references/hyperframes-prompts.md').read_text()
        for item in prompt_bank.query('list')['items']:
            self.assertIn('## '+item['id']+' — '+item['title'],doc)
