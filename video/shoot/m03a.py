"""Module 3 : Security Group web (443 ouvert a tous, 22 reserve a une plage de test)."""
from common import *

async def rule(r, n, port, cidr, desc=''):
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Plage de ports"]'), str(port)); await r.hold(0.5)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]'), cidr); await r.press('Enter', 0.8)
    if desc: await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Description - facultatif"]'), desc)

async def run(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4)
    await r.hold(1.0)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(2.0)
    await r.type(ph('MyWebServerGroup'), 'web-TP-AC'); await r.hold(0.5)
    await r.type(ph("Autorise l'accès SSH aux développeurs"), 'Web : 443 public, 22 plage de test'); await r.hold(0.5)
    await r.click('button:has-text("vpc-05507")'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    await r.scroll(400)
    await rule(r, 1, 443, '0.0.0.0/0', 'HTTPS public')
    r.mark('regle-443')
    await rule(r, 2, 22, '203.0.113.0/24', 'SSH plage de test')
    r.mark('regle-22'); await r.hold(1.0)
    await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', 'sg-web-TP-AC')], kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises'); await r.hold(1.0)
    await r.scroll(900)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(4.5)
    r.mark('cree'); await r.hold(2.0)
