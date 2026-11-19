"""Module 12 : la file SQS a recu les notifications de l'alarme (preuve de reception)."""
from common import *

SQS = 'https://eu-north-1.console.aws.amazon.com/sqs/v3/home?region=eu-north-1#'

async def run(r):
    await r.goto(SQS + '/queues', wait=8); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('link', name='sqs-exploitation-leman-TP-AC').first); await r.hold(3.0)
    await r.click(btn('Envoyer et recevoir des messages', True)); await r.hold(4.0)
    r.mark('page')
    await r.scroll(700); await r.hold(0.8)
    await r.click(btn('Rechercher des messages', True)); await r.hold(10.0)
    r.mark('messages'); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('2026-11-19')).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(btn('Afficher les détails', True)); await r.hold(4.0)
    r.mark('detail'); await r.hold(4.0)
