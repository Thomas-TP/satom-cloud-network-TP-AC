"""Module 9 : tests de l'ALB dans le navigateur (certificat auto-signe : avertissement attendu), et etat des groupes cibles."""
from common import *
import subprocess

def alb_dns():
    v = _alb_dns()
    return v if v and 'rror' not in v else _ids()['alb_dns']

def _alb_dns():
    return subprocess.run(['aws', 'elbv2', 'describe-load-balancers', '--names', 'alb-prod-leman-TP-AC', '--query', 'LoadBalancers[0].DNSName', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

def tg_url(name):
    arn = _ids().get('tg_' + name) or subprocess.run(['aws', 'elbv2', 'describe-target-groups', '--names', name, '--query', 'TargetGroups[0].TargetGroupArn', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()
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
    bs = await r.ctx.browser.new_browser_cdp_session()
    await bs.send('Security.setIgnoreCertificateErrors', {'ignore': True})
    nav = await r.ctx.new_page(); await r.follow(nav); await r.hold(1.0)
    await nav.goto('https://' + alb_dns() + '/api/health', wait_until='domcontentloaded'); await r.hold(3.0)
    r.mark('api')
    await nav.goto('https://' + alb_dns() + '/api/health?essai=2', wait_until='domcontentloaded'); await r.hold(3.0)
    await bs.send('Security.setIgnoreCertificateErrors', {'ignore': False})
