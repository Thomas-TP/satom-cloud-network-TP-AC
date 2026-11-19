"""Module 12 : tableau de bord du portail : cibles saines, temps de reponse, erreurs 5xx (widgets definis par la source JSON)."""
from common import *
from common import _ids
import json

def source():
    ids = _ids()
    lb = 'app/alb-prod-leman-TP-AC/' + ids['alb_arn'].rsplit('/', 1)[-1]
    tgw = ids['tg_tg-web-TP-AC'].split(':', 5)[-1]; tga = ids['tg_tg-app-TP-AC'].split(':', 5)[-1]
    R = 'eu-north-1'
    return json.dumps({'widgets': [
        {'type': 'metric', 'x': 0, 'y': 0, 'width': 12, 'height': 6, 'properties': {'title': 'Cibles saines', 'region': R, 'stat': 'Average', 'period': 60, 'view': 'timeSeries',
          'metrics': [['AWS/ApplicationELB', 'HealthyHostCount', 'TargetGroup', tgw, 'LoadBalancer', lb], ['...', tga, '.', '.']]}},
        {'type': 'metric', 'x': 12, 'y': 0, 'width': 12, 'height': 6, 'properties': {'title': 'Cibles non saines', 'region': R, 'stat': 'Average', 'period': 60, 'view': 'timeSeries',
          'metrics': [['AWS/ApplicationELB', 'UnHealthyHostCount', 'TargetGroup', tgw, 'LoadBalancer', lb], ['...', tga, '.', '.']]}},
        {'type': 'metric', 'x': 0, 'y': 6, 'width': 12, 'height': 6, 'properties': {'title': 'Temps de reponse de l ALB', 'region': R, 'stat': 'Average', 'period': 60, 'view': 'timeSeries',
          'metrics': [['AWS/ApplicationELB', 'TargetResponseTime', 'LoadBalancer', lb]]}},
        {'type': 'metric', 'x': 12, 'y': 6, 'width': 12, 'height': 6, 'properties': {'title': 'Erreurs 5xx de l ALB', 'region': R, 'stat': 'Sum', 'period': 60, 'view': 'timeSeries',
          'metrics': [['AWS/ApplicationELB', 'HTTPCode_ELB_5XX_Count', 'LoadBalancer', lb]]}}]}, indent=1)

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#dashboards', wait=8); await r.hold(1.5)
    await r.click(btn('Créer un tableau de bord', True)); await r.hold(2.5)
    await r.type(lambda f: f.get_by_label('Nom du tableau de bord'), 'db-portail-leman-TP-AC'); await r.hold(0.8)
    r.mark('nom')
    await r.click(lambda f: f.get_by_role('button', name='Créer un tableau de bord').last); await r.hold(5.0)
    r.mark('cree')
    await r.click(btn('Fermer le modal')); await r.hold(1.5)
    await r.click(lambda f: f.get_by_role('button', name='Actions').first); await r.hold(1.5)
    await r.click_xy(1530, 413); await r.hold(3.0)
    r.mark('source')
    await r.click_xy(900, 450); await r.hold(0.5)
    await r.press('Control+a', 0.3); await r.press('Delete', 0.3)
    await r.page.keyboard.insert_text(source()); await r.hold(3.0)
    r.mark('json')
    await r.click(btn('Mettre à jour', True)); await r.hold(4.0)
    r.mark('widgets')
    await r.click(lambda f: f.get_by_role('button', name='Enregistrer').last); await r.hold(4.0)
    r.mark('enregistre'); await r.hold(3.0)
