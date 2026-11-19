"""Module 4 : les journaux CloudWatch : l'alerte du flux bloque (example.com) et les flux vus par le pare-feu."""
from common import *

async def open_group(r, name):
    enc = name.replace('/', '$252F')
    await r.goto('https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#logsV2:log-groups/log-group/' + enc, wait=5)
    await r.hold(2.0)

async def run(r):
    await open_group(r, '/leman/nfw-alert-TP-AC')
    r.mark('groupe-alertes')
    await r.click(lambda f: f.locator('tr').filter(has_text=re.compile(r'\d{4}')).get_by_role('link').first); await r.hold(4.0)
    r.mark('evenements-alertes'); await r.hold(5.0)
    await open_group(r, '/leman/nfw-flow-TP-AC')
    await r.click(lambda f: f.locator('tr').filter(has_text=re.compile(r'\d{4}')).get_by_role('link').first); await r.hold(4.0)
    r.mark('evenements-flux'); await r.hold(5.0)
