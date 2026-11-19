"""Module 7 : dans la console, les deux tunnels de chaque VPN sont a l'etat Haut, et le Transit Gateway voit les routes des sites."""
from common import *
from m07i import vpn_id
from m06e import rtb

async def vpn(r, n):
    await r.goto(vpc_url('VpnConnections:'), wait=5); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(f'vpn-{n}-TP-AC.*Disponible')).get_by_role('radio').first); await r.hold(1.2)
    await r.click(tab('Détails du tunnel')); await r.hold(3.0)
    r.mark(f'{n}-tunnels'); await r.hold(3.0)

async def run(r):
    await vpn(r, 'siege'); await vpn(r, 'agence')
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb('tgw-rt-prod-TP-AC')), wait=4)
    await r.click(tab('Acheminements')); await r.hold(4.0)
    r.mark('routes-prod'); await r.hold(3.5)
