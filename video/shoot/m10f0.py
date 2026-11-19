"""Module 10 : une zone privee exige les noms d'hote DNS actives sur le VPC : on les active."""
from common import *

async def run(r):
    await r.goto(vpc_url('vpcs:'), wait=6); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('vpc-prod-leman-TP-AC')).get_by_role('checkbox').first); await r.hold(1.0)
    r.mark('details'); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Actions').first); await r.hold(1.5)
    await r.click_xy(1522, 373); await r.hold(3.0)
    r.mark('formulaire')
    await r.click(lambda f: f.get_by_text(re.compile('Activer les noms d.h.te DNS')).first); await r.hold(1.5)
    r.mark('coche')
    await r.click(btn('Enregistrer', True)); await r.hold(4.0)
    r.mark('enregistre'); await r.hold(2.0)
