"""Module 10 : la zone privee se resout depuis web-01 (resolveur du VPC)."""
from common import *
from m02f import terminal
from m07q import open_session

async def run(r):
    a = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i'], pause=1.5)
    await terminal(r, ['getent hosts web.prod.leman.internal', 'getent hosts app.prod.leman.internal', 'grep nameserver /etc/resolv.conf'], pause=3.5)
    r.mark('zone-privee'); await r.hold(3.0)
