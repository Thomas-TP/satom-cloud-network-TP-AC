"""Module 9 : tests de l'ALB avec son vrai nom (origin.leman.thomastp.ch) dans le navigateur : certificat ACM valide, pas d'avertissement ; etat des groupes cibles."""
from common import *
import subprocess

NOM = 'origin.leman.thomastp.ch'

def alb_dns():
    return _alb_dns()

def _alb_dns():
    return subprocess.run(['aws', 'elbv2', 'describe-load-balancers', '--names', 'alb-prod-leman-TP-AC', '--query', 'LoadBalancers[0].DNSName', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

def tg_url(name):
    arn = subprocess.run(['aws', 'elbv2', 'describe-target-groups', '--names', name, '--query', 'TargetGroups[0].TargetGroupArn', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()
    return ec2_url('TargetGroup:targetGroupArn=' + arn)

async def page(r, path):
    try: await r.page.goto('https://' + alb_dns() + path, wait_until='domcontentloaded')
    except Exception: pass
    await r.hold(2.5)

async def run(r):
    await r.goto(tg_url('tg-web-TP-AC'), wait=6); await r.hold(3.0)
    r.mark('sante-web'); await r.hold(2.0)
    await r.goto(tg_url('tg-app-TP-AC'), wait=6); await r.hold(3.0)
    r.mark('sante-app'); await r.hold(2.0)
    nav = await r.ctx.new_page(); await r.follow(nav); await r.hold(1.0)
    await nav.goto('https://' + NOM + '/api/health', wait_until='domcontentloaded'); await r.hold(3.0)
    r.mark('api')
    await nav.goto('https://' + NOM + '/', wait_until='domcontentloaded'); await r.hold(3.0)
    r.mark('web')
