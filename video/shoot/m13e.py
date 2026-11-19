"""Module 13 : on retire la regle manuelle, la pile redevient IN_SYNC (nouvelle detection de derive)."""
from common import *
from common import _ids
from m13b import stack_url

async def run(r):
    await r.goto(ec2_url('SecurityGroup:securityGroupId=' + _ids()['sg_web_cfn']), wait=6); await r.hold(1.5)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Modifier les règles entrantes').first); await r.hold(2.5)
    r.mark('editeur')
    await r.click_xy(1668, 362); await r.hold(1.5)
    r.mark('retiree')
    await r.click(btn('Enregistrer les règles', True)); await r.hold(4.0)
    r.mark('enregistree'); await r.hold(1.5)
    await r.goto(stack_url(), wait=9); await r.hold(2.0)
    await r.click(lambda f: f.get_by_role('button', name='Actions de pile').first); await r.hold(1.5)
    await r.click_xy(1495, 224); await r.hold(4.0)
    r.mark('detection'); await r.hold(25.0)
    await r.goto(stack_url(), wait=9); await r.hold(3.0)
    r.mark('en-phase'); await r.hold(3.0)
