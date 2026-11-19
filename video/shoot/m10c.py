"""Module 10 : zone hebergee publique leman-finance.example (domaine fictif : pas de delegation chez un bureau d'enregistrement)."""
from common import *

async def run(r):
    await r.goto(r53_url('CreateHostedZone'), wait=6); await r.hold(1.5)
    await r.type(ph('example.com'), 'leman-finance.example'); await r.hold(0.6)
    await r.type(lambda f: f.locator('textarea').first, 'Zone publique du portail (domaine fictif)'); await r.hold(0.6)
    r.mark('public')
    await r.scroll(500)
    await tags(r, 'prod', start=0, add='Ajouter une balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une zone hébergée', True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(3.0)
