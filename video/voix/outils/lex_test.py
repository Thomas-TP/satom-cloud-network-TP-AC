"""Test de prononciation : chaque terme difficile dans une phrase courte, plusieurs ecritures, retranscription par Whisper."""
import os, sys, re, json, glob, unicodedata
for d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):
    os.add_dll_directory(d); os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
import numpy as np, soundfile as sf, torch
sys.path.insert(0, r'C:\Perso\voice\final')
from lex_terms import T
V = r'C:\Perso\voice'; OUT = V + r'\final\lex'; os.makedirs(OUT, exist_ok=True)
def norm(t):
    t = unicodedata.normalize('NFD', t.lower()); t = ''.join(c for c in t if unicodedata.category(c) != 'Mn'); return re.sub(r'[^a-z0-9]', '', t)
jobs = []
for k, (vars_, acc) in T.items():
    seen = []
    for vi, v in enumerate(vars_):
        if v in seen: continue
        seen.append(v); jobs.append((k, vi, v))
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained('Qwen/Qwen3-TTS-12Hz-1.7B-Base', device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')
rd = V + r'\ref_final'
pr = m.create_voice_clone_prompt(ref_audio=rd + r'\ref.wav', ref_text=open(rd + r'\ref.txt', encoding='utf8').read().strip(), x_vector_only_mode=False)
todo = [(k, vi, v) for k, vi, v in jobs if not os.path.exists(f'{OUT}\{norm(k)}_{vi}.wav')]
import time; t0 = time.time()
for i in range(0, len(todo), 10):
    B = todo[i:i + 10]; torch.manual_seed(1000 + i)
    ws, s = m.generate_voice_clone(text=[f'Voici {v}, comme prévu.' for _, _, v in B], language=['French'] * len(B), voice_clone_prompt=[pr[0]] * len(B), max_new_tokens=130)
    for (k, vi, v), w in zip(B, ws): sf.write(f'{OUT}\{norm(k)}_{vi}.wav', np.asarray(w, dtype=np.float32), s)
    print(f'{i + len(B)}/{len(todo)} {time.time() - t0:.0f}s', flush=True)
print('generation finie', flush=True)
del m; torch.cuda.empty_cache()
from faster_whisper import WhisperModel
wm = WhisperModel('large-v3', device='cuda', compute_type='float16')
res = {}
for k, vi, v in jobs:
    p = f'{OUT}\\{norm(k)}_{vi}.wav'
    hyp = ' '.join(s.text for s in wm.transcribe(p, language='fr', beam_size=5, condition_on_previous_text=False)[0])
    ok = any(a in norm(hyp) for a in T[k][1])
    res.setdefault(k, []).append(dict(variante=v, ok=ok, entendu=hyp.strip()))
json.dump(res, open(V + r'\final\lex_resultats.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
for k, r in res.items():
    print(f'{k:22s}', ' | '.join(f"{'OK ' if x['ok'] else 'KO '}{x['variante']} -> {x['entendu'][:40]}" for x in r))
