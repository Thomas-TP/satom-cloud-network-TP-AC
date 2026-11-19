"""Images a OCRiser : on parcourt chaque rush retime a 30 i/s (miniature 240x135) et on retient toute image qui differe notablement de la derniere retenue.
Sortie : work/events/<id>.json = liste de temps (s)."""
import json, os, subprocess, sys
import numpy as np
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(HERE, 'work', 'events'), exist_ok=True)
W, H = 240, 135
MEAN_THR = float(os.environ.get('EV_MEAN', 0.6)); FRAC_THR = float(os.environ.get('EV_FRAC', 0.012))

def ev(sid):
    src = os.path.join(HERE, 'work', 'conf', sid + '.mp4')
    r = subprocess.run([FF, '-v', 'error', '-i', src, '-vf', f'scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-'], capture_output=True)
    n = len(r.stdout) // (W * H); fr = np.frombuffer(r.stdout[:n * W * H], np.uint8).reshape(n, H, W).astype(np.int16)
    out = [0.0]; ref = fr[0]
    for i in range(1, n):
        d = np.abs(fr[i] - ref)
        if d.mean() >= MEAN_THR or (d > 25).mean() >= FRAC_THR: out.append(round(i / 30, 3)); ref = fr[i]
    json.dump(out, open(os.path.join(HERE, 'work', 'events', sid + '.json'), 'w'))
    return sid, n, len(out)

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json'))); tn = te = 0
    with Pool(16) as p:
        for sid, n, e in p.imap_unordered(ev, ids): tn += n; te += e
    print('images', tn, 'retenues', te)
