"""Tourne une scene : python shoot.py m00 [--dry]  -> video/raw/<scene>.mp4 (+ .marks.json).
Le fichier scenes <scene>.py doit definir async def run(r). En cas d'erreur : capture + liste des elements, l'enregistrement est conserve en .FAILED.mp4."""
import asyncio, importlib.util, os, sys, traceback
sys.path.insert(0, r'C:\Perso\AWS\video\rig'); sys.path.insert(0, r'C:\Perso\AWS\video\shoot')
from rig import *
import dump_lib

RAW = r'C:\Perso\AWS\video\raw'

async def main():
    name = sys.argv[1]; dry = '--dry' in sys.argv
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + '.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    r = await Rig().connect()
    out = os.path.join(RAW, name + '.mp4')
    if not dry: await r.start(out)
    ok = True
    try:
        await mod.run(r)
    except Exception:
        ok = False; traceback.print_exc()
        try: await dump_lib.dump(r, shot=os.path.join(RAW, name + '.FAILED.png'))
        except Exception: pass
    if not dry:
        await r.stop()
        if not ok:
            os.replace(out, os.path.join(RAW, name + '.FAILED.mp4'))
    await r.pw.stop()
    print('OK' if ok else 'ECHEC', name); sys.exit(0 if ok else 1)

asyncio.run(main())
