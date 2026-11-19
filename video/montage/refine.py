"""Affine les fenetres de masquage image par image : pour chaque rectangle detecte par OCR, on compare le contenu du rectangle
a chaque image (30 i/s) autour de la detection ; le masque n'est actif que tant que le contenu est le meme.
Usage : python refine.py [ids...]   (lit/ecrit plan/<id>.masks.json)"""
import json, os, subprocess, sys
import numpy as np
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
THR = 10.0

def crops(src, t0, t1, x, y, w, h):
    t0 = max(0.0, t0)
    r = subprocess.run([FF, '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', src, '-vf', f'fps={FPS},crop={w}:{h}:{x}:{y},format=gray', '-f', 'rawvideo', '-'], capture_output=True)
    n = len(r.stdout) // (w * h)
    return t0, np.frombuffer(r.stdout[:n * w * h], np.uint8).reshape(n, h, w).astype(np.int16)

def refine(sid):
    mp = os.path.join(HERE, 'plan', sid + '.masks.json')
    raw = json.load(open(mp))
    if not raw: return sid, 0, 0
    src = os.path.join(HERE, 'work', 'conf', sid + '.mp4'); out = []
    for t0, t1, x, y, w, h in raw:
        x = max(0, x - 4); y = max(0, y - 3); w = min(1920 - x, w + 8); h = min(1080 - y, h + 6); w -= w % 2; h -= h % 2
        a, b = t0 + 0.35, t1 - 0.35          # fenetre brute sans le remplissage = images ou l'OCR a vu le texte (+- 0,5 s)
        s, C = crops(src, a - 1.2, b + 1.2, x, y, w, h)
        if len(C) == 0: out.append([t0, t1, x, y, w, h]); continue
        ref = C[min(len(C) - 1, max(0, int(round(((a + b) / 2 - s) * FPS))))]
        d = np.abs(C - ref).mean(axis=(1, 2))
        ok = d < THR
        # on ne garde que l'intervalle connexe qui recouvre la detection
        i0 = int(round((a - s) * FPS)); i1 = int(round((b - s) * FPS)); i0 = min(max(i0, 0), len(C) - 1); i1 = min(max(i1, 0), len(C) - 1)
        mid = (i0 + i1) // 2
        if not ok[mid]:
            cand = [i for i in range(i0, i1 + 1) if ok[i]]
            if not cand: out.append([t0, t1, x, y, w, h]); continue
            mid = cand[len(cand) // 2]
        lo = mid
        while lo > 0 and ok[lo - 1]: lo -= 1
        hi = mid
        while hi < len(C) - 1 and ok[hi + 1]: hi += 1
        ts = s + lo / FPS - 2 / FPS; te = s + (hi + 1) / FPS + 2 / FPS            # 2 images de marge
        out.append([round(ts, 3), round(te, 3), x, y, w, h])
    json.dump(out, open(mp, 'w'))
    return sid, len(raw), len(out)

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json')))
    with Pool(16) as pool:
        for r in pool.imap_unordered(refine, ids):
            if r[1]: print(r, flush=True)
