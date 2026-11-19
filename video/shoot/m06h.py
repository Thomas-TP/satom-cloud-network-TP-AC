"""Module 6 : test depuis dev-01 par le Transit Gateway (l'appairage est supprime), puis panne : on retire la propagation de dev dans la table prod."""
from common import *
from m02f import terminal
from m06e import rtb, pick

async def details(r, table, tabname):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb(table)), wait=4)
    await r.click(tab(tabname)); await r.hold(2.0)

async def run(r):
    main = r.page
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('dev-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    sess = [p for p in r.ctx.pages if p not in before][0]
    await r.follow(sess); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark('terminal')
    await terminal(r, ['hostname -I', 'curl -s -m 5 http://10.20.1.10:8080/api/health; echo'], pause=4.0)
    r.mark('api-via-tgw')
    await terminal(r, ['while true; do curl -s -m 2 http://10.20.1.10:8080/api/health || echo ECHEC; sleep 1; done'], pause=6.0)
    r.mark('boucle')
    await r.follow(main)
    await details(r, 'tgw-rt-prod-TP-AC', 'Propagations')
    await r.click(lambda f: f.get_by_role('row', name=re.compile('tgwa-dev-TP-AC|tgw-attach')).get_by_role('checkbox').first); await r.hold(1.2)
    await r.click(btn('Supprimer la propagation', True)); await r.hold(2.5)
    r.mark('confirmation')
    try:
        await r.click(lambda f: f.get_by_role('dialog').get_by_role('button', name=re.compile('Supprimer')).last); await r.hold(4.0)
    except Exception: await r.hold(1.0)
    r.mark('propagation-retiree')
    await r.follow(sess); await r.hold(16.0)
    r.mark('echecs')
    await r.follow(main)
    await details(r, 'tgw-rt-prod-TP-AC', 'Propagations')
    await r.click(btn('Créer une propagation', True)); await r.hold(2.5)
    await pick(r, 'tgwa-dev-TP-AC'); r.mark('choix')
    await r.click(btn('Créer une propagation', True)); await r.hold(4.0)
    r.mark('propagation-remise')
    await r.follow(sess); await r.hold(18.0)
    r.mark('retour')
    await r.page.keyboard.press('Control+C'); await r.hold(1.5)
