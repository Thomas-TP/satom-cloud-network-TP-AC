"""Module 8 : configuration de rtr-aws par Session Manager : FRRouting, deux tunnels GRE (liaison simulee et GRE dans le VPN), BGP AS 64513, NAT pour app-01."""
from common import *
from m02f import terminal
from m07n import lines
import subprocess

VTY = r'''vtysh <<'EOV'
configure terminal
ip route 10.20.0.0/22 10.20.0.65
ip route 192.168.10.10/32 10.20.0.65
router bgp 64513
 bgp router-id 10.20.0.74
 no bgp ebgp-requires-policy
 neighbor 169.254.100.2 remote-as 65010
 neighbor 169.254.100.2 timers 3 9
 neighbor 169.254.101.2 remote-as 65010
 neighbor 169.254.101.2 timers 3 9
 address-family ipv4 unicast
  network 10.20.0.0/22
 exit-address-family
end
write memory
EOV'''

async def session(r, name):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(name)).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    return new[0]

async def run(r):
    siege_pub = eip_ip('siege')
    await session(r, 'rtr-aws-TP-AC')
    r.mark('terminal')
    await terminal(r, ['sudo -i', 'export DEBIAN_FRONTEND=noninteractive'], pause=1.5)
    await terminal(r, ['apt-get update -qq && apt-get install -y -qq frr iptables >/dev/null 2>&1; echo installe'], pause=1.0)
    r.mark('install-debut', accelere=8); await r.hold(70.0); r.mark('install-fin')
    await terminal(r, ["sed -i 's/^bgpd=no/bgpd=yes/' /etc/frr/daemons && systemctl restart frr && echo frr redemarre",
                       'sysctl -w net.ipv4.ip_forward=1 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0 >/dev/null',
                       'D=$(ip -o -4 route show to default | cut -d" " -f5)'], pause=4.0)
    await lines(r, f'''ip tunnel add gre-dx mode gre local 10.20.0.74 remote {siege_pub} ttl 255
ip addr add 169.254.100.1/30 dev gre-dx; ip link set gre-dx up
ip tunnel add gre-vpn mode gre local 10.20.0.74 remote 192.168.10.10 ttl 255
ip addr add 169.254.101.1/30 dev gre-vpn; ip link set gre-vpn up
ip route replace 192.168.10.10/32 via 10.20.0.65 dev $D
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o $D -j MASQUERADE''', 0.5)
    r.mark('gre')
    await terminal(r, ['ip -br addr show | grep gre'], pause=2.5)
    await r.hold(1.5)
    r.mark('vtysh-debut', accelere=3)
    await lines(r, VTY, 0.3)
    r.mark('vtysh-fin')
    await r.hold(4.0)
    await terminal(r, ['vtysh -c "show bgp summary" | tail -6'], pause=4.0)
    r.mark('bgp-attente'); await r.hold(2.0)
