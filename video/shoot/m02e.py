"""Module 2 : route par defaut du sous-reseau prive vers la passerelle NAT."""
from common import *

async def run(r):
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.hold(1.5)
    await r.click(lambda f: f.locator('tr', has_text='rt-prive-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Destination'), '0.0.0.0/0'); await r.hold(0.8)
    await r.click(lambda f: f.get_by_role('option', name='0.0.0.0/0', exact=True)); await r.hold(1.0)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name='Passerelle NAT', exact=True)); await r.hold(1.2)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2 + 34); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(nat_id())).first); await r.hold(1.5)
    r.mark('route-nat')
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    r.mark('route-enregistree'); await r.hold(3.0)
