"""Module 7 : configuration d'un routeur de site par Session Manager : strongSwan, deux tunnels IPsec IKEv2, interfaces xfrm et bascule de route."""
from common import *
from m02f import terminal

GEN = r'''cat > gen.py <<'EOF'
import sys,json,xml.etree.ElementTree as E
S,P=sys.argv[1:3]; k=json.load(open('/root/psk.json')); c=s=x=''
for i,t in enumerate(E.parse('/root/vpn.xml').getroot().findall('ipsec_tunnel'),1):
 g=lambda a:t.find(a+'/tunnel_outside_address/ip_address').text
 pub,aws,ins=g('customer_gateway'),g('vpn_gateway'),t.find('customer_gateway/tunnel_inside_address/ip_address').text
 f=(10 if S=='siege' else 20)+i
 c+='  %s-t%d {\n    version = 2\n    local_addrs = %s\n    remote_addrs = %s\n    local { auth = psk\n id = %s }\n    remote { auth = psk\n id = %s }\n    proposals = aes256-sha256-modp2048\n    dpd_delay = 10s\n    children { %s-t%d { local_ts = 0.0.0.0/0\n remote_ts = 0.0.0.0/0\n esp_proposals = aes256-sha256-modp2048\n if_id_in = %d\n if_id_out = %d\n start_action = start\n dpd_action = restart } }\n  }\n'%(S,i,P,aws,pub,aws,S,i,f,f)
 s+='  ike-%s-t%d { id = %s\n secret = "%s" }\n'%(S,i,aws,k[S+str(i)])
 x+='ip link add xfrm-%s%d type xfrm dev $D if_id %d; ip addr add %s/30 dev xfrm-%s%d; ip link set xfrm-%s%d up\n'%(S,i,f,ins,S,i,S,i)
open('/etc/swanctl/conf.d/%s.conf'%S,'w').write('connections {\n'+c+'}\nsecrets {\n'+s+'}\n')
open('xfrm.sh','w').write('D=$(ip -o -4 route show to default|cut -d" " -f5)\n'+x)
EOF'''

WATCH = r'''cat > watch.sh <<'EOF'
while true; do for n in 1 2; do
 if swanctl --list-sas | grep -q "^SITE-t$n: .*ESTABLISHED"; then ip route replace 10.20.0.0/22 dev xfrm-SITE$n metric $((n*100)); else ip route del 10.20.0.0/22 dev xfrm-SITE$n 2>/dev/null; fi
done; sleep 1; done
EOF'''

async def lines(r, text, pause=0.25):
    for ln in text.split('\n'):
        await terminal(r, [ln], pause=pause)

async def conf(r, n, priv, wait=75.0):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(f'rtr-{n}-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark(f'{n}-terminal')
    await terminal(r, ['sudo -i', 'export AWS_DEFAULT_REGION=eu-north-1 DEBIAN_FRONTEND=noninteractive'], pause=1.5)
    await terminal(r, ['apt-get update -qq && apt-get install -y -qq strongswan-swanctl charon-systemd awscli >/dev/null 2>&1; echo installe'], pause=1.0)
    r.mark(f'{n}-install-debut', accelere=8); await r.hold(wait); r.mark(f'{n}-install-fin')
    await terminal(r, ['aws secretsmanager get-secret-value --secret-id Projet/SatomCloudNetwork/vpn --query SecretString --output text > psk.json; chmod 600 psk.json',
                       f"aws ec2 describe-vpn-connections --filters Name=tag:Name,Values=vpn-{n}-TP-AC Name=state,Values=available --query 'VpnConnections[0].CustomerGatewayConfiguration' --output text > vpn.xml",
                       'ls -l psk.json vpn.xml'], pause=4.0)
    r.mark(f'{n}-recup')
    r.mark(f'{n}-gen-debut', accelere=4)
    await lines(r, GEN, 0.2)
    r.mark(f'{n}-gen-fin')
    await terminal(r, [f'python3 gen.py {n} {priv} && bash xfrm.sh && cat /etc/swanctl/conf.d/{n}.conf | grep -vE "secret|id =" | head -14'], pause=3.0)
    r.mark(f'{n}-conf'); await r.hold(2.5)
    await terminal(r, ['sysctl -w net.ipv4.ip_forward=1 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0 >/dev/null',
                       'systemctl restart strongswan && sleep 3 && swanctl --load-all | tail -3'], pause=4.0)
    await lines(r, WATCH.replace('SITE', n), 0.2)
    await terminal(r, ['nohup bash watch.sh >/dev/null 2>&1 &'], pause=2.0)
    r.mark(f'{n}-negociation-debut', accelere=3); await r.hold(25.0); r.mark(f'{n}-negociation-fin')
    await terminal(r, ['swanctl --list-sas | grep -E "ESTABLISHED|INSTALLED"', 'ip route show | grep 10.20.0.0'], pause=3.0)
    r.mark(f'{n}-tunnels'); await r.hold(3.5)

async def run(r):
    await conf(r, 'siege', '192.168.10.10', 30.0)
