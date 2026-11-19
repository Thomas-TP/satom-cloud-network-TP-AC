"""Module 9 : panne de la cible web : nginx arrete -> 502 et cible non saine ; nginx relance -> cible saine."""
from common import *
from m02f import terminal
from m07q import open_session
from m09g import alb_dns, tg_url

async def refresh_wait(r, secs, url):
    t = 0
    while t < secs:
        await r.goto(url, wait=6); await r.hold(24.0); t += 30

async def run(r):
    main = r.page
    dns = alb_dns()
    a = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i', f'ALB={dns}'], pause=1.5)
    await terminal(r, ['curl -sk https://$ALB/; echo', 'curl -sk https://$ALB/api/health; echo'], pause=3.0)
    r.mark('ok')
    await terminal(r, ['systemctl stop nginx; curl -sk -o /dev/null -w "HTTP %{http_code}\n" https://$ALB/'], pause=4.0)
    r.mark('502')
    await r.follow(main)
    r.mark('attente1-debut', accelere=6)
    await refresh_wait(r, 90, tg_url('tg-web-TP-AC'))
    r.mark('attente1-fin'); await r.hold(2.5)
    await r.follow(a)
    await terminal(r, ['systemctl start nginx; curl -sk https://$ALB/; echo'], pause=4.0)
    r.mark('relance')
    await r.follow(main)
    r.mark('attente2-debut', accelere=8)
    await refresh_wait(r, 180, tg_url('tg-web-TP-AC'))
    r.mark('attente2-fin'); await r.hold(2.5)
