"""Montage de la video Satom Cloud Network (TP-AC).
Etapes (une commande chacune) :
  python build_video.py post      # volume de la voix : compresseur + loudnorm -14 LUFS, durees
  python build_video.py cards     # cartes titre + bandeaux de module (PNG)
  python build_video.py scenes    # une video par scene (zoom, bandeau, sous-titres, voix)
  python build_video.py concat    # assemblage final
L'alignement des sous-titres (align.py) tourne dans le venv de la voix (GPU)."""
import difflib, io, json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W_ = os.path.join(HERE, 'work'); sys.path.insert(0, HERE)
import scenario
FF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links')
os.environ['PATH'] += os.pathsep + FF
FONT, FONT_B = r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\segoeuib.ttf'
BG = (15, 23, 42); ACC = (99, 102, 241); GREEN = (34, 197, 94)
FPS = 30; LEAD = 0.45; TAIL = 0.75
for d in ('voix_fort', 'align', 'ass', 'cards', 'scenes', 'overlays'): os.makedirs(os.path.join(W_, d), exist_ok=True)

def sh(cmd, **k):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **k)
    if r.returncode: raise RuntimeError('\n'.join(r.stderr.splitlines()[-12:]))
    return r.stdout
def dur(path): return float(sh(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).strip())
def font(sz, bold=False): return ImageFont.truetype(FONT_B if bold else FONT, sz)

# ---------------------------------------------------------------- post : volume de la voix
def post():
    info = {}
    for s in scenario.S:
        if 'say' not in s: continue
        src = os.path.join(W_, 'voix', s['id'] + '.wav'); out = os.path.join(W_, 'voix_fort', s['id'] + '.wav')
        sh(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af',
            'highpass=f=80,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,'
            'acompressor=threshold=-24dB:ratio=3:attack=5:release=80:makeup=4,loudnorm=I=-14:TP=-1.5:LRA=6', '-ar', '48000', '-ac', '1', out])
        info[s['id']] = dur(out)
    json.dump(info, open(os.path.join(W_, 'durees.json'), 'w'), indent=1)
    print('voix traitees : %d, total %.0f s' % (len(info), sum(info.values())))

# ---------------------------------------------------------------- cartes et bandeaux
def grad(w, h):
    im = Image.new('RGB', (w, h), BG); d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h; d.line([(0, y), (w, y)], fill=(int(15 + 18 * k), int(23 + 14 * k), int(42 + 40 * k)))
    return im

def cards():
    mods = [s for s in scenario.S if s['kind'] == 'card']
    for s in mods:
        im = grad(1920, 1080); d = ImageDraw.Draw(im)
        if s['num'] is None:
            d.text((960, 430), s['title'], font=font(120, True), fill=(255, 255, 255), anchor='mm')
            d.rectangle([760, 520, 1160, 526], fill=ACC)
            d.text((960, 600), s['sub'], font=font(40), fill=(203, 213, 225), anchor='mm')
            d.text((960, 700), 'Formation AWS niveau 300  •  Geneva Institute of Technology', font=font(30), fill=(148, 163, 184), anchor='mm')
        else:
            d.ellipse([810, 270, 1110, 570], outline=ACC, width=10); d.text((960, 420), str(s['num']), font=font(170, True), fill=(255, 255, 255), anchor='mm')
            d.text((960, 680), s['title'].split('–', 1)[1].strip(), font=font(92, True), fill=(255, 255, 255), anchor='mm')
            d.text((960, 780), s['sub'], font=font(44), fill=(203, 213, 225), anchor='mm')
        im.save(os.path.join(W_, 'cards', s['id'] + '.png'))
    # bandeau commun a toutes les scenes d'un module : titre en haut a gauche + 14 points de progression
    for n in range(14):
        c = [s for s in scenario.S if s['kind'] == 'card' and s['num'] == n][0]
        ov = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        label = c['title']; wlab = int(d.textlength(label, font=font(34, True))) + 56
        d.rounded_rectangle([34, 30, 34 + wlab, 92], 18, fill=(15, 23, 42, 215), outline=ACC + (255,), width=3)
        d.text((62, 61), label, font=font(34, True), fill=(255, 255, 255), anchor='lm')
        for i in range(14):
            x = 1920 - 60 - (13 - i) * 34
            d.ellipse([x - 9, 52, x + 9, 70], fill=(GREEN + (255,)) if i == n else ((99, 102, 241, 200) if i < n else (148, 163, 184, 110)))
        ov.save(os.path.join(W_, 'overlays', 'm%02d.png' % n))
    print('cartes et bandeaux : ok')

# ---------------------------------------------------------------- sous-titres (alignes sur la voix)
def norm(w): return re.sub(r"[^a-z0-9àâäçéèêëîïôöùûüÿœ]", '', w.lower())
def ass_for(s, total_end):
    words = json.load(open(os.path.join(W_, 'align', s['id'] + '.json'), encoding='utf-8'))
    toks = s['text'].split()
    gw = [norm(w['w']) for w in words]; tn = [norm(t) for t in toks]
    t0 = [None] * len(toks); t1 = [None] * len(toks)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, tn, gw, autojunk=False).get_opcodes():
        if op == 'equal':
            for k in range(i2 - i1): t0[i1 + k] = words[j1 + k]['s']; t1[i1 + k] = words[j1 + k]['e']
    # interpolation des mots non apparies
    last = 0.0; i = 0
    while i < len(toks):
        if t0[i] is None:
            j = i
            while j < len(toks) and t0[j] is None: j += 1
            a = t1[i - 1] if i > 0 else 0.0; b = t0[j] if j < len(toks) else total_end
            for k in range(i, j): t0[k] = a + (b - a) * (k - i) / (j - i); t1[k] = a + (b - a) * (k - i + 1) / (j - i)
            i = j
        else: i += 1
    # lignes de 2 x ~36 caracteres
    cues = []; cur = [];
    for k, t in enumerate(toks):
        cur.append(k)
        txt = ' '.join(toks[x] for x in cur)
        end_sent = t.endswith(('.', '?', '!', ':', ';')) or (t.endswith(',') and len(txt) > 40)
        if len(txt) > 64 or (end_sent and len(txt) > 22) or k == len(toks) - 1:
            cues.append(cur); cur = []
    def wrap(txt):
        if len(txt) <= 38: return txt
        parts = txt.split(' '); best = None
        for i in range(1, len(parts)):
            a, b = ' '.join(parts[:i]), ' '.join(parts[i:])
            sc = abs(len(a) - len(b))
            if best is None or sc < best[0]: best = (sc, a, b)
        return best[1] + '\\N' + best[2]
    ts = lambda x: '%d:%02d:%05.2f' % (int(x // 3600), int(x % 3600 // 60), x % 60)
    head = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n'
            'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n'
            'Style: Default,Segoe UI,44,&H00FFFFFF,&H000000FF,&H00201008,&HA0201008,-1,0,0,0,100,100,0,0,3,8,0,2,160,160,34,1\n\n'
            '[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n')
    ev = []
    for n, c in enumerate(cues):
        a = t0[c[0]] + LEAD - 0.05; b = t1[c[-1]] + LEAD + 0.25
        if n + 1 < len(cues): b = min(b, t0[cues[n + 1][0]] + LEAD - 0.02)
        ev.append('Dialogue: 0,%s,%s,Default,,0,0,0,,%s' % (ts(max(a, 0)), ts(b), wrap(' '.join(toks[x] for x in c))))
    open(os.path.join(W_, 'ass', s['id'] + '.ass'), 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')

# ---------------------------------------------------------------- scenes
def zoom_expr(fx, fy, z0, z1, frames):
    z = f"({z0}+({z1}-{z0})*on/{frames})"
    return (f"zoompan=z='{z}':x='max(0,min(iw*{fx}-iw/zoom/2,iw-iw/zoom))':y='max(0,min(ih*{fy}-ih/zoom/2,ih-ih/zoom))':d=1:s=1920x1080:fps={FPS}")

def prep_still(s):
    """Image source 3840x2160 (nette pour le zoom). diagrams : remplit le cadre ; shots : capture centree sur fond sombre."""
    src = Image.open(os.path.join(ROOT, s['img'])).convert('RGB')
    out = os.path.join(W_, 'cards', s['id'] + '_src.png')
    if s['kind'] == 'diagram':
        im = src.resize((3840, 2160), Image.LANCZOS)
    else:
        im = grad(3840, 2160); sw = 3500; sh_ = int(src.height * sw / src.width)
        pic = src.resize((sw, sh_), Image.LANCZOS)
        sh_y = (2160 - sh_) // 2 + 40; x0 = (3840 - sw) // 2
        d = ImageDraw.Draw(im); d.rounded_rectangle([x0 - 14, sh_y - 14, x0 + sw + 14, sh_y + sh_ + 14], 26, fill=(99, 102, 241))
        im.paste(pic, (x0, sh_y))
    im.save(out); return out

def scene(s, durs):
    sid = s['id']; out = os.path.join(W_, 'scenes', sid + '.mp4')
    mod = int(re.match(r'm?(\d+)', sid).group(1)) if re.match(r'm\d\d', sid) else None
    ovl = os.path.join(W_, 'overlays', 'm%02d.png' % mod) if mod is not None else None
    enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2']
    if s['kind'] == 'card':
        d = s.get('dur', 2.4); frames = int(d * FPS)
        vf = f"zoompan=z='1+0.04*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps={FPS},fade=t=in:st=0:d=0.35,fade=t=out:st={d-0.35}:d=0.35"
        img = os.path.join(W_, 'cards', sid + '.png')
        sh(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', str(d), '-i', img, '-f', 'lavfi', '-t', str(d), '-i', 'anullsrc=r=48000:cl=stereo',
            '-vf', vf, '-shortest'] + enc + [out]); return dur(out)
    a = durs[sid]; total = LEAD + a + TAIL
    voice = os.path.join(W_, 'voix_fort', sid + '.wav')
    ass = 'ass/' + sid + '.ass'
    if s['kind'] == 'clip':
        clip = os.path.join(ROOT, s['clip']); cd = dur(clip)
        sp = min(max(cd / (total - 0.3), 1.0), 2.4); total = max(total, cd / sp + 0.9)
        base = f"[0:v]setpts=PTS/{sp:.4f},scale=1760:990:flags=lanczos,pad=1920:1080:80:84:color=0x0f172a,tpad=stop_mode=clone:stop_duration={total:.2f},trim=0:{total:.2f},setpts=PTS-STARTPTS,fps={FPS}[bg]"
        inputs = ['-i', clip]
    else:
        fx, fy, z0, z1 = s['focus']; frames = int(total * FPS)
        still = prep_still(s)
        base = f"[0:v]{zoom_expr(fx, fy, z0, z1, frames)}[bg]"
        inputs = ['-loop', '1', '-t', f'{total:.2f}', '-i', still]
    chain = base + ';'
    last = '[bg]'
    if ovl:
        chain += f"{last}[2:v]overlay=0:0[ov];"; last = '[ov]'
    chain += f"{last}subtitles={ass},fade=t=in:st=0:d=0.3,fade=t=out:st={total-0.3:.2f}:d=0.3[v]"
    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-i', voice]
    if ovl: cmd += ['-i', ovl]
    else: pass
    # l'ordre des entrees : 0 = video/image, 1 = voix, 2 = bandeau (si present)
    aud = f"[1:a]adelay={int(LEAD*1000)}:all=1,apad=whole_dur={total:.2f},afade=t=out:st={total-0.25:.2f}:d=0.25[a]"
    cmd += ['-filter_complex', chain + ';' + aud, '-map', '[v]', '-map', '[a]', '-t', f'{total:.2f}'] + enc + [out]
    sh(cmd, cwd=W_); return dur(out)

def scenes(only=None):
    durs = json.load(open(os.path.join(W_, 'durees.json')))
    seen = {}
    for s in scenario.S:
        if only and s['id'] not in only: continue
        if 'say' in s:
            ass_for(s, durs[s['id']])
        seen[s['id']] = scene(s, durs); print('%-10s %.1f s' % (s['id'], seen[s['id']]), flush=True)
    json.dump(seen, open(os.path.join(W_, 'scenes_dur.json'), 'w'), indent=1)

def concat():
    lst = os.path.join(W_, 'liste.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        for s in scenario.S: f.write("file 'scenes/%s.mp4'\n" % s['id'])
    out = os.path.join(HERE, 'satom-cloud-network-TP-AC.mp4')
    sh(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out])
    print('video : %s (%.1f min, %.0f Mo)' % (out, dur(out) / 60, os.path.getsize(out) / 1e6))

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'post': post()
    elif c == 'cards': cards()
    elif c == 'scenes': scenes(sys.argv[2:] or None)
    elif c == 'concat': concat()
