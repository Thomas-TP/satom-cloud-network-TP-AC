"""Module 6 : la connexion d'appairage est devenue inutile : le Transit Gateway la remplace, on la supprime."""
from common import *

async def run(r):
    await r.goto(vpc_url('PeeringConnections:'), wait=5)
    await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('pcx-lab-TP-AC')).get_by_role('radio')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('button', name='Actions').first); await r.hold(1.2)
    r.mark('menu')
    await r.click_xy(1720, 372); await r.hold(2.5)
    r.mark('confirmation')
    await r.type(ph('supprimer'), 'supprimer'); await r.hold(1.0)
    await r.click(btn('Supprimer', True)); await r.hold(4.0)
    r.mark('supprimee'); await r.hold(2.0)
