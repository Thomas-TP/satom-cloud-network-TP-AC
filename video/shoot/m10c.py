"""Module 10 : la zone publique reelle leman.thomastp.ch (sous-domaine delegue depuis le DNS du domaine) : serveurs de noms AWS attribues a la zone, enregistrement alias origin."""
from common import *
import subprocess

def zone_pub():
    return subprocess.run(['aws', 'route53', 'list-hosted-zones-by-name', '--dns-name', 'leman.thomastp.ch', '--query', 'HostedZones[0].Id', '--output', 'text', '--profile', 'TP-AC'], capture_output=True, text=True).stdout.strip().split('/')[-1]

async def run(r):
    await r.goto(f'https://us-east-1.console.aws.amazon.com/route53/v2/hostedzones#ListRecordSets/{zone_pub()}', wait=6); await r.hold(2.5)
    r.mark('zone'); await r.hold(1.5)
    await r.click(lambda f: f.get_by_text(re.compile('^Détails de la zone hébergée$')).first); await r.hold(2.5)
    r.mark('serveurs'); await r.hold(4.0)
    r.mark('origin'); await r.hold(3.0)
