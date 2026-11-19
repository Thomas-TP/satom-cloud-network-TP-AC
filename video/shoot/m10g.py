"""Module 10 : zone publique interrogee sur son serveur de noms AWS (depuis rtr-siege), puis basculement quand nginx s'arrete sur web-01."""
from common import *
from common import _ids
from m02f import terminal
from m07q import open_session

async def run(r):
    ns = _ids()['ns']
    main = r.page
    a = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i', 'apt-get install -y -qq dnsutils >/dev/null 2>&1; echo installe'], pause=1.0)
    r.mark('install-debut', accelere=6); await r.hold(25.0); r.mark('install-fin')
    await terminal(r, [f'NS={ns}', 'dig +short @$NS portefeuilles.leman-finance.example'], pause=4.0)
    r.mark('zone-publique')
    await terminal(r, ['while true; do echo "$(date +%T) $(dig +short @$NS portefeuilles.leman-finance.example | tr "\n" " ")"; sleep 3; done'], pause=8.0)
    r.mark('boucle')
    await r.follow(main)
    b = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i', 'systemctl stop nginx; date +%T'], pause=2.0)
    r.mark('arret')
    await r.follow(a); await r.hold(70.0)
    r.mark('bascule')
    await r.follow(b)
    await terminal(r, ['systemctl start nginx; date +%T'], pause=2.0)
    r.mark('relance')
    await r.follow(a)
    r.mark('retour-debut', accelere=4); await r.hold(240.0); r.mark('retour-fin')
    r.mark('retour')
    await r.page.keyboard.press('Control+C'); await r.hold(1.5)
