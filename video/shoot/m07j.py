"""Module 7 : routes statiques des sites dans la table de production du Transit Gateway (un VPN statique ne parle pas BGP)."""
from common import *
from m06e import rtb, pick
from m07i import vpn_id

async def route(r, n, cidr):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb('tgw-rt-prod-TP-AC')), wait=4); await r.hold(1.0)
    await r.click(tab('Acheminements')); await r.hold(2.0)
    await r.click(btn('Créer un acheminement statique', True)); await r.hold(3.0)
    await r.type(lambda f: f.get_by_role('combobox', name='CIDR'), cidr); await r.hold(0.8)
    await r.press('Enter', 0.6)
    await pick(r, vpn_id(n))
    r.mark(f'{n}-formulaire')
    await r.click(btn('Créer un acheminement statique', True)); await r.hold(4.0)
    r.mark(f'{n}-creee'); await r.hold(1.5)

async def run(r):
    await route(r, 'siege', '192.168.10.0/24'); await route(r, 'agence', '192.168.20.0/24')
