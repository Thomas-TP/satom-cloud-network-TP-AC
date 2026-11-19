"""Module 8 : verification BGP : sessions, local-pref 200 sur la liaison, prepend sur le VPN, et l'API d'app-01 par la liaison simulee."""
from common import *
from m02f import terminal
from m08h import session

async def run(r):
    await session(r, 'rtr-siege-TP-AC')
    r.mark('siege-terminal')
    await terminal(r, ['sudo -i', 'vtysh -c "show bgp summary" | tail -6'], pause=3.5)
    r.mark('siege-bgp')
    await terminal(r, ['vtysh -c "show ip bgp 10.20.0.0/22"'], pause=3.5)
    r.mark('siege-localpref'); await r.hold(2.0)
    await terminal(r, ['ip addr add 192.168.10.20/32 dev lo', 'ip route get 10.20.1.10 from 192.168.10.20 | head -1', 'curl -s -m 6 --interface 192.168.10.20 http://10.20.1.10:8080/api/health; echo'], pause=5.0)
    r.mark('siege-api'); await r.hold(1.5)
    await session(r, 'rtr-aws-TP-AC')
    r.mark('aws-terminal')
    await terminal(r, ['sudo -i', 'vtysh -c "show ip bgp 192.168.10.0/24"'], pause=3.5)
    r.mark('aws-prepend'); await r.hold(3.0)
