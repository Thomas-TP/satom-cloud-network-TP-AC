"""Module 11 : deux comportements : /static/* (cache 24 h) et /api/* (jamais de cache, tous les en-tetes et cookies)."""
from common import *

import subprocess
def dist_id():
    from m11d import DESCRIPTION
    return subprocess.run(['aws', 'cloudfront', 'list-distributions', '--query', f"DistributionList.Items[?Comment=='{DESCRIPTION}'].Id|[0]", '--output', 'text', '--profile', 'TP-AC'], capture_output=True, text=True).stdout.strip()
def BASE(): return 'https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=eu-north-1#/distributions/' + dist_id()

async def comportement(r, chemin, methodes, cache, origine_req=None):
    await r.goto(BASE() + '/behaviors', wait=8); await r.hold(1.5)
    await r.click(lambda f: f.get_by_text('Créer un comportement', exact=True).first); await r.hold(3.0)
    await r.type(lambda f: f.get_by_placeholder(re.compile('Exemple de modèle de chemin')), chemin); await r.hold(0.8)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('^Utilisation')).first); await r.hold(1.0)
    await r.click(btn("Sélectionner une origine ou un groupe d'origines")); await r.hold(3.0)
    await r.press('ArrowDown', 0.6); await r.press('Enter', 1.2)
    await r.click(f'input[value="{methodes}"]'); await r.hold(1.0)
    r.mark(f'{chemin}-formulaire')
    await r.scroll(600); await r.hold(0.8)
    if cache not in ('CachingDisabled', 'CachingOptimized'):
        await r.click(lambda f: f.get_by_role('button', name=re.compile('^CachingDisabled')).first); await r.hold(1.2)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('^' + cache)).first); await r.hold(1.2)
    if origine_req:
        await r.click(lambda f: f.get_by_text(re.compile('Politique de demande à l.origine')).first.locator('xpath=following::button[1]')); await r.hold(1.2)
        await r.click(lambda f: f.get_by_role('option', name=re.compile('^' + origine_req)).first); await r.hold(1.2)
    r.mark(f'{chemin}-cache')
    await r.scroll(2500); await r.hold(0.8)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Créer un comportement')).last); await r.hold(5.0)
    r.mark(f'{chemin}-cree'); await r.hold(2.0)

async def run(r):
    await comportement(r, '/static/*', '2', 'CachingOptimized')
