"""Module 8 : l'attachement de la production n'avait qu'un sous-reseau (zone A) : rtr-aws vit en zone B, on ajoute le sous-reseau public de la zone B."""
from common import *

async def run(r):
    await r.goto(vpc_url('TransitGatewayAttachments:'), wait=5); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('tgwa-prod-TP-AC')).get_by_role('checkbox').first); await r.hold(1.2)
    r.mark('attachement-choisi')
    await r.goto(vpc_url('ModifyTransitGatewayVpcAttachment:transitGatewayAttachmentId=tgw-attach-00c116189628aaf44'), wait=5); await r.hold(2.0)
    r.mark('formulaire')
    await r.click(lambda f: f.get_by_text('eu-north-1b', exact=True).first); await r.hold(1.5)
    await r.click(lambda f: f.locator('button:has-text("subnet-01a9a7681846402b1")').first); await r.hold(1.2)
    r.mark('zone-b')
    await r.press('Escape', 0.5)
    await r.click(btn("Modifier l'association pour Transit Gateway", True)); await r.hold(5.0)
    r.mark('modifiee')
    r.mark('attente-debut', accelere=6); await r.hold(75.0); r.mark('attente-fin')
