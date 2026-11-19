"""Module 4 : le pare-feu est pret ; la route par defaut du prive passe par son endpoint, et rt-nat renvoie le retour vers le pare-feu."""
from common import *
import subprocess

def endpoint_id():
    out = subprocess.run(['aws', 'network-firewall', 'describe-firewall', '--firewall-name', 'nfw-prod-leman-TP-AC', '--query', 'FirewallStatus.SyncStates', '--output', 'json', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout
    import json
    return list(json.loads(out).values())[0]['Attachment']['EndpointId']

async def run(r):
    await r.goto(vpc_url('NetworkFirewalls:'), wait=5)
    await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('link', name='nfw-prod-leman-TP-AC').first); await r.hold(2.5)
    await r.click(tab('Associations de points de terminaison')); await r.hold(2.5)
    r.mark('pare-feu-pret'); await r.hold(2.0)
    ep = endpoint_id()
    # rt-prive : 0.0.0.0/0 vers l'endpoint du pare-feu
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-prive-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Passerelle NAT').first); await r.hold(1.2)
    r.mark('type-cible')
    await r.click(lambda f: f.get_by_role('option', name=re.compile("Point de terminaison de l'équilibreur")).first); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, ep[5:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(ep)).first); await r.hold(1.5)
    r.mark('route-prive-pare-feu')
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    r.mark('route-prive-enregistree')
