"""Coupe le debut d'un enregistrement brut : python trim_raw.py <scene> <secondes>  (decale les marqueurs)."""
import json, os, subprocess, sys
RAW = r'C:\Perso\AWS\video\raw'
FF = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
name, t0 = sys.argv[1], float(sys.argv[2])
src = os.path.join(RAW, name + '.mp4'); tmp = os.path.join(RAW, name + '.trim.mp4')
subprocess.run([FF, '-y', '-loglevel', 'error', '-ss', str(t0), '-i', src, '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30', tmp], check=True)
os.replace(src, os.path.join(RAW, name + '.orig.mp4')); os.replace(tmp, src)
mp = os.path.join(RAW, name + '.marks.json'); m = json.load(open(mp, encoding='utf-8'))
out = []
for x in m:
    x = dict(x); x['t'] = round(max(x['t'] - t0, 0), 2); out.append(x)
json.dump(out, open(mp, 'w', encoding='utf-8'))
print('ok', name, len(out), 'marques')
