"""Module 13 : la pile est creee : evenements, ressources et sorties."""
from common import *
from common import _ids
import urllib.parse

def stack_url(tab=''):
    return 'https://eu-north-1.console.aws.amazon.com/cloudformation/home?region=eu-north-1#/stacks/stackinfo?stackId=' + urllib.parse.quote(_ids()['stack_id'], safe='')

async def run(r):
    await r.goto(stack_url(), wait=9); await r.hold(2.5)
    r.mark('pile')
    await r.click(tab('Événements')); await r.hold(4.0)
    r.mark('evenements'); await r.hold(2.0)
    await r.click(tab('Ressources')); await r.hold(4.0)
    r.mark('ressources'); await r.hold(2.0)
    await r.click(tab('Sorties')); await r.hold(3.5)
    r.mark('sorties'); await r.hold(2.0)
