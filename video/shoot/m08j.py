"""Module 8 : le sous-reseau de rtr-aws (zone B) utilise la table rt-nat : on y ajoute aussi la route vers le siege par le Transit Gateway."""
from common import *
from m06f import tgw_id

async def run(r):
    tgw = tgw_id()
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-nat-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Associations de sous-réseau')); await r.hold(2.0)
    r.mark('association')
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.5)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    dest = lambda f: f.get_by_role('combobox', name='Destination').last
    await r.type(dest, '192.168.10.0/24'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.0)
    b = await r._box(dest)
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name='Transit Gateway', exact=True)); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, tgw[4:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(tgw)).first); await r.hold(1.5)
    r.mark('route')
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
