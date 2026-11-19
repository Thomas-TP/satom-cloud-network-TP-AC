"""Module 8 : regles pour le GRE (protocole 47) sur rtr-aws et rtr-siege, et le 8080 d'app-01 pour rtr-aws."""
from common import *
import subprocess

def sg_id(name):
    v = _sg_id(name)
    return v if v.startswith('sg-') else _ids()['sg_' + name]

def _sg_id(name):
    return subprocess.run(['aws', 'ec2', 'describe-security-groups', '--filters', f'Name=group-name,Values={name}', '--query', 'SecurityGroups[0].GroupId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

def aws_pub():
    return subprocess.run(['aws', 'ec2', 'describe-instances', '--filters', 'Name=tag:Name,Values=rtr-aws-TP-AC', 'Name=instance-state-name,Values=running', '--query', 'Reservations[0].Instances[0].PublicIpAddress', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def editor(r, name):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + sg_id(name)), wait=5); await r.hold(1.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)

async def gre_rule(r, n, cidr, desc):
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('TCP personnalisé')).last); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name='Protocole personnalisé', exact=True)); await r.hold(1.0)
    await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Protocole"]' % n), '47'); await r.press('Enter', 0.6)
    await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Sélecteur CIDR"]' % n), cidr); await r.press('Enter', 0.8)
    await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Description - facultatif"]' % n), desc); await r.hold(0.8)

async def run(r):
    await editor(r, 'rtr-aws-TP-AC')
    await gre_rule(r, 1, eip_ip('siege') + '/32', 'GRE Direct Connect simule')
    await gre_rule(r, 2, '192.168.10.0/24', 'GRE dans le VPN')
    r.mark('aws-regles')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    await editor(r, 'rtr-siege-TP-AC')
    # deux regles existent deja (tunnels) : les nouvelles sont les numeros 3 et 4
    await gre_rule(r, 3, aws_pub() + '/32', 'GRE Direct Connect simule')
    await gre_rule(r, 4, '10.20.0.74/32', 'GRE dans le VPN')
    r.mark('siege-regles')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    await editor(r, 'app-TP-AC')
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante 7 Plage de ports"]'), '8080'); await r.hold(0.5)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante 7 Sélecteur CIDR"]'), '10.20.0.74/32'); await r.press('Enter', 0.8)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante 7 Description - facultatif"]'), 'API depuis rtr-aws'); await r.hold(1.0)
    r.mark('app-regle')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('fin'); await r.hold(1.5)
