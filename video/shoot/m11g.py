"""Module 11 : tests CloudFront (cdn.leman.thomastp.ch) depuis web-01 : Miss puis Hit sur le statique, jamais de cache sur l'API, invalidation apres modification, ALB injoignable en direct."""
from common import *
from m02f import terminal
from m07q import open_session
from m11e import dist_id


async def run(r):
    cf = 'cdn.leman.thomastp.ch'; alb = 'origin.leman.thomastp.ch'; DIST = dist_id()
    main = r.page
    a = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i', f'CF={cf}', f'ALB={alb}'], pause=1.5)
    f = 'curl -s -D - -o /dev/null https://$CF/static/logo.png | grep -iE "^HTTP|x-cache|x-amz-cf-pop"'
    await terminal(r, [f], pause=4.0)
    r.mark('miss')
    await terminal(r, [f], pause=4.0)
    r.mark('hit'); await r.hold(1.5)
    g = 'curl -s -D - -o /dev/null https://$CF/api/health | grep -iE "^HTTP|x-cache"'
    await terminal(r, [g, g], pause=4.0)
    r.mark('api'); await r.hold(1.0)
    await terminal(r, ['echo "logo v2" > /usr/share/nginx/html/static/logo.png; cat /usr/share/nginx/html/static/logo.png'], pause=2.5)
    r.mark('fichier-modifie')
    await terminal(r, ['curl -s https://$CF/static/logo.png'], pause=4.0)
    r.mark('ancien-cache'); await r.hold(1.5)
    await r.follow(main)
    await r.goto('https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=eu-north-1#/distributions/' + DIST + '/invalidations', wait=8); await r.hold(2.0)
    await r.click(lambda f: f.get_by_text('Créer une invalidation', exact=True).first); await r.hold(3.0)
    await r.type(lambda f: f.locator('textarea').first, '/static/*'); await r.hold(1.0)
    r.mark('invalidation')
    await r.scroll(600)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Créer une invalidation')).last); await r.hold(5.0)
    r.mark('creee')
    r.mark('attente-debut', accelere=4); await r.hold(40.0); r.mark('attente-fin')
    await r.follow(a)
    await terminal(r, ['curl -s https://$CF/static/logo.png'], pause=4.0)
    r.mark('nouveau'); await r.hold(1.5)
    await terminal(r, ['curl -s -m 6 -o /dev/null -w "ALB en direct : HTTP %{http_code}\n" https://$ALB/'], pause=8.0)
    r.mark('alb-direct'); await r.hold(2.0)
