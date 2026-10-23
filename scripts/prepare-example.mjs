import {copyFileSync, existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const source = new URL('../node_modules/gsap/dist/gsap.min.js', import.meta.url);
if (!existsSync(source)) throw new Error('Run npm ci first.');
copyFileSync(source, new URL('../examples/launch/gsap.min.js', import.meta.url));
console.log('Local GSAP prepared for the example.');
