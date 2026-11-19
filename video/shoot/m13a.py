"""Module 13 : creation de la pile par la console : televersement du modele, parametres, balises, role IAM."""
from common import *

TPL = r'C:\Perso\AWS\cfn\reseau-leman-etape1.yaml'
CERT = 'arn:aws:acm:eu-north-1:*:certificate/'

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/cloudformation/home?region=eu-north-1#/stacks/create', wait=9); await r.hold(2.0)
    await r.click('input[value=UPLOAD_TEMPLATE]'); await r.hold(1.5)
    r.mark('televersement')
    for f in r.page.frames:
        loc = f.locator('input[type=file]')
        if await loc.count():
            await loc.first.set_input_files(TPL); break
    await r.hold(3.0)
    r.mark('fichier')
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    await r.type(lambda f: f.locator('input[type=text]').first, 'stack-portail-leman-TP-AC'); await r.hold(0.8)
    r.mark('nom')
    from common import _ids
    cert = lambda f: f.get_by_label('CertificateArn').first
    await r.click(cert); await mask(cert, r)
    await r.type(cert, _ids()['cert_arn'], delay=10); await r.hold(1.0)
    r.mark('parametres')
    await r.scroll(2000)
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    r.mark('options')
    await r.scroll(-1500)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(4000); await r.hold(1.0)
    await r.click(lambda f: f.locator('input[type=checkbox]').last); await r.hold(1.5)
    r.mark('capacite')
    await r.click(btn('Suivant', True)); await r.hold(4.0)
    r.mark('verification'); await r.hold(2.0)
    await r.scroll(4000); await r.hold(1.0)
    await r.click(btn('Soumettre', True)); await r.hold(6.0)
    r.mark('soumise')
    r.mark('attente-debut', accelere=8); await r.hold(120.0); r.mark('attente-fin')
