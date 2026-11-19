"""Diagnostic : capture + liste des elements interactifs visibles de toutes les frames. Usage : python dump.py [url] [--wait N] [--shot sortie.png]"""
import asyncio, sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import Rig

JS = """() => [...document.querySelectorAll('button,a,input,textarea,select,[role=tab],[role=radio],[role=checkbox],[role=combobox],[role=option],[role=menuitem],[role=switch],label')]
  .filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && b.y < 1100 && b.y > -5 && !e.closest('[style*="display: none"]'); })
  .slice(0, 160).map(e => ({t: e.tagName[0] + (e.type ? ':' + e.type : ''), r: e.getAttribute('role') || '', n: (e.getAttribute('aria-label') || e.innerText || e.placeholder || e.value || '').trim().replace(/\\s+/g, ' ').slice(0, 55),
     x: Math.round(e.getBoundingClientRect().x), y: Math.round(e.getBoundingClientRect().y), dis: e.disabled || e.getAttribute('aria-disabled') === 'true' ? 'X' : ''}))"""


async def main():
    a = sys.argv[1:]
    r = await Rig().connect()
    wait = 5
    if '--wait' in a: wait = float(a[a.index('--wait') + 1])
    if a and a[0].startswith('http'): await r.goto(a[0], wait=wait)
    if '--shot' in a: await r.page.screenshot(path=a[a.index('--shot') + 1], scale='css')
    print('URL:', r.page.url.split('console.aws.amazon.com')[-1][:110])
    for i, f in enumerate(r.page.frames):
        if 'about:blank' not in f.url and 'console.aws.amazon.com' not in f.url: continue
        try: els = await f.evaluate(JS)
        except Exception: continue
        if not els: continue
        print(f'--- frame {i}')
        for e in els:
            if e['n'] or e['t'].startswith('I'): print(f"  {e['t']:<9}{e['r']:<9}{e['n']:<56}({e['x']},{e['y']}){e['dis']}")
    await r.pw.stop()

asyncio.run(main())
