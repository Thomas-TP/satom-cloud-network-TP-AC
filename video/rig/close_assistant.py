import asyncio, sys
from rig import *
async def main():
    r = await Rig().connect()
    for f in r.page.frames:
        try:
            n = await f.evaluate("""() => { const b=[...document.querySelectorAll('button')].find(x=>/Fermer AWS assistant|Close AWS assistant|Fermer le panneau/i.test(x.getAttribute('aria-label')||x.innerText)); if(b){b.click(); return 1} return 0 }""")
            if n: print('ferme'); break
        except Exception: pass
    await r.pw.stop()
asyncio.run(main())
