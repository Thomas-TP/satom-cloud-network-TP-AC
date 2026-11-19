"""Module 4 : sous-reseau dedie a l'endpoint du pare-feu."""
from common import *

async def run(r):
    await r.goto(vpc_url('CreateSubnet:'), wait=4)
    await r.hold(1.0)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.2)
    await r.click(txt('(vpc-prod-leman-TP-AC)')); await r.hold(1.5)
    await r.scroll(250)
    await r.type(lambda f: f.get_by_placeholder('my-subnet-01').nth(0), 'sub-fw-1a-TP-AC'); await r.hold(0.5)
    await r.click(lambda f: f.get_by_role('button', name='Aucune préférence').nth(0)); await r.hold(0.7)
    await r.click(opt(re.compile('eun1-az1'))); await r.hold(0.6)
    await r.type(lambda f: f.get_by_label("Bloc d'adresse CIDR de sous-réseau IPv4").nth(0), '10.20.2.0/28'); await r.hold(0.8)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise', which=0); await r.hold(0.6)
    r.mark('formulaire')
    await r.scroll(1500); await r.hold(1.0)
    await r.click(btn('Créer un sous-réseau', True)); await r.hold(5.0)
    r.mark('cree'); await r.hold(1.5)
    r.mark('termine'); await r.hold(1.5)
