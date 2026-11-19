"""Module 7 : le routeur de l'agence."""
from m07e import router

async def run(r):
    await router(r, 'agence', '192.168.20.10')
