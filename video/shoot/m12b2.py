"""Module 12 : abonnement de la file SQS a la rubrique SNS (la console ajoute elle-meme l'autorisation)."""
from common import *

SQS = 'https://eu-north-1.console.aws.amazon.com/sqs/v3/home?region=eu-north-1#'

async def run(r):
    await r.goto(SQS + '/queues', wait=8); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('link', name='sqs-exploitation-leman-TP-AC').first); await r.hold(3.0)
    await r.click(tab('Abonnements SNS')); await r.hold(2.0)
    await r.click(btn('Abonner à la rubrique Amazon SNS', True)); await r.hold(3.0)
    r.mark('formulaire')
    await r.click(btn('Sélectionner une rubrique')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('sns-exploitation-leman-TP-AC')).first); await r.hold(1.5)
    r.mark('rubrique')
    await r.click(btn('Enregistrer', True)); await r.hold(5.0)
    r.mark('abonnee'); await r.hold(2.5)
