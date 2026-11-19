"""Module 5 : le groupe app ouvre le 8080 aux adresses du VPC de dev (10.21.0.0/24), rien d'autre."""
from common import *

async def run(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='app-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    n = 4
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante %d Plage de ports"]' % n), '8080'); await r.hold(0.5)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante %d Sélecteur CIDR"]' % n), '10.21.0.0/24'); await r.press('Enter', 0.8)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante %d Description - facultatif"]' % n), 'API depuis le VPC de dev'); await r.hold(1.0)
    r.mark('regle')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
