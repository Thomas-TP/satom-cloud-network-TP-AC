"""Module 8 : panne de la liaison Direct Connect simulee : BGP bascule sur le chemin du VPN (prepend x3), puis retour sur la liaison dediee."""
from common import *
from m02f import terminal
from m07q import open_session
import subprocess

LOOP = 'while true; do R=$(ip route get 10.20.1.10 from 192.168.10.20 | head -1 | awk \'{print $5}\'); curl -s -m 1 --interface 192.168.10.20 http://10.20.1.10:8080/api/health >/dev/null && echo "$(date +%T) OK via $R" || echo "$(date +%T) ECHEC ($R)"; sleep 0.5; done'

async def run(r):
    aws_pub = subprocess.run(['aws', 'ec2', 'describe-instances', '--filters', 'Name=tag:Name,Values=rtr-aws-TP-AC', 'Name=instance-state-name,Values=running', '--query', 'Reservations[0].Instances[0].PublicIpAddress', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()
    main = r.page
    a = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i'], pause=1.5)
    await terminal(r, [LOOP], pause=8.0)
    r.mark('boucle')
    await r.follow(main)
    b = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i', f'A={aws_pub}'], pause=1.5)
    await terminal(r, ['iptables -I OUTPUT -p gre -d $A -j DROP; iptables -I INPUT -p gre -s $A -j DROP; date +%T'], pause=2.0)
    r.mark('panne')
    await r.follow(a); await r.hold(32.0)
    r.mark('bascule')
    await r.follow(b)
    await terminal(r, ['vtysh -c "show bgp summary" | tail -5', 'iptables -D OUTPUT -p gre -d $A -j DROP; iptables -D INPUT -p gre -s $A -j DROP; date +%T'], pause=3.0)
    r.mark('retablissement')
    await r.follow(a); await r.hold(60.0)
    r.mark('retour')
    await r.page.keyboard.press('Control+C'); await r.hold(1.0)
    await terminal(r, ['vtysh -c "show bgp summary" | tail -5'], pause=3.0)
    r.mark('fin'); await r.hold(2.0)
