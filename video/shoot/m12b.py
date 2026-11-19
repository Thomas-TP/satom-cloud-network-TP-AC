"""Module 12 : file SQS qui sert de preuve de reception des alertes, abonnee a la rubrique SNS."""
from common import *

SQS = 'https://eu-north-1.console.aws.amazon.com/sqs/v3/home?region=eu-north-1#'

async def run(r):
    await r.goto(SQS + '/create-queue', wait=8); await r.hold(1.5)
    await r.type(ph('MyQueue'), 'sqs-exploitation-leman-TP-AC'); await r.hold(0.8)
    r.mark('nom')
    await r.scroll(3000); await r.hold(1.0)
    for n, (k, v) in enumerate([('Projet', 'SatomCloudNetwork'), ('Equipe', 'TP-AC'), ('Environnement', 'prod')]):
        if n: await r.click(btn('Ajouter une nouvelle balise')); await r.hold(0.5)
        await r.type(lambda f, n=n: f.get_by_placeholder('Saisir la clé').nth(n), k, delay=40); await r.press('Tab', 0.2)
        await r.type(lambda f, n=n: f.get_by_placeholder('Saisir la valeur').nth(n), v, delay=40); await r.press('Tab', 0.2)
    r.mark('balises')
    await r.scroll(1500)
    await r.click(btn('Créer une file d’attente', True)); await r.hold(5.0)
    r.mark('creee'); await r.hold(2.0)
