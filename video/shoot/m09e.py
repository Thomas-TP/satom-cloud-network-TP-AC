"""Module 9 : le groupe app accepte aussi le 8080 depuis l'ALB."""
from common import *
from m08g import sg_id

async def run(r):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + sg_id('app-TP-AC')), wait=5); await r.hold(1.5)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    n = 8
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Plage de ports"]'), '8080'); await r.hold(0.5)
    await r.click(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]')); await r.hold(0.6)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]'), 'alb-TP'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(r'sg-[0-9a-f]+.*alb-TP-AC|alb-TP-AC.*sg-[0-9a-f]+')).first); await r.hold(0.8)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Description - facultatif"]'), 'API depuis alb'); await r.hold(1.0)
    r.mark('regle')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(1.5)
