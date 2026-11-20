import numpy as np
from scipy.ndimage import minimum_filter1d, uniform_filter1d
def limit(x, ceiling_db=-2.0, sr=24000, win_ms=12.0):
    """Limiteur de crete a anticipation (sans gain de compensation) : la crete ne depasse jamais le plafond. Gain lisse sur win_ms."""
    c = 10 ** (ceiling_db / 20); W = max(3, int(sr * win_ms / 1000)) | 1
    req = np.minimum(1.0, c / (np.abs(x) + 1e-9))
    g = uniform_filter1d(minimum_filter1d(req, size=W, mode='nearest'), size=W, mode='nearest')
    return (x * g).astype(np.float32)
