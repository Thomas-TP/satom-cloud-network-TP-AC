"""Module 12 : journal de flux du VPC de production vers CloudWatch Logs (tout le trafic), avec un nouveau role de service cree par la console."""
from common import *

async def run(r):
    await r.goto(vpc_url('VpcDetails:VpcId=vpc-0fcf09d8d94cf76d6'), wait=6); await r.hold(1.5)
    await r.click(tab('Journaux de flux')); await r.hold(2.0)
    await r.click(btn('Créer un journal de flux', True)); await r.hold(3.0)
    await r.type(ph('my-flow-log-01'), 'fl-vpc-prod-leman-TP-AC'); await r.hold(0.6)
    await r.click('input[value=ALL]'); await r.hold(0.8)
    r.mark('filtre')
    await r.type(lambda f: f.get_by_placeholder(re.compile('Choisir ou créer un nom de groupe')), '/leman/vpc-prod/flow-TP-AC'); await r.hold(1.5)
    await r.press('Enter', 1.0)
    await r.click('input[value=create-new-role]'); await r.hold(1.2)
    r.mark('role')
    await r.scroll(1500)
    await tags(r, 'prod', start=1, add='Ajouter la balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(1500)
    await r.click(btn('Créer un journal de flux', True)); await r.hold(6.0)
    r.mark('cree'); await r.hold(2.5)
