"""Camera des terminaux : sur les images sombres (Session Manager), cadre automatiquement la zone de texte.
Lit work/conf/<id>.mp4 (deja retime), remplace les cibles de camera des instants sombres, relisse, ecrit plan/<id>.json.
Usage : python camfix.py [ids...]"""
import json, os, subprocess, sys
import numpy as np
import plan as P
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 480, 270
HZ = 20

def fix(sid):
    pj = os.path.join(HERE, 'plan', sid + '.json'); p = json.load(open(pj))
    src = os.path.join(HERE, 'work', 'conf', sid + '.mp4')
    r = subprocess.run([FF, '-v', 'error', '-i', src, '-vf', f'fps=4,scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-'], capture_output=True)
    buf = np.frombuffer(r.stdout, np.uint8); nfr = len(buf) // (W * H)
    if nfr == 0: return sid, 0
    frames = buf[:nfr * W * H].reshape(nfr, W, H)[:] if False else buf[:nfr * W * H].reshape(nfr, H, W)
    tgt = np.array(p['tgt'], float); changed = 0
    prev = None; boxes = []
    for k in range(nfr):
        g = frames[k].astype(np.int16); dark = g.mean() < 90
        box = None
        if dark and prev is not None:
            m = (g > 40) & (prev > 40); m[:14, :] = False; m[262:, :] = False
            rows = np.nonzero(m.sum(1) >= 3)[0]; cols = np.nonzero(m.sum(0) >= 2)[0]
            if len(rows) > 2 and len(cols) > 4: box = (cols[0] * 4, rows[0] * 4, cols[-1] * 4, rows[-1] * 4)
        boxes.append((dark, box)); prev = g
    for i in range(len(tgt)):
        k = min(nfr - 1, int(i / HZ * 4)); dark, box = boxes[k]
        if not dark: continue
        if box is None: tgt[i] = (960, 540, 1.0); changed += 1; continue
        x0, y0, x1, y1 = box; bw = x1 - x0 + 160; bh = y1 - y0 + 130
        z = min(2.1, 1920 / bw, 1080 / bh); z = 1.0 if z < 1.12 else z
        tgt[i] = ((x0 + x1) / 2, (y0 + y1) / 2 + 10, z); changed += 1
    p['tgt'] = [[round(a, 1), round(b, 1), round(c, 3)] for a, b, c in tgt]
    p['cam'] = P.smooth(tgt, HZ)
    json.dump(p, open(pj, 'w'))
    return sid, changed

if __name__ == '__main__':
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json')))
    from multiprocessing import Pool
    with Pool(8) as pool:
        for r in pool.imap_unordered(fix, ids):
            if r[1]: print(r, flush=True)
