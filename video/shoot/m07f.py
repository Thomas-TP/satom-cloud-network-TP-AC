"""Module 7 : une adresse IP Elastic par routeur (adresse publique fixe : c'est celle de la Customer Gateway), puis association a l'instance."""
from common import *
import subprocess

async def eip(r, n):
    await r.goto(ec2_url('AllocateAddress:'), wait=4); await r.hold(1.2)
    await r.scroll(400)
    await tags(r, 'prod', start=0, add='Ajoutez une balise', extra=[('Name', f'eip-rtr-{n}-TP-AC')], kp='Saisissez la clé', vp='Saisissez la valeur')
    r.mark(f'{n}-balises')
    await r.scroll(900)
    await r.click(btn('Allouez', True)); await r.hold(4.5)
    r.mark(f'{n}-allouee')
    # association : on selectionne l'adresse dans la liste, puis Actions
    await r.goto(ec2_url('Addresses:'), wait=4); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(f'eip-rtr-{n}-TP-AC')).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('button', name='Actions').first); await r.hold(1.2)
    await r.click_xy(1723, 204); await r.hold(3.0)
    r.mark(f'{n}-associer')
    await r.click(lambda f: f.get_by_role('combobox', name=re.compile('instance', re.I)).first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(f'rtr-{n}-TP-AC')).first); await r.hold(1.5)
    await r.scroll(700)
    await r.click(btn('Associez', True)); await r.hold(4.0)
    r.mark(f'{n}-associee'); await r.hold(1.5)

async def run(r):
    await eip(r, 'siege'); await eip(r, 'agence')
