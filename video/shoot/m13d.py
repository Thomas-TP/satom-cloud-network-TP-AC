"""Module 13 : detection de derive : la pile est DRIFTED, le Security Group web a une regle qui n'est pas dans le modele."""
from common import *
from m13b import stack_url

async def run(r):
    await r.goto(stack_url(), wait=9); await r.hold(2.0)
    r.mark('avant')
    await r.click(lambda f: f.get_by_role('button', name='Actions de pile').first); await r.hold(1.5)
    await r.click_xy(1495, 224); await r.hold(4.0)
    r.mark('detection'); await r.hold(25.0)
    await r.goto(stack_url(), wait=9); await r.hold(3.0)
    r.mark('derive'); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Actions de pile').first); await r.hold(1.5)
    await r.click_xy(1541, 195); await r.hold(6.0)
    r.mark('resultats'); await r.hold(3.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('SgWeb')).get_by_role('radio').first); await r.hold(1.2)
    await r.click(btn("Afficher les détails de l'écart", True)); await r.hold(5.0)
    r.mark('detail'); await r.hold(4.0)
