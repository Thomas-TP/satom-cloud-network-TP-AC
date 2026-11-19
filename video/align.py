"""Alignement mot a mot de la voix (faster-whisper large-v3, GPU) -> work/align/<id>.json. A lancer avec le python du venv de la voix."""
import glob, json, os, sys
for d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):
    os.add_dll_directory(d); os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ.get('WORK', 'work'))
m = WhisperModel('large-v3', device='cuda', compute_type='float16')
for wav in sorted(glob.glob(os.path.join(W, 'voix_fort', '*.wav'))):
    sid = os.path.splitext(os.path.basename(wav))[0]
    segs, _ = m.transcribe(wav, language='fr', beam_size=5, word_timestamps=True, condition_on_previous_text=False)
    words = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words]
    json.dump(words, open(os.path.join(W, 'align', sid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(sid, len(words), 'mots', flush=True)
