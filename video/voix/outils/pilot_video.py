"""Apercu d'un module : video muette du montage + piste voix, avec la carte de chapitre prolongee (derniere image figee) pour laisser parler.
Usage : python pilot_video.py chap2 m02g   (scene de depart, scene de fin)"""
import json, os, subprocess, sys
V = r'C:\Perso\voice'; FF = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
SIL = r'C:\Perso\AWS\video\satom-cloud-network-TP-AC-montage-sans-voix.mp4'
a, b = sys.argv[1], sys.argv[2]
data = json.load(open(r'C:\Perso\AWS\video\montage\rm\src\data.json')); L = json.load(open(r'C:\Perso\AWS\video\voix\lignes.json', encoding='utf8'))
ids = []; chap = -1
for s in data['scenes']:
    t = s['type']; ids.append('title' if t == 'title' else 'intro' if t == 'intro' else 'end' if t == 'end' else (f"chap{s['mod']['num']}" if t == 'chapter' else s['id']))
ia, ib = ids.index(a), ids.index(b); sa, sb = data['scenes'][ia], data['scenes'][ib]
t0 = sa['from'] / 30; t1 = (sb['from'] + sb['dur']) / 30; orig_dur = sa['dur'] / 30
new_dur = next(s['dur'] for s in L['scenes'] if s['id'] == a); extra = max(0, new_dur - orig_dur)
cut = t0 + orig_dur - 8 / 30              # debut du fondu vers la scene suivante
tmp = V + r'\final\pilot_tmp'; os.makedirs(tmp, exist_ok=True)
def run(*args): subprocess.run([FF, '-y', '-loglevel', 'error', *args], check=True)
run('-ss', f'{t0:.3f}', '-t', f'{cut - t0:.3f}', '-i', SIL, '-an', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp + r'\a.mp4')
run('-sseof', '-0.1', '-i', tmp + r'\a.mp4', '-frames:v', '1', tmp + r'\last.png')
run('-loop', '1', '-framerate', '30', '-t', f'{extra:.3f}', '-i', tmp + r'\last.png', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp + r'\f.mp4')
run('-ss', f'{cut:.3f}', '-t', f'{t1 - cut:.3f}', '-i', SIL, '-an', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp + r'\b.mp4')
open(tmp + r'\list.txt', 'w').write(f"file 'a.mp4'\nfile 'f.mp4'\nfile 'b.mp4'\n")
run('-f', 'concat', '-safe', '0', '-i', tmp + r'\list.txt', '-i', V + r'\final\piste.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', V + r'\final\apercu_' + a + '.mp4')
print('apercu ecrit : carte prolongee de', round(extra, 1), 's')
