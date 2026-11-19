"""Module 7 : tests depuis les routeurs des sites : l'API d'app-01 repond, le ping est refuse, dev-01 est injoignable."""
from common import *
from m02f import terminal

async def test(r, n, src):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(f'rtr-{n}-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark(f'{n}-terminal')
    await terminal(r, ['sudo -i', f'ip route get 10.20.1.10 from {src} | head -1'], pause=2.0)
    await terminal(r, [f'curl -s -m 6 --interface {src} http://10.20.1.10:8080/api/health; echo'], pause=4.0)
    r.mark(f'{n}-api')
    await terminal(r, [f'ping -c 2 -W 2 -I {src} 10.20.1.10 | tail -2'], pause=6.0)
    r.mark(f'{n}-ping')
    await terminal(r, [f'ping -c 2 -W 2 -I {src} 10.21.0.10 | tail -2'], pause=6.0)
    r.mark(f'{n}-dev'); await r.hold(1.5)

async def run(r):
    await test(r, 'siege', '192.168.10.10')
    await test(r, 'agence', '192.168.20.10')
