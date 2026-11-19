"""Diagnostic : liste les frames et les champs de saisie de chaque frame. Usage : python probe.py [url]"""
import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import Rig


async def main():
    r = await Rig().connect()
    if len(sys.argv) > 1 and sys.argv[1].startswith('http'): await r.goto(sys.argv[1], wait=7)
    for f in r.page.frames:
        try:
            n = await f.evaluate("document.querySelectorAll('input').length")
            res = await f.evaluate("""() => [...document.querySelectorAll('input')].filter(e => e.getBoundingClientRect().width>0).slice(0,6).map(e => ({type:e.type, ph:(e.placeholder||'').slice(0,50)}))""")
            print(f.url[:90], '| inputs:', n, res)
        except Exception as e:
            print(f.url[:90], 'ERR', str(e)[:60])
    await r.pw.stop()

asyncio.run(main())
