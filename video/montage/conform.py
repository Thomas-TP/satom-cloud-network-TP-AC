"""Retime un rush selon son plan : selection d'images (coupes + vitesses), masquage du compte, encodage CFR 30 i/s.
Usage : python conform.py m02a [m02b ...]   ->  work/conf/<id>.mp4"""
import json, os, subprocess, sys
import numpy as np
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'work', 'conf'); os.makedirs(OUT, exist_ok=True)
FPS = 30

def dark_intervals(sid, minlen=1.0):
    a = json.load(open(os.path.join(HERE, 'analyse', sid + '.json')))
    lum = np.array(a['lum']); d = lum < 90; out = []; s = None
    for i, v in enumerate(list(d) + [False]):
        if v and s is None: s = i
        if not v and s is not None:
            if (i - s) * 0.1 >= minlen: out.append((s * 0.1, i * 0.1))
            s = None
    return out

def script(sid):
    p = json.load(open(os.path.join(HERE, 'plan', sid + '.json')))
    segs = []
    for sg in p['segs']:
        a = int(round(sg['a'] * FPS)); b = int(round(sg['b'] * FPS)) - 1
        if b >= a: segs.append((a, b, sg['speed']))
    def leaf(a, b, sp):
        if sp <= 1.0001: return f'between(n,{a},{b})'
        return f'between(n,{a},{b})*gt(floor((n-{a})/{sp:.5f}),floor((n-1-{a})/{sp:.5f}))'
    def build(lo, hi):
        if hi - lo == 1: return leaf(*segs[lo])
        mid = (lo + hi) // 2
        return f'if(lt(n,{segs[mid][0]}),{build(lo, mid)},{build(mid, hi)})'
    sel = build(0, len(segs))
    dk = dark_intervals(sid); en_term = '+'.join('between(t,%.2f,%.2f)' % d for d in dk) or '0'
    flt = f"select='{sel}',delogo=x=1596:y=3:w=320:h=46:enable='not({en_term})',delogo=x=4:y=4:w=530:h=36:enable='{en_term}'"
    for (x, y, w, h, t0, t1) in p.get('boxes', []): flt += f",delogo=x={x}:y={y}:w={w}:h={h}:enable='between(t,{t0},{t1})'"
    flt += f",setpts=N/{FPS}/TB,fps={FPS}"
    return flt, p

def run(sid):
    flt, p = script(sid)
    sp = os.path.join(OUT, sid + '.filter.txt'); open(sp, 'w').write(flt)
    out = os.path.join(OUT, sid + '.mp4')
    cmd = [FF, '-y', '-loglevel', 'error', '-i', os.path.join(ROOT, 'raw', sid + '.mp4'), '-/vf', sp, '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15',
           '-pix_fmt', 'yuv420p', '-x264-params', 'keyint=15:min-keyint=15:scenecut=0', '-r', str(FPS), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: return sid, 'ERR ' + r.stderr[-300:]
    d = float(subprocess.run([FF.replace('ffmpeg.exe', 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    return sid, round(d, 2), p['out_len']

if __name__ == '__main__':
    from multiprocessing import Pool
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json')))
    with Pool(8) as pool:
        for r in pool.imap_unordered(run, ids): print(r, flush=True)
