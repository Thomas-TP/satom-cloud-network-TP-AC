"""Module 13 : une regle SSH ajoutee a la main sur le Security Group web de la pile : c'est la derive."""
from common import *
from common import _ids

async def run(r):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + _ids()['sg_web_cfn']), wait=6); await r.hold(2.0)
    await r.click(tab('Règles entrantes')); await r.hold(2.0)
    r.mark('avant'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    n = 2
    await r.click(lambda f: f.get_by_role('button', name=re.compile('TCP personnalisé')).last); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name='SSH', exact=True)); await r.hold(1.0)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]'), '203.0.113.0/24'); await r.press('Enter', 0.8)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Description - facultatif"]'), 'SSH ajoute a la main'); await r.hold(1.0)
    r.mark('regle')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
