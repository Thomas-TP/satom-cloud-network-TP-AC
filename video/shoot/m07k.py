"""Module 7 : dans la table privee du VPC de production, les plages du siege et de l'agence passent par le Transit Gateway."""
from common import *
from m06f import tgw_id

async def run(r):
    tgw = tgw_id()
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-prive-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.5)
    for cidr in ('192.168.10.0/24', '192.168.20.0/24'):
        await r.click(btn('Ajouter une route')); await r.hold(1.2)
        dest = lambda f: f.get_by_role('combobox', name='Destination').last
        await r.type(dest, cidr); await r.hold(1.0)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.0)
        b = await r._box(dest)
        await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
        await r.click(lambda f: f.get_by_role('option', name='Transit Gateway', exact=True)); await r.hold(1.2)
        await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, tgw[4:], clear=False); await r.hold(1.5)
        await r.click(lambda f: f.get_by_role('option', name=re.compile(tgw)).first); await r.hold(1.5)
    r.mark('routes')
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)
    r.mark('enregistrees'); await r.hold(2.0)
