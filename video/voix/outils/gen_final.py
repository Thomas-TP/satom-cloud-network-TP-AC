"""Generation des voix finales (Qwen3-TTS 1.7B Base, local). Reprise automatique (ne refait pas ce qui existe).
Usage : python gen_final.py [--scenes m02a,chap2,...] [--takes 3] [--batch 6] [--first-take 0]
Sorties : C:\\Perso\\voice\\final\\takes\\<ligne>_<prise>.wav (24 kHz brut, avant etalonnage)."""
import os, sys, json, time, argparse, numpy as np, soundfile as sf, torch
sys.path.insert(0, r'C:\Perso\voice\final'); sys.path.insert(0, r'C:\Perso\AWS\video\voix')
from lines import load_lines
ap = argparse.ArgumentParser()
ap.add_argument('--scenes', default=''); ap.add_argument('--takes', type=int, default=3); ap.add_argument('--batch', type=int, default=6); ap.add_argument('--first-take', type=int, default=0)
a = ap.parse_args()
V = r'C:\Perso\voice'; OUT = V + r'\final\takes'; os.makedirs(OUT, exist_ok=True)
REF = {'T': V + r'\ref_final', 'A': V + r'\ref_abder_final'}
L = load_lines(a.scenes.split(',') if a.scenes else None)
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained('Qwen/Qwen3-TTS-12Hz-1.7B-Base', device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')
P = {w: m.create_voice_clone_prompt(ref_audio=d + r'\ref.wav', ref_text=open(d + r'\ref.txt', encoding='utf8').read().strip(), x_vector_only_mode=False)[0] for w, d in REF.items()}
t00 = time.time(); done = 0
for k in range(a.first_take, a.first_take + a.takes):
    for who in ('T', 'A'):
        todo = [l for l in L if l['who'] == who and not os.path.exists(f"{OUT}\\{l['id']}_{k}.wav")]
        todo.sort(key=lambda l: len(l['say']))
        for i in range(0, len(todo), a.batch):
            B = todo[i:i + a.batch]
            torch.manual_seed(5000 + 17 * k + i)
            est = max(len(l['say'].split()) for l in B) / 2.0
            mx = int(est * 12.5 * 2.0) + 60
            try:
                wavs, sr = m.generate_voice_clone(text=[l['say'] for l in B], language=['French'] * len(B), voice_clone_prompt=[P[who]] * len(B), max_new_tokens=mx)
            except Exception as e:
                print('ERREUR lot', [l['id'] for l in B], repr(e)[:200], flush=True); torch.cuda.empty_cache(); continue
            for l, w in zip(B, wavs): sf.write(f"{OUT}\\{l['id']}_{k}.wav", np.asarray(w, dtype=np.float32), sr)
            done += len(B)
            print(f'prise {k} voix {who} : {done} lignes, {(time.time() - t00) / 60:.1f} min', flush=True)
            torch.cuda.empty_cache()
print('termine', flush=True)
