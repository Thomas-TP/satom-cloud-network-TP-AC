"""Module 6 : les routes vers l'autre VPC passent de l'appairage au Transit Gateway."""
from common import *
import subprocess

def tgw_id():
    return subprocess.run(['aws', 'ec2', 'describe-transit-gateways', '--filters', 'Name=tag:Name,Values=tgw-leman-TP-AC', 'Name=state,Values=available', '--query', 'TransitGateways[0].TransitGatewayId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def to_tgw(r, rt, tgw):
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text=rt).get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.5)
    await r.click(lambda f: f.get_by_role('button', name="Connexion d'appairage").first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name='Transit Gateway', exact=True)); await r.hold(1.2)
    tgt = lambda f: f.get_by_role('combobox', name='Cible').nth(1)
    await r.type(tgt, tgw[4:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(tgw)).first); await r.hold(1.5)
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)

async def run(r):
    tgw = tgw_id()
    await to_tgw(r, 'rt-prive-leman-TP-AC', tgw); r.mark('route-prive')
    await to_tgw(r, 'rt-dev-leman-TP-AC', tgw); r.mark('route-dev'); await r.hold(2.0)
