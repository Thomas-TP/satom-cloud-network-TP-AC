"""Module 9 : Security Group de l'ALB (443 ouvert a tous)."""
from common import *
from m03a import rule

async def run(r):
    await r.goto(ec2_url('SecurityGroups:'), wait=4); await r.hold(1.0)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(2.0)
    await r.type(ph('MyWebServerGroup'), 'alb-TP-AC'); await r.hold(0.5)
    await r.type(ph("Autorise l'accès SSH aux développeurs"), 'ALB : 443 public'); await r.hold(0.5)
    await r.click('button:has-text("vpc-05507")'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    await r.scroll(400)
    await rule(r, 1, 443, '0.0.0.0/0', 'HTTPS public')
    r.mark('regle-443'); await r.hold(1.0)
    await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', 'sg-alb-TP-AC')], kp='Saisir la clé', vp='Saisir la valeur')
    await r.scroll(900)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(4.5)
    r.mark('cree'); await r.hold(2.0)
