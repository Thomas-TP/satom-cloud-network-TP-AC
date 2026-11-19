"""Sondage rapide : 4 images par scene -> quelles scenes montrent un identifiant a masquer ? (python du venv de la voix)"""
import json, os, subprocess, sys, time
import numpy as np
import ocrmask as M

def work(sid):
    d = M.dur(sid); hits = []
    for q in (0.2, 0.4, 0.6, 0.8):
        t = d * q
        r = subprocess.run([M.FF, '-v', 'error', '-ss', f'{t:.2f}', '-i', os.path.join(M.HERE, 'work', 'conf', sid + '.mp4'), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        if len(r.stdout) < M.W * M.H * 3: continue
        img = np.frombuffer(r.stdout, np.uint8).reshape(M.H, M.W, 3)
        res, _ = M._ocr(img[:, :, ::-1])
        for box, txt, conf in (res or []):
            low = txt.replace(' ', '').lower()
            for key in M.KEYS + M.PARTS:
                if key and key.replace(' ', '').lower() in low: hits.append((round(t, 1), txt[:60])); break
    return sid, hits

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = json.load(open(os.path.join(M.HERE, 'used.json'))); out = {}
    t0 = time.time()
    with Pool(12, initializer=M.init) as pool:
        for sid, h in pool.imap_unordered(work, ids):
            out[sid] = h
            if h: print(sid, h[:2], flush=True)
    json.dump(out, open('survey.json', 'w')); print('fin', round(time.time() - t0))
