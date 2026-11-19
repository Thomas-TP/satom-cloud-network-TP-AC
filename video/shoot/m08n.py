"""Module 8 : l'association est active, et le Transit Gateway a un attachement de type Direct Connect Gateway."""
from common import *

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/directconnect/v2/home?region=eu-north-1#/dxgateways', wait=6); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('dxgw-leman-TP-AC')).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('link', name='Afficher les détails').first); await r.hold(3.0)
    await r.click(tab('Associations des passerelles')); await r.hold(4.0)
    r.mark('association'); await r.hold(2.5)
    await r.goto(vpc_url('TransitGatewayAttachments:'), wait=5); await r.hold(4.0)
    r.mark('attachements'); await r.hold(4.0)
