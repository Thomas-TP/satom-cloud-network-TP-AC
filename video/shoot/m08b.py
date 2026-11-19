"""Module 8 : association de la passerelle Direct Connect au Transit Gateway, avec les prefixes autorises."""
from common import *

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/directconnect/v2/home?region=eu-north-1#/dxgateways', wait=6); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('dxgw-leman-TP-AC')).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('link', name='Afficher les détails').first); await r.hold(3.0)
    await r.click(tab('Associations des passerelles')); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('link', name='Associer la passerelle').first); await r.hold(3.0)
    await r.click(btn('Ma passerelle')); await r.hold(1.5)
    r.mark('liste-passerelles')
    await r.click(lambda f: f.get_by_role('option', name=re.compile('tgw-leman-TP-AC')).first); await r.hold(1.5)
    await r.click(lambda f: f.locator('textarea').first); await r.hold(0.5)
    await r.page.keyboard.type('10.20.0.0/22,192.168.10.0/24', delay=50); await r.hold(1.2)
    r.mark('prefixes')
    await r.click(btn('Associer la passerelle', True)); await r.hold(5.0)
    r.mark('associee'); await r.hold(3.0)
    r.mark('attente-debut', accelere=8); await r.hold(90.0); r.mark('attente-fin')
