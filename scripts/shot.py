"""Extrait une capture de la console AWS depuis un rush video/raw/<scene>.mp4, au repere donne (ou a une seconde donnee).
Le bandeau du haut a droite (compte, role) est masque. Sortie : JPEG 1600 px.
Usage :
  python scripts/shot.py marks <scene>                      -> liste les reperes de la scene (nom, seconde)
  python scripts/shot.py sheet <scene> [dossier]            -> planche contact (un cadre par repere) pour choisir les captures
  python scripts/shot.py get <scene> <repere|secondes> <sortie.jpg> [decalage]   -> capture finale (decalage en secondes, 0 par defaut)
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); RAW = os.path.join(ROOT, 'video', 'raw')
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links', 'ffmpeg.exe')
# zone du bandeau (1920x1080) : compte et role en haut a droite ; remplie avec la couleur de l'en-tete (echantillonnee)
BOX = (1540, 0, 1920, 48)

def marks(scene):
    p = os.path.join(RAW, scene + '.marks.json')
    return [(m['name'], float(m['t'])) for m in json.load(open(p, encoding='utf8'))] if os.path.exists(p) else []

def frame(scene, t, out, width=1600):
    from PIL import Image
    src = os.path.join(RAW, scene + '.mp4'); tmp = out + '.tmp.png'
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    for back in (0, 0.5, 1.0, 2.0, 4.0):      # si le repere tombe apres la fin du rush, on recule
        r = subprocess.run([FF, '-loglevel', 'error', '-y', '-ss', f'{max(t - back, 0):.2f}', '-i', src, '-frames:v', '1', tmp], capture_output=True, text=True)
        if not r.returncode and os.path.exists(tmp): break
    else: raise SystemExit(f'echec ffmpeg {scene} @ {t}: {r.stderr}')
    im = Image.open(tmp).convert('RGB'); os.remove(tmp)
    fill = im.getpixel((1500, 24))      # couleur de l'en-tete, a gauche du bandeau
    for x in range(BOX[0], BOX[2]):
        for y in range(BOX[1], BOX[3]): im.putpixel((x, y), fill)
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(out, 'JPEG', quality=84, optimize=True)
    return out

def get(scene, ref, out, off=0.0):
    try: t = float(ref)
    except ValueError:
        d = dict(marks(scene))
        if ref not in d: raise SystemExit(f'repere inconnu {ref} ; reperes : {list(d)}')
        t = d[ref]
    return frame(scene, t + off, out)

def sheet(scene, outdir=None):
    ms = marks(scene) or [('debut', 5.0)]
    outdir = outdir or os.path.join(os.environ.get('TEMP', '.'), 'planches'); os.makedirs(outdir, exist_ok=True)
    files = []
    for i, (n, t) in enumerate(ms):
        f = os.path.join(outdir, f'{scene}_{i:02d}.jpg'); frame(scene, t, f, 640); files.append((n, t, f))
    cols = 3; rows = (len(files) + cols - 1) // cols
    inputs = sum([['-i', f] for _, _, f in files], [])
    lay = '|'.join(f'{(i % cols) * 640}_{(i // cols) * 360}' for i in range(len(files)))
    out = os.path.join(outdir, f'{scene}_planche.jpg')
    if len(files) == 1:
        os.replace(files[0][2], out)
    else:
        subprocess.run([FF, '-loglevel', 'error', '-y', *inputs, '-filter_complex', f'xstack=inputs={len(files)}:layout={lay}', '-q:v', '4', out], check=True)
    print(out)
    for i, (n, t, _) in enumerate(files): print(f'  [{i}] {n} @ {t:.1f} s')

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == 'marks':
        for n, t in marks(a[1]): print(f'{n}\t{t:.1f}')
    elif a[0] == 'sheet': sheet(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == 'get': print(get(a[1], a[2], a[3], float(a[4]) if len(a) > 4 else 0.0))
    else: raise SystemExit(__doc__)
