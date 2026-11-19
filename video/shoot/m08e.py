"""Module 8 : le quota de vCPU de la classe est atteint : on arrete dev-01, dont nous n'avons plus besoin pour l'instant."""
from common import *

async def run(r):
    await r.goto(ec2_url('Instances:'), wait=6); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('dev-01-TP-AC')).get_by_role('checkbox').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('tat de l.instance')).first); await r.hold(1.5)
    r.mark('menu')
    await r.click_xy(1527, 155); await r.hold(2.5)
    r.mark('confirmation')
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Stop .Arrêter.')).last); await r.hold(4.0)
    r.mark('arret'); await r.hold(4.0)
