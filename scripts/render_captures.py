"""Rend en images de terminal (PNG) les fichiers texte de captures/mNN et les preuves docs/modules/mNN/tests.txt."""
import os, glob, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONT = r"C:\Windows\Fonts\consola.ttf"
BG, FG, DIM, ACC, OKC, KOC = (22, 27, 34), (201, 209, 217), (125, 133, 144), (88, 166, 255), (63, 185, 80), (248, 81, 73)
W, LH, PAD = 1500, 24, 24
fnt = ImageFont.truetype(FONT, 18)
fb = ImageFont.truetype(FONT.replace('consola', 'consolab'), 18)


def color(line):
    l = line.lower()
    if line.startswith('$'):
        return ACC
    if line.startswith('==='):
        return ACC
    if any(k in l for k in ('echec', 'failed', 'refus', 'denied', 'error', 'ko ', 'unhealthy', 'drifted', 'bloque')):
        return KOC
    if any(k in l for k in ('success', 'ok', 'healthy', 'established', 'hit from', 'in_sync', 'complete', 'available', 'active')):
        return OKC
    return FG


def render(lines, title, out, maxlines=34):
    chunks = [lines[i:i + maxlines] for i in range(0, len(lines), maxlines)] or [[]]
    paths = []
    for k, ch in enumerate(chunks):
        h = 60 + LH * len(ch) + PAD
        im = Image.new('RGB', (W, h), BG)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 38], fill=(13, 17, 23))
        for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            d.ellipse([16 + i * 24, 12, 28 + i * 24, 24], fill=c)
        suffix = f"  ({k + 1}/{len(chunks)})" if len(chunks) > 1 else ''
        d.text((W // 2, 19), f"TP-AC \u2013 {title}{suffix}", font=fb, fill=DIM, anchor='mm')
        y = 52
        for ln in ch:
            d.text((PAD, y), ln.replace('\t', '    '), font=fnt, fill=color(ln))
            y += LH
        p = out if len(chunks) == 1 else out.replace('.png', f'-{k + 1}.png')
        im.save(p)
        paths.append(p)
    return paths


def wrap(text):
    out = []
    for raw in text.splitlines():
        out.extend(textwrap.wrap(raw, 120, replace_whitespace=False, drop_whitespace=False) or [''])
    return out


n = 0
for t in sorted(glob.glob(os.path.join(ROOT, 'captures', 'm??', '*.txt'))):
    title = os.path.basename(os.path.dirname(t)) + ' \u2013 ' + os.path.basename(t)[:-4]
    n += len(render(wrap(open(t, encoding='utf-8').read()), title, t[:-4] + '.png'))
for t in sorted(glob.glob(os.path.join(ROOT, 'docs', 'modules', 'm??', 'tests.txt'))):
    m = os.path.basename(os.path.dirname(t))
    out = os.path.join(ROOT, 'captures', m, '99-preuves-tests.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n += len(render(wrap(open(t, encoding='utf-8').read()), f'{m} \u2013 preuves de tests', out))
print('images generees :', n)
