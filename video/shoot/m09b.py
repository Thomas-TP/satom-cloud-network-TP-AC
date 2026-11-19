"""Module 9 : deux groupes cibles (web en HTTPS 443, application en HTTP 8080) avec leur controle de sante, et leurs cibles."""
from common import *

async def tg(r, name, proto, port, health, inst):
    await r.goto(ec2_url('CreateTargetGroup:'), wait=5); await r.hold(1.5)
    await r.type(lambda f: f.locator('input[type=text]').first, name); await r.hold(0.5)
    if proto != 'HTTP':
        await r.click(lambda f: f.locator('button:has-text("HTTP")').first); await r.hold(1.0)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('^' + proto + ' ')).first); await r.hold(0.8)
    await r.type(lambda f: f.locator('input[type=number]').first, str(port)); await r.hold(0.8)
    await r.click(lambda f: f.locator('button:has-text("vpc-05507")').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    r.mark(f'{name}-detail')
    await r.scroll(700); await r.hold(0.8)
    if proto == 'HTTPS':
        await r.click(lambda f: f.get_by_text('Protocole de vérification de l’état', exact=True).first.locator('xpath=following::button[1]')); await r.hold(1.0)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('^HTTPS')).first); await r.hold(0.8)
    await r.type(lambda f: f.locator('textarea').first, health); await r.hold(0.8)
    r.mark(f'{name}-sante')
    await r.scroll(900)
    await r.click(lambda f: f.get_by_text('Balises', exact=False).filter(has_text='facultatif').first); await r.hold(1.0)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', name)], kp='Clé', vp='Valeur')
    await r.scroll(900)
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(inst)).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(btn('Inclure comme étant en attente ci-dessous', True)); await r.hold(1.5)
    r.mark(f'{name}-cible')
    await r.scroll(900)
    await r.click(btn('Suivant', True)); await r.hold(3.0)
    await r.scroll(1200)
    await r.click(btn('Créer un groupe cible', True)); await r.hold(4.5)
    r.mark(f'{name}-cree'); await r.hold(1.5)

async def run(r):
    await tg(r, 'tg-web-TP-AC', 'HTTPS', 443, '/', 'web-01-TP-AC')
    await tg(r, 'tg-app-TP-AC', 'HTTP', 8080, '/api/health', 'app-01-TP-AC')
