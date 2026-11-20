"""Module 11 : la distribution porte le nom alternatif cdn.leman.thomastp.ch et le certificat ACM de Virginie (us-east-1) : parametres affiches dans la console."""
from common import *
from m11e import dist_id

async def run(r):
    d = dist_id()
    await r.goto(f'https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=eu-north-1#/distributions/{d}', wait=8); await r.hold(2.5)
    r.mark('detail')
    await r.scroll(450); await r.hold(2.0)
    r.mark('parametres'); await r.hold(3.5)
