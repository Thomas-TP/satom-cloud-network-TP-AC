"""Module 3 : panne volontaire - on retire le 8080 du groupe app pendant que web-01 interroge l'API, puis on le remet."""
from common import *
from m02f import terminal

async def open_rules(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='app-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)

async def run(r):
    main = r.page
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('web-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    sess = [p for p in r.ctx.pages if p not in before][0]
    await r.follow(sess); await r.hold(7.0)
    await r.click_xy(900, 500)
    await terminal(r, ['while true; do curl -s -m 2 http://10.20.1.10:8080/api/health || echo ECHEC; echo; sleep 1; done'], pause=6.0)
    r.mark('boucle')
    await r.follow(main)
    await open_rules(r)
    await r.click(lambda f: f.locator('xpath=//input[@value="8080"]/ancestor::*[.//button[normalize-space()="Supprimer"]][1]').get_by_role('button', name='Supprimer')); await r.hold(1.2)
    r.mark('regle-8080-retiree')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    await r.follow(sess); await r.hold(12.0)
    r.mark('echecs')
    await r.follow(main)
    await open_rules(r)
    await r.click(lambda f: f.get_by_role('button', name='Ajouter une règle').first); await r.hold(1.0)
    n = 3
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante %d Plage de ports"]' % n), '8080'); await r.hold(0.5)
    await r.type(lambda f: f.locator('input[aria-label="Règle entrante %d Sélecteur CIDR"]' % n), 'web-TP'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(r'sg-[0-9a-f]+.*web-TP-AC|web-TP-AC.*sg-[0-9a-f]+')).first); await r.hold(0.8)
    r.mark('regle-8080-remise')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    await r.follow(sess); await r.hold(12.0)
    r.mark('retour')
    await r.page.keyboard.press('Control+C'); await r.hold(1.5)
