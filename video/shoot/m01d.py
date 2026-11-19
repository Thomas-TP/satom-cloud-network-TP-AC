"""Module 1 : role IAM pour que les instances soient administrables par SSM (sans SSH)."""
from common import *

async def run(r):
    await r.goto('https://us-east-1.console.aws.amazon.com/iam/home#/roles', wait=5)
    await r.hold(1.5)
    await r.goto('https://us-east-1.console.aws.amazon.com/iam/home#/roles/create?step=selectEntities', wait=3)
    r.mark('assistant')
    await r.click(btn("Choisissez un service ou un cas d'utilisation")); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name='EC2', exact=True)); await r.hold(1.5)
    await r.click(btn('Suivant', True)); await r.hold(2.5)
    r.mark('autorisations')
    await r.type(lambda f: f.get_by_placeholder(re.compile('Filtrer|Rechercher')).last, 'AmazonSSMManagedInstanceCore'); await r.press('Enter', 2.0)
    await r.click(lambda f: f.get_by_role('checkbox').nth(1) if False else f.locator('tr', has_text='AmazonSSMManagedInstanceCore').get_by_role('checkbox')); await r.hold(1.2)
    r.mark('politique-cochee')
    for _ in range(3):
        await r.click(btn('Suivant', True)); await r.hold(2.0)
        if await r.present(lambda f: f.get_by_label('Nom du rôle'), 1.0): break
    await r.type(lambda f: f.get_by_label('Nom du rôle'), 'TP-AC-ec2-ssm-role'); await r.hold(1.0)
    await r.scroll(1500); await r.hold(1.0)
    r.mark('nom')
    await r.click(btn('Créer un rôle')); await r.hold(4.0)
    r.mark('cree'); await r.hold(2.5)
