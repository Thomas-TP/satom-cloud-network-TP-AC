"""Module 6 : les routes apprises dans chaque table du Transit Gateway : chacune ne voit que l'autre VPC."""
from common import *
from m06e import rtb

async def routes(r, table):
    await r.goto(vpc_url('TransitGatewayRouteTableDetails:transitGatewayRouteTableId=' + rtb(table)), wait=4)
    await r.hold(1.0)
    await r.click(tab('Acheminements')); await r.hold(3.0)

async def run(r):
    await routes(r, 'tgw-rt-prod-TP-AC'); r.mark('routes-prod'); await r.hold(3.5)
    await routes(r, 'tgw-rt-dev-TP-AC'); r.mark('routes-dev'); await r.hold(3.5)
