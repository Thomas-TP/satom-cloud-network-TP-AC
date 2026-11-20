"""Controle du texte de voix : place chaque phrase sur la chronologie du montage, estime les durees, signale les depassements,
mesure l'equilibre Thomas / Abderahmane et ecrit TEXTE-VOIX.md (lisible) + lignes.json (pour la generation des voix).
Usage : python check.py [--rate 2.6]
Les durees de parole sont des ESTIMATIONS (mots / debit) : elles seront remplacees par les durees reelles au moment de la generation."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MON = os.path.join(HERE, '..', 'montage')
RATE = 2.6
if '--rate' in sys.argv: RATE = float(sys.argv[sys.argv.index('--rate') + 1])
GAP = 0.35; OVERLAP = 8 / 30; TRIM = 0.4
REAL = {}
_p = r'C:' + chr(92) + 'Perso' + chr(92) + 'voice' + chr(92) + 'final' + chr(92) + 'durees_reelles.json'
if os.path.exists(_p) and '--estime' not in sys.argv: REAL = json.load(open(_p, encoding='utf8'))   # durees mesurees des voix etalonnees
NAMES = {'T': 'Thomas', 'A': 'Abderahmane'}

def nwords(t):
    toks = re.findall(r"[\w'’-]+", t); n = 0.0
    for w in toks:
        n += 1
        if w.isupper() and len(w) >= 2 and w not in ('NAT', 'NACL', 'ALB'): n += 0.45 * len(w) - 0.5   # sigles epeles
    return n + 0.35 * len(re.findall(r'[,;:]', t)) / 1.0 * 0   # (virgules : deja dans la pause fixe)

def dur_of(t): return nwords(t) / RATE + 0.25

def mod_of(sid, cur):
    m = re.match(r'chap(\d+)', sid)
    return int(m.group(1)) if m else cur

def parse():
    scenes = []; cur = None
    for raw in open(os.path.join(HERE, 'texte.txt'), encoding='utf8'):
        raw = raw.rstrip('\n')
        if not raw.strip() or raw.startswith('#'): continue
        if raw.startswith('=='):
            cur = dict(id=raw[2:].strip(), lines=[]); scenes.append(cur); continue
        m = re.match(r'^([TA])\s*(?:@(\S+))?\s*\|\s*(.+)$', raw)
        if not m: raise SystemExit('ligne illisible : ' + raw)
        cur['lines'].append(dict(who=m.group(1), anc=m.group(2), text=m.group(3).strip()))
    return {s['id']: s for s in scenes}

def anchor(sid, a, marks):
    """secondes de contenu de la scene."""
    if a is None: return None
    m = re.match(r'^(?:([A-Za-z0-9_/*\-]+?))?(?:([+-])(\d+(?:\.\d+)?))?$', a)
    if a.startswith('+'): return float(a[1:])
    # nom de repere, eventuellement suivi de +x / -x
    mm = re.match(r'^(.*?)([+-]\d+(?:\.\d+)?)?$', a)
    name, off = mm.group(1), float(mm.group(2) or 0)
    norm = lambda x: x.replace('-TP-AC', '')
    nm = {norm(k): v for k, v in marks.items()}; name = norm(name)
    if name not in nm:
        cand = [k for k in nm if k.endswith('-' + name)]
        if len(cand) == 1: name = cand[0]
        else: raise SystemExit(f'repere inconnu {sid}:{name}  (reperes : {list(nm)})')
    return nm[name] - TRIM + off

def main():
    data = json.load(open(os.path.join(MON, 'rm', 'src', 'data.json')))
    texts = parse(); used = set()
    t = 0.0; prev_end = 0.0; out = []; warns = []; modn = None; chap_i = -1
    for sc in data['scenes']:
        typ = sc['type']
        if typ == 'title': sid = 'title'
        elif typ == 'intro': sid = 'intro'
        elif typ == 'end': sid = 'end'
        elif typ == 'chapter': chap_i += 1; sid = f'chap{sc["mod"]["num"]}'
        else: sid = sc['id']
        orig = sc['dur'] / 30; modn = sc['mod']['num'] if sc.get('mod') else modn
        marks = {}
        if typ == 'gui':
            marks = {n: v for n, v in json.load(open(os.path.join(MON, 'plan', sid + '.json')))['marks']}
        S = texts.get(sid); used.add(sid); first = True; ph = []
        if S:
            for li, L in enumerate(S['lines']):
                a = anchor(sid, L['anc'], marks)
                abs_a = t + a if a is not None else None
                base = t + (0.5 if typ != 'gui' else 0.3) if first else prev_end + GAP
                if abs_a is None: start = max(base, prev_end + GAP if not first else base)
                else: start = max(abs_a, prev_end + GAP)
                d = REAL.get(f'{sid}_{li:02d}', dur_of(L['text'])); end = start + d
                delay = (start - abs_a) if abs_a is not None else 0
                ph.append(dict(id=f'{sid}_{li:02d}', sc=sid, mod=modn, who=L['who'], text=L['text'], start=start, end=end, rel=start - t, anchor=abs_a, delay=delay, words=round(nwords(L['text']), 1)))
                prev_end = end; first = False
        dur = orig
        if typ != 'gui' and ph: dur = max(orig, ph[-1]['end'] - t + 0.6)
        scene_end = t + dur
        for p in ph:
            if p['delay'] > 1.0: warns.append(f'{sid} : phrase retardee de {p["delay"]:.1f} s ({p["text"][:45]}...)')
            if typ == 'gui' and p['end'] > scene_end + 0.8: warns.append(f'{sid} : la phrase deborde de {p["end"] - scene_end:.1f} s sur la scene suivante ({p["text"][:45]}...)')
        out.append(dict(id=sid, type=typ, mod=modn, start=t, dur=dur, orig=orig, lines=ph))
        t = t + dur - OVERLAP
    missing = [k for k in texts if k not in used]
    if missing: raise SystemExit('scenes inconnues dans texte.txt : ' + str(missing))
    total = t + OVERLAP
    # stats
    words = {'T': 0, 'A': 0}; secs = {'T': 0, 'A': 0}; permod = {}
    for s in out:
        for p in s['lines']:
            words[p['who']] += p['words']; secs[p['who']] += p['end'] - p['start']
            d = permod.setdefault(s['mod'], {'T': 0, 'A': 0}); d[p['who']] += p['words']
    gui = [s for s in out if s['type'] == 'gui']
    cov = sum(sum(p['end'] - p['start'] for p in s['lines']) for s in out) / total
    print(f'duree totale estimee : {total / 60:.1f} min (montage muet : {sum(x["dur"] for x in data["scenes"]) / 30 / 60 - len(data["scenes"]) * OVERLAP / 60:.1f} min)')
    print(f'mots  Thomas {words["T"]:.0f}  Abderahmane {words["A"]:.0f}   ({words["T"] / (words["T"] + words["A"]) * 100:.0f} % / {words["A"] / (words["T"] + words["A"]) * 100:.0f} %)')
    print(f'temps de parole  Thomas {secs["T"] / 60:.1f} min  Abderahmane {secs["A"] / 60:.1f} min   couverture {cov * 100:.0f} %')
    print('par module :', ' | '.join(f'{k}: T{v["T"]:.0f}/A{v["A"]:.0f}' for k, v in sorted(permod.items(), key=lambda kv: (kv[0] is None, kv[0]))))
    # trous longs
    gaps = []
    allp = [p for s in out for p in s['lines']]
    for a, b in zip(allp, allp[1:]):
        if b['start'] - a['end'] > 7.0: gaps.append(f'{a["sc"]} -> {b["sc"]} : {b["start"] - a["end"]:.1f} s sans parole a {a["end"] / 60:.0f}:{a["end"] % 60:04.1f}')
    print('trous > 7 s :', len(gaps));  [print('  ', g) for g in gaps]
    print('avertissements :', len(warns)); [print('  ', w) for w in warns]

    # lignes trop longues pour leur creneau
    print('--- phrases trop longues pour leur creneau (rate %.1f) ---' % RATE)
    for s in out:
        L = s['lines']
        for i, p in enumerate(L):
            nxt = L[i + 1]['anchor'] if i + 1 < len(L) and L[i + 1]['anchor'] is not None else None
            lim = nxt if nxt is not None else (s['start'] + s['dur'] + (0.4 if s['type'] == 'gui' else 99))
            if s['type'] != 'gui' and nxt is None: continue
            over = p['end'] - lim
            if over > 0.3: print(f"  {s['id']:7s} @{p['rel']:5.1f}  {p['words']:4.0f} mots  deborde de {over:4.1f} s  : {p['text'][:70]}")

    # document lisible
    MN = {0: 'Cadrage', 1: 'Réseaux', 2: 'Routage', 3: 'Sécurité', 4: 'Pare-feu', 5: 'Appairage', 6: 'Transit Gateway', 7: 'VPN site à site', 8: 'Direct Connect', 9: 'Load balancer', 10: 'Route 53', 11: 'CloudFront', 12: 'Surveillance', 13: 'CloudFormation'}
    CAP = {}
    try:
        sys.path.insert(0, MON); import captions; CAP = {k: v[0] for k, v in captions.C.items()}
    except Exception: pass
    mm = lambda x: f'{int(x // 60)}:{x % 60:04.1f}'
    L = ['# Texte de voix off - Satom Cloud Network (TP-AC)', '',
         f'Durée estimée avec la voix : **{total / 60:.1f} min** (montage muet : 32 min ; les cartes de titre, de schéma et de chapitre sont allongées pour laisser parler).',
         f'Répartition : Thomas **{words["T"]:.0f} mots** ({words["T"] / (words["T"] + words["A"]) * 100:.0f} %), Abderahmane **{words["A"]:.0f} mots** ({words["A"] / (words["T"] + words["A"]) * 100:.0f} %).', '',
         'Chaque phrase est calée sur un geste précis à l’écran (repère entre crochets : minute:seconde dans la vidéo avec voix). Les nombres sont écrits comme ils seront prononcés (septante, huitante, nonante).', '']
    curmod = object()
    for s_ in out:
        if s_['type'] == 'gui' and s_['mod'] != curmod or s_['type'] == 'chapter' and False: pass
        if s_['id'].startswith('chap'):
            n = int(s_['id'][4:]); L += ['', f'## Module {n} - {MN[n]}', '']
        elif s_['id'] == 'title': L += ['## Ouverture', '']
        elif s_['id'] == 'intro': pass
        elif s_['id'] == 'end': L += ['', '## Conclusion', '']
        if not s_['lines']: continue
        if s_['type'] == 'gui': L += [f"*{CAP.get(s_['id'], s_['id'])}* ({s_['id']})"]
        elif s_['id'] == 'intro': L += ['*Schéma global*']
        for p in s_['lines']:
            L += [f"- [{mm(p['start'])}] **{NAMES[p['who']]}** : {p['text']}"]
        L += ['']
    open(os.path.join(HERE, 'TEXTE-VOIX.md'), 'w', encoding='utf8').write(chr(10).join(L))
    json.dump(dict(rate=RATE, total=total, scenes=out), open(os.path.join(HERE, 'lignes.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return out, total, words, secs, permod, cov

if __name__ == '__main__': main()
