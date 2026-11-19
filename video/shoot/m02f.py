"""Module 2 : Session Manager sur app-01 (sans adresse publique) : Internet est visible avec l'adresse de la NAT."""
from common import *

async def terminal(r, cmds, pause=2.5):
    for c in cmds:
        for ch in c:
            await r.page.keyboard.type(ch); await asyncio.sleep(0.05)
        await r.page.keyboard.press('Enter'); await asyncio.sleep(pause)

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('app-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    r.mark('instance-choisie')
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    assert new, 'onglet de session introuvable'
    await r.follow(new[0]); await r.hold(8.0)
    r.mark('terminal')
    await r.click_xy(900, 500)
    await terminal(r, ['whoami', 'hostname -I', 'curl -s https://checkip.amazonaws.com'])
    r.mark('ip-nat'); await r.hold(3.0)
