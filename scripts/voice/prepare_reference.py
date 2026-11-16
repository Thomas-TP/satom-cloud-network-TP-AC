"""Prepare l'echantillon de voix : conversion en WAV mono 24 kHz + transcription (faster-whisper) -> ref.wav et ref.txt.
Usage : python prepare_reference.py <fichier_audio> <dossier_sortie>
(l'echantillon de voix reste sur le PC, hors du depot Git)"""
import os, subprocess, sys

src, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
wav = os.path.join(out_dir, 'ref.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', '24000', '-sample_fmt', 's16', wav], check=True)

# a placer AVANT l'import de faster_whisper : rend visibles les DLL CUDA installees par pip (cublas, cudnn) dans le venv
import glob, os, sys
for _d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):
    os.add_dll_directory(_d)
    os.environ['PATH'] = _d + os.pathsep + os.environ.get('PATH', '')
from faster_whisper import WhisperModel


def transcrire(device, compute):
    model = WhisperModel('large-v3', device=device, compute_type=compute)
    segs, info = model.transcribe(wav, language='fr', beam_size=5)
    return ' '.join(s.text.strip() for s in segs).strip(), info


try:
    text, info = transcrire('cuda', 'float16')
    mode = 'GPU'
except Exception as e:  # bibliotheque CUDA manquante (cublas) ou carte non geree : repli processeur
    print('GPU indisponible pour la transcription (' + str(e)[:70] + ') -> CPU')
    text, info = transcrire('cpu', 'int8')
    mode = 'CPU'
open(os.path.join(out_dir, 'ref.txt'), 'w', encoding='utf-8').write(text)
print('transcription', mode, '| langue', info.language, '| duree', round(info.duration, 1), 's')
print(text)

