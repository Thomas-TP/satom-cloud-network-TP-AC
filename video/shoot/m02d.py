"""Module 2 : passerelle NAT dans le sous-reseau public, avec une adresse IP Elastic."""
from common import *
import time

async def run(r):
    await r.goto(vpc_url('NatGateways:'), wait=4)
    await r.hold(1.5)
    await r.click(btn('Créer une passerelle NAT', True)); await r.hold(2.0)
    await r.type(ph('my-nat-gateway-01'), 'nat-prod-leman-TP-AC'); await r.hold(0.8)
    await r.click('input[value=ZonalNatGateway]'); await r.hold(1.2)
    await r.click(btn('Sélectionner un sous-réseau')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('sub-public-1a-TP-AC')).first); await r.hold(1.5)
    await r.click(btn('Allouer une adresse IP Elastic')); await r.hold(3.0)
    r.mark('eip')
    await r.scroll(500)
    await tags(r, 'prod', start=1, add='Ajouter une nouvelle balise')
    r.mark('balises'); await r.hold(1.0)
    await r.scroll(800)
    await r.click(btn('Créer une passerelle NAT', True)); await r.hold(3.0)
    r.mark('quota-refuse'); await r.hold(5.0)
    await r.scroll(-2000); await r.hold(0.8)
    await r.click(lambda f: f.locator('button:has-text("sub-public-1a-TP-AC")').first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('sub-public-1b-TP-AC')).first); await r.hold(1.5)
    if await r.present(btn('Allouer une adresse IP Elastic'), 0.5) and not await r.present(lambda f: f.locator('button:has-text("eipalloc-")').first, 0.8):
        await r.click(btn('Allouer une adresse IP Elastic')); await r.hold(3.0)
    r.mark('zone-b'); await r.hold(1.0)
    await r.scroll(2000); await r.hold(0.8)
    await r.click(btn('Créer une passerelle NAT', True)); await r.hold(4.0)
    r.mark('creee')
    r.mark('attente-debut', accelere=10)
    t0 = time.time()
    while time.time() - t0 < 300:
        await r.hold(15)
        await r.page.reload(); await r.hold(4.0); await r.page.evaluate(CURSOR_JS)
        if await r.present(lambda f: f.get_by_text(re.compile('^(Available|Disponible)$')).first, 1.5): break
    r.mark('attente-fin'); await r.hold(3.0)
