# Scenario de la video "Satom Cloud Network - TP-AC" : une liste de scenes.
# kind : 'card' (titre, sans voix) | 'diagram' (docs/images) | 'shot' (capture console reelle) | 'clip' (enregistrement reel du terminal)
# text : narration affichee en sous-titres. say = texte envoye a la synthese vocale (sigles epeles, nombres suisses).
import re

# prononciation : le texte affiche reste propre, la synthese recoit une version epelee
PRON = [(r'\bTP-AC\b', 'T-P-A-C'),
        (r'\bVPC\b', 'V-P-C'),
        (r'\bNAT\b', 'nat'),
        (r'\bBGP\b', 'B-G-P'),
        (r'\bGRE\b', 'G-R-E'),
        (r'\bSNS\b', 'S-N-S'),
        (r'\bASN\b', 'A-S-N'),
        (r'\bDNS\b', 'D-N-S'),
        (r'\bAPI\b', 'A-P-I'),
        (r'\bAWS\b', 'A-W-S'),
        (r'\bIPsec\b', 'I-P-sec'),
        (r'\bstrongSwan\b', 'strong-Swan'),
        (r'\bnginx\b', 'engine-x'),
        (r'\bVPN\b', 'V-P-N'),
        (r'\bCloudFront\b', 'Cloud-Front'),
        (r'\bCloudWatch\b', 'Cloud-Watch'),
        (r'\bCloudFormation\b', 'Cloud-Formation'),
        (r'\bGitHub\b', 'Guite-Hub'),
        (r'\bTransit Gateway\b', 'Transit Gué-te-oué'),
        (r'\bload balancer\b', 'lode balanceur'),
        (r'\bpeering\b', 'pi-ring'),
        (r'\bpoint com\b', 'point comme'),
        (r'\b8080\b', 'huit mille huitante'),
        (r'\b22\b', 'vingt-deux'),
        (r'\b64513\b', 'soixante-quatre mille cinq cent treize'),
        (r'Route 53', 'Route cinquante-trois'),
        (r'80\s%', 'huitante pour cent'),
        (r'100 dollars', 'cent dollars')]
def say(t):
    for a, b in PRON: t = re.sub(a, b, t)
    return t

M = lambda n, title, sub: dict(kind='card', id=f'm{n:02d}-card', title=title, sub=sub, num=n)
S = [
 dict(kind='card', id='00-titre', title='Satom Cloud Network', sub='Groupe Léman Finance SA  •  équipe TP-AC  •  Thomas et Abderahmane', num=None, dur=3.2),
 dict(kind='diagram', id='00-intro', img='docs/images/global.png', focus=(0.5, 0.5, 1.0, 1.06),
      text="Bonjour, nous sommes Thomas et Abderahmane. Pour le groupe Léman Finance, nous avons construit sur AWS un réseau complet qui relie un siège, une agence et le cloud. Voici, étape par étape, ce que nous avons fait, et comment nous l'avons vérifié."),

 M(0, 'Module 0 – Cadrage', 'plan d\'adressage, nommage, budget'),
 dict(kind='shot', id='m00a', img='captures/m00/00-console-budgets.png', focus=(0.5, 0.3, 1.0, 1.15),
      text="Module zéro, le cadrage. Chaque ressource porte le suffixe TP-AC et trois étiquettes. Un budget envoie une alerte à 80 % de nos 100 dollars de crédit."),
 dict(kind='clip', id='m00b', clip='video/clips/m00.mp4',
      text="Avant de construire, nous écrivons le plan d'adressage. Ensuite, toutes nos ressources se retrouvent par leur étiquette."),

 M(1, 'Module 1 – Réseaux', 'VPC prod et dev, sous-réseaux'),
 dict(kind='diagram', id='m01a', img='docs/images/m01-vpc.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module un, les réseaux. Un VPC de production et un VPC de développement, avec des sous-réseaux publics et privés sur deux zones de disponibilité."),
 dict(kind='shot', id='m01b', img='captures/m01/00-console-sous-reseaux.png', focus=(0.45, 0.4, 1.0, 1.15),
      text="Dans la console, chaque sous-réseau a sa plage d'adresses, sa zone, et son nom en TP-AC."),
 dict(kind='clip', id='m01c', clip='video/clips/m01.mp4',
      text="La ligne de commande donne le même résultat, filtré sur l'étiquette de notre équipe."),

 M(2, 'Module 2 – Routage', 'passerelle Internet et NAT'),
 dict(kind='diagram', id='m02a', img='docs/images/m02-routage.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module deux, le routage. La passerelle Internet sert le sous-réseau public, et la passerelle NAT permet aux serveurs privés de sortir, sans être joignables de l'extérieur."),
 dict(kind='shot', id='m02b', img='captures/m02/00-console-tables-routage.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Chaque sous-réseau a sa table de routage : la route par défaut vise soit Internet, soit la NAT."),
 dict(kind='clip', id='m02c', clip='video/clips/m02.mp4',
      text="La preuve : app-01 n'a pas d'adresse publique, et Internet la voit avec l'adresse de la NAT."),

 M(3, 'Module 3 – Sécurité', 'Security Groups et NACL'),
 dict(kind='diagram', id='m03a', img='docs/images/m03-securite.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module trois, la sécurité. Les Security Groups retiennent l'état des connexions, et les listes de contrôle d'accès réseau filtrent dans les deux sens."),
 dict(kind='shot', id='m03b', img='captures/m03/00-console-groupes-securite.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Chaque rôle a son groupe : web, application et load balancer, avec le minimum de règles."),
 dict(kind='clip', id='m03c', clip='video/clips/m03.mp4',
      text="Depuis dev-01, le port 8080 répond, et le port 22 reste fermé."),

 M(4, 'Module 4 – Network Firewall', 'filtrage des domaines sortants'),
 dict(kind='diagram', id='m04a', img='docs/images/m04-firewall.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module quatre, le pare-feu managé. Il filtre ce qui sort du sous-réseau privé : seuls les dépôts de mises à jour passent, le reste est bloqué et journalisé."),
 dict(kind='shot', id='m04b', img='captures/m04/00-console-paquets-bloques.png', focus=(0.65, 0.5, 1.0, 1.12),
      text="Deux groupes de règles en ordre strict, et le graphique montre les paquets bloqués par le moteur à états."),
 dict(kind='clip', id='m04c', clip='video/clips/m04.mp4',
      text="Les domaines autorisés répondent, example point com expire, et l'alerte arrive dans CloudWatch. Ce pare-feu coûte à l'heure : nous l'avons supprimé après les tests."),

 M(5, 'Module 5 – Peering', 'prod et dev, non transitif'),
 dict(kind='diagram', id='m05a', img='docs/images/m05-peering.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module cinq, le peering. Il relie la production et le développement, avec le seul port 8080 ouvert. Il n'est pas transitif, et deux réseaux qui se chevauchent sont refusés."),
 dict(kind='shot', id='m05b', img='captures/m05/00-console-peering.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Voici la connexion, active. Le sujet demande de la supprimer au module suivant, ce que nous avons fait."),
 dict(kind='clip', id='m05c', clip='video/clips/m05.mp4',
      text="Le journal des tests : la requête passe, le chevauchement échoue, et la transitivité est refusée."),

 M(6, 'Module 6 – Transit Gateway', 'un point central, une table par environnement'),
 dict(kind='diagram', id='m06a', img='docs/images/m06-tgw.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module six, le Transit Gateway. Il remplace le peering : un seul attachement par réseau, et une table de routage par environnement."),
 dict(kind='shot', id='m06b', img='captures/m06/00-console-attachements.png', focus=(0.5, 0.4, 1.0, 1.15),
      text="Les attachements de la production et du développement sont disponibles. Celui du Direct Connect s'y ajoutera au module huit."),
 dict(kind='clip', id='m06c', clip='video/clips/m06.mp4',
      text="Les routes sont apprises par propagation, et dev-01 joint toujours app-01. Si on retire la propagation, la réponse n'a plus de chemin, et le test échoue."),

 M(7, 'Module 7 – VPN site à site', 'siège et agence, deux tunnels chacun'),
 dict(kind='diagram', id='m07a', img='docs/images/m07-vpn.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module sept, le VPN site à site. Le siège et l'agence ont chacun deux tunnels chiffrés vers AWS. Les sites sont simulés par des routeurs strongSwan, mais le VPN est bien celui d'AWS."),
 dict(kind='shot', id='m07b', img='captures/m07/00-console-tunnels-vpn.png', focus=(0.5, 0.75, 1.0, 1.15),
      text="Les quatre tunnels sont à l'état haut. Les routes des sites sont dans la table de production, et aucune n'arrive dans celle du développement."),
 dict(kind='clip', id='m07c', clip='video/clips/m07.mp4',
      text="Le siège joint app-01. Quand nous coupons le premier tunnel, le trafic reprend sur le second après une vingtaine de secondes, le temps qu'AWS détecte la panne."),

 M(8, 'Module 8 – Direct Connect', 'passerelle réelle, liaison simulée'),
 dict(kind='diagram', id='m08a', img='docs/images/m08-dx.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module huit, Direct Connect. La passerelle est réelle, et associée au Transit Gateway. Comme nous ne commandons pas de fibre, la liaison est simulée par un tunnel GRE et du BGP."),
 dict(kind='shot', id='m08b', img='captures/m08/00-console-dx-gateway.png', focus=(0.5, 0.55, 1.0, 1.15),
      text="La passerelle porte l'ASN 64513, et les deux préfixes autorisés."),
 dict(kind='clip', id='m08c', clip='video/clips/m08.mp4',
      text="Le BGP préfère le chemin Direct Connect. Si on le coupe, le trafic passe par le VPN en huit secondes environ, puis revient tout seul."),

 M(9, 'Module 9 – Load balancer', 'répartition de charge et pannes'),
 dict(kind='diagram', id='m09a', img='docs/images/m09-alb.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module neuf, le load balancer. Il répartit les requêtes sur deux zones, et une règle envoie les appels de l'API vers les serveurs d'application."),
 dict(kind='shot', id='m09b', img='captures/m09/00-console-alb.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Le load balancer est actif, avec un certificat et un écouteur sécurisé."),
 dict(kind='clip', id='m09c', clip='video/clips/m09.mp4',
      text="Les groupes de cibles sont en bonne santé. Quand nous arrêtons un serveur, l'erreur est détectée, puis le service revient."),

 M(10, 'Module 10 – Route 53', 'noms privés, publics et bascule'),
 dict(kind='diagram', id='m10a', img='docs/images/m10-route53.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module dix, les noms. Une zone privée pour les noms internes, une zone publique, et un contrôle de santé qui fait basculer le DNS vers un site de secours."),
 dict(kind='shot', id='m10b', img='captures/m10/00-console-zones.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Voici nos zones Route 53, privée et publique."),
 dict(kind='clip', id='m10c', clip='video/clips/m10.mp4',
      text="Les serveurs retrouvent app par son nom, et les sondes du contrôle de santé répondent. Quand nous coupons nginx, la réponse DNS bascule en trente-quatre secondes."),

 M(11, 'Module 11 – CloudFront', 'cache et origine protégée'),
 dict(kind='diagram', id='m11a', img='docs/images/m11-cloudfront.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module onze, CloudFront. Les pages statiques sont gardées en cache près des utilisateurs, et le load balancer n'accepte plus que CloudFront."),
 dict(kind='shot', id='m11b', img='captures/m11/00-console-cloudfront.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="La distribution a deux comportements : l'API sans cache, et les images en cache."),
 dict(kind='clip', id='m11c', clip='video/clips/m11.mp4',
      text="Première requête : le cache ne l'a pas encore. Deuxième requête : elle est servie par le cache."),

 M(12, 'Module 12 – Surveillance', 'tableau de bord, alarme, Flow Logs'),
 dict(kind='diagram', id='m12a', img='docs/images/m12-monitoring.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module douze, la surveillance. Un tableau de bord, une alarme sur les erreurs, des notifications par SNS, et les journaux de flux du réseau."),
 dict(kind='shot', id='m12b', img='captures/m12/00-console-alarme.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="L'alarme passe en alerte quand les erreurs dépassent le seuil, puis revient à la normale."),
 dict(kind='clip', id='m12c', clip='video/clips/m12.mp4',
      text="Les tentatives de connexion refusées se retrouvent dans Logs Insights, avec l'adresse source et le port."),

 M(13, 'Module 13 – CloudFormation', 'tout le réseau dans un modèle'),
 dict(kind='diagram', id='m13a', img='docs/images/m13-cloudformation.png', focus=(0.5, 0.5, 1.0, 1.07),
      text="Module treize, CloudFormation. Tout le réseau est décrit dans un seul modèle, qu'on peut redéployer à l'identique."),
 dict(kind='shot', id='m13b', img='captures/m13/00-console-piles-cloudformation.png', focus=(0.5, 0.35, 1.0, 1.15),
      text="Voici la pile : créée, puis agrandie par un change set."),
 dict(kind='clip', id='m13c', clip='video/clips/m13.mp4',
      text="Une règle ajoutée à la main est détectée comme une dérive. Nous la retirons, et la pile revient en synchronisation."),

 dict(kind='diagram', id='99-fin', img='docs/images/global.png', focus=(0.5, 0.5, 1.06, 1.0),
      text="Voilà ce que nous avons construit : un réseau sur trois sites, cloisonné, surveillé, et redéployable. Les services payants à l'heure ont été supprimés après les tests, et le code, les preuves et le dossier sont sur GitHub. Merci de nous avoir suivis."),
]
for s in S:
    if 'text' in s: s['say'] = say(s['text'])
