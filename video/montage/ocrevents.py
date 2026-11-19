"""OCR evenementiel : lit les images retenues par events.py (chaque changement notable de l'ecran) dans les rushs retimes, detecte les
identifiants a masquer et ecrit plan/<id>.masks.json = [[t0, t1, x, y, w, h], ...] (secondes de la scene, pixels 1920x1080).
A lancer avec le python du venv de la voix (rapidocr). Usage : python ocrevents.py [ids...]"""
import json, os, subprocess, sys, time
import numpy as np
import ocrmask as M

NPROC = int(os.environ.get('NPROC', 18)); CHUNK = 24
BASE = os.environ.get('OCR_SRC_DIR', os.path.join(M.HERE, 'work', 'conf'))

def frame(src, t):
    r = subprocess.run([M.FF, '-v', 'error', '-ss', f'{max(0, t):.3f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    if len(r.stdout) < M.W * M.H * 3: return None
    return np.frombuffer(r.stdout, np.uint8).reshape(M.H, M.W, 3)

def lines(img, scale=1.0):
    """[(texte, x0, y0, x1, y1)] en pixels 1920x1080 ; scale > 1 : image agrandie (meilleur rappel sur le petit texte)."""
    import cv2
    im = img if scale == 1.0 else cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    res, _ = M._ocr(im[:, :, ::-1]); out = []
    for box, txt, conf in (res or []):
        xs = [q[0] / scale for q in box]; ys = [q[1] / scale for q in box]
        out.append((txt, min(xs), min(ys), max(xs), max(ys)))
    return out

def matches(ls):
    cur = []
    for txt, x0, y0, x1, y1 in ls:
        low = txt.replace(' ', '').lower()
        if any(k and k.replace(' ', '').lower() in low for k in M.KEYS + M.PARTS) or 'accountfullaccessrole' in low:
            cur.append((max(0, x0 - 8), y0 - 4, min(M.W, x1 + 8), y1 + 4))      # on masque toujours la ligne entiere
    return cur

def task(a):
    sid, times = a
    src = os.path.join(BASE, sid + '.mp4'); out = []
    for t in times:
        img = frame(src, t)
        if img is None: continue
        cur = matches(lines(img))
        if cur: cur += matches(lines(img, 1.4))          # 2e passe sur les images qui contiennent un identifiant
        out.append((t, cur))
    return sid, out

def build(times, hits, dur):
    """hits : {t: [(x0,y0,x1,y1)]} -> fenetres [t0,t1,x,y,w,h] (une fenetre court d'un evenement jusqu'au suivant)."""
    spans = []; open_ = []
    for k, t in enumerate(times):
        nxt = times[k + 1] if k + 1 < len(times) else dur
        newopen = []
        for (x0, y0, x1, y1) in hits.get(t, []):
            for s in open_:
                if not (x1 < s['x0'] - 25 or x0 > s['x1'] + 25 or y1 < s['y0'] - 12 or y0 > s['y1'] + 12):
                    s['t1'] = nxt; s['x0'] = min(s['x0'], x0); s['y0'] = min(s['y0'], y0); s['x1'] = max(s['x1'], x1); s['y1'] = max(s['y1'], y1)
                    newopen.append(s); open_.remove(s); break
            else:
                s = dict(t0=t, t1=nxt, x0=x0, y0=y0, x1=x1, y1=y1); spans.append(s); newopen.append(s)
        open_ = newopen
    return [[round(max(0, s['t0'] - 0.07), 3), round(s['t1'] + 0.03, 3), round(s['x0']), round(s['y0']), round(s['x1'] - s['x0']), round(s['y1'] - s['y0'])] for s in spans]

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = sys.argv[1:] or json.load(open(os.path.join(M.HERE, 'used.json')))
    ev = {sid: json.load(open(os.path.join(M.HERE, 'work', 'events', sid + '.json'))) for sid in ids}
    tasks = []
    only = os.environ.get('ONLY_WINDOWS') == '1'
    for sid in ids:
        T = ev[sid]
        if only:
            old = json.load(open(os.path.join(M.HERE, 'plan_masks_v3', sid + '.masks.json')))
            T = sorted(set([t for t in T if any(w[0] - 0.02 <= t <= w[1] for w in old)] + T[:4]))
        for i in range(0, len(T), CHUNK): tasks.append((sid, T[i:i + CHUNK]))
    print(len(tasks), 'taches', flush=True)
    hits = {sid: {} for sid in ids}; t00 = time.time(); n = 0
    with Pool(NPROC, initializer=M.init) as pool:
        for sid, out in pool.imap_unordered(task, tasks):
            for t, cur in out:
                if cur: hits[sid][t] = cur
            n += 1
            if n % 15 == 0: print(n, '/', len(tasks), round(time.time() - t00), 's', flush=True)
    tot = 0
    for sid in ids:
        d = M.dur(sid); out = build(ev[sid], hits[sid], d); tot += len(out)
        json.dump(out, open(os.path.join(M.HERE, 'plan', sid + '.masks.json'), 'w'))
    print('termine :', tot, 'masques', round(time.time() - t00), 's', flush=True)
