"""Spectre moyen de la parole (tiers d'octave) + indices de timbre, et courbe de correction limitee."""
import numpy as np, soundfile as sf, scipy.signal as ss
BANDS = [100 * 2 ** (i / 3) for i in range(0, 20)]      # 100 Hz ... ~8 kHz (centres)
def load(p, sr=24000):
    w, s = sf.read(p, dtype='float32'); w = w if w.ndim == 1 else w.mean(1)
    if s != sr:
        import math; g = math.gcd(s, sr); w = ss.resample_poly(w, sr // g, s // g)
    return w.astype(np.float32)
def ltas(w, sr=24000):
    f, t, S = ss.stft(w, sr, nperseg=2048, noverlap=1536); P = np.abs(S) ** 2
    e = P.sum(0); keep = e > e.max() * 10 ** (-40 / 10)            # trames de parole (40 dB sous le max)
    m = P[:, keep].mean(1); out = []
    for c in BANDS:
        lo, hi = c / 2 ** (1 / 6), c * 2 ** (1 / 6); out.append(10 * np.log10(m[(f >= lo) & (f < hi)].sum() + 1e-12))
    out = np.array(out); return out - out.mean()
def indices(w, sr=24000):
    f, t, S = ss.stft(w, sr, nperseg=2048, noverlap=1536); P = (np.abs(S) ** 2); e = P.sum(0); keep = e > e.max() * 1e-4; m = P[:, keep].mean(1)
    cen = float((f * m).sum() / m.sum()); sib = 10 * np.log10(m[(f >= 5000) & (f < 9000)].sum() / m[(f >= 100) & (f < 5000)].sum() + 1e-12)
    return dict(centroide_hz=cen, sibilance_db=float(sib))
def correction(real_curve, gen_curve, limit=3.0):
    d = real_curve - gen_curve; d = np.convolve(np.pad(d, 1, mode='edge'), [0.25, 0.5, 0.25], 'valid'); return np.clip(d, -limit, limit)
