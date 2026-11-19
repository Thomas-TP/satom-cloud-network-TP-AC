"""Module 5 : connexion d'appairage entre le VPC de production et le VPC de developpement, puis acceptation de la demande."""
from common import *

async def run(r):
    await r.goto(vpc_url('PeeringConnections:'), wait=5)
    await r.hold(1.5)
    await r.click(btn("Créer une connexion d'appairage", True)); await r.hold(2.5)
    await r.type(ph('my-pc-01'), 'pcx-lab-TP-AC'); await r.hold(0.6)
    await r.click(lambda f: f.get_by_role('button', name='Sélectionner un VPC').nth(0)); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('button', name='Sélectionner un VPC').nth(0)); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-dev-leman-TP-AC')).first); await r.hold(1.2)
    r.mark('vpc')
    await r.scroll(500)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn("Créer une connexion d'appairage", True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(1.5)
    await r.click(btn('Actions', True)); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('menuitem', name=re.compile('Accepter')).first, straight=True); await r.hold(2.0)
    r.mark('menu-accepter'); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Accepter la demande').last); await r.hold(5.0)
    r.mark('acceptee'); await r.hold(2.0)
