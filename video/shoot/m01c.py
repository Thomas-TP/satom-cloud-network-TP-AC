"""Module 1 : test de chevauchement - un sous-reseau 10.20.0.0/27 dans le /26 existant est refuse."""
from common import *

async def run(r):
    await r.goto(vpc_url('CreateSubnet:'), wait=4)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.0)
    await r.click(txt('(vpc-prod-leman-TP-AC)')); await r.hold(1.5)
    await r.type(lambda f: f.get_by_placeholder('my-subnet-01').nth(0), 'sub-test-chevauchement'); await r.hold(0.6)
    await r.click(lambda f: f.get_by_role('button', name='Aucune préférence').nth(0)); await r.hold(0.7)
    await r.click(opt(re.compile('eun1-az1'))); await r.hold(0.6)
    await r.type(lambda f: f.get_by_label("Bloc d'adresse CIDR de sous-réseau IPv4").nth(0), '10.20.0.0/27'); await r.hold(1.2)
    r.mark('cidr-chevauche')
    await r.scroll(1500); await r.hold(0.8)
    await r.click(btn('Créer un sous-réseau')); await r.hold(1.5)
    r.mark('refus'); await r.hold(4.0)
    await r.scroll(-1500); await r.hold(2.0)
