import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\shoot')
from common import *
from m13b import stack_url
async def main():
    r = await Rig().connect()
    await r.goto(stack_url(), wait=9)
    await r.click(lambda f: f.get_by_role('button', name='Actions de pile').first); await r.hold(1.5)
    await r.page.screenshot(path=r'C:\Perso\AWS\video\work\shot.png', scale='css')
    await r.pw.stop()
asyncio.run(main())
