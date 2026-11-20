// Usage : node render.mjs stills 100,200,300      -> out/still_<frame>.png
//         node render.mjs clip 3612 3975 out/x.mp4 [concurrency]
//         node render.mjs full out/final.mp4 [concurrency]
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const [mode, a, b, c, d] = process.argv.slice(2);
const entry = path.resolve('src/index.ts');
const serveUrl = await bundle({entryPoint: entry, onProgress: () => {}});
const comp = await selectComposition({serveUrl, id: 'Main'});
fs.mkdirSync('out', {recursive: true});
const common = {composition: comp, serveUrl, chromiumOptions: {gl: 'angle'}, timeoutInMilliseconds: 180000};

if (mode === 'stills') {
  for (const f of a.split(',').map(Number)) {
    await renderStill({...common, frame: f, output: `out/still_${f}.png`, imageFormat: 'png'});
    console.log('still', f);
  }
} else if (mode === 'clip' || mode === 'full') {
  const out = mode === 'clip' ? c : a;
  const conc = Number(mode === 'clip' ? d : b) || 8;
  const t0 = Date.now(); let last = 0;
  await renderMedia({
    ...common, codec: 'h264', outputLocation: out, concurrency: conc,
    frameRange: mode === 'clip' ? [Number(a), Number(b)] : null,
    crf: 14, pixelFormat: 'yuv420p', x264Preset: 'medium', videoImageFormat: 'jpeg', jpegQuality: 96, muted: process.env.MUET === '1', audioCodec: 'aac', audioBitrate: '256k', overwrite: true,
    onProgress: (p) => { if (p.renderedFrames - last >= 300) { last = p.renderedFrames; console.log(`frames ${p.renderedFrames}/${p.progress ? Math.round(p.renderedFrames / p.progress) : '?'}  ${((Date.now() - t0) / 1000).toFixed(0)}s`); } },
  });
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
process.exit(0);
