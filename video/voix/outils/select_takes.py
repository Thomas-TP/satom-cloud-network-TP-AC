"""Evalue chaque prise (ressemblance ECAPA, intelligibilite Whisper, anomalies) et choisit la meilleure par ligne.
Usage : python select_takes.py [--scenes m02a,chap2] ; ecrit final/scores.json et final/choix.json"""
import os, sys, re, json, glob, unicodedata, argparse, difflib
for d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):
    os.add_dll_directory(d); os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
import numpy as np, soundfile as sf, torch, torchaudio
sys.path.insert(0, r'C:\Perso\voice\final'); sys.path.insert(0, r'C:\Perso\voice\essai')
from lines import load_lines
ap = argparse.ArgumentParser(); ap.add_argument('--scenes', default=''); a = ap.parse_args()
V = r'C:\Perso\voice'; TK = V + r'\final\takes'
L = load_lines(a.scenes.split(',') if a.scenes else None)
from speechbrain.inference.speaker import EncoderClassifier
enc = EncoderClassifier.from_hparams(source='speechbrain/spkrec-ecapa-voxceleb', savedir=V + r'\essai\ecapa', run_opts={'device': 'cuda:0'})
def wav16(p):
    w, sr = sf.read(p, dtype='float32'); w = w if w.ndim == 1 else w.mean(1); return torchaudio.functional.resample(torch.from_numpy(w), sr, 16000), w, sr
def emb(t):
    with torch.no_grad(): e = enc.encode_batch(t.unsqueeze(0).cuda()).squeeze().cpu().numpy()
    return e / np.linalg.norm(e)
# empreinte de reference de chaque voix : moyenne des vraies phrases
C = {}
for who, name in (('T', 'thomas'), ('A', 'abder')):
    es = [emb(wav16(o['file'] if os.path.isabs(o['file']) else os.path.join(V, o['file']))[0]) for o in json.load(open(f'{V}\\real\\{name}.json', encoding='utf8')) if o['dur'] > 2.0]
    c = np.mean(es, 0); C[who] = c / np.linalg.norm(c)
def norm(t):
    t = unicodedata.normalize('NFD', t.lower()); t = ''.join(c for c in t if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9]', '', t)
from num2words import num2words
def digits_to_words(t): return re.sub(r'\d+', lambda m: num2words(int(m.group(0)), lang='fr_CH'), t)
from faster_whisper import WhisperModel
wm = WhisperModel('large-v3', device='cuda', compute_type='float16')
S = json.load(open(V + r'\final\scores.json', encoding='utf8')) if os.path.exists(V + r'\final\scores.json') else {}
for l in L:
    for f in sorted(glob.glob(f"{TK}\\{l['id']}_*.wav")):
        key = os.path.basename(f)[:-4]
        if key in S: continue
        t16, w, sr = wav16(f); dur = len(w) / sr
        hyp = ' '.join(s.text for s in wm.transcribe(f, language='fr', beam_size=5, condition_on_previous_text=False)[0])
        exp = norm(l['say']); got = norm(digits_to_words(hyp))
        ratio = difflib.SequenceMatcher(None, exp, got).ratio()
        # anomalies : silences internes longs, ecretage, debut/fin
        fr = int(0.02 * sr); e = np.array([np.abs(w[i:i + fr]).mean() for i in range(0, len(w) - fr, fr)]); thr = e.max() * 0.03
        voiced = np.where(e > thr)[0]; lead = voiced[0] * 0.02 if len(voiced) else dur; trail = dur - (voiced[-1] + 1) * 0.02 if len(voiced) else dur
        gap = 0; mx = 0
        for v in e[voiced[0]:voiced[-1]] if len(voiced) else []:
            gap = gap + 0.02 if v < thr else 0; mx = max(mx, gap)
        S[key] = dict(id=l['id'], sim=float(emb(t16) @ C[l['who']]), ratio=float(ratio), dur=float(dur), lead=float(lead), trail=float(trail), gap=float(mx), peak=float(np.abs(w).max()), entendu=hyp.strip())
    json.dump(S, open(V + r'\final\scores.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
def rat(say, entendu):
    # normalisation tolerante : « zéro un » entendu « 01 », mots tres courts plus indulgents
    got = norm(digits_to_words(entendu)).replace('01', 'zeroun').replace('02', 'zerodeux'); exp = norm(say)
    return difflib.SequenceMatcher(None, exp, got).ratio()
# choix : filtre (intelligible, pas de boucle, pas de long silence) puis meilleure ressemblance
choix = {}; retake = []
for l in L:
    c = [(k, v) for k, v in S.items() if v['id'] == l['id']]
    for k, v in c: v['ratio'] = rat(l['say'], v['entendu'])
    thr = 0.80 if len(l['say'].split()) <= 4 else 0.90
    ok = [(k, v) for k, v in c if v['ratio'] >= thr and v['gap'] < 1.2 and v['dur'] < max(2.5, 1.7 * l['dur_est']) and v['peak'] < 0.999]
    if ok: k, v = max(ok, key=lambda kv: kv[1]['sim'] + 0.3 * kv[1]['ratio']); choix[l['id']] = dict(prise=k, **v)
    else:
        # repli : meilleure prise disponible (signalee), sauf si elle est franchement inintelligible
        k, v = max(c, key=lambda kv: (kv[1]['ratio'], kv[1]['sim']))
        if v['ratio'] >= 0.78 and v['gap'] < 1.5: choix[l['id']] = dict(prise=k, repli=True, **v)
        else: retake.append(l['id'])
json.dump(dict(choix=choix, a_refaire=retake), open(V + r'\final\choix.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
WP = V + r'\final\lignes_who.json'
w = json.load(open(WP, encoding='utf8')) if os.path.exists(WP) else {}
w.update({l['id']: l['who'] for l in L}); json.dump(w, open(WP, 'w', encoding='utf8'))
sims = [v['sim'] for v in choix.values()]
print(f'{len(choix)} lignes retenues, {len(retake)} a refaire ; ressemblance moyenne {np.mean(sims):.3f} (min {np.min(sims):.3f})' if sims else 'rien')
