"""Module 0 : budget de 100 USD avec alerte a 80 %."""
from rig import *

BUDGETS = 'https://us-east-1.console.aws.amazon.com/costmanagement/home#/budgets'

async def next_step(r, still_here):
    await r.hold(0.8)
    for _ in range(3):
        await r.click(btn('Suivant', True)); await r.hold(1.6)
        if not await r.present(still_here, 0.6): return

async def run(r):
    await r.goto(BUDGETS, wait=5)
    r.mark('liste-budgets'); await r.hold(2.5)
    await r.click(btn('Créer un budget')); await r.hold(2.0)
    r.mark('assistant')
    await r.click('input[value=CUSTOM]'); await r.hold(1.2)
    await r.click(btn('Suivant', True)); await r.hold(2.0)
    await r.type(field('Nom du budget'), 'budget-TP-AC-satom'); await r.hold(0.8)
    await r.type(field('Saisissez votre montant budgété'), '100'); await r.hold(1.0)
    r.mark('montant')
    await r.scroll(1500)
    await next_step(r, field('Saisissez votre montant budgété'))
    await r.click(btn("Ajouter un seuil d'alerte")); await r.hold(1.0)
    await r.type('input[type=number]', '80'); await r.hold(0.8)
    await r.type(ph('Séparer les adresses e-mail'), 'budget-tp-ac@example.com'); await r.hold(1.0)
    r.mark('alerte')
    await r.scroll(1500)
    await next_step(r, field('Destinataires'))
    await r.hold(1.5); await r.click(btn('Suivant', True)); await r.hold(2.0)
    r.mark('verification'); await r.hold(2.5)
    await r.scroll(3000)
    await r.click(btn('Créer un budget')); await r.hold(4.0)
    r.mark('cree')
    await r.hold(2.0)
