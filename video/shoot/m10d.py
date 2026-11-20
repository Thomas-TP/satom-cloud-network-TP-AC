"""Module 10 : surveillance de l'etat (HTTPS sur l'ALB, toutes les 10 s, 2 echecs) pour piloter le basculement DNS."""
from common import *
from m09g import NOM

async def run(r):
    await r.goto('https://us-east-1.console.aws.amazon.com/route53/healthchecks/home?region=eu-north-1#/create', wait=6); await r.hold(1.5)
    await r.click(btn("Créer une surveillance de l'état", True)); await r.hold(3.0)
    await r.type(ph('Entrez un nom'), 'hc-portail-TP-AC'); await r.hold(0.6)
    await r.click('input[value=ENDPOINT]'); await r.hold(1.0)
    await r.click('input[value=DOMAIN]'); await r.hold(1.2)
    r.mark('domaine')
    await r.click(lambda f: f.locator('button:has-text("HTTP")').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('^HTTPS')).first); await r.hold(1.0)
    await r.type(lambda f: f.get_by_placeholder(re.compile('www.example.com')), NOM); await r.hold(1.0)
    r.mark('adresse')
    await r.click('input[value="10"]'); await r.hold(1.0)
    await r.scroll(400); await r.hold(0.8)
    await r.type(lambda f: f.locator('input[type=number]').first, '2'); await r.hold(0.8)
    r.mark('seuils')
    await r.scroll(900)
    await r.click(btn("Créer une surveillance de l'état", True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(3.0)
