import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dlib import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'images')


def base(title, sub):
    g = Diagram(title, sub)
    g.box(250, 130, 1100, 620, "vpc-prod-leman-TP-AC  •  10.20.0.0/22  •  eu-north-1 (AZ eu-north-1a)", C["vpc"], C["vpc_b"], lw=4, size=22)
    g.box(300, 200, 420, 260, "sub-public-1a-TP-AC", C["pub"], C["pub_b"], sub="10.20.0.0/26")
    g.box(850, 200, 420, 260, "sub-prive-1a-TP-AC", C["priv"], C["priv_b"], sub="10.20.1.0/26")
    g.node(510, 380, "web-01-TP-AC", "10.20.0.10", C["white"], C["pub_b"])
    g.node(1060, 380, "app-01-TP-AC", "10.20.1.10", C["white"], C["priv_b"])
    return g


# ---------- Module 1 ----------
g = base("Module 1 – VPC et sous-réseaux", "Plan d'adressage validé par l'architecte réseau – route locale uniquement")
g.box(300, 500, 420, 100, "Réservé BDD (non créé)", C["white"], C["grey"], sub="10.20.3.0/26", dash=True)
g.line((690, 380 - 0), (870 - 0, 380), C["ok"], 5, arrow=True)
g.line((590, 380), (975, 380), C["ok"], 5, arrow=True)
g.num(780, 350, 1)
g.label(780, 410, "ping 10.20.1.10 : OK (route locale)", C["ok"], 16, True)
g.line((510, 420), (510, 560), C["ko"], 5, dash=True, arrow=True)
g.label(510, 600, "② pas d'Internet : bloqué", C["ko"], 16, True)
g.legend([(C["ok"], "① liaison validée", False), (C["ko"], "② liaison bloquée", True), (C["vpc_b"], "VPC", False)])
g.save(os.path.join(OUT, 'm01-vpc.png'))

# ---------- Module 2 ----------
g = base("Module 2 – Routage : Internet Gateway et NAT", "rt-public : 0.0.0.0/0 → IGW   |   rt-prive : 0.0.0.0/0 → NAT")
g.node(800, 105, "Internet", None, C["onp"], C["onp_b"], w=200, h=44)
g.node(510, 175, "igw-prod-leman-TP-AC", None, C["white"], C["blue"], w=240, h=40)
g.node(700, 300, "nat-prod-leman-TP-AC", "EIP", C["white"], C["blue"], w=210, h=60)
g.line((800, 127), (560, 155), C["ok"], 5, arrow=True)
g.line((510, 195), (510, 350), C["ok"], 5, arrow=True)
g.num(480, 260, 1)
g.line((975, 380), (790, 320), C["ok"], 5, arrow=True)
g.line((700, 270), (560, 190), C["ok"], 4, arrow=True)
g.num(900, 330, 2)
g.label(1060, 520, "Test : route 0.0.0.0/0 retirée → ping 8.8.8.8 échoue (23 s)", C["ko"], 16, True)
g.label(1060, 550, "route rétablie → ping réussit", C["ok"], 16, True)
g.legend([(C["ok"], "flux validé", False), (C["blue"], "composants réseau", False)])
g.save(os.path.join(OUT, 'm02-routage.png'))

# ---------- Module 3 ----------
g = base("Module 3 – Security Groups et NACL", "sg-web → sg-app (8080)  |  nacl-public sans état (443 + éphémères)")
g.box(290, 170, 440, 300, "", C["white"], C["fw_b"], dash=True, lw=2)
g.label(500, 160, "NACL nacl-public-TP-AC (sous-réseau)", C["fw_b"], 15, True, bg=False)
g.node(510, 440, "sg-web-TP-AC", "443 ← 0.0.0.0/0 | 22 ← salle expl.", C["fw"], C["fw_b"], w=300, h=54)
g.node(1060, 440, "sg-app-TP-AC", "8080/22/ICMP ← sg-web", C["fw"], C["fw_b"], w=300, h=54)
g.line((665, 380), (905, 380), C["ok"], 5, arrow=True)
g.label(785, 350, "8080", C["ok"], 18, True)
g.label(510, 540, "Internet → web-01 : HTTPS 443 OK", C["ok"], 16, True)
g.label(510, 570, "Internet → app-01 : ping KO (pas d'IP publique, SG fermé)", C["ko"], 16, True)
g.legend([(C["ok"], "flux autorisé", False), (C["fw_b"], "SG / NACL", False)])
g.save(os.path.join(OUT, 'm03-securite.png'))

# ---------- Module 4 ----------
g = Diagram("Module 4 – AWS Network Firewall", "Chemin sortant : sub-prive → pare-feu (sub-fw) → NAT → Internet • retour symétrique")
g.box(250, 130, 1100, 620, "vpc-prod-leman-TP-AC  •  10.20.0.0/22", C["vpc"], C["vpc_b"], lw=4, size=22)
g.box(280, 200, 300, 180, "sub-prive-1a", C["priv"], C["priv_b"], sub="10.20.1.0/26")
g.node(430, 340, "app-01-TP-AC", "10.20.1.10", C["white"], C["priv_b"], w=190)
g.box(640, 200, 300, 180, "sub-fw-1a-TP-AC", C["fw"], C["fw_b"], sub="10.20.2.0/28")
g.node(790, 340, "nfw-prod-leman-TP-AC", "endpoint vpce", C["white"], C["fw_b"], w=240)
g.box(1000, 200, 320, 180, "sub-public-1a", C["pub"], C["pub_b"], sub="10.20.0.0/26")
g.node(1160, 340, "NAT + web-01", None, C["white"], C["pub_b"], w=200)
g.line((525, 340), (670, 340), C["ok"], 5, arrow=True); g.num(600, 310, 1)
g.line((910, 340), (1060, 340), C["ok"], 5, arrow=True); g.num(985, 310, 2)
g.node(1160, 120, "Internet", None, C["onp"], C["onp_b"], w=180, h=44)
g.line((1160, 180), (1160, 142), C["ok"], 5, arrow=True)
g.box(300, 450, 1000, 250, "Règles (ordre strict, drop_established + alert)", C["white"], C["fw_b"], lw=2, size=18)
g.d.text((320, 495), "1. pass ip 10.20.0.0/22 -> 10.20.0.0/22  (flux internes, modules 3, 5, 6)", font=f(17), fill=C["ink"])
g.d.text((320, 525), "2. ALLOWLIST domaines : .amazonlinux.com, .amazonaws.com  (dépôts de mises à jour + SSM)", font=f(17), fill=C["ink"])
g.d.text((320, 555), "3. défaut : drop + alerte → CloudWatch Logs /leman/nfw-alert-TP-AC", font=f(17), fill=C["ink"])
g.d.text((320, 600), "Tables : rt-prive 0.0.0.0/0 → vpce | rt-fw 0.0.0.0/0 → NAT | rt-public 10.20.1.0/26 → vpce (retour)", font=f(17), fill=C["mute"])
g.legend([(C["ok"], "flux autorisé", False), (C["fw_b"], "pare-feu", False)])
g.save(os.path.join(OUT, 'm04-firewall.png'))
