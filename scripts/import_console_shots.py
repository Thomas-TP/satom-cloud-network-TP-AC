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
 ('m04', 'pare-feux', '1794943584907-a39rca', [(1290, 4, 1558, 40)]),
 ('m04', 'pare-feu-details', '1794943597288-mzwaqo', [(1290, 4, 1558, 40), (690, 396, 1090, 432)]),
 ('m04', 'paquets-bloques', '1794943625400-ldv22c', [(1290, 4, 1558, 40)]),
 ('m04', 'politique-regles', '1794943625400-3xycbz', [(1290, 4, 1558, 40)]),
 ('m06', 'passerelle-transit', '1794943353170-mobsmj', [(1290, 4, 1558, 40), (800, 258, 890, 277)]),
 ('m06', 'attachements', '1794943447840-nx8m1i', [(1290, 4, 1558, 40)]),
 ('m06', 'tables-tgw', '1794943408043-ur9saq', [(1290, 4, 1558, 40)]),
 ('m06', 'routes-tgw-prod', '1794943503775-2t8qwg', [(1290, 4, 1558, 40)]),
 ('m07', 'connexions-vpn', '1794943408043-umy7n9', [(1290, 4, 1558, 40)]),
 ('m07', 'tunnels-vpn', '1794943478744-nb5pi6', [(1290, 4, 1558, 40)]),
 ('m08', 'dx-gateway', '1794943556823-uc3t6u', [(1290, 4, 1558, 40), (237, 88, 1548, 142), (691, 308, 775, 325), (718, 530, 805, 548)]),
 ('m05', 'peering', '1794835192249-dfv47j', []),
 ('m09', 'alb', '1794835246547-xzo4au', []),
 ('m09', 'groupes-cibles', '1794835246547-8mun7r', []),
 ('m10', 'zones', '1794835246547-6uu185', []),
 ('m10', 'enregistrements', '1794835405216-zjun3t', []),
 ('m11', 'cloudfront', '1794835310966-jn6847', []),
 ('m12', 'alarme', '1794835310967-y3ju6h', []),
 ('m12', 'tableau-de-bord', '1794835358916-csul6f', []),
 ('m13', 'piles-cloudformation', '1794943659762-ywebo6', [(1290, 4, 1568, 40)]),
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

