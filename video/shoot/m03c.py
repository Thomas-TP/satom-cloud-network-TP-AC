"""Module 3 : application des Security Groups aux instances web-01 et app-01 (en remplacement du groupe par defaut)."""
import subprocess
from common import *

def iid(name):
    return subprocess.run(['aws', 'ec2', 'describe-instances', '--filters', f'Name=tag:Name,Values={name}', 'Name=instance-state-name,Values=running,pending', '--query', 'Reservations[0].Instances[0].InstanceId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

async def change_sg(r, inst, sg):
    await r.goto(ec2_url('Instances:instanceState=running'), wait=4)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(inst)).get_by_role('checkbox')); await r.hold(1.0)
    await r.click(btn('Actions', True)); await r.hold(1.2)
    await r.hover(lambda f: f.get_by_role('menuitem', name=re.compile('Sécurité')).first, pause=1.8)
    await r.press('Escape', 0.5)
    await r.goto(ec2_url('ChangeSecurityGroups:instanceId=' + iid(inst)), wait=3)
    r.mark('modifier-' + inst)
    await r.click(ph('Sélectionner les groupes de sécurité')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(sg)).first); await r.hold(1.0)
    await r.click(btn('Ajouter un groupe de sécurité', True)); await r.hold(1.5)
    await r.click(lambda f: f.locator('tr', has_text='default').get_by_role('button', name='Supprimer')); await r.hold(1.2)
    r.mark('groupes-' + inst)
    await r.click(btn('Enregistrer', True)); await r.hold(4.0)

async def run(r):
    await change_sg(r, 'web-01-TP-AC', 'web-TP-AC')
    await change_sg(r, 'app-01-TP-AC', 'app-TP-AC')
    r.mark('termine'); await r.hold(2.0)
