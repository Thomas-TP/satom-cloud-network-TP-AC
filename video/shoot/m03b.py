"""Module 3 : Security Group app (8080, 22 et ICMP depuis le groupe web uniquement)."""
from common import *

async def sg_source(r, n, desc):
    await r.click(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]')); await r.hold(0.6)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Sélecteur CIDR"]'), 'web-TP'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(r'sg-[0-9a-f]+.*web-TP-AC|web-TP-AC.*sg-[0-9a-f]+')).first); await r.hold(0.8)
    await r.type(lambda f: f.locator(f'input[aria-label="Règle entrante {n} Description - facultatif"]'), desc)

async def run(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4)
    await r.hold(1.0)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(2.0)
    await r.type(ph('MyWebServerGroup'), 'app-TP-AC'); await r.hold(0.5)
    await r.type(ph("Autorise l'accès SSH aux développeurs"), 'App : 8080, 22 et ICMP depuis le groupe web'); await r.hold(0.5)
    await r.click('button:has-text("vpc-05507")'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    await r.scroll(400)
    for n, port, desc in [(1, 8080, 'API depuis web'), (2, 22, 'SSH depuis web')]:
        await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
        await r.type(lambda f, n=n: f.locator(f'input[aria-label="Règle entrante {n} Plage de ports"]'), str(port)); await r.hold(0.5)
        await sg_source(r, n, desc)
    r.mark('regles-tcp')
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('button', name='TCP personnalisé').last); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile("Tous les ICMP - IPv4")).first); await r.hold(1.0)
    await sg_source(r, 3, 'ping depuis web')
    r.mark('regle-icmp'); await r.hold(1.0)
    await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', 'sg-app-TP-AC')], kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises'); await r.hold(1.0)
    await r.scroll(900)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(4.5)
    r.mark('cree'); await r.hold(2.0)
