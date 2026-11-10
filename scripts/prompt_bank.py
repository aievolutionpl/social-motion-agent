"""Offline HyperFrames recipe lookup. Selection never executes a prompt."""
import json
import unicodedata
from studio_core import ROOT


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold().replace('ł', 'l')) if not unicodedata.combining(c))


def query(action, text='', category=None):
    data = json.loads((ROOT / 'config/hyperframes-prompts.json').read_text(encoding='utf-8'))
    items = data['items']
    if action == 'show':
        key = 'hf-' + text.zfill(2) if text.isdigit() else text
        item = next((x for x in items if x['id'] == key), None)
        if not item:
            raise ValueError('Unknown prompt ID; use prompts list')
        return {**item, 'source': data['source'], 'ready_to_use_prompt': data['contract'] + '\n\n' + item['prompt']}
    if action == 'find' and not text.strip():
        raise ValueError('Provide a search phrase')
    if category:
        items = [x for x in items if x['category'] == category]
    if action == 'find':
        terms = normalize(text).split()
        items = [x for x in items if all(t in normalize(x['title']+' '+x['prompt']+' '+' '.join(x['inputs'])) for t in terms)]
    return {'count': len(items), 'items': [{k:x[k] for k in ('id','title','category','duration_sec','inputs','status')} for x in items],
            'note': 'Recipes, not rendered presets. prompts show ID returns the complete HyperFrames contract.'}
