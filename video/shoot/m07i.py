"""Module 7 : table de routage des sites sur le Transit Gateway : les deux VPN y sont associes, seule la production s'y propage."""
from common import *
import subprocess
from m06d import table
from m06e import rtb, pick

def vpn_id(n):
    return subprocess.run(['aws', 'ec2', 'describe-vpn-connections', '--filters', f'Name=tag:Name,Values=vpn-{n}-TP-AC', 'Name=state,Values=available', '--query', 'VpnConnections[0].VpnConnectionId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def assoc_vpn(r, n):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb('tgw-rt-sites-TP-AC')), wait=4); await r.hold(1.0)
    await r.click(btn('Créer une association', True)); await r.hold(2.5)
    await pick(r, vpn_id(n))
    r.mark(f'choix-{n}')
    await r.click(btn('Créer une association', True)); await r.hold(3.5)

async def run(r):
    await table(r, 'tgw-rt-sites-TP-AC', 'prod'); r.mark('table-creee')
    await assoc_vpn(r, 'siege'); r.mark('assoc-siege')
    await assoc_vpn(r, 'agence'); r.mark('assoc-agence')
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb('tgw-rt-sites-TP-AC')), wait=4)
    await r.click(tab('Propagations')); await r.hold(1.5)
    await r.click(btn('Créer une propagation', True)); await r.hold(2.5)
    await pick(r, 'tgwa-prod-TP-AC'); r.mark('choix-prop')
    await r.click(btn('Créer une propagation', True)); await r.hold(4.0)
    r.mark('prop-prod'); await r.hold(1.5)
