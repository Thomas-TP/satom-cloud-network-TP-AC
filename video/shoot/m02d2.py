"""Module 2 : la passerelle NAT est passee a l'etat disponible."""
from common import *

async def run(r):
    await r.goto(vpc_url('NatGateways:'), wait=5)
    await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('link', name=nat_id()).first); await r.hold(2.0)
    for _ in range(12):
        if await r.present(lambda f: f.get_by_text(re.compile('^Available$|^Disponible$')).first, 1.0): break
        await r.hold(10); await r.page.reload(); await r.hold(4.0)
    r.mark('disponible'); await r.hold(4.0)
