"""Module 11 : un fichier statique sur web-01 (/static/logo.png) servi par nginx."""
from common import *
from m02f import terminal
from m07q import open_session

async def run(r):
    a = await open_session(r, 'web-01-TP-AC')
    await terminal(r, ['sudo -i'], pause=1.5)
    await terminal(r, ['mkdir -p /usr/share/nginx/html/static; echo "logo v1" > /usr/share/nginx/html/static/logo.png'], pause=2.0)
    await terminal(r, [r"sed -i '/location \/ {/i\  location /static/ { root /usr/share/nginx/html; default_type image/png; }' /etc/nginx/conf.d/web.conf"], pause=2.0)
    await terminal(r, ['nginx -t && systemctl reload nginx', 'curl -sk https://localhost/static/logo.png'], pause=4.0)
    r.mark('statique'); await r.hold(2.5)
