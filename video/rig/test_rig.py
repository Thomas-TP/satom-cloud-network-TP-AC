import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import Rig


async def main():
    r = await Rig().connect()
    await r.goto('https://eu-north-1.console.aws.amazon.com/vpcconsole/home?region=eu-north-1#vpcs:', wait=4)
    await r.start(r'C:\Perso\AWS\video\work\test-rig.mp4')
    try:
        r.mark('debut')
        await r.hold(1.5)
        await r.click('a:has-text("Sous-réseaux") >> nth=0')
        await r.hold(3)
        await r.type('input[placeholder*="attribut ou par balise"]', 'TP-AC')
        await r.press('Enter', 2)
        r.mark('filtre')
        await r.hover(lambda f: f.get_by_role('row').nth(1))
        await r.click('a:has-text("Tables de routage") >> nth=0')
        await r.hold(3)
        r.mark('fin')
    finally:
        await r.stop(); await r.pw.stop()

asyncio.run(main())
