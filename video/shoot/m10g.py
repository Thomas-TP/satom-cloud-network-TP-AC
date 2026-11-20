"""Module 10 : vraie zone publique interrogee sur son serveur de noms AWS (depuis web-01), puis basculement quand nginx s'arrete sur web-01."""
from common import *
import subprocess
from m02f import terminal
from m07q import open_session
from m10c import zone_pub

async def run(r):
    ns = subprocess.run(['aws', 'route53', 'get-hosted-zone', '--id', zone_pub(), '--query', 'DelegationSet.NameServers[0]', '--output', 'text', '--profile', 'TP-AC'], capture_output=True, text=True).stdout.strip()
    main = r.page
    a = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i', 'dnf install -y -q bind-utils >/dev/null 2>&1; echo installe'], pause=1.0)
    r.mark('install-debut', accelere=6); await r.hold(20.0); r.mark('install-fin')
    await terminal(r, [f'NS={ns}', 'dig +short @$NS portefeuilles.leman.thomastp.ch'], pause=4.0)
    r.mark('zone-publique')
    await terminal(r, ['while true; do echo "$(date +%T) $(dig +short @$NS portefeuilles.leman.thomastp.ch | tr "\n" " ")"; sleep 3; done'], pause=8.0)
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
