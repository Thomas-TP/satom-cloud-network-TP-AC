"""Module 2 : test de panne - on retire la route par defaut du prive pendant que app-01 interroge Internet, puis on la remet."""
from common import *
from m02f import terminal

async def edit_prive_routes(r):
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-prive-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.0)

async def run(r):
    main = r.page
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('app-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    sess = [p for p in r.ctx.pages if p not in before][0]
    await r.follow(sess); await r.hold(7.0)
    await r.click_xy(900, 500)
    await terminal(r, ['while true; do curl -s -m 2 https://checkip.amazonaws.com || echo ECHEC; sleep 1; done'], pause=6.0)
    r.mark('boucle')
    await r.follow(main)
    await edit_prive_routes(r)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('^Supprimer')).last); await r.hold(1.2)
    r.mark('route-retiree')
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    await r.follow(sess); await r.hold(14.0)
    r.mark('echecs')
    await r.follow(main)
    await edit_prive_routes(r)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Destination'), '0.0.0.0/0'); await r.hold(0.8)
    await r.click(lambda f: f.get_by_role('option', name='0.0.0.0/0', exact=True)); await r.hold(1.0)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name='Passerelle NAT', exact=True)); await r.hold(1.2)
    b = await r._box(lambda f: f.get_by_role('combobox', name='Destination'))
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2 + 34); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(nat_id())).first); await r.hold(1.5)
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    r.mark('route-remise')
    await r.follow(sess); await r.hold(12.0)
    r.mark('retour')
    await r.page.keyboard.press('Control+C'); await r.hold(1.5)
