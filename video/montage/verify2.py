"""Verification evenementielle de la video finale : OCR de chaque image qui change notablement. Usage : python verify2.py video.mp4"""
import json, os, subprocess, sys, time
import numpy as np
import ocrmask as M
SRC = sys.argv[1]
W_, H_ = 240, 135

def events():
    r = subprocess.run([M.FF, '-v', 'error', '-i', SRC, '-vf', f'scale={W_}:{H_}:flags=area,format=gray', '-f', 'rawvideo', '-'], capture_output=True)
    n = len(r.stdout) // (W_ * H_); fr = np.frombuffer(r.stdout[:n * W_ * H_], np.uint8).reshape(n, H_, W_).astype(np.int16)
    out = [0.0]; ref = fr[0]
    for i in range(1, n):
        d = np.abs(fr[i] - ref)
        if d.mean() >= 0.6 or (d > 25).mean() >= 0.012: out.append(round(i / 30, 3)); ref = fr[i]
    return out

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
    ev = events(); print(len(ev), 'images a verifier', flush=True)
    tasks = [ev[i:i + 24] for i in range(0, len(ev), 24)]
    allh = []; t0 = time.time(); n = 0
    with Pool(int(os.environ.get('NPROC', 18)), initializer=M.init) as pool:
        for h in pool.imap_unordered(task, tasks):
            allh += h; n += 1
            if n % 15 == 0: print(n, '/', len(tasks), round(time.time() - t0), 's', flush=True)
    allh.sort()
    print('RESULTAT :', len(allh), 'occurrence(s) restante(s)')
    for h in allh: print(h)
