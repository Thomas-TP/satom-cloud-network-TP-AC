"""Decoupe le dossier en notes HackMD (limite 100 000 caracteres par note) : un sommaire avec la video integree, puis trois parties de modules.
Usage : python scripts/build_hackmd.py          -> ecrit docs/hackmd/*.md (liens entre notes = jetons {{URL_...}})
Le depot GitHub public sert les images (URL absolues)."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(ROOT, 'docs'); OUT = os.path.join(D, 'hackmd')
RAW = 'https://raw.githubusercontent.com/Thomas-TP/satom-cloud-network-TP-AC/main/docs/images'
os.makedirs(OUT, exist_ok=True)
rd = lambda p: open(p, encoding='utf-8').read().replace('\r\n', '\n')
fix = lambda t: re.sub(r'\]\(\.\./images/', '](' + RAW + '/', t)
PARTS = [('partie1', 'Partie 1 : modules 0 à 4', range(0, 5), 'cadrage, réseaux, routage, sécurité, pare-feu'),
         ('partie2', 'Partie 2 : modules 5 à 8', range(5, 9), 'peering, Transit Gateway, VPN, Direct Connect'),
         ('partie3', 'Partie 3 : modules 9 à 13', range(9, 14), 'ALB, Route 53, CloudFront, surveillance, CloudFormation')]
NOM = {k: t.split(' : ')[0] for k, t, _, _ in PARTS}
SUJET = {k: t.split(' : ')[1] for k, t, _, _ in PARTS}
nav = lambda cur: ' · '.join(('**' + t + '**') if k == cur else f'[{t}]({{{{URL_{k}}}}})' for k, t in [('sommaire', 'Sommaire')] + [(k, NOM[k]) for k, _, _, _ in PARTS])

def module(n): return fix(rd(os.path.join(D, 'modules', f'm{n:02d}.md')))

for k, title, rng, sub in PARTS:
    body = '\n\n---\n\n'.join(module(n) for n in rng)
    txt = f"# Satom Cloud Network (TP-AC) – {title}\n\n{nav(k)}\n\n[TOC]\n\n---\n\n{body}\n\n---\n\n{nav(k)}\n"
    open(os.path.join(OUT, k + '.md'), 'w', encoding='utf-8', newline='\n').write(txt); print(k, len(txt))

# --- sommaire : introduction, liens bien visibles, video, tableau des modules (avec lien vers la partie), schema
head = fix(rd(os.path.join(D, 'src', 'entete.md')))
part_of = lambda n: next(k for k, _, rng, _ in PARTS if n in rng)

def ligne(m):
    k = part_of(int(m.group(1)))
    return m.group(0) + f" **[{NOM[k]}]({{{{URL_{k}}}}})** |"

head = re.sub(r'^\| (\d+) \| [^|]+\| terminé \|', ligne, head, flags=re.M)
head = head.replace('| Module | Sujet | État |\n|---|---|---|', '| Module | Sujet | État | Lire |\n|---|---|---|---|')
entetes = ' | '.join(f'[{NOM[k]}]({{{{URL_{k}}}}})' for k, _, _, _ in PARTS)
cellules = ' | '.join(f'**[{SUJET[k]}]({{{{URL_{k}}}}})**<br>{sub}' for k, _, _, sub in PARTS)
lire = f"## Lire le dossier\n\n| {entetes} |\n|:---:|:---:|:---:|\n| {cellules} |\n\n"
titre, p1, reste = head.split('\n\n', 2)
som = titre + '\n\n' + p1 + '\n\n' + lire + reste
open(os.path.join(OUT, 'sommaire.md'), 'w', encoding='utf-8', newline='\n').write(som); print('sommaire', len(som))
