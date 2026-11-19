"""Module 1 : deux sous-reseaux (public et prive) dans le VPC de production."""
from common import *

async def sub(r, i, name, az, cidr, env='prod'):
    await r.type(lambda f, i=i: f.get_by_placeholder('my-subnet-01').nth(i), name); await r.hold(0.5)
    await r.click(lambda f, i=i: f.get_by_role('button', name='Aucune préférence').nth(0)); await r.hold(0.7)
    await r.click(opt(re.compile(az))); await r.hold(0.6)
    await r.type(lambda f, i=i: f.get_by_label("Bloc d'adresse CIDR de sous-réseau IPv4").nth(i), cidr); await r.hold(0.8)
    await tags(r, env, start=4 * i + 1, add='Ajouter une nouvelle balise', which=i); await r.hold(0.6)

async def run(r):
    await r.goto(vpc_url('CreateSubnet:'), wait=4)
    await r.hold(1.0)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.2)
    await r.click(txt('(vpc-prod-leman-TP-AC)')); await r.hold(1.5)
    r.mark('vpc-choisi')
    await r.click(btn('Ajouter un nouveau sous-réseau')); await r.hold(1.5)
    await r.scroll(250)
    await sub(r, 0, 'sub-public-1a-TP-AC', 'eun1-az1', '10.20.0.0/26'); r.mark('public')
    await r.scroll(700)
    await sub(r, 1, 'sub-prive-1a-TP-AC', 'eun1-az1', '10.20.1.0/26'); r.mark('prive')
    await r.scroll(1500); await r.hold(1.0)
    await r.click(btn('Créer un sous-réseau')); await r.hold(5.0)
    r.mark('cree'); await r.hold(2.5)
