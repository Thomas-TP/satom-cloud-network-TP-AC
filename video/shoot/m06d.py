"""Module 6 : les deux tables de routage du Transit Gateway (prod et dev)."""
from common import *

async def table(r, name, env):
    await r.goto(vpc_url('CreateTransitGatewayRouteTable:'), wait=4)
    await r.type(ph('transit-gateway-route-table-01'), name); await r.hold(0.6)
    await r.click(btn('Sélectionner une passerelle de transit')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('tgw-leman-TP-AC')).first); await r.hold(1.2)
    await r.scroll(400)
    await tags(r, env, start=1, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une table de routage pour la passerelle de transit', True)); await r.hold(4.0)

async def run(r):
    await table(r, 'tgw-rt-prod-TP-AC', 'prod'); r.mark('prod-creee')
    await table(r, 'tgw-rt-dev-TP-AC', 'dev'); r.mark('dev-creee'); await r.hold(2.0)
