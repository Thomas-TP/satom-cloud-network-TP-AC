"""Module 9 : demande d'un vrai certificat public ACM pour leman.thomastp.ch et *.leman.thomastp.ch, valide par DNS (enregistrement cree dans Route 53)."""
from common import *
import subprocess, json

def dernier_certificat():
    """Identifiant du certificat leman.thomastp.ch demande le plus recemment."""
    v = json.loads(subprocess.run(['aws', 'acm', 'list-certificates', '--region', REGION, '--profile', 'TP-AC', '--output', 'json'], capture_output=True, text=True).stdout)['CertificateSummaryList']
    c = [x for x in v if x['DomainName'] == 'leman.thomastp.ch']
    c.sort(key=lambda x: x['CreatedAt'])
    return c[-1]['CertificateArn'].split('/')[-1]

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/acm/home?region=eu-north-1#/certificates/request', wait=6); await r.hold(1.5)
    await r.click('input[value=public]'); await r.hold(1.0)
    await r.click(btn('Suivant', True)); await r.hold(2.5)
    r.mark('formulaire')
    await r.type(lambda f: f.locator('input[type=text]').first, 'leman.thomastp.ch', delay=40); await r.hold(0.8)
    await r.click(btn('Ajouter un autre nom à ce certificat')); await r.hold(1.2)
    await r.type(lambda f: f.locator('input[type=text]').nth(1), '*.leman.thomastp.ch', delay=40); await r.hold(1.0)
    r.mark('noms')
    await r.scroll(500); await r.hold(1.0)
    r.mark('validation-dns')
    await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle identification', extra=[('Name', 'cert-leman-TP-AC')], kp='Saisir une clé', vp='Saisir une valeur')
    r.mark('balises')
    await r.scroll(1500)
    await r.click(btn('Demander', True)); await r.hold(5.0)
    r.mark('demande'); await r.hold(2.0)
    url = f'https://{REGION}.console.aws.amazon.com/acm/home?region={REGION}#/certificates/' + dernier_certificat()
    await r.goto(url, wait=6); await r.hold(2.5)
    r.mark('details')
    await r.scroll(300); await r.hold(1.0)
    await r.click(btn(re.compile("Cr.ation d.enregistrements dans Route 53"))); await r.hold(3.0)
    r.mark('creer-dns')
    await r.click(btn('Créer des enregistrements', True)); await r.hold(4.0)
    r.mark('enregistrements-crees')
    r.mark('attente-debut', accelere=8)
    for _ in range(8):
        await r.goto(url, wait=6); await r.hold(24.0)
        try:
            if await r.page.get_by_text('Émis', exact=True).count(): break
        except Exception: pass
    r.mark('attente-fin'); await r.hold(2.5)
    r.mark('emis'); await r.hold(2.0)
