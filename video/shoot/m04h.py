"""Module 4 : route de retour - rt-nat renvoie le trafic destine au sous-reseau prive vers l'endpoint du pare-feu (symetrie)."""
from common import *
from m04g import endpoint_id

async def run(r):
    ep = endpoint_id()
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-nat-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Destination').last, '10.20.1.0/26'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.0)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination').last)
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile("Point de terminaison de l'équilibreur")).first); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, ep[5:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(ep)).first); await r.hold(1.5)
    r.mark('route-retour'); await r.hold(1.5)
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
