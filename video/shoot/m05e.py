"""Module 5 : routes des deux cotes de la connexion d'appairage (prive vers dev, dev vers prod)."""
from common import *
import subprocess

def pcx_id():
    return subprocess.run(['aws', 'ec2', 'describe-vpc-peering-connections', '--filters', 'Name=tag:Name,Values=pcx-lab-TP-AC', 'Name=status-code,Values=active', '--query', 'VpcPeeringConnections[0].VpcPeeringConnectionId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def route_pcx(r, rt, cidr, pcx):
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text=rt).get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    dest = lambda f: f.get_by_role('combobox', name='Destination').last
    await r.type(dest, cidr); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.0)
    b = await r._box(dest)
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name="Connexion d'appairage", exact=True)); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, pcx[4:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(pcx)).first); await r.hold(1.5)
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)

async def run(r):
    pcx = pcx_id()
    await route_pcx(r, 'rt-prive-leman-TP-AC', '10.21.0.0/24', pcx); r.mark('route-prive')
    await route_pcx(r, 'rt-dev-leman-TP-AC', '10.20.0.0/22', pcx); r.mark('route-dev'); await r.hold(2.0)
