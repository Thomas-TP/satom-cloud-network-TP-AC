"""Module 11 : la NACL du sous-reseau public bloquait le port 80 : CloudFront n'atteint pas l'ALB (erreur 504). On ajoute la regle 105."""
from common import *

async def run(r):
    await r.goto(vpc_url('acls:'), wait=5); await r.hold(1.5)
    await r.click(lambda f: f.locator('tr', has_text='nacl-public-TP-AC').get_by_role('link').first); await r.hold(2.5)
    await r.click(tab('Règles entrantes')); await r.hold(2.0)
    r.mark('regles-actuelles'); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Modifier les règles entrantes')).first); await r.hold(2.5)
    await r.click(btn('Ajouter une nouvelle règle')); await r.hold(1.0)
    k = 3
    await r.type(lambda f: f.locator('input[aria-label^="Entrée du numéro de règle"]').nth(k), '105'); await r.hold(0.4)
    await r.type(lambda f: f.locator('input[aria-label^="Plage de ports de règle"]').nth(k), '80'); await r.hold(1.0)
    r.mark('regle-105')
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
