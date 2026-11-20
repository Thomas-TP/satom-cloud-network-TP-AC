"""Assemble la piste voix a partir des phrases etalonnees et de la chronologie (video/voix/lignes.json recalculee avec les durees reelles).
Usage : python assemble.py durees               -> ecrit final/durees_reelles.json (duree de chaque phrase etalonnee)
        python assemble.py piste [scenes...]    -> final/piste.wav (toute la video, ou seulement les scenes donnees, a partir de leur debut)
Niveau final de la piste : -16 LUFS integre, crete vraie <= -1,5 dBTP (deux passes)."""
import os, sys, json, glob, numpy as np, soundfile as sf, scipy.signal as ss, pyloudnorm as pyln
V = r'C:\Perso\voice'; M = V + r'\final\master'; SR = 48000
def load48(p):
    w, sr = sf.read(p, dtype='float32'); w = w if w.ndim == 1 else w.mean(1)
    return ss.resample_poly(w, SR // sr, 1) if SR % sr == 0 else w
if sys.argv[1] == 'durees':
    d = {os.path.basename(f)[:-4]: round(sf.info(f).duration, 3) for f in glob.glob(M + r'\*.wav')}
    json.dump(d, open(V + r'\final\durees_reelles.json', 'w'), indent=0); print(len(d), 'durees ecrites')
else:
    scenes = sys.argv[2:]
    D = json.load(open(r'C:\Perso\AWS\video\voix\lignes.json', encoding='utf8')); S = D['scenes']
    sel = [s for s in S if (not scenes or s['id'] in scenes)]; t0 = sel[0]['start'] if sel else 0
    end = max([p['end'] for s in sel for p in s['lines']] + [sel[-1]['start'] + sel[-1]['dur']]) - t0 + 1.0
    track = np.zeros(int(end * SR) + SR, dtype=np.float32); missing = []
    for s in sel:
        for p in s['lines']:
            f = f"{M}\\{p['id']}.wav"
            if not os.path.exists(f): missing.append(p['id']); continue
            w = load48(f); i = int((p['start'] - t0) * SR); track[i:i + len(w)] += w[:len(track) - i]
    meter = pyln.Meter(SR); l = meter.integrated_loudness(track); y = track * 10 ** ((-16.0 - l) / 20)
    sys.path.insert(0, os.path.join(V, 'final')); import dsp
    for _ in range(3):        # gain -> limiteur de crete (plafond -2 dB pour viser -1,5 dBTP) -> re-mesure, jusqu'a -16 LUFS integre
        y = dsp.limit(y, -2.4, SR); cur = meter.integrated_loudness(y)
        if abs(cur + 16.0) < 0.25: break
        y = y * 10 ** ((-16.0 - cur) / 20)
    y = dsp.limit(y, -2.4, SR)
    sf.write(V + r'\final\piste.wav', y, SR, subtype='PCM_16')
    print(f'piste : {len(y) / SR / 60:.1f} min, niveau {meter.integrated_loudness(y):.1f} LUFS, crete {20 * np.log10(np.abs(y).max()):.1f} dB, manquantes {len(missing)}')
    json.dump(dict(t0=t0), open(V + r'\final\piste_info.json', 'w'))
