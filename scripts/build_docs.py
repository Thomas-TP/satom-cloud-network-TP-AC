"""Assemble les modules : docs/src/mNN.md + preuves docs/modules/mNN/tests.txt -> docs/modules/mNN.md et docs/DOSSIER.md
Usage : python -I scripts/build_docs.py [URL_BASE_IMAGES]   (ex. https://raw.githubusercontent.com/<user>/<repo>/main/docs/images)
"""
import os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'docs', 'src')
MOD = os.path.join(ROOT, 'docs', 'modules')
base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else None

NAMES = {}
parts = []
for path in sorted(glob.glob(os.path.join(SRC, 'm??.md'))):
    n = os.path.basename(path)[:-3]
    text = open(path, encoding='utf-8').read()
    tp = os.path.join(MOD, n, 'tests.txt')
    tests = open(tp, encoding='utf-8').read().rstrip() if os.path.exists(tp) else "(module non deployable : voir la section Statut - aucune mesure)"
    out = text.replace('{{TESTS}}', tests)
    open(os.path.join(MOD, n + '.md'), 'w', encoding='utf-8', newline='\n').write(out)
    parts.append(out)

dossier = "\n\n---\n\n".join(parts)
if base:
    dossier = re.sub(r'\]\(\.\./images/', '](' + base + '/', dossier)
header = open(os.path.join(ROOT, 'docs', 'src', 'entete.md'), encoding='utf-8').read() if os.path.exists(os.path.join(ROOT, 'docs', 'src', 'entete.md')) else ''
open(os.path.join(ROOT, 'docs', 'DOSSIER.md'), 'w', encoding='utf-8', newline='\n').write(header + "\n\n" + dossier)
print('modules assembles :', len(parts))
