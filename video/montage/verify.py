"""Verification finale : OCR de la video rendue (1 image par seconde, images quasi identiques ignorees). Affiche toute occurrence restante
de l'identifiant de compte / session / organisation. Usage : python verify.py chemin.mp4"""
import json, os, subprocess, sys, time
import numpy as np
import ocrmask as M
SRC = sys.argv[1] if len(sys.argv) > 1 else r'C:\Perso\AWS\video\montage\rm\out\final.mp4'
CH = 30.0; STEP = 1.0

def task(a):
    t0, t1 = a
    p = subprocess.Popen([M.FF, '-v', 'error', '-ss', f'{t0:.2f}', '-t', f'{t1 - t0:.2f}', '-i', SRC, '-vf', f'fps={1 / STEP},format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    hits = []; k = 0; prev = None
    while True:
        buf = p.stdout.read(M.W * M.H * 3)
        if len(buf) < M.W * M.H * 3: break
        img = np.frombuffer(buf, np.uint8).reshape(M.H, M.W, 3); t = t0 + k * STEP; k += 1
        small = img[::8, ::8].mean(axis=2)
        if prev is not None and np.abs(small - prev).mean() < 0.4: continue
        prev = small
        res, _ = M._ocr(img[:, :, ::-1])
        for box, txt, conf in (res or []):
            low = txt.replace(' ', '').lower()
            for key in M.KEYS + M.PARTS:
                kk = key.replace(' ', '').lower()
                if kk and kk in low: hits.append((round(t, 1), txt[:70], [round(box[0][0]), round(box[0][1])])); break
    p.wait()
    return hits

if __name__ == '__main__':
    from multiprocessing import Pool
    d = float(subprocess.run([M.FF.replace('ffmpeg.exe', 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC], capture_output=True, text=True).stdout)
    tasks = []; t = 0.0
    while t < d: tasks.append((t, min(d, t + CH))); t += CH
    allh = []; t00 = time.time(); n = 0
    with Pool(12, initializer=M.init) as pool:
        for h in pool.imap_unordered(task, tasks):
            allh += h; n += 1
            if n % 10 == 0: print(n, '/', len(tasks), round(time.time() - t00), 's', flush=True)
    allh.sort()
    print('RESULTAT :', len(allh), 'occurrence(s) restante(s)')
    for h in allh: print(h)
