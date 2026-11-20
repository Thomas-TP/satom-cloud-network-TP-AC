"""Assemble le scenario du montage -> rm/src/data.json (lu par la composition Remotion).
Usage : python export.py"""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import scenario2 as sc
import captions
FPS = 30; OVERLAP = 8
BASE = 'http://127.0.0.1:8765'
IMG = {0: 'global', 1: 'm01-vpc', 2: 'm02-routage', 3: 'm03-securite', 4: 'm04-firewall', 5: 'm05-peering', 6: 'm06-tgw', 7: 'm07-vpn', 8: 'm08-dx', 9: 'm09-alb',
       10: 'm10-route53', 11: 'm11-cloudfront', 12: 'm12-monitoring', 13: 'm13-cloudformation'}
CH_DUR = 5.0
TRIM = 12          # images retirees au debut de chaque scene console (restes de la page precedente)
PAD_SCENE = {'m07e': 0.7, 'm08a': 1.0, 'm08b': 1.0}   # scenes ou la verification finale a encore trouve des restes
PAD = 0.13         # marge (s) ajoutee de part et d'autre de chaque masque

def disp(t):
    """Texte affiche : retire les traits d'union de prononciation (G-R-E -> GRE)."""
    return re.sub(r"(?<![A-Za-z])[A-Z](?:-[A-Z])+(?![A-Za-z])", lambda m: m.group(0).replace("-", ""), t)

def dark_ratio(sid):
    a = json.load(open(os.path.join(HERE, 'analyse', sid + '.json'))); lum = np.array(a['lum'])
    return float((lum < 90).mean())

VOIX = {}
_vp = os.path.join(ROOT, 'voix', 'lignes.json')
if os.path.exists(_vp) and os.environ.get('SANS_VOIX') != '1':
    _v = json.load(open(_vp, encoding='utf8')); VOIX = {x['id']: x for x in _v['scenes']}
def vdur(sid, default):
    """duree d'une carte : celle que demande la voix (video/voix/lignes.json recalculee avec les durees reelles), au moins la duree par defaut."""
    return int(round(max(default, VOIX[sid]['dur'] if sid in VOIX else 0) * FPS))
def intro_focus():
    """mouvements de camera sur le schema global, calés sur les phrases de l'intro (x, y en fraction de l'image, zoom)."""
    if 'intro' not in VOIX: return []
    v = VOIX['intro']; t0 = v['start']; L = v['lines']; rel = lambda t: round(t - t0, 2)
    kf = [[0, 0.5, 0.5, 1.0]]
    if len(L) >= 4:
        s1, e1, s2, e2, s3 = L[1]['start'], L[1]['end'], L[2]['start'], L[2]['end'], L[3]['start']
        d1 = e1 - s1; d2 = e2 - s2
        kf += [[rel(s1 - 0.2), 0.5, 0.5, 1.0], [rel(s1 + 0.5), 0.37, 0.42, 1.9], [rel(s1 + 0.5 * d1), 0.74, 0.43, 1.55], [rel(s1 + 0.82 * d1), 0.37, 0.72, 2.0],
               [rel(s2 + 0.3), 0.13, 0.45, 2.0], [rel(s2 + 0.58 * d2), 0.74, 0.72, 1.9], [rel(s3), 0.5, 0.5, 1.0]]
    return kf

def main(only_mod=None):
    scenes = []; mod = None
    scenes.append(dict(type='title', dur=vdur('title', 4.0)))
    scenes.append(dict(type='intro', img=f'{BASE}/docs/images/global.png', dur=vdur('intro', 7.0), focus=intro_focus()))
    for s in sc.S:
        if s['kind'] == 'card' and s['num'] is not None:
            mod = dict(num=s['num'], name=disp(s['title'].split('–', 1)[1].strip()), sub=disp(s['sub']))
            scenes.append(dict(type='chapter', mod=mod, img=f"{BASE}/docs/images/{IMG[s['num']]}.png", dur=vdur(f"chap{s['num']}", CH_DUR)))
        elif s['kind'] == 'gui':
            sid = s['id']; p = json.load(open(os.path.join(HERE, 'plan', sid + '.json')))
            n = int(round(p['out_len'] * FPS)) - TRIM; sh = TRIM / FPS
            cam = [[round(k[0] - sh, 3)] + k[1:] for k in p['cam'] if k[0] - sh > -0.1]
            badges = [[round(max(0, b[0] - sh), 2), round(b[1] - sh, 2), b[2]] for b in p['badges'] if b[1] - sh > 0.5]
            cap = captions.C.get(sid, ('', ''))
            mp = os.path.join(HERE, 'plan', sid + '.masks.json'); masks = [[round(m[0] - sh - PAD_SCENE.get(sid, PAD), 3), round(m[1] - sh + PAD_SCENE.get(sid, PAD), 3)] + m[2:] for m in json.load(open(mp))] if os.path.exists(mp) else []
            scenes.append(dict(type='gui', id=sid, src=f'{BASE}/video/montage/work/conf/{sid}.mp4', dur=n, cam=cam, badges=badges, trim=TRIM,
                               title=cap[0], detail=cap[1], mod=mod, dark=dark_ratio(sid) > 0.5, masks=masks))
    scenes.append(dict(type='end', img=f'{BASE}/docs/images/global.png', dur=vdur('end', 8.0)))
    t = 0
    for sc_ in scenes:
        sc_['from'] = t; t += sc_['dur'] - OVERLAP
    total = t + OVERLAP
    out = dict(fps=FPS, overlap=OVERLAP, total=total, scenes=scenes)
    if os.path.exists(os.path.join(HERE, 'work', 'piste.wav')) and os.environ.get('SANS_VOIX') != '1': out['audio'] = f'{BASE}/video/montage/work/piste.wav'
    path = os.path.join(HERE, 'rm', 'src', 'data.json'); json.dump(out, open(path, 'w'))
    print(f'{len(scenes)} scenes, {total / FPS / 60:.1f} min  -> {path} ({os.path.getsize(path) / 1e6:.1f} Mo)')

if __name__ == '__main__': main()
