"""Module 12 : une sonde SSH non autorisee vers web-01 depuis rtr-agence : le Security Group la refuse, le journal de flux la retiendra (REJECT)."""
from common import *
from common import _ids
from m02f import terminal
from m07q import open_session

async def run(r):
    ip = _ids()['web_ip']
    a = await open_session(r, 'rtr-agence-TP-AC')
    await terminal(r, ['sudo -i', f'WEB={ip}'], pause=1.5)
    await terminal(r, ['for i in 1 2 3 4 5; do timeout 3 bash -c "</dev/tcp/$WEB/22" && echo ouvert || echo "port 22 refuse ($i)"; done'], pause=18.0)
    r.mark('sonde'); await r.hold(2.0)
