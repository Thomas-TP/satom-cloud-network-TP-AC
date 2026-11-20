"""Publie les notes de docs/hackmd/ sur HackMD par l'API (jeton dans la variable d'environnement HACKMD_TOKEN, jamais dans un fichier).
Usage : HACKMD_TOKEN=... python scripts/publish_hackmd.py   -> cree les notes (ou met a jour celles de docs/hackmd/notes.json) et remplace les liens entre notes."""
import json, os, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = os.path.join(ROOT, 'docs', 'hackmd'); MAP = os.path.join(H, 'notes.json')
TOKEN = os.environ['HACKMD_TOKEN']
def api(method, path, data=None):
    req = urllib.request.Request('https://api.hackmd.io/v1' + path, method=method, data=json.dumps(data).encode() if data is not None else None,
                                 headers={'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json', 'User-Agent': 'tp-ac-docs'})
    with urllib.request.urlopen(req, timeout=120) as r:
        b = r.read(); return json.loads(b) if b else {}
KEYS = ['sommaire', 'partie1', 'partie2', 'partie3']
TITLES = {'sommaire': 'Satom Cloud Network (TP-AC) : sommaire et vidéo', 'partie1': 'Satom Cloud Network (TP-AC) : partie 1, modules 0 à 4', 'partie2': 'Satom Cloud Network (TP-AC) : partie 2, modules 5 à 8', 'partie3': 'Satom Cloud Network (TP-AC) : partie 3, modules 9 à 13'}
notes = json.load(open(MAP)) if os.path.exists(MAP) else {}
text = {k: open(os.path.join(H, k + '.md'), encoding='utf-8').read() for k in KEYS}
for k in KEYS:
    if k not in notes:
        r = api('POST', '/notes', {'title': TITLES[k], 'content': text[k].replace('{{URL_', '(#'), 'readPermission': 'guest', 'writePermission': 'owner', 'commentPermission': 'disabled'})
        notes[k] = {'id': r['id'], 'url': r.get('publishLink') or ('https://hackmd.io/' + r['id'])}
        print('cree', k, notes[k]['url']); json.dump(notes, open(MAP, 'w'), indent=1)
for k in KEYS:
    t = text[k]
    for kk in KEYS: t = t.replace('{{URL_' + kk + '}}', notes[kk]['url'])
    api('PATCH', '/notes/' + notes[k]['id'], {'content': t, 'readPermission': 'guest', 'writePermission': 'owner'})
    print('contenu', k, len(t))
