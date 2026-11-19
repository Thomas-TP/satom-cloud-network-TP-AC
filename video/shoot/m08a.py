"""Module 8 : la passerelle Direct Connect (ASN 64513, different de celui du Transit Gateway)."""
from common import *

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/directconnect/v2/home?region=eu-north-1#/dxgateways', wait=6); await r.hold(2.5)
    r.mark('page-dx')
    await r.click(lambda f: f.get_by_role('link', name='Créer une passerelle Direct Connect').first); await r.hold(2.5)
    await r.type(ph('Ma passerelle Direct Connect'), 'dxgw-leman-TP-AC'); await r.hold(0.6)
    await r.type(lambda f: f.locator('input[type=number]'), '64513'); await r.hold(1.0)
    r.mark('asn')
    await r.scroll(400)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle identification', kp='Saisir une clé', vp='Saisir une valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une passerelle Direct Connect', True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(2.0)
