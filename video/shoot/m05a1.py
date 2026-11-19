"""Module 5 : creation du VPC de developpement."""
from common import *

async def run(r):
    await r.goto(vpc_url('vpcs:'), wait=4)
    await r.hold(1.5)
    await r.click(btn('Créer un VPC')); await r.hold(2.0)
    r.mark('formulaire')
    await r.type(ph('my-vpc-01'), 'vpc-dev-leman-TP-AC'); await r.hold(0.6)
    await r.type(ph('10.0.0.0/24'), '10.21.0.0/24'); await r.hold(1.2)
    r.mark('cidr')
    await r.scroll(500)
    await tags(r, 'dev', start=1)
    r.mark('balises'); await r.hold(1.5)
    await r.scroll(800)
    await r.click(btn('Créer un VPC')); await r.hold(4.5)
    r.mark('cree'); await r.hold(2.5)
