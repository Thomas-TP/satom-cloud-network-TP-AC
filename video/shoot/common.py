"""Gestes communs aux scenes de tournage."""
import sys
sys.path.insert(0, r'C:\Perso\AWS\video\rig')
from rig import *

REGION = 'eu-north-1'
def vpc_url(frag): return f'https://{REGION}.console.aws.amazon.com/vpcconsole/home?region={REGION}#{frag}'
def ec2_url(frag): return f'https://{REGION}.console.aws.amazon.com/ec2/home?region={REGION}#{frag}'

async def _dd(r, on):
    css = "[class*=awsui_dropdown-content-wrapper]{visibility:hidden !important}"
    js = "(on) => { const id='__nodd'; let s=document.getElementById(id); if (on) { if(!s){ s=document.createElement('style'); s.id=id; s.textContent=%r; document.documentElement.appendChild(s);} } else if (s) s.remove(); }" % css
    for f in r.page.frames:
        try: await f.evaluate(js, on)
        except Exception: pass

async def tags(r, env, start=0, add='Ajouter une balise', which=0, kp='Entrer la clé', vp='Entrer la valeur', extra=()):
    """Ajoute les trois balises du projet dans un formulaire de creation. kp/vp : placeholder ou aria-label des champs cle / valeur."""
    await _dd(r, True)
    key = lambda f, i: (f.locator('input[aria-label="%s"]' % kp[1:]) if kp.startswith('@') else f.get_by_placeholder(kp)).nth(i)
    val = lambda f, i: (f.locator('input[aria-label="%s"]' % vp[1:]) if vp.startswith('@') else f.get_by_placeholder(vp)).nth(i)
    for i, (k, v) in enumerate(list(extra) + [('Projet', 'SatomCloudNetwork'), ('Equipe', 'TP-AC'), ('Environnement', env)], start):
        await r.click(lambda f: f.get_by_role('button', name=add).nth(which))
        await r.type(lambda f, i=i: key(f, i), k, delay=40); await r.press('Tab', 0.2)
        await r.type(lambda f, i=i: val(f, i), v, delay=40); await r.press('Tab', 0.2)
    await _dd(r, False)
    # supprime une eventuelle ligne de balise vide restee en fin de liste (bouton 'Supprimer' de la meme ligne)
    try:
        for f in r.page.frames:
            keys = f.locator('input[placeholder="Entrer la clé"]')
            n = await keys.count()
            for k in range(n - 1, -1, -1):
                if n and not await keys.nth(k).input_value():
                    row = keys.nth(k).locator('xpath=ancestor::*[.//button[starts-with(normalize-space(.), "Supprimer")]][1]')
                    await r.click(row.get_by_role('button', name=re.compile('^Supprimer')).first)
    except Exception: pass

async def settle(r, sec=1.5): await r.hold(sec)

import subprocess
def nat_id():
    """Identifiant de la passerelle NAT disponible (les NAT supprimees restent quelque temps dans les listes de la console)."""
    return subprocess.run(['aws', 'ec2', 'describe-nat-gateways', '--filter', 'Name=tag:Name,Values=nat-prod-leman-TP-AC', 'Name=state,Values=available,pending', '--query', 'NatGateways[0].NatGatewayId', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

# ---- cles pre-partagees (jamais affichees ni ecrites dans le depot : fichier dans le profil Chrome ignore par git)
import json as _json, os as _os, secrets as _secrets, string as _string
PSK_FILE = r'C:\Perso\AWS\video\rig\profile\psk.json'
def psk():
    if not _os.path.exists(PSK_FILE):
        al = _string.ascii_letters + _string.digits
        mk = lambda: _secrets.choice(_string.ascii_letters) + ''.join(_secrets.choice(al) for _ in range(31))
        _json.dump({k: mk() for k in ('siege1', 'siege2', 'agence1', 'agence2')}, open(PSK_FILE, 'w'))
    return _json.load(open(PSK_FILE))

async def mask(loc_fn, r):
    """Affiche des pastilles a la place des caracteres d'un champ (le secret reste invisible a l'ecran)."""
    for f in r.page.frames:
        try:
            loc = loc_fn(f)
            if await loc.count(): await loc.first.evaluate("e => { e.style.webkitTextSecurity = 'disc'; }")
        except Exception: pass

async def fill(r, fn, text, hold=0.8):
    """Clic (curseur visible) puis saisie instantanee : pour les champs CIDR de l'assistant VPC, qui perdent le focus a chaque frappe."""
    await r.click(fn)
    loc = await r._resolve(fn)
    await loc.fill(text); await r.hold(hold)

def eip_ip(n):
    return subprocess.run(['aws', 'ec2', 'describe-addresses', '--filters', f'Name=tag:Name,Values=eip-rtr-{n}-TP-AC', '--query', 'Addresses[0].PublicIp', '--output', 'text', '--profile', 'TP-AC', '--region', REGION], capture_output=True, text=True).stdout.strip()

def _ids():
    try: return _json.load(open('C:/Perso/AWS/video/rig/profile/ids.json'))
    except Exception: return {}

def zone_id(name, private=None):
    if ('zone_' + name) in _ids():
        try: return _zone_id(name)
        except Exception: return _ids()['zone_' + name]
    return _zone_id(name)

def _zone_id(name, private=None):
    """Identifiant de NOTRE zone (etiquette Equipe=TP-AC) : d'autres eleves ont des zones du meme nom."""
    import json as J
    zs = J.loads(subprocess.run(['aws', 'route53', 'list-hosted-zones', '--output', 'json', '--profile', 'TP-AC'], capture_output=True, text=True).stdout)['HostedZones']
    for z in zs:
        if z['Name'] != name: continue
        zid = z['Id'].split('/')[-1]
        tg = J.loads(subprocess.run(['aws', 'route53', 'list-tags-for-resource', '--resource-type', 'hostedzone', '--resource-id', zid, '--output', 'json', '--profile', 'TP-AC'], capture_output=True, text=True).stdout)
        if any(t['Key'] == 'Equipe' and t['Value'] == 'TP-AC' for t in tg.get('ResourceTagSet', {}).get('Tags', [])): return zid
    raise RuntimeError('zone introuvable : ' + name)

def r53_url(frag): return 'https://us-east-1.console.aws.amazon.com/route53/v2/hostedzones?region=eu-north-1#' + frag
