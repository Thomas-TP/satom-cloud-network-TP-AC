"""Capture d'ecran du Chrome dedie (diagnostic). Usage : python shot.py [sortie.png]"""
import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import Rig


async def main():
    r = await Rig().connect()
    out = sys.argv[1] if len(sys.argv) > 1 else r'C:\Perso\AWS\video\work\shot.png'
    await r.page.screenshot(path=out, scale='css')
    from PIL import Image
    im = Image.open(out); im.thumbnail((1400, 800)); im.save(out)
    print(r.page.url.split('#')[-1][:80], '->', out)
    await r.pw.stop()

asyncio.run(main())
