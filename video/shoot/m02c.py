"""Module 2 : table de routage privee associee au sous-reseau prive (la route vers la NAT viendra apres sa creation)."""
from common import *

async def run(r):
    await r.goto(vpc_url('CreateRouteTable:'), wait=4)
    await r.hold(1.0)
    await r.type(ph('my-route-table-01'), 'rt-prive-leman-TP-AC'); await r.hold(0.8)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC'))); await r.hold(1.0)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise')
    r.mark('formulaire'); await r.hold(1.0)
    await r.click(btn('Créer une table de routage')); await r.hold(4.0)
    r.mark('creee'); await r.hold(1.5)
    await r.click(tab('Associations de sous-réseau')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les associations de sous-réseau').first); await r.hold(2.0)
    await r.click(lambda f: f.locator('tr', has_text='sub-prive-1a-TP-AC').get_by_role('checkbox')); await r.hold(1.2)
    r.mark('sous-reseau-coche')
    await r.click(btn('Enregistrer les associations')); await r.hold(4.0)
    r.mark('associee'); await r.hold(2.0)
