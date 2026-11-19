"""Analyse d'un rush : activite (10 Hz), clics (anneaux bleus du rig), luminance, blanc/sombre. Sortie : analyse/<id>.json"""
import json, os, subprocess, sys
import numpy as np
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(os.path.dirname(HERE), 'raw')
W, H = 960, 540

def run(name):
    out = os.path.join(HERE, 'analyse', name + '.json')
    src = os.path.join(RAW, name + '.mp4')
    p = subprocess.Popen([FF, '-v', 'error', '-i', src, '-vf', f'fps=10,scale={W}:{H}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = W * H * 3; prev = None; act = []; lum = []; ink = []; cen = []; clicks = []; ripple = []; pm = [None, None, None]
    i = 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        a = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        g = a.astype(np.int16).mean(axis=2)
        lum.append(float(g.mean()))
        small = g[::2, ::2]
        if prev is None: act.append(0.0); cen.append((0, 0, 0, 0, 0, 0))
        else:
            dm = np.abs(small - prev) > 18; cnt = int(dm.sum()); act.append(cnt)
            if cnt:
                ys, xs = np.nonzero(dm); cen.append((round(float(xs.mean()) * 4), round(float(ys.mean()) * 4), round(float(xs.min()) * 4), round(float(ys.min()) * 4), round(float(xs.max()) * 4), round(float(ys.max()) * 4)))
            else: cen.append((0, 0, 0, 0, 0, 0))
        prev = small
        R = a[..., 0].astype(np.int16); G = a[..., 1].astype(np.int16); B = a[..., 2].astype(np.int16)
        m = (abs(R - 79) < 28) & (abs(G - 140) < 28) & (B > 232)
        old = pm[0]
        new = m if old is None else (m & ~old)
        pm = pm[1:] + [m | (pm[2] if pm[2] is not None else False)]
        ink.append(round(float((g[60:500, 90:960] < 200).mean()), 4))
        c = int(new.sum())
        if c > 25:
            ys, xs = np.nonzero(new); ripple.append((i, float(xs.mean()) * 2, float(ys.mean()) * 2, c))
        i += 1
    p.wait()
    # regroupe les detections consecutives en clics (premiere image)
    last = -9
    for (k, x, y, c) in ripple:
        if k - last > 3: clicks.append({'t': round(k / 10, 2), 'x': round(x), 'y': round(y)})
        last = k
    json.dump({'id': name, 'n': i, 'act': act, 'cen': cen, 'lum': [round(x, 1) for x in lum], 'ink': ink, 'clicks': clicks}, open(out, 'w'))
    return name, i, len(clicks)

if __name__ == '__main__':
    names = sys.argv[1:]
    for n in names: print(run(n), flush=True)
