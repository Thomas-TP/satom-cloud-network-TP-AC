"""Module 11 : listener HTTP 80 sur l'ALB (origine de CloudFront : le certificat auto-signe de l'ALB ne peut pas etre valide par CloudFront)."""
from common import *

async def run(r):
    await r.goto(ec2_url('LoadBalancers:'), wait=6); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('link', name='alb-prod-leman-TP-AC').first); await r.hold(3.0)
    await r.click(btn('Ajouter un écouteur', True)); await r.hold(3.0)
    r.mark('formulaire')
    await r.click(lambda f: f.get_by_role('button', name='Sélectionner un groupe cible').first); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('tg-web-TP-AC')).first); await r.hold(1.5)
    r.mark('cible')
    await r.scroll(900)
    await r.click(btn('Ajouter un écouteur', True)); await r.hold(5.0)
    r.mark('ajoute'); await r.hold(2.0)
