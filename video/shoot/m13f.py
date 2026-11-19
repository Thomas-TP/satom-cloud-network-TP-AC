"""Module 13 : suppression de la pile : CloudFormation supprime dans l'ordre inverse de la creation."""
from common import *
from m13b import stack_url

async def run(r):
    await r.goto(stack_url(), wait=9); await r.hold(2.0)
    await r.click(btn('Supprimer la pile', True)); await r.hold(2.5)
    r.mark('confirmation')
    await r.type(ph('stack-portail-leman-TP-AC'), 'stack-portail-leman-TP-AC'); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('button', name='Supprimer la pile').last); await r.hold(5.0)
    r.mark('suppression')
    await r.click(tab('Événements')); await r.hold(3.0)
    r.mark('attente-debut', accelere=8)
    for _ in range(6):
        await r.click(lambda f: f.get_by_role('button', name=re.compile('Actualiser|Refresh')).first); await r.hold(14.0)
    r.mark('attente-fin'); await r.hold(2.0)
