"""Module 3 : session sur web-01 - web et app se parlent (ping, 8080), puis nginx en HTTPS avec un certificat auto-signe."""
from common import *
from m02f import terminal

async def run(r):
    await r.goto('https://eu-north-1.console.aws.amazon.com/systems-manager/session-manager/start-session?region=eu-north-1', wait=5)
    await r.hold(1.0)
    await r.click(lambda f: f.get_by_role('row', name=re.compile('web-01-TP-AC')).get_by_role('radio')); await r.hold(1.0)
    before = set(r.ctx.pages)
    await r.click(btn('Démarrer la session')); await r.hold(3.0)
    new = [p for p in r.ctx.pages if p not in before]
    await r.follow(new[0]); await r.hold(7.0)
    await r.click_xy(900, 500)
    r.mark('terminal')
    await terminal(r, ['ping -c 3 10.20.1.10', 'curl -s http://10.20.1.10:8080/api/health; echo'], pause=5.0)
    r.mark('web-vers-app')
    await terminal(r, ['sudo dnf -y install nginx'], pause=1.0)
    r.mark('install-debut', accelere=4)
    await r.hold(35.0)
    r.mark('install-fin')
    await terminal(r, ['sudo mkdir -p /etc/pki/nginx && sudo openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout /etc/pki/nginx/web.key -out /etc/pki/nginx/web.crt -subj /CN=portefeuilles.leman-finance.example 2>/dev/null && ls /etc/pki/nginx'], pause=4.0)
    for line in ["sudo tee /etc/nginx/conf.d/web.conf <<'EOF'", 'server {', '  listen 443 ssl;', '  ssl_certificate /etc/pki/nginx/web.crt;', '  ssl_certificate_key /etc/pki/nginx/web.key;', '  location / { return 200 "web-01 TP-AC"; }', '  location /api/ { proxy_pass http://10.20.1.10:8080; }', '}', 'EOF']:
        await terminal(r, [line], pause=0.35)
    r.mark('conf')
    await terminal(r, ['sudo nginx -t && sudo systemctl enable --now nginx', 'curl -sk https://localhost/; echo', 'curl -sk https://localhost/api/health; echo'], pause=4.0)
    r.mark('nginx'); await r.hold(3.0)
