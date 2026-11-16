"""Monte la video de rendu : cartes de titre + schemas + captures de preuve -> video/satom-cloud-network-TP-AC.mp4 (ffmpeg)."""
import os, glob, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(ROOT, 'video'); TMP = os.path.join(OUT_DIR, '_frames')
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
W, H = 1920, 1080
FB = r"C:\Windows\Fonts\segoeuib.ttf"; FR = r"C:\Windows\Fonts\segoeui.ttf"
TITLES = {
 'm00': 'Cadrage, mandat et equipe', 'm01': 'VPC et sous-reseaux', 'm02': 'Routage : IGW et NAT', 'm03': 'Security Groups et NACL',
 'm04': 'Network Firewall (bloque par SCP)', 'm05': 'VPC Peering', 'm06': 'Transit Gateway (bloque par SCP)',
 'm07': 'VPN site a site (simulation IPsec)', 'm08': 'Direct Connect (simulation GRE + BGP)', 'm09': 'Elastic Load Balancing',
 'm10': 'Route 53', 'm11': 'CloudFront', 'm12': 'CloudWatch et Flow Logs', 'm13': 'CloudFormation'}
DIAG = {'m01': 'm01-vpc', 'm02': 'm02-routage', 'm03': 'm03-securite', 'm04': 'm04-firewall', 'm05': 'm05-peering', 'm06': 'm06-tgw',
        'm07': 'm07-vpn', 'm08': 'm08-dx', 'm09': 'm09-alb', 'm10': 'm10-route53', 'm11': 'm11-cloudfront', 'm12': 'm12-monitoring', 'm13': 'm13-cloudformation'}
frames = []  # (path, seconds)


def card(title, sub, name, bg=(15, 23, 42)):
    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
    d.text((W // 2, H // 2 - 40), title, font=ImageFont.truetype(FB, 72), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, H // 2 + 50), sub, font=ImageFont.truetype(FR, 36), fill=(148, 163, 184), anchor='mm')
    d.text((W // 2, H - 60), 'GIT \u2013 Satom  |  Equipe TP-AC  |  Groupe L\u00e9man Finance SA', font=ImageFont.truetype(FR, 28), fill=(100, 116, 139), anchor='mm')
    p = os.path.join(TMP, name); im.save(p); return p


def fit(path, name, bg=(255, 255, 255)):
    im = Image.open(path).convert('RGB'); r = min(W / im.width, H / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    canvas = Image.new('RGB', (W, H), bg); canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    p = os.path.join(TMP, name); canvas.save(p); return p


n = 0
def add(p, s):
    global n; frames.append((p, s)); n += 1

add(card('Satom Cloud Network', 'Groupe L\u00e9man Finance SA \u2013 R\u00e9alisation de l\'\u00e9quipe TP-AC', f'{n:03d}.png'), 5)
add(fit(os.path.join(ROOT, 'docs', 'images', 'global.png'), f'{n:03d}.png'), 9)
for m in sorted(TITLES):
    add(card(f'Module {int(m[1:])}', TITLES[m], f'{n:03d}.png', bg=(30, 41, 59)), 3)
    if m in DIAG:
        add(fit(os.path.join(ROOT, 'docs', 'images', DIAG[m] + '.png'), f'{n:03d}.png'), 7)
    for c in sorted(glob.glob(os.path.join(ROOT, 'captures', m, '*.png'))):
        if '99-preuves' in c: continue
        add(fit(c, f'{n:03d}.png', bg=(13, 17, 23)), 4)
    for c in sorted(glob.glob(os.path.join(ROOT, 'captures', m, '99-preuves*.png'))):
        add(fit(c, f'{n:03d}.png', bg=(13, 17, 23)), 8)
add(card('Merci', 'Code, scripts, templates et preuves : d\u00e9p\u00f4t GitHub TP-AC-satom-cloud-network', f'{n:03d}.png'), 5)

lst = os.path.join(TMP, 'list.txt')
with open(lst, 'w', encoding='utf-8') as f:
    for p, s in frames:
        f.write(f"file '{os.path.basename(p)}'\nduration {s}\n")
    f.write(f"file '{os.path.basename(frames[-1][0])}'\n")
out = os.path.join(OUT_DIR, 'satom-cloud-network-TP-AC.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-vf', 'fps=24,format=yuv420p', '-c:v', 'libx264', '-crf', '23', os.path.abspath(out)], cwd=TMP, check=True)
shutil.rmtree(TMP, ignore_errors=True)
print('video :', out, '| images :', len(frames), '| duree ~', sum(s for _, s in frames), 's')
