"""Assemble les modules : docs/src/mNN.md + preuves docs/modules/mNN/tests.txt + captures captures/mNN/*.png
 -> docs/modules/mNN.md (liens relatifs) et docs/DOSSIER.md (liens absolus si URL de base fournie)
Usage : python -I scripts/build_docs.py [URL_BASE_IMAGES]
   ex. https://raw.githubusercontent.com/<user>/<repo>/main/docs/images
"""
import os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'docs', 'src')
MOD = os.path.join(ROOT, 'docs', 'modules')
base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else None
base_root = base.rsplit('/docs/images', 1)[0] if base else None

LABELS = {'00-console': 'Console AWS', '99-preuves': 'Journal des tests'}


def label(fn):
    n = os.path.basename(fn)[:-4]
    for k, v in LABELS.items():
        if n.startswith(k):
            return v + ' – ' + n.split('-', 2)[-1].replace('-', ' ') if k == '00-console' else v
    return 'Terminal – ' + n.split('-', 1)[-1].replace('-', ' ')


def captures_section(m, absolute):
    pngs = sorted(glob.glob(os.path.join(ROOT, 'captures', m, '*.png')))
    pngs = [p for p in pngs if re.search(r'-\d\.png$', os.path.basename(p)) is None or '99-preuves' in p]
    if not pngs:
        return ''
    out = ['\n## Captures\n']
    for p in pngs:
        fn = os.path.basename(p)
        url = f'{base_root}/captures/{m}/{fn}' if absolute else f'../../captures/{m}/{fn}'
        out.append(f'**{label(p)}**\n\n![{label(p)}]({url})\n')
    return '\n'.join(out)


parts = []
for path in sorted(glob.glob(os.path.join(SRC, 'm??.md'))):
    n = os.path.basename(path)[:-3]
    text = open(path, encoding='utf-8').read()
    tp = os.path.join(MOD, n, 'tests.txt')
    tests = open(tp, encoding='utf-8').read().rstrip() if os.path.exists(tp) else "(module non deployable : voir la section Statut - aucune mesure)"
    body = text.replace('{{TESTS}}', tests)
    open(os.path.join(MOD, n + '.md'), 'w', encoding='utf-8', newline='\n').write(body + captures_section(n, False))
    parts.append(body + (captures_section(n, True) if base else captures_section(n, False)))

header_path = os.path.join(SRC, 'entete.md')
header = open(header_path, encoding='utf-8').read() if os.path.exists(header_path) else ''
dossier = header + "\n\n" + "\n\n---\n\n".join(parts)
if base:
    dossier = re.sub(r'\]\(\.\./images/', '](' + base + '/', dossier)
open(os.path.join(ROOT, 'docs', 'DOSSIER.md'), 'w', encoding='utf-8', newline='\n').write(dossier)
print('modules assembles :', len(parts), '| caracteres :', len(dossier))

