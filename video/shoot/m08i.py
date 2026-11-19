"""Module 8 : configuration de rtr-siege : FRRouting, GRE (liaison simulee et GRE dans le VPN), BGP AS 65010, local-pref 200 sur la liaison et prepend x3 sur le VPN."""
from common import *
from m02f import terminal
from m07n import lines
import subprocess
from m08h import session

VTY = r'''vtysh <<'EOV'
configure terminal
ip route 192.168.10.0/24 192.168.10.1
ip route 10.20.0.0/22 xfrm-siege1 150
ip route 10.20.0.0/22 xfrm-siege2 160
route-map DX-IN permit 10
 set local-preference 200
route-map VPN-IN permit 10
route-map VPN-OUT permit 10
 set as-path prepend 65010 65010 65010
router bgp 65010
 bgp router-id 192.168.10.10
 no bgp ebgp-requires-policy
 neighbor 169.254.100.1 remote-as 64513
 neighbor 169.254.100.1 timers 3 9
 neighbor 169.254.101.1 remote-as 64513
 neighbor 169.254.101.1 timers 3 9
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.100.1 route-map DX-IN in
  neighbor 169.254.101.1 route-map VPN-IN in
  neighbor 169.254.101.1 route-map VPN-OUT out
 exit-address-family
end
write memory
EOV'''

WATCH = r'''cat > watch.sh <<'EOF'
while true; do for n in 1 2; do
 if swanctl --list-sas | grep -q "^siege-t$n: .*ESTABLISHED"; then ip route replace 10.20.0.74/32 dev xfrm-siege$n metric $((n*100)); else ip route del 10.20.0.74/32 dev xfrm-siege$n 2>/dev/null; fi
done; sleep 1; done
EOF'''

async def run(r):
    aws_pub = subprocess.run(['aws', 'ec2', 'describe-instances', '--filters', 'Name=tag:Name,Values=rtr-aws-TP-AC', 'Name=instance-state-name,Values=running', '--query', 'Reservations[0].Instances[0].PublicIpAddress', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()
    await session(r, 'rtr-siege-TP-AC')
    r.mark('terminal')
    await terminal(r, ['sudo -i', 'export DEBIAN_FRONTEND=noninteractive'], pause=1.5)
    await terminal(r, ['apt-get update -qq && apt-get install -y -qq frr iptables >/dev/null 2>&1; echo installe'], pause=1.0)
    r.mark('install-debut', accelere=8); await r.hold(60.0); r.mark('install-fin')
    await terminal(r, ["sed -i 's/^bgpd=no/bgpd=yes/' /etc/frr/daemons && systemctl restart frr && echo frr redemarre"], pause=4.0)
    await terminal(r, ['pkill -f watch.sh; ip route del 10.20.0.0/22 dev xfrm-siege1; ip route del 10.20.0.0/22 dev xfrm-siege2; ip route | grep 10.20'], pause=2.5)
    await lines(r, WATCH, 0.3)
    await terminal(r, ['nohup bash watch.sh >/dev/null 2>&1 &'], pause=2.0)
    await lines(r, f'''ip tunnel add gre-dx mode gre local 192.168.10.10 remote {aws_pub} ttl 255
ip addr add 169.254.100.2/30 dev gre-dx; ip link set gre-dx up
ip tunnel add gre-vpn mode gre local 192.168.10.10 remote 10.20.0.74 ttl 255
ip addr add 169.254.101.2/30 dev gre-vpn; ip link set gre-vpn up''', 0.5)
    r.mark('gre')
    r.mark('vtysh-debut', accelere=3)
    await lines(r, VTY, 0.3)
    r.mark('vtysh-fin')
    await terminal(r, ['sleep 15; vtysh -c "show bgp summary" | tail -7'], pause=20.0)
    r.mark('bgp'); await r.hold(4.0)
