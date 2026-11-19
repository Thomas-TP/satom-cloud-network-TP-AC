"""Module 10 : zone hebergee privee prod.leman.internal, associee au VPC de production."""
from common import *

async def run(r):
    await r.goto('https://us-east-1.console.aws.amazon.com/route53/v2/hostedzones?region=eu-north-1#CreateHostedZone', wait=6); await r.hold(1.5)
    await r.type(ph('example.com'), 'prod.leman.internal'); await r.hold(0.6)
    await r.type(lambda f: f.locator('textarea').first, 'Noms internes du VPC de production'); await r.hold(0.6)
    await r.click('input[value=PRIVATE]'); await r.hold(1.5)
    r.mark('prive')
    await r.scroll(300); await r.hold(0.8)
    await r.click(btn('Choisir une région')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Stockholm')).first); await r.hold(1.5)
    await r.click(lambda f: f.get_by_placeholder('Choisir le VPC')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    r.mark('vpc')
    await r.scroll(500)
    await tags(r, 'prod', start=0, add='Ajouter une balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une zone hébergée', True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(2.0)
