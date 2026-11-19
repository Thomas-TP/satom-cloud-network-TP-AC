"""Module 12 : test de l'alarme : nginx arrete, 40 requetes par CloudFront font des 502 ; l'alarme passe en ALARME puis revient a OK, et la file SQS a recu les messages."""
from common import *
from common import _ids
from m02f import terminal
from m07q import open_session

ALARM = 'https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#alarmsV2:alarm/alarm-5xx-portail-TP-AC'

async def attendre(r, url, secs):
    t = 0
    while t < secs:
        await r.goto(url, wait=7); await r.hold(22.0); t += 30

async def run(r):
    cf = _ids()['cf']
    main = r.page
    await r.goto(ALARM, wait=8); await r.hold(3.0)
    r.mark('alarme-ok'); await r.hold(2.0)
    b = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i', 'systemctl stop nginx; echo nginx arrete'], pause=2.5)
    r.mark('arret')
    await r.follow(main)
    a = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i', f'CF={cf}'], pause=1.5)
    await terminal(r, ['for i in $(seq 1 60); do curl -s -o /dev/null -w "%{http_code} " https://$CF/essai$i; sleep 1; done; echo'], pause=70.0)
    r.mark('requetes')
    await r.follow(main)
    r.mark('attente1-debut', accelere=5)
    await attendre(r, ALARM, 150)
    r.mark('attente1-fin'); await r.hold(3.0)
    await r.follow(b)
    await terminal(r, ['systemctl start nginx; echo nginx relance'], pause=2.5)
    r.mark('relance')
    await r.follow(main)
    r.mark('attente2-debut', accelere=6)
    await attendre(r, ALARM, 330)
    r.mark('attente2-fin'); await r.hold(3.0)
