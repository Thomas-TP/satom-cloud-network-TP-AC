"""Module 11 : distribution CloudFront (paiement a l'utilisation) : nom, type classique, origine = origin.leman.thomastp.ch (HTTPS par defaut)."""
from common import *
from m09g import NOM

DESCRIPTION = 'Portail Leman Finance TP-AC (origine ALB, HTTPS)'

async def run(r):
    await r.goto('https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=eu-north-1#/distributions', wait=8); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Créer une distribution').first); await r.hold(3.0)
    await r.click('input[value=payg]'); await r.hold(1.5)
    r.mark('forfait')
    await r.scroll(2000); await r.hold(0.8)
    await r.click(btn('Choisir le paiement à l’utilisation', True)); await r.hold(3.0)
    await r.type(lambda f: f.locator('input[type=text]').first, 'cf-portail-TP-AC'); await r.hold(0.6)
    await r.type(lambda f: f.locator('input[type=text]').nth(1), DESCRIPTION); await r.hold(0.8)
    await r.click('input[value=classic]'); await r.hold(1.5)
    r.mark('nom')
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    r.mark('etape3')
    await r.click('input[value=elb]'); await r.hold(1.5)
    r.mark('elb')
    pass
    await r.type(lambda f: f.get_by_placeholder('exemple-load-balancer.elb.us-east-1.amazonaws.com'), NOM, delay=20); await r.hold(1.2)
    r.mark('domaine')
    await r.scroll(700); await r.hold(1.5)
    r.mark('https-defaut'); await r.hold(1.5)
    await r.scroll(2500); await r.hold(0.8)
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    r.mark('securite')
    await r.click('input[value=DISABLE_WAF]'); await r.hold(1.5)
    r.mark('sans-waf')
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    r.mark('verification'); await r.hold(2.0)
    await r.scroll(600); await r.hold(1.5)
    await r.click(btn('Créer une distribution', True)); await r.hold(6.0)
    r.mark('creee'); await r.hold(2.0)
