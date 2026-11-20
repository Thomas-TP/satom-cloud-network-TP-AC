"""Module 9 : enregistrement alias origin.leman.thomastp.ch -> ALB, pour que le certificat de l'ALB corresponde a un nom reel."""
from common import *
import subprocess

def zone_pub():
    return subprocess.run(['aws', 'route53', 'list-hosted-zones-by-name', '--dns-name', 'leman.thomastp.ch', '--query', 'HostedZones[0].Id', '--output', 'text', '--profile', 'TP-AC'], capture_output=True, text=True).stdout.strip().split('/')[-1]

async def run(r):
    z = zone_pub()
    await r.goto(f'https://us-east-1.console.aws.amazon.com/route53/v2/hostedzones#ListRecordSets/{z}', wait=6); await r.hold(2.0)
    r.mark('zone')
    await r.click(btn('Créer un enregistrement', True)); await r.hold(3.0)
    await r.type(ph('subdomain'), 'origin', delay=40); await r.hold(0.8)
    await r.click(lambda f: f.get_by_text(re.compile('^Alias$')).first); await r.hold(1.2)
    r.mark('alias')
    await r.click(btn('Choisir un point de terminaison')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('application et Classic Load Balancer')).first); await r.hold(1.2)
    await r.click(btn('Choisir une région')); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name=re.compile('Filtrer les régions')).first, 'eu-north'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('eu-north-1')).first); await r.hold(1.5)
    await r.click(lambda f: f.get_by_placeholder(re.compile('quilibreur de charge')).first); await r.hold(1.5)
    r.mark('alb-liste')
    await r.click(lambda f: f.get_by_role('option', name=re.compile('alb-prod-leman-TP-AC')).first); await r.hold(1.5)
    r.mark('alb')
    await r.click(btn('Créer des enregistrements', True)); await r.hold(5.0)
    r.mark('cree'); await r.hold(2.0)
