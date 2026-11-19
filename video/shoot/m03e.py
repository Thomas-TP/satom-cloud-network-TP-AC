"""Module 3 : liste de controle d'acces reseau (NACL) du sous-reseau public : 443, ports ephemeres et trafic interne."""
from common import *

async def regles(r):
    """Trois regles : 100 (TCP 443), 110 (ports ephemeres), 120 (tout le trafic interne du VPC)."""
    num = lambda k: (lambda f: f.locator('input[aria-label^="Entrée du numéro de règle"]').nth(k))
    port = lambda k: (lambda f: f.locator('input[aria-label^="Plage de ports de règle"]').nth(k))
    src = lambda k: (lambda f: f.locator('input[aria-label^="Source de règle"]').nth(k))
    for k, (n, p) in enumerate([(100, '443'), (110, '1024-65535')]):
        await r.click(btn('Ajouter une nouvelle règle')); await r.hold(1.0)
        await r.type(num(k), str(n)); await r.type(port(k), p); await r.hold(0.6)
    await r.click(btn('Ajouter une nouvelle règle')); await r.hold(1.0)
    await r.type(num(2), '120')
    await r.click(lambda f: f.get_by_role('button', name='TCP personnalisé').last); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('^Tout le trafic')).first); await r.hold(1.0)
    await r.type(src(2), '10.20.0.0/22'); await r.hold(0.8)

async def run(r):
    await r.goto(vpc_url('acls:'), wait=4)
    await r.hold(1.0)
    await r.click(btn('Créer une liste ACL réseau', True)); await r.hold(2.0)
    await r.type(ph('my-acl-01'), 'nacl-public-TP-AC'); await r.hold(0.6)
    await r.click(btn('Sélectionner un VPC')); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.0)
    await tags(r, 'prod', start=1, add='Ajouter une balise')
    r.mark('formulaire'); await r.hold(1.0)
    await r.click(btn('Créer une liste ACL réseau', True)); await r.hold(4.0)
    r.mark('creee'); await r.hold(1.5)
    await r.goto(vpc_url('acls:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='nacl-public-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Règles entrantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Modifier les règles entrantes')).first); await r.hold(2.0)
    r.mark('editeur-entrant')
    await regles(r); r.mark('regles-entrantes'); await r.hold(1.0)
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    await r.click(tab('Règles sortantes')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Modifier les règles sortantes')).first); await r.hold(2.0)
    await regles(r); r.mark('regles-sortantes'); await r.hold(1.0)
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    await r.click(tab('Associations de sous-réseau')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name=re.compile('Modifier les associations de sous-réseau')).first); await r.hold(2.0)
    await r.click(lambda f: f.locator('tr', has_text='sub-public-1a-TP-AC').get_by_role('checkbox')); await r.hold(1.2)
    await r.click(btn('Enregistrer les modifications')); await r.hold(4.0)
    r.mark('associee'); await r.hold(2.0)
