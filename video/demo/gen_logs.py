"""Genere video/demo/lNN.ps1 : affiche docs/modules/mNN/tests.txt dans le vrai terminal, page par page (une capture par page)."""
import io, math, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = os.path.dirname(os.path.abspath(__file__)); NL = chr(10); COLS = 118; ROWS = 25
n_total = 0
for n in range(1, 14):
    m = 'm%02d' % n
    f = os.path.join(ROOT, 'docs', 'modules', m, 'tests.txt')
    if not os.path.exists(f): continue
    lines = io.open(f, encoding='utf-8').read().split(NL)
    while lines and not lines[-1].strip(): lines.pop()
    pages = []; cur = []; rows = 0
    for ln in lines:
        r = max(1, math.ceil(len(ln.expandtabs(8)) / COLS))
        if rows + r > ROWS and cur: pages.append(cur); cur = []; rows = 0
        cur.append(ln); rows += r
    if cur: pages.append(cur)
    out = []; skip = 0
    for i, pg in enumerate(pages, 1):
        rel = 'docs' + chr(92) + 'modules' + chr(92) + m + chr(92) + 'tests.txt'
        sel = ('Select-Object -First %d' % len(pg)) if skip == 0 else ('Select-Object -Skip %d -First %d' % (skip, len(pg)))
        out.append('Clear-Host')
        out.append("Show-Note 'Journal du test du module %d (page %d sur %d)'" % (n, i, len(pages)))
        out.append("Show-Cmd 'Get-Content %s | %s' 4 600" % (rel, sel))
        out.append("Show-Shot 'l%02d-%d'" % (n, i))
        skip += len(pg); n_total += 1
    io.open(os.path.join(D, 'l%02d.ps1' % n), 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    print(m, len(pages), 'page(s)')
print(n_total, 'captures de journaux prevues')
