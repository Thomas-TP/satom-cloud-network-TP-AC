"""Module 11 : l'ALB n'accepte plus que CloudFront : la regle 443 publique est remplacee par le 443 depuis la liste de prefixes geree par AWS."""
from common import *
from m08g import sg_id

async def run(r):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + sg_id('alb-TP-AC')), wait=5); await r.hold(1.5)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    n = 2
    await r.click(lambda f: f.get_by_role('button', name=re.compile('TCP personnalisé')).last); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name='HTTPS', exact=True)); await r.hold(1.0)
    sel = lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]')
    await r.click(sel); await r.hold(1.0)
    for ch in 'cloudfront':
        await r.page.keyboard.type(ch); await asyncio.sleep(0.12)
    await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('com.amazonaws.global.cloudfront')).first); await r.hold(1.2)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Description - facultatif"]'), 'HTTPS depuis CloudFront'); await r.hold(1.0)
    r.mark('regle-cloudfront')
    await r.click_xy(1668, 301); await r.hold(1.5)
    r.mark('retire-443')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(2.0)
