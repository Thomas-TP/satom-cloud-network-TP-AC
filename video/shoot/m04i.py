"""Module 4 : depuis app-01, un depot autorise repond, un site non autorise est bloque par le pare-feu."""
from common import *
from m02f import terminal

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('app-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark('terminal')
    await terminal(r, ['curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://cdn.amazonlinux.com/; echo'], pause=5.0)
    r.mark('autorise')
    await terminal(r, ['curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://example.com/; echo'], pause=14.0)
    r.mark('bloque')
    await terminal(r, ['curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://www.wikipedia.org/; echo'], pause=14.0)
    r.mark('bloque2'); await r.hold(1.0)
