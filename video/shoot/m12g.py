"""Module 12 : Logs Insights sur le journal de flux : les connexions refusees (REJECT) par source et par port."""
from common import *

QUERY = 'filter action="REJECT" | stats count(*) as refus by srcAddr, dstPort | sort refus desc | limit 10'

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#logsV2:logs-insights', wait=9); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name=re.compile("Sélectionner jusqu'à 50 groupes")).first); await r.hold(1.5)
    await r.click(lambda f: f.get_by_text('/leman/vpc-prod/flow-TP-AC', exact=True).first); await r.hold(1.5)
    await r.press('Escape', 0.8)
    r.mark('groupe')
    await r.click_xy(520, 400); await r.hold(0.6)
    await r.press('Control+a', 0.3); await r.press('Delete', 0.3)
    await r.page.keyboard.insert_text(QUERY); await r.hold(2.0)
    r.mark('requete')
    await r.click(btn('Exécuter la requête', True)); await r.hold(12.0)
    r.mark('resultat'); await r.hold(3.0)
