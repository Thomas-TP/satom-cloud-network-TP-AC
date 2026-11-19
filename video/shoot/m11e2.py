"""Module 11 : comportement /api/* (jamais de cache, tous les en-tetes et cookies)."""
from m11e import comportement

async def run(r):
    await comportement(r, '/api/*', '7', 'CachingDisabled', 'AllViewer')
