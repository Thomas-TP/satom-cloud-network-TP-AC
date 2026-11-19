"""Module 4 : deux tables de routage pour le pare-feu : rt-fw (vers la NAT) et rt-nat (vers Internet, sous-reseau de la NAT)."""
from common import *

async def create_rt(r, name):
    await r.goto(vpc_url('CreateRouteTable:'), wait=4)
    await r.type(ph('my-route-table-01'), name); await r.hold(0.6)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC'))); await r.hold(1.0)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise')
    await r.click(btn('Créer une table de routage', True)); await r.hold(4.0)

async def add_route(r, kind, regex):
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Destination'), '0.0.0.0/0'); await r.hold(0.8)
    await r.click(lambda f: f.get_by_role('option', name='0.0.0.0/0', exact=True)); await r.hold(1.0)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=kind, exact=True)); await r.hold(1.2)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2 + 34); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(regex)).first); await r.hold(1.5)
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)

async def associate(r, subnet):
    await r.click(tab('Associations de sous-réseau')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les associations de sous-réseau').first); await r.hold(2.0)
    await r.click(lambda f: f.locator('tr', has_text=subnet).get_by_role('checkbox')); await r.hold(1.2)
    await r.click(btn('Enregistrer les associations')); await r.hold(4.0)

async def run(r):
    await create_rt(r, 'rt-fw-leman-TP-AC'); r.mark('rt-fw-creee')
    await add_route(r, 'Passerelle NAT', nat_id()); r.mark('rt-fw-route')
    await associate(r, 'sub-fw-1a-TP-AC'); r.mark('rt-fw-associee')
    await create_rt(r, 'rt-nat-leman-TP-AC'); r.mark('rt-nat-creee')
    await add_route(r, 'Passerelle Internet', 'igw-prod-leman-TP-AC'); r.mark('rt-nat-route')
    await associate(r, 'sub-public-1b-TP-AC'); r.mark('rt-nat-associee'); await r.hold(2.0)
