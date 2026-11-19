"""Execute quelques gestes puis liste la page. Usage : python step.py "click:btn:Creer un budget" "type:field:Nom:budget" ... (puis dump)"""
import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import *
import dump_lib

async def main():
    r = await Rig().connect()
    for s in sys.argv[1:]:
        k, *rest = s.split('|')
        if k == 'goto': await r.goto(rest[0], wait=6)
        elif k == 'click': await r.click(eval(rest[0]))
        elif k == 'type': await r.type(eval(rest[0]), rest[1])
        elif k == 'press': await r.press(rest[0], 1.5)
        elif k == 'scroll': await r.scroll(int(rest[0]))
        elif k == 'wait': await asyncio.sleep(float(rest[0]))
    await dump_lib.dump(r)
    await r.pw.stop()
asyncio.run(main())
