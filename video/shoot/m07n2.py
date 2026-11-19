"""Module 7 : le routeur de l'agence."""
from m07n import conf

async def run(r):
    await conf(r, 'agence', '192.168.20.10')
