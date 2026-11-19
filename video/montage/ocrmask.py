"""Detecte par OCR les identifiants a masquer (compte, identite de session, organisation) dans les rushs retimes et ecrit plan/<id>.masks.json :
[[t0, t1, x, y, w, h], ...] en secondes de la scene et pixels 1920x1080 (espace video).
A lancer avec le python du venv de la voix (rapidocr). Usage : python ocrmask.py [ids...]"""
import json, os, subprocess, sys, time
import numpy as np
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__))
MASKS = json.load(open(r'C:\Perso\AWS\video\rig\profile\masks.json', encoding='utf-8'))
KEYS = [v for v in MASKS.values() if v]
PARTS = [k[:7] for k in KEYS] + [k[-6:] for k in KEYS if len(k) >= 12]
STEP = 0.5; CHUNK = 20.0       # secondes de scene par tache
W, H = 1920, 1080
_ocr = None

def init():
    global _ocr
    from rapidocr_onnxruntime import RapidOCR
    _ocr = RapidOCR(intra_op_num_threads=1, inter_op_num_threads=1)

def task(a):
    sid, t0, t1 = a
    src = os.path.join(HERE, 'work', 'conf', sid + '.mp4')
    p = subprocess.Popen([FF, '-v', 'error', '-ss', f'{t0:.2f}', '-t', f'{t1 - t0:.2f}', '-i', src, '-vf', f'fps={1 / STEP},format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    hits = []; k = 0; prev = None; prev_hits = []
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        small = img[::8, ::8].mean(axis=2)
        t = t0 + k * STEP; k += 1
        if prev is not None and np.abs(small - prev).mean() < 0.5:       # image quasi identique : on reprend les detections precedentes
            hits += [(t, *h[1:]) for h in prev_hits]; continue
        prev = small; cur = []
        res, _ = _ocr(img[:, :, ::-1])
        for box, txt, conf in (res or []):
            low = txt.replace(' ', '').lower()
            for key in KEYS + PARTS:
                kk = key.replace(' ', '').lower()
                if kk and kk in low:
                    xs = [q[0] for q in box]; ys = [q[1] for q in box]
                    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                    i = low.find(kk); L = max(len(low), 1)
                    a_ = x0 + (x1 - x0) * i / L; b_ = x0 + (x1 - x0) * (i + max(len(kk), 12)) / L
                    if len(kk) < 12: a_ = x0 + (x1 - x0) * max(0, i - 5) / L; b_ = x0 + (x1 - x0) * min(L, i + 14) / L
                    cur.append((t, max(0, a_ - 8), y0 - 4, min(W, b_ + 8), y1 + 4)); break
        hits += cur; prev_hits = cur
    p.wait()
    return sid, hits

def merge(hits):
    spans = []
    for t, x0, y0, x1, y1 in sorted(hits):
        for s in spans:
            if abs(s[1] - t) <= STEP * 1.6 and not (x1 < s[2] - 20 or x0 > s[4] + 20 or y1 < s[3] - 10 or y0 > s[5] + 10):
                s[1] = t; s[2] = min(s[2], x0); s[3] = min(s[3], y0); s[4] = max(s[4], x1); s[5] = max(s[5], y1); break
        else: spans.append([t, t, x0, y0, x1, y1])
    return [[round(max(0, s[0] - 0.35), 2), round(s[1] + STEP + 0.35, 2), round(s[2]), round(s[3]), round(s[4] - s[2]), round(s[5] - s[3])] for s in spans]

def dur(sid):
    r = subprocess.run([FF.replace('ffmpeg.exe', 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(HERE, 'work', 'conf', sid + '.mp4')], capture_output=True, text=True)
    return float(r.stdout)

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json')))
    tasks = []
    for sid in ids:
        d = dur(sid); t = 0.0
        while t < d: tasks.append((sid, t, min(d, t + CHUNK))); t += CHUNK
    print(len(tasks), 'taches', flush=True)
    allhits = {sid: [] for sid in ids}; t00 = time.time(); done = 0
    with Pool(12, initializer=init) as pool:
        for sid, hits in pool.imap_unordered(task, tasks):
            allhits[sid] += hits; done += 1
            if done % 20 == 0: print(done, '/', len(tasks), round(time.time() - t00), 's', flush=True)
    tot = 0
    for sid, hits in allhits.items():
        out = merge(hits); tot += len(out)
        json.dump(out, open(os.path.join(HERE, 'plan', sid + '.masks.json'), 'w'))
    print('termine :', tot, 'masques', round(time.time() - t00), 's')
