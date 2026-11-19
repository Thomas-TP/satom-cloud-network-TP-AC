"""Verification ciblee de la video finale : OCR des images situees dans / aux bords de chaque fenetre de masquage et au debut de chaque scene.
Usage : python verify3.py rm/out/final.mp4"""
import json, os, subprocess, sys, time
import numpy as np
import ocrmask as M
SRC = sys.argv[1]
FPS = 30

def times():
    d = json.load(open(os.path.join(M.HERE, 'rm', 'src', 'data.json'))); ts = []
    for s in d['scenes']:
        base = s['from'] / FPS
        if s['type'] != 'gui': continue
        for t in (0.0, 0.1, 0.2, 0.35): ts.append(round(base + t, 3))
        for m in s.get('masks', []):
            a, b = m[0], m[1]
            for t in (a + 1 / FPS, (a + b) / 2, b - 1 / FPS): 
                if 0 <= t <= s['dur'] / FPS: ts.append(round(base + t, 3))
    return sorted(set(ts))

def task(ts):
    out = []
    for t in ts:
        r = subprocess.run([M.FF, '-v', 'error', '-ss', f'{t:.3f}', '-i', SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        if len(r.stdout) < M.W * M.H * 3: continue
        img = np.frombuffer(r.stdout, np.uint8).reshape(M.H, M.W, 3)
        res, _ = M._ocr(img[:, :, ::-1])
        for box, txt, conf in (res or []):
            low = txt.replace(' ', '').lower()
            for key in M.KEYS + M.PARTS:
                kk = key.replace(' ', '').lower()
                if kk and kk in low: out.append((t, txt[:70], [round(box[0][0]), round(box[0][1])])); break
    return out

if __name__ == '__main__':
    from multiprocessing import Pool
    ts = times(); print(len(ts), 'images a verifier', flush=True)
    tasks = [ts[i:i + 24] for i in range(0, len(ts), 24)]
    allh = []; t0 = time.time(); n = 0
    with Pool(int(os.environ.get('NPROC', 20)), initializer=M.init) as pool:
        for h in pool.imap_unordered(task, tasks):
            allh += h; n += 1
            if n % 10 == 0: print(n, '/', len(tasks), round(time.time() - t0), 's', flush=True)
    allh.sort()
    print('RESULTAT :', len(allh), 'occurrence(s) restante(s)')
    for h in allh: print(h)
