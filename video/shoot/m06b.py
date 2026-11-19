"""Module 6 : attachement du VPC de production au Transit Gateway."""
from common import *

async def attach(r, name, vpc, subnet):
    await r.goto(vpc_url('CreateTransitGatewayAttachment:'), wait=4)
    await r.type(ph('transit-de transit-attachment-01'), name); await r.hold(0.6)
    await r.click(btn('Sélectionner une passerelle de transit')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('tgw-leman-TP-AC')).first); await r.hold(1.2)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(vpc)).first); await r.hold(1.5)
    await r.hold(1.0)
    r.mark('vpc')
    if 'prod' in vpc:
        await r.click(lambda f: f.locator('button:has-text("subnet-")').first); await r.hold(1.0)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('sub-prive-1a-TP-AC')).first); await r.hold(1.2)
        await r.click(lambda f: f.get_by_text('eu-north-1b', exact=True).first); await r.hold(1.2)
    await r.hold(0.5)
    await r.scroll(500)
    await tags(r, 'prod' if 'prod' in vpc else 'dev', start=1, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une association pour Transit Gateway', True)); await r.hold(5.0)

async def run(r):
    await attach(r, 'tgwa-prod-TP-AC', 'vpc-prod-leman-TP-AC', 'sub-prive-1a-TP-AC')
    r.mark('creee'); await r.hold(2.0)
