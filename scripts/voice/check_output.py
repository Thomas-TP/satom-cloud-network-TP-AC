"""Verifie l'intelligibilite : retranscrit chaque .wav genere et le compare au texte d'origine.
Usage : python check_output.py <dossier_textes> <dossier_audio>"""
import difflib, glob, os, re, sys

# a placer AVANT l'import de faster_whisper : rend visibles les DLL CUDA installees par pip (cublas, cudnn) dans le venv
import glob, os, sys
for _d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):
    os.add_dll_directory(_d)
    os.environ['PATH'] = _d + os.pathsep + os.environ.get('PATH', '')
from faster_whisper import WhisperModel

in_dir, audio_dir = sys.argv[1:3]
try:
    model = WhisperModel('large-v3', device='cuda', compute_type='float16')
except Exception:
    model = WhisperModel('medium', device='cpu', compute_type='int8')


def norm(s):
    return re.sub(r'[^a-z0-9àâäçéèêëîïôöùûüÿœ ]', '', s.lower().replace('-', ' ')).split()


for path in sorted(glob.glob(os.path.join(in_dir, '*.txt'))):
    name = os.path.splitext(os.path.basename(path))[0]
    wav = os.path.join(audio_dir, name + '.wav')
    if not os.path.exists(wav):
        print('absent :', name); continue
    ref = norm(open(path, encoding='utf-8').read())
    segs, info = model.transcribe(wav, language='fr', beam_size=5)
    got = norm(' '.join(s.text for s in segs))
    ratio = difflib.SequenceMatcher(None, ref, got).ratio()
    print(f'{name}: {info.duration:.1f} s | concordance mots {ratio * 100:.0f} %')

