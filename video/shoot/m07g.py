"""Module 7 : les deux Customer Gateways (la description de chaque routeur de site : son adresse publique)."""
from common import *

async def cgw(r, n):
    await r.goto(vpc_url('CreateCustomerGateway:'), wait=4); await r.hold(1.2)
    await r.type(ph('customer-gateway-01'), f'cgw-{n}-TP-AC'); await r.hold(0.6)
    await r.type(ph('Saisir le numéro ASN BGP'), '65000'); await r.hold(0.8)
    await r.type(ph('192.0.2.1'), eip_ip(n)); await r.hold(1.0)
    r.mark(f'{n}-formulaire')
    await r.scroll(500)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    await r.scroll(900)
    await r.click(btn('Création d’une passerelle client', True)); await r.hold(4.5)
    r.mark(f'{n}-creee'); await r.hold(1.5)

async def run(r):
    await cgw(r, 'siege'); await cgw(r, 'agence')
