"""Importe les captures reelles de la console AWS (Chrome, 1568x633) dans captures/mNN/00-console-*.png.
L'identifiant de compte AWS est masque (rectangles) sur les ecrans qui l'affichent."""
import os, glob
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.expanduser('~'), '.claude', 'projects', 'C--Perso-AWS', '*', 'tool-results')   # toutes les sessions
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# (module, nom, identifiant du fichier source, rectangles a masquer)
SHOTS = [
 ('m01', 'vpcs', '1794835009895-g8c52f', []),
 ('m01', 'sous-reseaux', '1794835088140-dqe6eu', []),
 ('m01', 'instances', '1794835246547-sakp9j', []),
 ('m02', 'tables-routage', '1794835131887-2gzxv6', [(1128, 280, 1232, 522)]),
 ('m02', 'passerelles-internet', '1794835131887-qs2mqm', [(960, 274, 1052, 386)]),
 ('m02', 'passerelle-nat', '1794835131887-aqle74', []),
 ('m03', 'groupes-securite', '1794835192249-aen3k6', [(1450, 204, 1546, 336)]),
 ('m03', 'nacl', '1794835192249-78m8d3', []),
 ('m04', 'pare-feux', '1794904312433-efb2mm', [(240, 292, 1548, 322)]),
 ('m04', 'pare-feu-details', '1794904325479-0qnq5i', [(700, 395, 1080, 428)]),
 ('m04', 'paquets-bloques', '1794904345738-qgx0e7', []),
 ('m04', 'politique-regles', '1794904374724-8mgpgg', []),
 ('m06', 'passerelle-transit', '1794911892646-0aebux', [(790, 218, 885, 260)]),
 ('m06', 'attachements', '1794911892646-qfnps0', [(1290, 4, 1558, 40)]),
 ('m06', 'tables-tgw', '1794911892646-0ndl7z', [(1290, 4, 1558, 40)]),
 ('m06', 'routes-tgw-prod', '1794912004841-ewzefx', [(1290, 4, 1558, 40)]),
 ('m07', 'connexions-vpn', '1794911916777-egl6rd', [(1290, 4, 1558, 40)]),
 ('m07', 'tunnels-vpn', '1794911940223-a5zd2c', [(1290, 4, 1558, 40)]),
 ('m08', 'dx-gateway', '1794912039308-kxwimo', [(1290, 4, 1558, 40), (237, 88, 1548, 142), (687, 308, 780, 325), (715, 530, 805, 548)]),
 ('m05', 'peering', '1794835192249-dfv47j', []),
 ('m09', 'alb', '1794835246547-xzo4au', []),
 ('m09', 'groupes-cibles', '1794835246547-8mun7r', []),
 ('m10', 'zones', '1794835246547-6uu185', []),
 ('m10', 'enregistrements', '1794835405216-zjun3t', []),
 ('m11', 'cloudfront', '1794835310966-jn6847', []),
 ('m12', 'alarme', '1794835310967-y3ju6h', []),
 ('m12', 'tableau-de-bord', '1794835358916-csul6f', []),
 ('m13', 'piles-cloudformation', '1794835358916-c3rzd0', []),
 ('m07', 'secret-vpn', '1794835358916-reih21', []),
 ('m00', 'credits', '1794838004654-rucvo8', []),
 ('m00', 'quetes-credits', '1794837985356-ggoegj', []),
 ('m00', 'budgets', '1794837985356-516oj5', []),
]
n = 0
for mod, name, ident, rects in SHOTS:
    hits = glob.glob(os.path.join(SRC, f'mcp-claude-in-chrome-blob-{ident}.jpg'))
    if not hits:
        print('introuvable :', ident); continue
    im = Image.open(hits[0]).convert('RGB'); d = ImageDraw.Draw(im)
    for r in rects:
        d.rectangle(r, fill=(40, 44, 52))
        d.text((r[0] + 4, (r[1] + r[3]) // 2), 'masque', fill=(150, 156, 166))
    out_dir = os.path.join(ROOT, 'captures', mod); os.makedirs(out_dir, exist_ok=True)
    im.save(os.path.join(out_dir, f'00-console-{name}.png')); n += 1
print('captures console importees :', n)

