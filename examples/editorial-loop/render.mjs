import {createCanvas} from '@napi-rs/canvas';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {runInNewContext} from 'node:vm';
import {spawnSync} from 'node:child_process';
const dir=resolve('output/editorial-loop');mkdirSync(dir,{recursive:true});
const canvas=createCanvas(960,540);
const source=readFileSync('examples/editorial-loop/index.html','utf8').split('<script>')[1].split('</script>')[0];
const context={document:{querySelector:()=>canvas},window:{}};
runInNewContext(source,context);
for(let i=0;i<240;i++){
 context.window.seek(i/30);
 writeFileSync(`${dir}/${String(i).padStart(4,'0')}.png`,canvas.toBuffer('image/png'));
}
function ff(args){const r=spawnSync('ffmpeg',['-y',...args],{stdio:'inherit'});if(r.status!==0)throw Error('FFmpeg failed')}
mkdirSync('docs/media',{recursive:true});mkdirSync('docs/images',{recursive:true});
ff(['-framerate','30','-i',`${dir}/%04d.png`,'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','docs/media/editorial-loop.mp4']);
ff(['-i','docs/media/editorial-loop.mp4','-filter_complex','fps=20,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0','docs/images/editorial-loop.gif']);
