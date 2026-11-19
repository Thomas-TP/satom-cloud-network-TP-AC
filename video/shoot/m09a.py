"""Module 9 : import du certificat auto-signe dans ACM (la cle privee est masquee a l'ecran)."""
from common import *

CERT = r'C:\Perso\AWS\video\rig\profile\cert'

async def run(r):
    crt = open(CERT + r'\alb.crt').read(); key = open(CERT + r'\alb.key').read()
    await r.goto('https://eu-north-1.console.aws.amazon.com/acm/home?region=eu-north-1#/certificates/import', wait=5); await r.hold(1.5)
    await r.click(lambda f: f.locator('textarea').nth(0)); await r.hold(0.4)
    await r.page.keyboard.insert_text(crt); await r.hold(2.0)
    r.mark('certificat')
    ta = lambda f: f.locator('textarea').nth(1)
    await r.click(ta); await mask(ta, r)
    await r.page.keyboard.insert_text(key); await r.hold(2.0)
    r.mark('cle-masquee')
    await r.scroll(500)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle identification', extra=[('Name', 'cert-portail-TP-AC')], kp='Saisir une clé', vp='Saisir une valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Importer le certificat', True)); await r.hold(5.0)
    r.mark('importe'); await r.hold(2.0)
