"""Module 7 : les deux connexions VPN Site-to-Site vers le Transit Gateway (routage statique, deux tunnels, cles pre-partagees masquees)."""
from common import *

async def vpn(r, n):
    keys = psk()
    await r.goto(vpc_url('CreateVpnConnection:'), wait=5); await r.hold(1.2)
    await r.type(ph('vpn-01'), f'vpn-{n}-TP-AC'); await r.hold(0.6)
    await r.click('input[value=tgw]'); await r.hold(1.0)
    await r.click(btn('Sélectionner une passerelle de transit')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('tgw-leman-TP-AC')).first); await r.hold(1.2)
    await r.click(btn('Sélectionner une passerelle client')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(f'cgw-{n}-TP-AC')).first); await r.hold(1.2)
    r.mark(f'{n}-cible')
    await r.click(lambda f: f.get_by_text('Statique', exact=True).first); await r.hold(1.2)
    r.mark(f'{n}-statique')
    await r.scroll(700); await r.hold(0.6)
    await r.scroll(500); await r.hold(0.6)
    for t in (1, 2):
        await r.click(lambda f, t=t: f.get_by_text(f'Options du tunnel {t}').first); await r.hold(1.2)
        await r.scroll(300); await r.hold(0.4)
        fld = lambda f, t=t: f.locator('input[placeholder="Généré par Amazon"]:visible').nth(2 * t - 1)
        await r.click(fld); await mask(fld, r)
        await r.type(fld, keys[f'{n}{t}'], delay=15); await r.hold(0.6)
    r.mark(f'{n}-cles')
    await r.scroll(900)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise', kp='Saisir la clé', vp='Saisir la valeur')
    r.mark(f'{n}-balises')
    await r.scroll(900)
    await r.click(btn('Création d’une connexion VPN', True)); await r.hold(5.0)
    r.mark(f'{n}-creee'); await r.hold(2.0)

async def run(r):
    await vpn(r, 'siege'); await vpn(r, 'agence')
    r.mark('attente-debut', accelere=8); await r.hold(150)
    r.mark('attente-fin')
