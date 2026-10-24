"""Prepare or reproduce the published 30-second intro without generation APIs."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from studio_core import ROOT, create_job, now, read, write, register_asset, probe_job

EXAMPLE = ROOT / 'examples/premium-intro'

def prepare(folder):
    source = folder / 'source'
    if (source / 'index.html').exists():
        raise ValueError('Composition exists; create a new job to preserve edits.')
    job = read(folder / 'job.json')
    if (job['width'], job['height'], job['duration_sec']) != (1920, 1080, 30):
        raise ValueError('Premium intro requires 1920x1080 and 30 seconds.')
    gsap = ROOT / 'node_modules/gsap/dist/gsap.min.js'
    if not gsap.is_file():
        raise ValueError('Run npm ci first.')
    shutil.copytree(EXAMPLE / 'source', source, dirs_exist_ok=True)
    shutil.copy2(gsap, source / 'gsap.min.js')
    shutil.copytree(EXAMPLE / 'audio', folder / 'audio')
    shutil.copy2(EXAMPLE / 'captions.srt', folder / 'captions.srt')
    brief = read(folder / 'brief.json')
    brief.update(goal='Reproduce the published premium intro', audience='Polish Codex users',
                 direction='Platinum architecture, cinematic desert, actual skill screenshots and kinetic typography',
                 cta='Daj swojemu agentowi warsztat filmowy', audio_required=True, captions_required=True,
                 engine='hyperframes', engine_reason='Pinned local renderer; supplied media require no generation API')
    write(folder / 'brief.json', brief)
    intake = read(folder / 'intake.json')
    for q in intake['questions']:
        if not q.get('answer'):
            q['answer'] = 'Bundled approved creative specification, not a new user answer; see examples/premium-intro/README.md.'
    write(folder / 'intake.json', intake)
    write(folder / 'research.json', {'sources':[dict(id='project',title='Published source and provenance',
        url='https://github.com/aievolutionpl/social-motion-agent/tree/main/examples/premium-intro',
        accessed_at=now(),used_for='Actual skill files, source media and reproducible timeline')],
        'claims':[], 'conclusions':'Animated genuine Codex screenshots, not a continuous agent execution recording. No claim that source collection implies installed providers.'})
    storyboard = read(EXAMPLE / 'storyboard.json')
    write(folder / 'storyboard.json', {'scenes':[dict(id=s['id'],duration_sec=round(s['end']-s['start'],3),visual=s['description'],asset_ids=[]) for s in storyboard['scenes']]})
    for file in sorted((source / 'media').iterdir()):
        if file.suffix.lower() in {'.png','.jpg','.ttf'}:
            register_asset(folder,file,'Bundled premium intro; see provenance.json','See examples/premium-intro/README.md and font OFL','Premium intro visual')
    for file in sorted((folder / 'audio').glob('*')):
        if file.suffix in {'.mp3','.wav'}:
            register_asset(folder,file,'Owner-authorized published soundtrack','See docs/MEDIA_RIGHTS.md; not MIT-licensed voice or music','Narration and music')
    (source / 'script.md').write_text('# Narration\n\n'+(EXAMPLE / 'narration.txt').read_text(encoding='utf-8'),encoding='utf-8')
    (folder / 'HANDOFF.md').write_text('# Premium intro reproduction\n\nLocal source and supplied soundtrack. No paid calls. Inspect the actual render and listen before recording review approval. Original screenshots are animated stills.\n',encoding='utf-8')
    return folder

def render(folder):
    from hyperframes_adapter import render as render_html
    render_html(folder, 'premium-picture', 'high')
    target = folder / 'renders/premium-intro.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-n',
        '-i',str(folder/'renders/premium-picture.mp4'),'-i',str(folder/'audio/mix.wav'),
        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','30',
        '-movflags','+faststart',str(target)],check=True,timeout=180)
    return probe_job(folder,'renders/premium-intro.mp4')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    folder=prepare(create_job('Premium intro','showcase','16:9',30,'pl'))
    result={'job':str(folder),'reviewed':False}
    if args.render: result['technical']=render(folder)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
