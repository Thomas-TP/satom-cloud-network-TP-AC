"""Module 6 : creation du Transit Gateway (association et propagation par defaut desactivees)."""
from common import *

async def run(r):
    await r.goto(vpc_url('TransitGateways:'), wait=5)
    await r.hold(1.5)
    await r.click(btn('Créer une passerelle de transit', True)); await r.hold(2.5)
    await r.type(ph('transit-de transit-01'), 'tgw-leman-TP-AC'); await r.hold(0.6)
    await r.type(ph('description'), 'Transit Gateway du projet Satom Cloud Network'); await r.hold(0.6)
    await r.type(ph('ASN'), '64512'); await r.hold(0.8)
    await r.click(lambda f: f.get_by_text('Association de table de routage par défaut').first); await r.hold(0.8)
    await r.click(lambda f: f.get_by_text('Propagation par défaut de la table de routage').first); await r.hold(1.0)
    r.mark('options')
    await r.scroll(900)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark('balises')
    await r.scroll(900)
    await r.click(btn('Créer une passerelle de transit', True)); await r.hold(5.0)
    r.mark('creee')
    r.mark('attente-debut', accelere=8)
    import time
    t0 = time.time()
    while time.time() - t0 < 240:
        await r.hold(10); await r.page.reload(); await r.hold(4.0); await r.page.evaluate(CURSOR_JS)
        if await r.present(lambda f: f.get_by_text(re.compile('^(Available|Disponible)$')).first, 1.5): break
    r.mark('attente-fin'); await r.hold(3.0)
