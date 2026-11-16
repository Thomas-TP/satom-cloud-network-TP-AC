"""Lit chaque fichier .txt d'un dossier avec la voix clonee (Qwen3-TTS 1.7B Base, local, GPU) -> un .wav par fichier.
Usage : python clone_say.py <dossier_reference> <dossier_textes> <dossier_sortie>
Les textes longs sont decoupes par phrases (plus stable), puis recolles avec un court silence."""
import glob, os, re, sys

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

ref_dir, in_dir, out_dir = sys.argv[1:4]
os.makedirs(out_dir, exist_ok=True)
ref_wav = os.path.join(ref_dir, 'ref.wav')
ref_text = open(os.path.join(ref_dir, 'ref.txt'), encoding='utf-8').read().strip()

model = Qwen3TTSModel.from_pretrained('Qwen/Qwen3-TTS-12Hz-1.7B-Base', device_map='cuda:0', dtype=torch.bfloat16, attn_implementation='sdpa')
prompt = model.create_voice_clone_prompt(ref_audio=ref_wav, ref_text=ref_text, x_vector_only_mode=False)

for path in sorted(glob.glob(os.path.join(in_dir, '*.txt'))):
    text = open(path, encoding='utf-8').read().strip()
    phrases = [p.strip() for p in re.split(r'(?<=[.!?:;])\s+', text) if p.strip()]
    pieces, sr = [], 24000
    for ph in phrases:
        wavs, sr = model.generate_voice_clone(text=ph, language='French', voice_clone_prompt=prompt)
        pieces.append(np.asarray(wavs[0], dtype=np.float32))
        pieces.append(np.zeros(int(sr * 0.25), dtype=np.float32))
    audio = np.concatenate(pieces) if pieces else np.zeros(1, dtype=np.float32)
    out = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + '.wav')
    sf.write(out, audio, sr)
    print('OK', os.path.basename(path), '->', round(len(audio) / sr, 1), 's')
