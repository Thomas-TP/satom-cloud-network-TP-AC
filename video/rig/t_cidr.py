import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\shoot')
from common import *
async def main():
    r = await Rig().connect()
    await r.goto(vpc_url('CreateVpc:createMode=vpcWithResources'), wait=5)
    print('loaded', flush=True)
    for f in r.page.frames:
        loc = f.locator('input[value=projet]')
        if await loc.count():
            await loc.click(); print('clicked', flush=True)
            await loc.fill('siege-TP-AC'); print('filled', await loc.input_value(), flush=True)
            await asyncio.wait_for(r.page.keyboard.type('x'), 5); print('typed', flush=True)
            break
    await r.pw.stop()
asyncio.run(main())
