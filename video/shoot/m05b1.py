"""Module 5 : passerelle Internet du dev creee puis attachee au VPC de production."""
from common import *

async def run(r):
    await r.goto(vpc_url('igws:'), wait=4)
    await r.hold(1.5)
    await r.click(btn('Créer une passerelle Internet')); await r.hold(2.0)
    await r.type(ph('my-internet-gateway'), 'igw-dev-leman-TP-AC'); await r.hold(0.8)
    r.mark('nom')
    await r.scroll(300)
    await tags(r, 'dev', start=1, add='Ajouter une nouvelle balise')
    r.mark('balises'); await r.hold(1.0)
    await r.scroll(800)
    await r.click(btn('Créer une passerelle Internet')); await r.hold(4.0)
    r.mark('creee'); await r.hold(1.5)
    await r.click(btn('Actions')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('menuitem', name=re.compile('Attacher au VPC'))); await r.hold(2.0)
    r.mark('attacher')
    await r.click(ph('Sélectionner un VPC')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-dev-leman-TP-AC')).first); await r.hold(1.5)
    await r.scroll(600); await r.hold(0.8)
    await r.click(btn('Attacher une passerelle Internet')); await r.hold(4.0)
    r.mark('attachee'); await r.hold(2.5)
