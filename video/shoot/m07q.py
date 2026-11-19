"""Module 7 : panne d'un tunnel du siege : les requetes echouent le temps que IKE detecte la panne, puis passent par le tunnel 2 ; on retablit le tunnel 1."""
from common import *
from m02f import terminal

LOOP = 'while true; do curl -s -m 1 --interface 192.168.10.10 http://10.20.1.10:8080/api/health >/dev/null && echo "$(date +%T) OK" || echo "$(date +%T) ECHEC"; sleep 0.5; done'

async def open_session(r, name):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5); await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile(name)).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    return new[0]

async def run(r):
    main = r.page
    a = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i'], pause=1.5)
    await terminal(r, ["printf 'charon {\n  retransmit_tries = 3\n  retransmit_timeout = 2.0\n}\n' > /etc/strongswan.d/tpac.conf", 'systemctl restart strongswan && sleep 4 && swanctl --load-all | tail -1'], pause=5.0)
    r.mark('reglage-debut', accelere=3); await r.hold(25.0); r.mark('reglage-fin')
    await terminal(r, ['swanctl --list-sas | grep -c ESTABLISHED'], pause=2.0)
    await terminal(r, [LOOP], pause=8.0)
    r.mark('boucle')
    await r.follow(main)
    b = await open_session(r, 'rtr-siege-TP-AC')
    await terminal(r, ['sudo -i', "E=$(grep -m1 remote_addrs /etc/swanctl/conf.d/siege.conf | awk '{print $3}'); echo tunnel 1 : $E"], pause=2.5)
    await terminal(r, ['iptables -I OUTPUT -d $E -j DROP; iptables -I INPUT -s $E -j DROP; date +%T'], pause=2.0)
    r.mark('panne')
    await r.follow(a); await r.hold(40.0)
    r.mark('echecs-puis-reprise')
    await r.follow(b)
    await terminal(r, ['ip route show | grep 10.20.0.0', 'iptables -D OUTPUT -d $E -j DROP; iptables -D INPUT -s $E -j DROP; swanctl --initiate --child siege-t1 >/dev/null; date +%T'], pause=2.5)
    r.mark('retablissement')
    await r.follow(a); await r.hold(20.0)
    await r.page.keyboard.press('Control+C'); await r.hold(1.0)
    await terminal(r, ['swanctl --list-sas | grep -E "^siege-t[12]:" | cut -c1-40'], pause=3.0)
    r.mark('fin'); await r.hold(2.0)
