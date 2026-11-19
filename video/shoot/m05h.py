"""Module 5 : deux VPC dont les plages se chevauchent ne peuvent pas etre apparies : AWS refuse la demande."""
from common import *

async def run(r):
    await r.goto(vpc_url('vpcs:'), wait=4)
    await r.click(btn('Créer un VPC')); await r.hold(2.0)
    await r.type(ph('my-vpc-01'), 'vpc-chevauche-TP-AC'); await r.hold(0.6)
    await r.type(ph('10.0.0.0/24'), '10.20.0.0/24'); await r.hold(1.0)
    r.mark('vpc-test')
    await r.scroll(1500); await r.hold(0.6)
    await r.click(btn('Créer un VPC', True)); await r.hold(4.5)
    await r.goto(vpc_url('CreatePeeringConnection:'), wait=4)
    await r.type(ph('my-pc-01'), 'pcx-chevauche-TP-AC'); await r.hold(0.6)
    await r.click(lambda f: f.get_by_role('button', name='Sélectionner un VPC').nth(0)); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('button', name='Sélectionner un VPC').nth(0)); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-chevauche-TP-AC')).first); await r.hold(1.2)
    r.mark('demande')
    await r.scroll(900)
    await r.click(btn("Créer une connexion d'appairage", True)); await r.hold(5.0)
    r.mark('refus'); await r.hold(4.0)
