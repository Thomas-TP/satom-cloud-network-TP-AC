"""Teste le demarrage d'une session Session Manager (attend d'abord N secondes). Usage : python test_session.py [attente] [instance]"""
import asyncio, re, sys
sys.path.insert(0, r'C:\Perso\AWS\video\shoot')
from common import *


async def main():
    wait = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    name = sys.argv[2] if len(sys.argv) > 2 else 'app-01-TP-AC'
    r = await Rig().connect()
    await asyncio.sleep(wait)
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=6)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(name)).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(5)
    print('pages', len(before), len(r.ctx.pages))
    await r.pw.stop()

asyncio.run(main())
