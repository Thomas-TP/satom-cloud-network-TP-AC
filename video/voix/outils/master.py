"""Etalonnage des prises retenues, fidele a la vraie voix.
Chaine : rognage -> passe-haut 75 Hz -> correction de timbre mesuree sur la vraie voix (<= +/-3 dB) -> compresseur doux -> niveau commun.
Usage : python master.py eq     (calcule la courbe de correction de chaque voix et l'ecrit dans final/eq_<voix>.json)
        python master.py clips  (applique la chaine aux prises retenues -> final/master/<ligne>.wav)"""
import os, sys, json, glob, numpy as np, soundfile as sf
sys.path.insert(0, r'C:\Perso\voice\essai')
import spec
from pedalboard import time_stretch, Pedalboard, HighpassFilter, PeakFilter, Compressor, Limiter
import pyloudnorm as pyln
import scipy.signal as ss
import dsp
V = r'C:\Perso\voice'; SR = 24000
TEMPO = {'T': 0.95, 'A': 1.0}      # debit : < 1 = plus lent ; cale sur le debit reel de chaque voix (clone ~ +7 % / +4 %)
EQ_SCALE = 1.0
LIMIT_DB = 3.0; TARGET_LUFS = -20.0       # niveau de chaque phrase ; la piste finale est amenee a -16 LUFS integre (crete vraie <= -1,5 dBTP) par assemble.py
def real_wave(who):
    name = {'T': 'thomas', 'A': 'abder'}[who]
    ws = [spec.load(o['file'] if os.path.isabs(o['file']) else os.path.join(V, o['file'])) for o in json.load(open(f'{V}\\real\\{name}.json', encoding='utf8')) if o['dur'] > 2.0]
    return np.concatenate(ws)
def trim(w, thr=0.015, head=0.08, tail=0.14):
    idx = np.where(np.abs(w) > thr * np.abs(w).max())[0]
    return w[max(0, idx[0] - int(head * SR)): min(len(w), idx[-1] + int(tail * SR))]
def eq_curves():
    ch = json.load(open(V + r'\final\choix.json', encoding='utf8'))['choix']
    for who in ('T', 'A'):
        gen = np.concatenate([spec.load(f"{V}\\final\\takes\\{v['prise']}.wav") for k, v in ch.items() if k and v['id'] and json.load(open(V + r'\final\lignes_who.json', encoding='utf8'))[v['id']] == who])
        real = real_wave(who)
        rc, gc = spec.ltas(real), spec.ltas(gen); corr = spec.correction(rc, gc, LIMIT_DB)
        ri, gi = spec.indices(real), spec.indices(gen)
        json.dump(dict(bands=spec.BANDS, corr_db=corr.tolist(), reel=ri, clone=gi), open(f'{V}\\final\\eq_{who}.json', 'w'), indent=1)
        print(who, 'correction max', float(np.abs(corr).max()), 'dB ; centroide reel/clone', round(ri['centroide_hz']), round(gi['centroide_hz']), '; sibilance reel/clone', round(ri['sibilance_db'], 1), round(gi['sibilance_db'], 1))
def apply_eq(w, who, scale=1.0):
    eq = json.load(open(f'{V}\\final\\eq_{who}.json'))
    f = [0] + eq['bands'] + [SR / 2]; g = [eq['corr_db'][0]] + eq['corr_db'] + [eq['corr_db'][-1]]
    h = ss.firwin2(1025, f, 10 ** (np.array(g) * scale / 20), fs=SR)
    return ss.fftconvolve(w, h, mode='same').astype(np.float32)
def board(who):
    eq = json.load(open(f'{V}\\final\\eq_{who}.json'))
    fx = [HighpassFilter(75)]
    return Pedalboard(fx)
def master_clip(w, who):
    """rognage -> etirement de debit -> passe-haut -> correction de timbre (FIR unique) -> niveau -> limiteur de crete (pas de compresseur : il degradait la ressemblance)."""
    w = trim(w)
    if TEMPO[who] != 1.0: w = time_stretch(w.astype(np.float32)[None, :], SR, stretch_factor=TEMPO[who])[0]
    y = board(who)(w.astype(np.float32)[None, :], SR)[0]
    y = apply_eq(y, who, EQ_SCALE)
    y = y * 10 ** ((TARGET_LUFS - pyln.Meter(SR).integrated_loudness(y)) / 20)
    y = dsp.limit(y, -2.0, SR)
    n = int(0.015 * SR); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    return np.clip(y, -0.98, 0.98).astype(np.float32)
if __name__ == '__main__':
    if sys.argv[1] == 'eq': eq_curves()
    else:
        ch = json.load(open(V + r'\final\choix.json', encoding='utf8'))['choix']; who_of = json.load(open(V + r'\final\lignes_who.json', encoding='utf8'))
        os.makedirs(V + r'\final\master', exist_ok=True)
        for lid, v in ch.items():
            w = spec.load(f"{V}\\final\\takes\\{v['prise']}.wav"); sf.write(f'{V}\\final\\master\\{lid}.wav', master_clip(w, who_of[lid]), SR, subtype='PCM_16')
        print(len(ch), 'phrases etalonnees')
