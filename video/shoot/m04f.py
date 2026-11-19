"""Module 4 : journalisation du pare-feu dans CloudWatch Logs (alertes et flux)."""
from common import *

async def run(r):
    await r.goto(vpc_url('NetworkFirewalls:'), wait=5)
    await r.click(lambda f: f.get_by_role('link', name='nfw-prod-leman-TP-AC').first); await r.hold(2.5)
    await r.scroll(2500); await r.hold(1.0)
    await r.click(lambda f: f.locator('xpath=//*[normalize-space(text())="Journalisation"]/ancestor::*[.//button[normalize-space()="Modifier"]][1]').get_by_role('button', name='Modifier')); await r.hold(3.0)
    r.mark('editeur')
    await r.click(lambda f: f.locator('input[type=checkbox]').nth(0)); await r.hold(1.0)
    await r.click('input[value=CloudWatchLogs] >> nth=0'); await r.hold(1.0)
    await r.type(ph('Rechercher le groupe de journaux CloudWatch par nom'), 'nfw-alert'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('nfw-alert-TP-AC')).first); await r.hold(1.2)
    r.mark('alertes')
    await r.click(lambda f: f.locator('input[type=checkbox]').nth(1)); await r.hold(1.5)
    await r.scroll(500); await r.hold(0.8)
    await r.click('input[value=CloudWatchLogs] >> nth=1'); await r.hold(1.0)
    await r.type(lambda f: f.get_by_placeholder('Rechercher le groupe de journaux CloudWatch par nom').nth(1), 'nfw-flow'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('nfw-flow-TP-AC')).first); await r.hold(1.2)
    r.mark('flux')
    await r.scroll(1200); await r.hold(0.8)
    await r.click(btn('Enregistrer', True)); await r.hold(4.0)
    r.mark('enregistre'); await r.hold(2.0)
