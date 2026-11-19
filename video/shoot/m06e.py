"""Module 6 : associations et propagations des tables du Transit Gateway."""
from common import *
import subprocess

def rtb(name):
    import time
    for _ in range(30):
        v = _rtb(name)
        if v and v != 'None': return v
        time.sleep(3)
    return v

def _rtb(name):
    return subprocess.run(['aws', 'ec2', 'describe-transit-gateway-route-tables', '--filters', f'Name=tag:Name,Values={name}', 'Name=state,Values=available', '--query', 'TransitGatewayRouteTables[0].TransitGatewayRouteTableId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def pick(r, att):
    await r.click(btn('Sélectionner un attachement de la passerelle de transit')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(att)).first); await r.hold(1.2)

async def assoc(r, table, att):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb(table)), wait=4)
    await r.hold(1.0)
    await r.click(btn('Créer une association', True)); await r.hold(2.5)
    await pick(r, att)
    r.mark('choix-' + att)
    await r.click(btn('Créer une association', True)); await r.hold(3.5)

async def prop(r, table, att):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb(table)), wait=4)
    await r.click(tab('Propagations')); await r.hold(1.5)
    await r.click(btn('Créer une propagation', True)); await r.hold(2.5)
    await pick(r, att)
    r.mark('choixp-' + att)
    await r.click(btn('Créer une propagation', True)); await r.hold(3.5)

async def run(r):
    await assoc(r, 'tgw-rt-prod-TP-AC', 'tgwa-prod-TP-AC'); r.mark('assoc-prod')
    await assoc(r, 'tgw-rt-dev-TP-AC', 'tgwa-dev-TP-AC'); r.mark('assoc-dev')
    await prop(r, 'tgw-rt-prod-TP-AC', 'tgwa-dev-TP-AC'); r.mark('prop-prod')
    await prop(r, 'tgw-rt-dev-TP-AC', 'tgwa-prod-TP-AC'); r.mark('prop-dev'); await r.hold(2.0)
