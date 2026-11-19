"""Module 7 : chaque routeur n'accepte le trafic que depuis les deux adresses publiques de ses tunnels AWS."""
from common import *
import json, subprocess

def tunnels(n):
    out = subprocess.run(['aws', 'ec2', 'describe-vpn-connections', '--filters', f'Name=tag:Name,Values=vpn-{n}-TP-AC', 'Name=state,Values=available', '--query', 'VpnConnections[0].VgwTelemetry[].OutsideIpAddress', '--output', 'json', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout
    return json.loads(out)

def sg_id(n):
    return subprocess.run(['aws', 'ec2', 'describe-security-groups', '--filters', f'Name=group-name,Values=rtr-{n}-TP-AC', '--query', 'SecurityGroups[0].GroupId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def regles(r, n):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + sg_id(n)), wait=5); await r.hold(1.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    for k, ip in enumerate(tunnels(n), 1):
        await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
        await r.click(lambda f, k=k: f.get_by_role('button', name=re.compile('TCP personnalisé')).last); await r.hold(1.0)
        await r.click(lambda f: f.get_by_role('option', name='Tout le trafic', exact=True)); await r.hold(1.0)
        await r.type(lambda f, k=k: f.locator('input[aria-label="Règle entrante %d Sélecteur CIDR"]' % k), ip + '/32'); await r.press('Enter', 0.8)
        await r.type(lambda f, k=k: f.locator('input[aria-label="Règle entrante %d Description - facultatif"]' % k), f'Tunnel {k} AWS'); await r.hold(0.8)
    r.mark(f'{n}-regles')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark(f'{n}-enregistrees'); await r.hold(1.5)

async def run(r):
    await regles(r, 'siege'); await regles(r, 'agence')
