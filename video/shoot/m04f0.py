"""Module 4 : deux groupes de journaux CloudWatch (alertes et flux) pour recevoir les journaux du pare-feu."""
from common import *

async def run(r):
    for name in ('/leman/nfw-alert-TP-AC', '/leman/nfw-flow-TP-AC'):
        await r.goto('https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#logsV2:log-groups/create-log-group', wait=5)
        await r.hold(1.0)
        await r.type(ph('Saisir le nom du groupe de journaux'), name); await r.hold(1.0)
        r.mark('nom-' + name.split('-')[1])
        await r.scroll(1200); await r.hold(0.8)
        await r.click(btn('Créer', True)); await r.hold(4.0)
    r.mark('termine'); await r.hold(1.5)
