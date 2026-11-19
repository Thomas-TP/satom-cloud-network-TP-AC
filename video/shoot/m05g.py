"""Module 5 : test depuis dev-01 : le 8080 de app-01 repond, le ping et le port 22 sont refuses."""
from common import *
from m02f import terminal

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('dev-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark('terminal')
    await terminal(r, ['hostname -I', 'curl -s -m 5 http://10.20.1.10:8080/api/health; echo'], pause=4.0)
    r.mark('api')
    await terminal(r, ['ping -c 2 -W 2 10.20.1.10 | tail -2'], pause=7.0)
    r.mark('ping-refuse')
    await terminal(r, ["timeout 4 bash -c '</dev/tcp/10.20.1.10/22' && echo port 22 ouvert || echo port 22 ferme"], pause=6.0)
    r.mark('ssh-ferme'); await r.hold(1.5)
