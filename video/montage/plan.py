"""Plan de montage d'un rush : coupes (chargements, temps morts), vitesses, badges d'acceleration, trajectoire de camera (zoom).
Usage : python plan.py m02a [m02b ...]   (ecrit plan/<id>.json et affiche un resume)"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, 'raw'); DT = 0.1
os.makedirs(os.path.join(HERE, 'plan'), exist_ok=True)
NO_LOADING = {'m09g'}                     # pages blanches legitimes (reponse de l'API dans le navigateur)
EXTRA_BOXES = {'m01a': [(1500, 486, 170, 28, 42, 60)]}   # (x, y, w, h, t0, t1) en secondes du brut

P = dict(static_hold=0.30, static_prot=1.5, typing_speed=3.2, change_speed=1.5, long_run=6.0, acc_min=2.0, acc_max=4.5, mark_before=0.15, mark_after=1.5, min_run=6)

def load(sid):
    a = json.load(open(os.path.join(HERE, 'analyse', sid + '.json')))
    mp = os.path.join(RAW, sid + '.marks.json')
    marks = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else []
    return a, marks

def rle(keys):
    out = []; s = 0
    for i in range(1, len(keys) + 1):
        if i == len(keys) or keys[i] != keys[s]: out.append([s, i, keys[s]]); s = i
    return out

def plan_once(sid, p=P, write=True):
    a, marks = load(sid)
    act = np.array(a['act']); lum = np.array(a['lum']); ink = np.array(a['ink']); n = len(act)
    cen = a['cen']
    t_of = lambda i: i * DT
    # chargements : page presque vide et claire
    load_ = (ink < 0.004) & (lum > 200) if sid not in NO_LOADING else np.zeros(n, bool)
    # ne couper que les runs de chargement >= 0.4 s
    for s, e, k in rle(list(load_)):
        if k and (e - s) < 4: load_[s:e] = False
    # intervalles accelere
    accel = np.zeros(n, int); aid = np.zeros(n, int); intervals = []
    ends = {m['name'][:-4]: m['t'] for m in marks if m['name'].endswith('-fin')}
    for m in marks:
        if m['name'].endswith('-debut') and 'accelere' in m:
            key = m['name'][:-6]; t0 = m['t']; t1 = ends.get(key, n * DT)
            intervals.append((t0, t1, m['accelere']))
    for k, (t0, t1, N) in enumerate(intervals, 1):
        i0, i1 = int(round(t0 / DT)), min(n, int(round(t1 / DT)))
        accel[i0:i1] = N; aid[i0:i1] = k
    prot = np.zeros(n, bool)
    for m in marks:
        if m['name'].endswith(('-debut', '-fin')): continue
        i0 = max(0, int((m['t'] - p['mark_before']) / DT)); i1 = min(n, int((m['t'] + p['mark_after']) / DT) + 1)
        prot[i0:i1] = True
    dark = lum < 90
    cls = np.where(act == 0, 0, np.where(act <= 30, 1, 2))     # 0 immobile, 1 curseur/frappe, 2 changement
    keys = []
    for i in range(n):
        if load_[i]: keys.append(('L', 0, False))
        elif accel[i]: keys.append(('A', int(aid[i]), bool(dark[i])))
        else: keys.append((int(cls[i]), int(prot[i]), bool(dark[i])))
    # absorbe les runs trop courts (< 0.4 s) dans le precedent
    for _ in range(3):
        runs = rle(keys)
        for r, (s, e, k) in enumerate(runs):
            if e - s < p['min_run'] and k[0] in (0, 1, 2) and len(runs) > 1:
                nb = runs[r - 1][2] if r > 0 else runs[r + 1][2]
                if nb[0] in (0, 1, 2) or nb[0] == 'A':
                    for i in range(s, e): keys[i] = (nb[0], keys[i][1], keys[i][2]) if nb[0] != 'A' else keys[i]
    segs = []     # (i0, i1, speed, kind, dark)
    for s, e, k in rle(keys):
        L = (e - s) * DT; kind = k[0]
        if kind == 'L': continue
        if kind == 'A':
            segs.append((s, e, ('A', k[1]), 'acc', k[2])); continue
        if kind == 0:
            hold = min(L, p['static_prot'] if k[1] else p['static_hold'])
            segs.append((s, e, L / hold, 'static', k[2]))
        elif kind == 1:
            segs.append((s, e, p['typing_speed'] if not k[1] else 1.8, 'move', k[2]))
        else:
            sp = p['change_speed']
            if L > p['long_run']: sp = L / (p['long_run'] / p['change_speed'] + (L - p['long_run']) * 0.12)
            segs.append((s, e, sp, 'change', k[2]))
    # intervalles accelere : duree de sortie globale par intervalle (repartie sur ses segments)
    tot = {}
    for (s, e, sp, kind, dk) in segs:
        if kind == 'acc': tot[sp[1]] = tot.get(sp[1], 0) + (e - s) * DT
    fix = {}
    for aid_, Lk in tot.items():
        N = intervals[aid_ - 1][2]; out = min(max(Lk / max(N, 1), p['acc_min']), p['acc_max']); out = min(out, Lk); fix[aid_] = Lk / out
    segs = [(s, e, fix[sp[1]] if kind == 'acc' else sp, kind, dk) for (s, e, sp, kind, dk) in segs]
    # fusionne les segments consecutifs de meme vitesse arrondie
    merged = []
    for sg in segs:
        if merged and merged[-1][1] == sg[0] and merged[-1][3] == sg[3] and merged[-1][4] == sg[4] and abs(merged[-1][2] - sg[2]) < 0.05:
            merged[-1] = (merged[-1][0], sg[1], merged[-1][2], sg[3], sg[4])
        else: merged.append(sg)
    segs = merged
    ov = p.get('over', 1.0)
    if ov > 1.0: segs = [(s, e, sp * ov if kind != 'acc' else sp, kind, dk) for (s, e, sp, kind, dk) in segs]
    # images retenues, exactement comme conform.py (select) ; temps de sortie exacts
    FPS = 30; frames = []; seg_out = []
    for (s_, e_, sp, kind, dk) in segs:
        a_ = int(round(s_ * DT * FPS)); b_ = int(round(e_ * DT * FPS)) - 1
        c0 = len(frames)
        for nfr in range(a_, b_ + 1):
            if sp <= 1.0001 or int(np.floor((nfr - a_) / sp)) > int(np.floor((nfr - 1 - a_) / sp)): frames.append(nfr)
        seg_out.append((c0 / FPS, len(frames) / FPS))
    frames = np.array(frames); total = len(frames) / FPS
    out_t = np.full(n + 1, np.nan); kept = np.zeros(n, bool)
    for i in range(n):
        k = int(np.searchsorted(frames, i * 3))
        if k < len(frames) and frames[k] < i * 3 + 3: kept[i] = True; out_t[i] = k / FPS
    # badges
    raw_b = [[a_, b_, sp] for (a_, b_), (s, e, sp, kind, dk) in zip(seg_out, segs) if (kind == 'acc' and sp >= 3.0) or (kind == 'change' and sp >= 9.0)]
    mb = []
    for x in raw_b:
        if mb and x[0] - mb[-1][1] < 0.35: mb[-1][1] = x[1]; mb[-1][2] = max(mb[-1][2], x[2])
        else: mb.append(list(x))
    badges = [(round(a_, 2), round(b_, 2), int(round(sp))) for a_, b_, sp in mb if b_ - a_ >= 1.4]
    # evenements de camera
    ev = []      # (t_out, x, y, poids)
    for c in a['clicks']:
        i = int(round(c['t'] / DT))
        if i < n and kept[i] and not (c['x'] < 90 and c['y'] < 160): ev.append((out_t[i], c['x'], c['y'], 6.0))
    for i in range(n):
        if kept[i] and 3 <= act[i] <= 2500 and cen[i][0] > 0: ev.append((out_t[i], cen[i][0], cen[i][1], 1.0))
    big = [(out_t[i]) for i in range(n) if kept[i] and act[i] > 3000]
    keys_cam, tgt = camera(ev, big, total, bool(dark[kept].mean() > 0.5) if kept.any() else False)
    # delogo : zones de masquage (secondes du brut)
    res = dict(id=sid, raw_len=n * DT, out_len=round(total, 2),
               segs=[dict(a=round(s * DT, 2), b=round(e * DT, 2), speed=round(sp, 3), kind=kind, dark=bool(dk)) for (s, e, sp, kind, dk) in segs],
               badges=badges, cam=keys_cam, tgt=[[round(a_, 1), round(b_, 1), round(c_, 3)] for a_, b_, c_ in tgt], boxes=EXTRA_BOXES.get(sid, []),
               marks=[(m['name'], round(float(out_t[min(n - 1, int(m['t'] / DT))]), 2)) for m in marks if kept[min(n - 1, int(m['t'] / DT))]])
    res['active'] = float(((act > 0) & ~load_ & (accel == 0)).sum() * DT)
    if write: json.dump(res, open(os.path.join(HERE, 'plan', sid + '.json'), 'w'))
    return res

def camera(ev, big, total, terminal, hz=20, zmax=1.55):
    """Trajectoire [t, cx, cy, zoom] lissee (filtre du second ordre) : suit les clics et les zones qui changent."""
    n = int(total * hz) + 1
    if not ev: return smooth(np.tile([960, 540, 1.0], (n, 1)), hz), [[960, 540, 1.0]] * n
    E = np.array(ev); ts = E[:, 0]
    bigt = np.array(big) if big else np.array([-9.0])
    tgt = np.zeros((n, 3)); last = None
    for k in range(n):
        t = k / hz
        sel = (ts > t - 0.7) & (ts < t + 0.4)
        w = E[sel, 3]
        if w.sum() >= 2.0:
            cx = float((E[sel, 1] * w).sum() / w.sum()); cy = float((E[sel, 2] * w).sum() / w.sum())
            wide = (ts > t - 2.0) & (ts < t + 1.0)
            bw = E[wide, 1].max() - E[wide, 1].min(); bh = E[wide, 2].max() - E[wide, 2].min()
            z = min(zmax, 1920 / (bw + 560), 1080 / (bh + 380)); z = 1.0 if z < 1.18 else z
            last = (t, cx, cy, z)
        elif last is not None and t - last[0] < 2.2:
            pass
        else: last = None
        if np.any((bigt > t - 0.8) & (bigt < t + 0.1)): last = None
        tgt[k] = (last[1], last[2], last[3]) if last else (960, 540, 1.0)
    return smooth(tgt, hz), tgt.tolist()

def smooth(tgt, hz=20):
    n = len(tgt); tgt = np.array(tgt, float)
    # lissage : deux filtres du premier ordre en cascade (critiquement amorti)
    out = np.zeros_like(tgt); a1 = np.array(tgt[0]); a2 = np.array(tgt[0]); dt = 1 / hz; om = 4.2
    al = 1 - np.exp(-om * dt)
    for k in range(n):
        a1 += (tgt[k] - a1) * al; a2 += (a1 - a2) * al; out[k] = a2
    res = []
    for k in range(n):
        z = float(out[k][2]); cx = float(out[k][0]); cy = float(out[k][1])
        cx = min(max(cx, 960 / z), 1920 - 960 / z); cy = min(max(cy, 540 / z), 1080 - 540 / z)
        res.append([round(k / hz, 3), round(cx, 1), round(cy, 1), round(z, 4)])
    return res

BUDGET = dict(base=3.5, k=0.10, lo=5.0, hi=40.0)

# scenes qui repetent une procedure deja montree : budget reduit
REPEAT = {'m07c2': 0.35, 'm07e2': 0.35, 'm07n2': 0.4, 'm05a1': 0.7, 'm05a2': 0.7, 'm05b1': 0.5, 'm05b2': 0.5, 'm05c1': 0.6, 'm05c2': 0.6, 'm06c': 0.6, 'm08f': 0.5, 'm02c': 0.7, 'm11e2': 0.6, 'm07j': 0.8}

# duree minimale (s) demandee par la voix pour certaines scenes refilmees (vrai domaine)
MINB = {'m10c': 13.0, 'm11d': 15.0, 'm11d2': 9.0, 'm11g': 38.0, 'm10d': 9.5, 'm09g': 8.0}

def plan(sid):
    r0 = plan_once(sid, P, write=False)
    B = min(max(BUDGET['base'] + BUDGET['k'] * r0['active'], BUDGET['lo']), BUDGET['hi']) * REPEAT.get(sid, 1.0)
    B = max(B, MINB.get(sid, 0))
    f = 1.0; best = r0
    for f in (1.0, 1.25, 1.55, 1.9, 2.3, 2.7):
        p = dict(P); p['typing_speed'] = P['typing_speed'] * f; p['change_speed'] = P['change_speed'] * f
        p['static_hold'] = max(0.09, P['static_hold'] / f); p['static_prot'] = max(1.0, P['static_prot'] - 0.15 * (f - 1)); p['acc_max'] = P['acc_max']
        best = plan_once(sid, p, write=False)
        if best['out_len'] <= B: break
    if best['out_len'] > B: p['over'] = min(1.4, best['out_len'] / B)
    best = plan_once(sid, p, write=True); best['budget'] = round(B, 1); best['factor'] = f
    json.dump(best, open(os.path.join(HERE, 'plan', sid + '.json'), 'w'))
    return best

if __name__ == '__main__':
    ids = sys.argv[1:] or json.load(open(os.path.join(HERE, 'used.json')))
    tot_raw = tot_out = 0
    for sid in ids:
        r = plan(sid); tot_raw += r['raw_len']; tot_out += r['out_len']
        print(f"{sid:7s} brut {r['raw_len']:6.1f}s actif {r['active']:6.1f}s -> {r['out_len']:6.1f}s (budget {r['budget']:5.1f}, x{r['factor']})  segs {len(r['segs']):3d}  badges {len(r['badges'])}", flush=True)
    print(f'TOTAL brut {tot_raw/60:.1f} min -> {tot_out/60:.1f} min')
