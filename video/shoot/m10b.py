"""Module 10 : enregistrements web et app dans la zone privee."""
from common import *

async def run(r):
    await r.goto(r53_url('ListRecordSets/' + zone_id('prod.leman.internal.')), wait=6); await r.hold(2.0)
    await r.click(btn('Créer un enregistrement', True)); await r.hold(3.0)
    await r.type(ph('subdomain'), 'web'); await r.hold(0.5)
    await r.type(lambda f: f.locator('textarea').first, '10.20.0.10'); await r.hold(0.8)
    r.mark('web')
    await r.click(btn('Ajouter un autre enregistrement', True)); await r.hold(1.5)
    await r.type(lambda f: f.get_by_placeholder('subdomain').nth(1), 'app'); await r.hold(0.5)
    await r.type(lambda f: f.locator('textarea').nth(1), '10.20.1.10'); await r.hold(0.8)
    r.mark('app')
    await r.scroll(900)
    await r.click(btn('Créer des enregistrements', True)); await r.hold(5.0)
    r.mark('crees'); await r.hold(2.0)
