"""Job-local editing tools. No cloud providers, implicit approvals or shared client memory."""
import html
import json
import math
import re
import subprocess
import uuid
from pathlib import Path
from urllib.parse import quote

import studio_core as core

GALLERY_STYLE = """<style>
*{box-sizing:border-box}body{margin:0;background:#f5f2eb;color:#20272c;font:16px/1.55 system-ui;padding:clamp(20px,5vw,70px);max-width:1500px;margin:auto}h1{font-size:clamp(30px,4vw,54px);letter-spacing:-.04em;margin:0 0 16px}h2{font-size:20px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:24px;margin-top:36px}section{background:#fff;border:1px solid #d9d7d0;border-radius:16px;padding:20px;overflow:hidden}section img{width:100%;height:auto;border-radius:8px}section p{color:#505963}pre{font:12px/1.6 monospace;white-space:pre-wrap;overflow-wrap:anywhere}figure{margin:12px 0}figcaption{color:#505963}body>p{max-width:780px}</style>"""


def number(value):
    if isinstance(value, bool):
        raise ValueError('Expected finite number')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Expected finite number')
    return value


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise ValueError(result.stderr[-2000:])
    return result


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)


def save(folder, name, data):
    path = core.local(folder, name, exists=False)
    core.write(path, data)
    return data


def version_dir(folder, label):
    path = core.local(folder, 'previews/' + label + '-' + uuid.uuid4().hex[:10], exists=False)
    path.mkdir(parents=True)
    return path


def inventory(folder):
    """Probe registered assets and sample actual frames; candidates are not semantic selections."""
    dest = version_dir(folder, 'inventory')
    items = []
    for asset in core.read(folder / 'assets.json')['items']:
        item = {'asset_id': asset['id'], 'path': asset['path'], 'rights': asset.get('rights'), 'samples': []}
        try:
            source = core.local(folder, asset['path'])
            item['sha256'] = core.sha(source)
            info = probe(source)
            video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
            audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
            duration = number(info.get('format', {}).get('duration', 0))
            item.update(duration_sec=duration, has_audio=bool(audio), width=video.get('width') if video else None,
                        height=video.get('height') if video else None, fps=video.get('avg_frame_rate') if video else None,
                        observations=[], review_status='needs_visual_review')
            if video:
                for i, t in enumerate([duration * x for x in (.1, .5, .9)] if duration else [0]):
                    target = dest / (str(len(items)) + '-' + str(i) + '.jpg')
                    run(['ffmpeg', '-v', 'error', '-nostdin', '-ss', str(t), '-i', str(source), '-frames:v', '1',
                         '-vf', 'scale=480:-2', '-threads', '1', '-y', str(target)])
                    if not target.exists():
                        raise ValueError('No sampled frame produced')
                    item['samples'].append({'at_sec': t, 'path': target.relative_to(folder).as_posix()})
                if video.get('width', 0) < 720:
                    item['observations'].append('Low horizontal resolution; inspect intended crop')
            item['candidate_ranges'] = []
            if duration and video:
                cuts = run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(source), '-an',
                            '-vf', "select='gt(scene,0.35)',showinfo", '-f', 'null', '-']).stderr
                boundaries = [0.0] + [float(t) for t in re.findall(r'pts_time:([0-9.]+)', cuts)] + [duration]
                boundaries = sorted(set(t for t in boundaries if 0 <= t <= duration))
                item['candidate_ranges'] = [{'in_sec': a, 'out_sec': b, 'reason': 'Visual scene boundaries; content/quality require agent review'}
                                            for a,b in zip(boundaries, boundaries[1:]) if b-a >= .3][:100]
            if audio:
                silence = run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(source), '-vn',
                               '-af', 'silencedetect=n=-35dB:d=0.4', '-f', 'null', '-']).stderr
                item['silence_events'] = [line.strip() for line in silence.splitlines() if 'silence_start:' in line or 'silence_end:' in line]
                item['observations'].append('Silence detection is not speech recognition')
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            item['error'] = str(exc)
        items.append(item)
    report = {'items': items, 'created_at': core.now(), 'semantic_analysis': False,
              'missing': ['No registered assets'] if not items else []}
    save(folder, dest.relative_to(folder).as_posix() + '/inventory.json', report)
    cards = []
    for item in items:
        images = ''.join('<figure><img width="240" src="' + quote(Path(s['path']).name) + '"><figcaption>' + str(round(s['at_sec'], 2)) + ' s</figcaption></figure>' for s in item['samples'])
        cards.append('<section><h2>' + html.escape(item['asset_id']) + '</h2>' + images + '<pre>' + html.escape(json.dumps(item, ensure_ascii=False, indent=2)) + '</pre></section>')
    (dest / 'index.html').write_text('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Media inventory</title>' + GALLERY_STYLE + '<h1>Przegląd materiałów</h1><p>Próbki obrazu i wykryte granice scen. Obejrzyj materiał przed wyborem ujęć.</p><main>' + ''.join(cards) + '</main>', encoding='utf-8')
    return {'report': report, 'gallery': (dest / 'index.html').relative_to(folder).as_posix()}


def preferences(folder, source=None):
    path = core.local(folder, 'preferences.json', exists=False)
    current = core.read(path) if path.exists() else {'schema_version': 1, 'scope': 'this_job', 'history': [], 'values': {}}
    if source:
        update = core.read(core.local(folder, source))
        allowed = {'palette', 'font', 'pace', 'keep', 'avoid', 'style'}
        if not isinstance(update.get('values'), dict) or set(update['values']) - allowed:
            raise ValueError('Allowed preferences: palette, font, pace, keep, avoid, style')
        if not isinstance(update.get('evidence'), str) or not update['evidence'].strip():
            raise ValueError('Provide actual user instruction in evidence')
        for key, value in update['values'].items():
            if key == 'palette':
                if not isinstance(value, list) or not 2 <= len(value) <= 5 or not all(isinstance(c, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', c) for c in value):
                    raise ValueError('palette requires 2..5 hex colors')
            elif not isinstance(value, str) or not value.strip() or len(value) > 2000:
                raise ValueError('Preference must be 1..2000 characters')
        current['history'].append({'at': core.now(), 'previous': dict(current['values']), 'evidence': update['evidence']})
        current['values'].update(update['values'])
        save(folder, 'preferences.json', current)
    return current


def directions(folder):
    job = core.read(folder / 'job.json')
    prefs = preferences(folder)['values']
    dest = version_dir(folder, 'directions')
    title = html.escape(job['title'])
    w, h = job['width'], job['height']
    scale = min(w, h)
    palettes = [('#f6f1e8', '#172324', '#c64b31'), ('#17212c', '#ffffff', '#d6ff63'), ('#ede7ff', '#241444', '#793bea')]
    names = ['Editorial / opowieść', 'Kinetic / kontrast skali', 'Diagram / mechanizm']
    cards = []
    for i, (name, colors) in enumerate(zip(names, palettes)):
        if prefs.get('palette'):
            colors = (prefs['palette'] + prefs['palette'])[:3]
        bg, ink, accent = colors
        if i == 0:
            geometry = f'<rect x="{w*.08}" y="{h*.15}" width="{w*.56}" height="{h*.43}" fill="{accent}"/><circle cx="{w*.72}" cy="{h*.43}" r="{scale*.13}" fill="{ink}"/>'
        elif i == 1:
            geometry = f'<text x="{w*.08}" y="{h*.5}" font-size="{scale*.32}" font-weight="900" fill="{accent}">01</text><path d="M {w*.55} {h*.2} L {w*.9} {h*.5} L {w*.55} {h*.6} Z" fill="{ink}"/>'
        else:
            geometry = f'<path d="M {w*.2} {h*.38} H {w*.8}" stroke="{ink}" stroke-width="8"/>' + ''.join(f'<circle cx="{w*x}" cy="{h*.38}" r="{scale*.09}" fill="{accent}"/><text x="{w*x}" y="{h*.39}" text-anchor="middle" fill="{bg}" font-size="{scale*.04}">{n}</text>' for n,x in enumerate((.2,.5,.8),1))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="{bg}"/>{geometry}<foreignObject x="{w*.08}" y="{h*.65}" width="{w*.84}" height="{h*.3}"><div xmlns="http://www.w3.org/1999/xhtml" style="font:700 {scale*.055}px sans-serif;color:{ink};overflow-wrap:anywhere">{title}<p style="font-size:{scale*.025}px">{html.escape(name)} · koncept, nie gotowa scena</p></div></foreignObject></svg>'
        (dest / f'{i+1}.svg').write_text(svg, encoding='utf-8')
        cards.append(f'<section><h2>{name}</h2><img width="300" src="{i+1}.svg"><p>Wybierz {i+1} i opisz co zachować lub zmienić.</p></section>')
    (dest / 'index.html').write_text('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kierunki</title>' + GALLERY_STYLE + '<h1>Jedna historia. Trzy kierunki.</h1><p>Wstępne styleframe’y do rozmowy o kompozycji. Agent dopasuje obiekty, fonty i ruch do twojego briefu. Wybierz punkt wyjścia i powiedz, co warto zachować.</p><main>' + ''.join(cards) + '</main>', encoding='utf-8')
    save(folder, dest.relative_to(folder).as_posix() + '/manifest.json', {'approved': False, 'preferences': prefs, 'names': names})
    return {'gallery': (dest / 'index.html').relative_to(folder).as_posix(), 'approved': False}


def plan(folder, source=None):
    """Edit the renderer's existing timeline, preserving a version before applying validated changes."""
    if not source:
        return core.read(folder / 'timeline.json')
    data = core.read(core.local(folder, source))
    job = core.read(folder / 'job.json')
    assets = {a['id']: a for a in core.read(folder / 'assets.json')['items']}
    clips = data.get('clips')
    if not isinstance(clips, list) or not clips:
        raise ValueError('Plan requires clips')
    total = 0
    for clip in clips:
        duration, start = number(clip.get('duration_sec', 0)), number(clip.get('in_sec', 0))
        if duration <= 0 or start < 0 or clip.get('asset_id') not in assets or clip.get('fit') not in ('cover', 'contain'):
            raise ValueError('Invalid clip source, range or fit')
        path = core.local(folder, assets[clip['asset_id']]['path'])
        info = probe(path)
        if not any(s['codec_type'] == 'video' for s in info['streams']):
            raise ValueError('Clip needs picture')
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.bmp'):
            available = number(info.get('format', {}).get('duration', 0))
            if start + duration > available + 1 / job['fps']:
                raise ValueError('Clip exceeds source duration')
        total += duration
    if abs(total - job['duration_sec']) > 1 / job['fps']:
        raise ValueError('Clip durations must match job.duration_sec; adjust the job explicitly for a new length')
    audio = data.get('audio', {})
    for key in ('voice', 'music'):
        if audio.get(key) and audio[key] not in assets:
            raise ValueError('Unknown audio asset')
    if not 0 <= number(audio.get('music_gain', .12)) <= 1:
        raise ValueError('music_gain outside 0..1')
    backup = 'notes/timeline-' + uuid.uuid4().hex + '.json'
    save(folder, backup, core.read(folder / 'timeline.json'))
    save(folder, 'timeline.json', data)
    return {'applied': True, 'backup': backup, 'duration_sec': total, 'render_required': True}


def quality(folder, render):
    source = core.local(folder, render)
    info = probe(source)
    video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    if not video:
        raise ValueError('Export has no video')
    audio = any(s['codec_type'] == 'audio' for s in info['streams'])
    cmd = ['ffmpeg', '-hide_banner', '-nostdin', '-i', str(source), '-vf', 'blackdetect=d=0.2:pix_th=0.10,freezedetect=n=-50dB:d=2']
    if audio:
        cmd += ['-af', 'volumedetect']
    result = run(cmd + ['-f', 'null', '-'])
    events = [line.strip() for line in result.stderr.splitlines() if any(k in line for k in ('black_start:', 'freeze_start:', 'freeze_end:', 'freeze_duration:', 'max_volume:', 'mean_volume:'))]
    job = core.read(folder / 'job.json')
    failures = []
    if (video['width'], video['height']) != (job['width'], job['height']):
        failures.append('Dimensions differ from job')
    if abs(number(info['format']['duration']) - job['duration_sec']) > .15:
        failures.append('Duration differs from job')
    if core.read(folder / 'brief.json').get('audio_required') and not audio:
        failures.append('Required audio missing')
    report = {'render': render, 'sha256': core.sha(source), 'decode_passed': True, 'failures': failures,
              'events_to_review': events, 'technical_passed': not failures, 'creative_approval': False,
              'not_checked': ['Text clipping/OCR', 'Caption reading speed', 'Speech intelligibility', 'True-peak loudness', 'Art direction'],
              'note': 'Black/frozen frames can be intentional; volume maxima are not proof of clipping.'}
    save(folder, 'notes/quality-' + report['sha256'] + '.json', report)
    return report


def review(folder, render, previous=None):
    source = core.local(folder, render)
    identity = core.sha(source)
    dest = version_dir(folder, 'review')
    payload = {'render': render, 'sha256': identity, 'duration': number(probe(source)['format']['duration'])}
    videos = '<video id="video" controls src="../../' + quote(render, safe='/') + '"></video>'
    if previous:
        core.local(folder, previous)
        videos += '<h2>Poprzednia wersja</h2><video controls src="../../' + quote(previous, safe='/') + '"></video>'
    template = (Path(__file__).parent.parent / 'templates/editor-review.html').read_text(encoding='utf-8')
    page = template.replace('<!--VIDEOS-->', videos).replace('/*PAYLOAD*/', json.dumps(payload).replace('<', '\\u003c'))
    (dest / 'index.html').write_text(page, encoding='utf-8')
    return {'page': (dest / 'index.html').relative_to(folder).as_posix(), 'sha256': identity,
            'comments': 'Stored locally in browser; export JSON and import with editor feedback-import'}


def import_feedback(folder, source):
    data = core.read(core.local(folder, source))
    render = core.local(folder, data['render'])
    if core.sha(render) != data.get('sha256'):
        raise ValueError('Feedback render hash mismatch')
    duration = number(probe(render)['format']['duration'])
    comments = data.get('comments')
    if not isinstance(comments, list) or len(comments) > 1000:
        raise ValueError('Expected at most 1000 comments')
    for c in comments:
        if not 0 <= number(c['at']) <= duration or not 0 <= number(c['x']) <= 1 or not 0 <= number(c['y']) <= 1:
            raise ValueError('Comment coordinates/time out of range')
        if not isinstance(c.get('text'), str) or not 1 <= len(c['text'].strip()) <= 2000:
            raise ValueError('Invalid comment')
    # Server owns statuses: browser input cannot mark changes implemented.
    record = {'render': data['render'], 'sha256': data['sha256'], 'comments': [dict(at=c['at'], x=c['x'], y=c['y'], text=c['text'], status='open') for c in comments]}
    path = 'notes/review-comments-' + uuid.uuid4().hex + '.json'
    save(folder, path, record)
    return {'file': path, 'imported': len(comments), 'applied': False}
