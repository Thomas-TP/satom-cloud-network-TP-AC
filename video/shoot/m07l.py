"""Module 7 : le groupe app ouvre le 8080 au siege et a l'agence, rien d'autre."""
from common import *

async def run(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='app-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    for n, (cidr, desc) in zip((5, 6), (('192.168.10.0/24', 'API depuis siege'), ('192.168.20.0/24', 'API depuis agence'))):
        await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
        await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Plage de ports"]' % n), '8080'); await r.hold(0.5)
        await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Sélecteur CIDR"]' % n), cidr); await r.press('Enter', 0.8)
        await r.type(lambda f, n=n: f.locator('input[aria-label="Règle entrante %d Description - facultatif"]' % n), desc); await r.hold(1.0)
    r.mark('regles')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistrees'); await r.hold(2.0)
