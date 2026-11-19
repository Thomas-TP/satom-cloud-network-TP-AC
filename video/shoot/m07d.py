"""Module 7 : un Security Group par routeur de site (aucune entree pour l'instant ; les regles IPsec viendront une fois les tunnels connus)."""
from common import *

async def sg(r, n):
    await r.goto(ec2_url('SecurityGroups:'), wait=4); await r.hold(1.0)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(2.0)
    await r.type(ph('MyWebServerGroup'), f'rtr-{n}-TP-AC'); await r.hold(0.5)
    await r.type(ph("Autorise l'accès SSH aux développeurs"), f'Routeur du site {n} : IPsec uniquement'); await r.hold(0.5)
    await r.click(lambda f: f.locator('button:has-text("vpc-05507")').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(f'vpc-{n}-TP-AC')).first); await r.hold(1.5)
    await r.scroll(400); await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', f'sg-rtr-{n}-TP-AC')], kp='Saisir la clé', vp='Saisir la valeur')
    await r.scroll(900)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(4.5)
    r.mark(f'{n}-cree'); await r.hold(1.5)

async def run(r):
    await sg(r, 'siege'); await sg(r, 'agence')
