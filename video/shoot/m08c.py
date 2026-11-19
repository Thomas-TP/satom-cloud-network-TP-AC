"""Module 8 : route du sous-reseau public vers le siege par le Transit Gateway (pour le GRE dans le VPN), et Security Group du routeur cote AWS."""
from common import *
from m06f import tgw_id

async def run(r):
    tgw = tgw_id()
    await r.goto(vpc_url('RouteTables:'), wait=4)
    await r.click(lambda f: f.locator('tr', has_text='rt-public-leman-TP-AC').get_by_role('link').first); await r.hold(2.0)
    await r.click(tab('Routes')); await r.hold(1.5)
    await r.click(btn('Modifier des routes')); await r.hold(2.5)
    await r.click(btn('Ajouter une route')); await r.hold(1.2)
    dest = lambda f: f.get_by_role('combobox', name='Destination').last
    await r.type(dest, '192.168.10.0/24'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('Utiliser')).first); await r.hold(1.0)
    b = await r._box(dest)
    await r.click_xy(b['x'] + b['width'] + 206, b['y'] + b['height'] / 2); await r.hold(1.2)
    await r.click(lambda f: f.get_by_role('option', name='Transit Gateway', exact=True)); await r.hold(1.2)
    await r.type(lambda f: f.get_by_role('combobox', name='Cible').last, tgw[4:], clear=False); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('option', name=re.compile(tgw)).first); await r.hold(1.5)
    r.mark('route')
    await r.click(btn('Enregistrer les modifications'), straight=True); await r.hold(4.0)
    r.mark('route-enregistree'); await r.hold(1.5)
    # Security Group du routeur AWS
    await r.goto(ec2_url('SecurityGroups:'), wait=4); await r.hold(1.0)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(2.0)
    await r.type(ph('MyWebServerGroup'), 'rtr-aws-TP-AC'); await r.hold(0.5)
    await r.type(ph("Autorise l'accès SSH aux développeurs"), "Routeur cote AWS : GRE depuis le siege"); await r.hold(0.5)
    await r.click(lambda f: f.locator('button:has-text("vpc-05507")').first); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('option', name=re.compile('vpc-prod-leman-TP-AC')).first); await r.hold(1.5)
    await r.scroll(400); await r.scroll(700)
    await tags(r, 'prod', start=0, add='Ajouter une nouvelle balise', extra=[('Name', 'sg-rtr-aws-TP-AC')], kp='Saisir la clé', vp='Saisir la valeur')
    await r.scroll(900)
    await r.click(btn('Créer un groupe de sécurité', True)); await r.hold(4.5)
    r.mark('sg-cree'); await r.hold(1.5)
