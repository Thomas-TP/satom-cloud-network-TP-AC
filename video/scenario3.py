# Version courte (7 a 8 min) : une preuve par module, memes enregistrements reels que la version complete.
import re
import scenario2 as _full
from scenario2 import say, M
G = lambda sid, raw, text, **kw: dict(kind='gui', id=sid + '-c', raw=f'video/raw/{raw}.mp4', text=text, **kw)
S = [
 dict(kind='card', id='00-titre', title='Satom Cloud Network', sub='Groupe Léman Finance SA  •  équipe TP-AC  •  version courte', num=None, dur=3.0),
 dict(kind='diagram', id='00-intro-c', img='docs/images/global.png', focus=(0.5, 0.5, 1.0, 1.06),
      text="Nous sommes Thomas et Abderahmane. Voici, en huit minutes, le réseau du groupe Léman Finance construit à la main dans la console A-W-S : une preuve par module. La version complète montre toutes les étapes."),
 M(0, 'Module 0 – Cadrage', 'budget et nommage'),
 G('m00', 'm00', "Avant tout, un budget de cent dollars avec une alerte à huitante pour cent. Chaque ressource porte le suffixe T-P-A-C et trois étiquettes.", max_speed=8),
 M(1, 'Module 1 – Réseaux', 'V-P-C et sous-réseaux'),
 G('m01a', 'm01a', "Le V-P-C de production en dix point vingt point zéro barre vingt-deux, mille vingt-quatre adresses, étiqueté et prêt à recevoir ses sous-réseaux.", max_speed=4),
 M(2, 'Module 2 – Routage', 'passerelle Internet et NAT'),
 G('m02g', 'm02g', "La preuve du routage : une boucle interroge Internet depuis le serveur privé. Nous retirons la route par défaut, les requêtes échouent, nous la remettons et tout repart.", max_speed=5),
 M(3, 'Module 3 – Sécurité', 'Security Groups et NACL'),
 G('m03f', 'm03f', "Un Security Group retient l'état des connexions. Nous retirons le port huit mille huitante : l'application ne répond plus, c'est donc bien lui qui bloquait. Nous le remettons.", max_speed=5),
]
S += [
 M(4, 'Module 4 – Pare-feu', 'AWS Network Firewall'),
 G('m04i', 'm04i', "Le pare-feu ne laisse passer que deux domaines : le dépôt Amazon Linux répond, example point com et Wikipédia expirent.", max_speed=5),
 M(5, 'Module 5 – Appairage', 'VPC de développement'),
 G('m05g', 'm05g', "Depuis le développement, l'A-P-I de l'application répond sur le port huit mille huitante. Le ping et le port vingt-deux restent refusés.", max_speed=4),
 M(6, 'Module 6 – Transit Gateway', 'tables prod et dev'),
 G('m06h', 'm06h', "Le Transit Gué-te-oué remplace l'appairage. Nous retirons une propagation : les requêtes échouent. Nous la remettons : tout repart.", max_speed=5),
 M(7, 'Module 7 – VPN site à site', 'siège et agence'),
 G('m07q', 'm07q', "Quatre tunnels I-P-sec vers le Transit Gué-te-oué. Quand nous coupons le premier tunnel du siège, les requêtes échouent une trentaine de secondes, puis passent par le second : ce n'est pas une bascule sans coupure.", max_speed=5),
 M(8, 'Module 8 – Direct Connect', 'passerelle, G-R-E et B-G-P'),
 G('m08m', 'm08m', "La liaison dédiée est simulée par un tunnel G-R-E avec B-G-P. Quand elle tombe, B-G-P bascule sur le chemin du V-P-N en quelques secondes, puis revient.", max_speed=5),
 M(9, 'Module 9 – Load balancer', 'ALB, HTTPS et groupes cibles'),
 G('m09h', 'm09h', "L'équilibreur de charge sert le portail en H-T-T-P-S. Nous arrêtons nginx : la cible devient non saine et l'équilibreur répond par une erreur cinq cent deux, puis tout redevient sain.", max_speed=14),
 M(10, 'Module 10 – Route 53', 'zones, santé et basculement'),
 G('m10g', 'm10g', "Quand le site tombe, la surveillance de l'état fait basculer le D-N-S vers l'adresse de secours, puis revenir vers l'équilibreur quand il est rétabli.", max_speed=14),
 M(11, 'Module 11 – CloudFront', 'cache et invalidation'),
 G('m11g', 'm11g', "Le fichier statique : Miss, puis Hit. L'A-P-I n'est jamais mise en cache. Une invalidation remplace l'ancienne version, et l'équilibreur n'est plus joignable que par Cloud-Front.", max_speed=5),
 M(12, 'Module 12 – Surveillance', 'alarme et journaux de flux'),
 G('m12h', 'm12h', "Nous provoquons des erreurs cinq cent deux : l'alarme passe en alarme et la file S-Q-S reçoit la notification.", max_speed=30),
 M(13, 'Module 13 – CloudFormation', 'pile et dérive'),
 G('m13d', 'm13d', "Une règle ajoutée à la main sur la pile est détectée comme une dérive, avec le détail de la différence. Retirée, la pile revient en phase.", max_speed=6),
 dict(kind='diagram', id='99-fin-c', img='docs/images/global.png', focus=(0.5, 0.5, 1.06, 1.0),
      text="Voilà le réseau complet. Les sites et la liaison Direct Connect sont simulés, le domaine est fictif : tout est dit dans le dossier. Merci de nous avoir suivis."),
]
ABDER = ('m04', 'm05', 'm06', 'm09', 'm10', 'm11', 'm12', 'm13')
for s in S:
    if 'text' in s:
        s['say'] = say(s['text']); s['voice'] = 'abder' if s['id'][:3] in ABDER else 'thomas'
