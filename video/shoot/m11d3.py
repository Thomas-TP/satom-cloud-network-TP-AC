"""Module 11 : enregistrement alias cdn.leman.thomastp.ch -> distribution CloudFront, dans la zone publique."""
from common import *
from m10c import zone_pub
from m11e import dist_id
import subprocess

def cf_domaine():
    return subprocess.run(['aws', 'cloudfront', 'get-distribution', '--id', dist_id(), '--query', 'Distribution.DomainName', '--output', 'text', '--profile', 'TP-AC'], capture_output=True, text=True).stdout.strip()

async def run(r):
    z = zone_pub()
    await r.goto(f'https://us-east-1.console.aws.amazon.com/route53/v2/hostedzones#ListRecordSets/{z}', wait=6); await r.hold(2.0)
    await r.click(btn('Créer un enregistrement', True)); await r.hold(3.0)
    await r.type(ph('subdomain'), 'cdn', delay=40); await r.hold(0.8)
    await r.click(lambda f: f.get_by_text(re.compile('^Alias$')).first); await r.hold(1.2)
    r.mark('alias')
    await r.click(btn('Choisir un point de terminaison')); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('distribution CloudFront')).first); await r.hold(1.5)
    await r.click(lambda f: f.get_by_placeholder(re.compile('Choisir une distribution')).first); await r.hold(1.5)
    await r.type(lambda f: f.get_by_placeholder(re.compile('Choisir une distribution')).first, cf_domaine(), delay=30); await r.hold(1.5)
    r.mark('liste')
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.5)
    r.mark('distribution')
    await r.click(btn('Créer des enregistrements', True)); await r.hold(5.0)
    r.mark('cree'); await r.hold(2.0)
