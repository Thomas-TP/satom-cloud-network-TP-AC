"""Module 12 : la rubrique SNS des alertes d'exploitation, avec un abonne e-mail (adresse fictive pour la video)."""
from common import *

SNS = 'https://eu-north-1.console.aws.amazon.com/sns/v3/home?region=eu-north-1#'

async def run(r):
    await r.goto(SNS + '/create-topic', wait=7); await r.hold(1.5)
    await r.click('input[value=standard]'); await r.hold(1.0)
    await r.type(ph('MyTopic'), 'sns-exploitation-leman-TP-AC'); await r.hold(0.6)
    await r.type(ph('Ma rubrique'), 'Alertes exploitation Leman'); await r.hold(0.8)
    r.mark('nom')
    await r.scroll(1500)
    await r.click(lambda f: f.get_by_role('heading', name=re.compile('^Balises')).first); await r.hold(1.0)
    await r.scroll(600)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle identification', kp='Saisir une clé', vp='Saisir une valeur')
    r.mark('balises')
    await r.scroll(2000)
    await r.click(btn('Créer la rubrique', True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(2.0)
    await r.click(btn('Créer un abonnement', True)); await r.hold(3.0)
    r.mark('abonnement')
    await r.click(btn('Sélectionner un protocole')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('^Adresse de messagerie')).first); await r.hold(1.2)
    r.mark('protocole')
    await r.type(lambda f: f.get_by_placeholder(re.compile('exemple|example|name@', re.I)).first, 'exploitation-tp-ac@example.com'); await r.hold(1.0)
    r.mark('adresse')
    await r.scroll(900)
    await r.click(btn('Créer un abonnement', True)); await r.hold(5.0)
    r.mark('abonne'); await r.hold(2.5)
