# Satom Cloud Network – Dossier du binôme TP-AC

Projet réalisé par Thomas Prud'homme et Abderahmane Chaouche pour le client fictif Groupe Léman Finance SA (formation AWS niveau 300, Geneva Institute of Technology, promo E3, semaine du 16 au 20 novembre 2026).

Tout est fait dans la région de Stockholm (`eu-north-1`). Nos ressources portent le suffixe `-TP-AC` et les tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC` et `Environnement=prod` ou `dev`.

## Vidéo
<video controls preload="metadata" width="100%" src="https://raw.githubusercontent.com/Thomas-TP/satom-cloud-network-TP-AC/main/video/satom-cloud-network-TP-AC.mp4"></video>

Si le lecteur ne s'affiche pas : [voir la vidéo sur GitHub](https://github.com/Thomas-TP/satom-cloud-network-TP-AC/blob/main/video/satom-cloud-network-TP-AC.mp4).

## Où nous en sommes
| Module | Sujet | Ce que nous avons fait |
|---|---|---|
| 0 | Cadrage et plan d'adressage | fait |
| 1 | VPC et sous-réseaux | déployé et testé |
| 2 | Routage, IGW et NAT | déployé et testé |
| 3 | Security Groups et NACL | déployé et testé |
| 4 | Network Firewall | **non déployé** : le service est bloqué sur le compte de formation |
| 5 | VPC Peering | déployé et testé |
| 6 | Transit Gateway | **non déployé** : service bloqué |
| 7 | VPN site à site | **simulé** avec strongSwan (le VPN AWS est bloqué) |
| 8 | Direct Connect | **simulé** avec un tunnel GRE et du BGP (Direct Connect est bloqué) |
| 9 | Load balancer | déployé et testé |
| 10 | Route 53 | déployé et testé |
| 11 | CloudFront | déployé et testé |
| 12 | CloudWatch et Flow Logs | déployé et testé |
| 13 | CloudFormation | déployé et testé |

Les services bloqués le sont par une règle de l'organisation AWS du formateur. Nous avons relevé les erreurs exactes dans le fichier `docs/01-services-bloques.md` du dépôt.

![Schéma réseau final](../images/global.png)

Tout le code (scripts AWS CLI, templates CloudFormation), les preuves et les captures sont dans le dépôt GitHub public `Thomas-TP/satom-cloud-network-TP-AC`.


# Module 0 – Cadrage et plan d'adressage

## Le projet
Léman Finance veut un réseau AWS sécurisé qui sépare la production du développement, relie le siège de Genève et l'agence de Lausanne, garde une trace des accès et reste maîtrisé en coût. Tout doit pouvoir être redéployé depuis un template.

Nous sommes deux sur le projet. Le sujet prévoit une répartition en binômes avec des rôles (architecte, sécurité, exploitation…) ; nous ne l'avons pas appliquée et avons traité tous les modules ensemble.

## Ce qui a changé par rapport au sujet
Le compte AWS est partagé avec toute la classe et l'organisation du formateur impose des limites. Voilà ce que nous avons dû adapter.

- **Région** : le sujet parle de Zurich, mais seule Stockholm est utilisable (Zurich n'est pas activée, Francfort est refusée).
- **Services bloqués** : Network Firewall, Transit Gateway, VPN et Direct Connect sont refusés. Nous avons relevé les messages d'erreur (voir `01-services-bloques.md`).
- **Budget** : le sujet annonce 150 CHF par équipe, mais le compte dispose de 100 USD de crédits partagés. Nous avons créé un budget de 100 USD par mois avec une alerte à 80 %.
- **Domaine et certificats** : nous n'avons pas acheté de domaine. Le certificat du load balancer est donc auto-signé, et la zone publique `leman-finance.example` n'est pas réellement déléguée.
- **Adresses IP** : les autres équipes utilisent déjà `10.0.0.0/16`, et le prof nous a dit qu'un /16 était trop grand. Nous avons pris des plages plus petites.
- **Accès aux machines** : pas de SSH ni de clé, nous passons par AWS Systems Manager (SSM).

## Plan d'adressage
| Réseau | Plage | Contenu |
|---|---|---|
| vpc-prod-leman-TP-AC | 10.20.0.0/22 | production |
| sub-public-1a | 10.20.0.0/26 | web-01 (10.20.0.10), NAT |
| sub-public-1b | 10.20.0.64/26 | deuxième zone du load balancer, routeur rtr-aws (10.20.0.74) |
| sub-prive-1a | 10.20.1.0/26 | app-01 (10.20.1.10) |
| sub-fw-1a | 10.20.2.0/28 | endpoint du pare-feu (prévu, non créé) |
| réservé | 10.20.3.0/26 | base de données (non créé) |
| vpc-dev-leman-TP-AC | 10.21.0.0/24 | développement, dev-01 (10.21.0.10) |
| siège (simulé) | 192.168.10.0/24 | selon le sujet |
| agence (simulée) | 192.168.20.0/24 | selon le sujet |

![Plan global](../images/global.png)

## Crédits et budget
Le compte part avec 100 USD. Les activités « Gagnez des crédits AWS » nous ont rapporté 100 USD de plus (EC2, Lambda, DynamoDB, RDS et Budgets). Nous les avons faites en ligne de commande et supprimé les ressources juste après. L'écran de la console affichait encore 180 USD au dernier contrôle ; le report des derniers crédits peut prendre du temps.

Le budget `budget-TP-AC-satom` envoie son alerte à 80 % vers le topic SNS d'exploitation.

## Méthode
Nous avons tout scripté avec l'AWS CLI (un script par module dans `scripts/`). Chaque test écrit son résultat dans un fichier du dépôt, que l'on retrouve dans la partie « Résultats des tests » de chaque module.

## Captures

**Console AWS – budgets**

![Console AWS – budgets](../../captures/m00/00-console-budgets.png)

**Console AWS – credits**

![Console AWS – credits](../../captures/m00/00-console-credits.png)

**Console AWS – quetes credits**

![Console AWS – quetes credits](../../captures/m00/00-console-quetes-credits.png)


---

# Module 1 – VPC et sous-réseaux

## Objectif
Créer le réseau de production, un sous-réseau public et un privé, deux serveurs, et vérifier qu'ils se parlent.

## Ce qu'il faut savoir
Un VPC est un réseau isolé dans une région, avec une plage d'adresses (CIDR). Un sous-réseau vit dans une seule zone de disponibilité et AWS y réserve 5 adresses, donc un /26 offre 59 adresses utilisables. Au départ, la table de routage ne contient que la route locale : les machines du VPC se voient, mais rien ne sort.

Le sujet propose un /16. Le prof nous a dit que c'était trop large pour deux serveurs, nous avons pris un /22.

## Ce que nous avons fait
- Le VPC `vpc-prod-leman-TP-AC` en `10.20.0.0/22`.
- Un sous-réseau public `10.20.0.0/26` et un privé `10.20.1.0/26`, tous les deux en `eu-north-1a`.
- Deux instances `t3.micro` sous Amazon Linux 2023 : `web-01` (`10.20.0.10`, public) et `app-01` (`10.20.1.10`, privé).
- Un rôle IAM pour que les instances soient administrables par SSM, sans SSH.
- Un test de chevauchement : créer `10.20.0.0/27` dans un /26 existant est refusé.
- La plage `10.20.3.0/26` est réservée pour une future base de données.

Script : `scripts/m01-vpc.ps1`.

![Module 1](../images/m01-vpc.png)

| Ressource | Valeur |
|---|---|
| VPC | `vpc-prod-leman-TP-AC`, `10.20.0.0/22` |
| Sous-réseau public | `sub-public-1a-TP-AC`, `10.20.0.0/26` |
| Sous-réseau privé | `sub-prive-1a-TP-AC`, `10.20.1.0/26` |
| web-01 / app-01 | `10.20.0.10` / `10.20.1.10` |

## Comment nous testons
Nous vérifions les CIDR et la zone de chaque sous-réseau, nous essayons de créer un sous-réseau qui chevauche (AWS doit refuser), et nous faisons un ping de `web-01` vers `app-01`. Pour la sortie vers Internet, nous avons lancé une petite instance de test dans un sous-réseau sans route par défaut : elle a lancé un ping et un `curl` au démarrage et nous avons lu le résultat dans la console série.

## Résultats des tests
```
=== Module 1 : VPC et sous-reseaux (region eu-north-1) ===
Creation du VPC vpc-prod-leman-TP-AC 10.20.0.0/22, sub-public-1a-TP-AC 10.20.0.0/26 et sub-prive-1a-TP-AC 10.20.1.0/26 (eu-north-1a)
Adresses disponibles apres lancement des instances (un /26 = 64 adresses, 5 reservees par AWS = 59 utilisables, moins 1 instance = 58 libres) :
  sub-prive-1a-TP-AC  10.20.1.0/26  58 adresses libres
  sub-public-1a-TP-AC 10.20.0.0/26  58 adresses libres

Test de chevauchement : create-subnet --cidr-block 10.20.0.0/27 (inclus dans 10.20.0.0/26)
  -> aws: [ERROR]: An error occurred (InvalidSubnet.Conflict) when calling the CreateSubnet operation: The CIDR '10.20.0.0/27' conflicts with another subnet

Joignabilite web-01 (10.20.0.10) -> app-01 (10.20.1.10) : ping 3/3 recus, 0 % de perte, rtt moyen 0,25 ms (route locale du VPC)
TEST REEL (instance de test sans route par defaut, sous-reseau prive 10.20.3.0/26, resultat lu dans la console serie) :
  ip-10-20-3-20 login: TPAC-TEST table de routage :
  default via [35m10.20.3.1 [0mdev [36mens5 [0mproto dhcp src [35m10.20.3.20 [0mmetric 512
  TPAC-TEST ping 8.8.8.8 :
  3 packets transmitted, 0 received, 100% packet loss, time 2077ms
  code retour ping = 1
  TPAC-TEST curl :
  code retour curl = 28
  TPAC-TEST-FIN
Note : l'outil Reachability Analyzer (tiros:CreateQuery) est bloque par l'organisation ; les tests de ping ont donc ete faits via SSM apres le module 2.
```

## Nettoyage
Nous arrêtons `web-01` et `app-01` après chaque séance. Le VPC et les sous-réseaux restent.

## Problèmes rencontrés
L'outil Reachability Analyzer est bloqué par l'organisation. Et SSM a besoin d'un accès Internet pour fonctionner : le ping entre `web-01` et `app-01` n'a donc été possible qu'après le module 2.

## Captures

**Console AWS – instances**

![Console AWS – instances](../../captures/m01/00-console-instances.png)

**Console AWS – sous reseaux**

![Console AWS – sous reseaux](../../captures/m01/00-console-sous-reseaux.png)

**Console AWS – vpcs**

![Console AWS – vpcs](../../captures/m01/00-console-vpcs.png)

**Terminal – vpc**

![Terminal – vpc](../../captures/m01/01-vpc.png)

**Terminal – subnets**

![Terminal – subnets](../../captures/m01/02-subnets.png)

**Terminal – instances**

![Terminal – instances](../../captures/m01/03-instances.png)

**Journal des tests**

![Journal des tests](../../captures/m01/99-preuves-tests.png)


---

# Module 2 – Routage : IGW et NAT

## Objectif
Donner un accès Internet au sous-réseau public, un accès sortant seulement au privé, et savoir trouver une panne de route.

## Ce qu'il faut savoir
Un sous-réseau est public quand sa table de routage envoie `0.0.0.0/0` vers une Internet Gateway (et que l'instance a une IP publique). Pour un sous-réseau privé, on met une NAT Gateway dans le sous-réseau public : les machines privées peuvent sortir, mais personne ne peut entrer. La NAT coûte environ 0,045 USD de l'heure, ce qui compte avec un budget limité. Quand plusieurs routes correspondent, la plus précise gagne.

## Ce que nous avons fait
- Une Internet Gateway `igw-prod-leman-TP-AC`, et une table `rt-public-leman-TP-AC` avec `0.0.0.0/0` vers l'IGW, associée aux sous-réseaux publics.
- Une Elastic IP sur `web-01`.
- Une NAT Gateway `nat-prod-leman-TP-AC` dans le sous-réseau public, et une table `rt-prive-leman-TP-AC` avec `0.0.0.0/0` vers la NAT.
- Un test de panne : nous avons supprimé la route par défaut du privé pendant que `app-01` pinguait `8.8.8.8` chaque seconde, puis nous l'avons remise.

Script : `scripts/m02-routage.ps1`.

![Module 2](../images/m02-routage.png)

| Table | Routes |
|---|---|
| rt-public-leman-TP-AC | `10.20.0.0/22` local ; `0.0.0.0/0` vers l'IGW |
| rt-prive-leman-TP-AC | `10.20.0.0/22` local ; `0.0.0.0/0` vers la NAT |

## Si ça ne marche pas : quatre vérifications
1. Le sous-réseau est-il associé à la bonne table de routage ?
2. La route par défaut existe-t-elle ?
3. Pointe-t-elle vers la bonne cible (IGW ou NAT) ?
4. La cible est-elle en bon état (NAT `available`, IGW attachée, IP publique sur l'instance) ?

## Résultats des tests
```
=== Module 2 : routage ===
TP1 - IGW + rt-public (0.0.0.0/0 -> igw) + IP publique (Elastic IP) sur web-01
  web-01 -> ping 8.8.8.8 : 2/2 recus (ttl 119, ~3 ms)
  web-01 -> app-01 ping 10.20.1.10 : 3/3 recus
TP2 - NAT nat-prod-leman-TP-AC + rt-prive (0.0.0.0/0 -> nat)
  app-01 -> ping 8.8.8.8 : 2/2 recus (~4 ms) ; curl https://checkip.amazonaws.com -> IP de la NAT (l'adresse de app-01 reste privee)
  app-01 n'a aucune adresse IP publique (describe-instances : PublicIpAddress = None) : il n'est pas joignable depuis Internet
TP3 - route par defaut retiree puis retablie (ping 8.8.8.8 chaque seconde depuis app-01, heures UTC de l'instance) :
  10:49:04 a 10:49:18  OK    (route 0.0.0.0/0 -> NAT presente)
  10:49:19 a 10:49:37  ECHEC (route retiree a 10:49:20 UTC, soit 19 s d'echec)
  10:49:39 a 10:49:59  OK    (route retablie a 10:49:39 UTC)
Tables de routage finales :
  rt-public-leman-TP-AC : 10.20.0.0/22 local | 0.0.0.0/0 -> igw-prod-leman-TP-AC
  rt-prive-leman-TP-AC  : 10.20.0.0/22 local | 0.0.0.0/0 -> nat-prod-leman-TP-AC
```

## Nettoyage
Le sujet demande de supprimer la NAT en fin de séance. Nous la gardons pour l'instant, car elle donne à `app-01` l'accès SSM, et nous la supprimerons à la fin du cours.

## Problèmes rencontrés
Le compte n'autorise que 5 Elastic IP pour toute la classe. Les autres machines du projet utilisent donc des IP publiques automatiques.

## Captures

**Console AWS – passerelle nat**

![Console AWS – passerelle nat](../../captures/m02/00-console-passerelle-nat.png)

**Console AWS – passerelles internet**

![Console AWS – passerelles internet](../../captures/m02/00-console-passerelles-internet.png)

**Console AWS – tables routage**

![Console AWS – tables routage](../../captures/m02/00-console-tables-routage.png)

**Terminal – routes**

![Terminal – routes](../../captures/m02/01-routes.png)

**Terminal – nat**

![Terminal – nat](../../captures/m02/02-nat.png)

**Journal des tests**

![Journal des tests](../../captures/m02/99-preuves-tests.png)


---

# Module 3 – Security Groups et NACL

## Objectif
Filtrer le trafic à deux endroits : sur chaque instance (Security Group) et sur chaque sous-réseau (NACL), et savoir dire lequel bloque.

## Ce qu'il faut savoir
Un Security Group garde l'état des connexions : si l'aller est autorisé, le retour l'est aussi. Il ne contient que des autorisations. Une NACL ne garde pas l'état : il faut autoriser l'aller et le retour (les ports éphémères 1024-65535). Elle accepte des refus, et ses règles sont lues par numéro croissant : la première qui correspond gagne.

## Ce que nous avons fait
- `sg-web-TP-AC` : 443 ouvert à tous, 22 ouvert seulement à une plage de test. Le sujet parle de l'adresse de la « salle d'exploitation » sans la donner ; nous avons mis `203.0.113.0/24` (plage réservée à la documentation).
- `sg-app-TP-AC` : 8080, 22 et ICMP autorisés seulement depuis `sg-web`.
- Un petit nginx (80 et 443 avec certificat auto-signé) sur `web-01`, et une mini-API Python sur le port 8080 de `app-01`.
- Une NACL `nacl-public-TP-AC` sur le sous-réseau public : entrée 443 et ports éphémères, sortie 443 et ports éphémères, plus tout le trafic interne du VPC.
- Trois pannes volontaires : retirer la règle de retour de la NACL, retirer le 8080 de `sg-app`, et placer un refus explicite avant l'autorisation (règle 50 contre règle 100).

Scripts : `scripts/m03-securite.ps1` et `scripts/m03-tests.ps1`.

![Module 3](../images/m03-securite.png)

| Groupe | Sens | Port | Source |
|---|---|---|---|
| sg-web | entrée | 443 | tout Internet |
| sg-web | entrée | 22 | 203.0.113.0/24 |
| sg-app | entrée | 8080, 22, ICMP | sg-web |

NACL : entrée 100 (TCP 443, tous), 110 (TCP 1024-65535, tous), 120 (tout, VPC) ; sortie 100, 110 et 120 identiques.

## Si ça ne marche pas : quatre vérifications
1. Le Security Group de la cible ouvre-t-il le port pour cette source ?
2. La source de la règle est-elle correcte (une plage ou un autre groupe) ?
3. La NACL du sous-réseau autorise-t-elle l'aller et le retour, dans le bon ordre ?
4. La route de retour existe-t-elle ?

## Résultats des tests
```
=== TP1 : Security Groups ===
curl https depuis Internet vers web-01 : HTTP 200
ping depuis Internet vers web-01 (ICMP non autorise) : pas de reponse (attendu)
app-01 n'a pas d'IP publique : None

=== TP2 : SG (avec etat) vs NACL (sans etat) ===
web-01 -> app-01:8080 : Success	app-01 TP-AC /api/health 	
NACL : regle de retour (sortie ephemere 1024-65535) retiree -> curl externe : HTTP 000 ECHEC (code curl 28 : timeout/refus)
NACL : regle de retour retablie -> curl externe : HTTP 200

=== TP3 : diagnostic ===
8080 retire de sg-app -> web-01 -> app-01:8080 : Success	ECHEC 	
8080 retabli -> web-01 -> app-01:8080 : Success	app-01 TP-AC /api/health 	
NACL : refus explicite regle 50 (avant l'autorisation 100) -> curl externe : HTTP 000 ECHEC (code curl 28 : timeout/refus)  [la regle au numero le plus bas gagne]
refus supprime -> curl externe : HTTP 200
```

## Nettoyage
Nous gardons les deux groupes et la NACL, et arrêtons les instances après chaque séance.

## Problèmes rencontrés
AWS interdit les noms de groupe qui commencent par `sg-`. Le nom `sg-web-TP-AC` est donc dans le tag `Name`, et le groupe s'appelle `web-TP-AC`. Le port 22 est ouvert pour respecter le sujet, mais nous administrons par SSM.

## Captures

**Console AWS – groupes securite**

![Console AWS – groupes securite](../../captures/m03/00-console-groupes-securite.png)

**Console AWS – nacl**

![Console AWS – nacl](../../captures/m03/00-console-nacl.png)

**Terminal – sg**

![Terminal – sg](../../captures/m03/01-sg.png)

**Terminal – nacl**

![Terminal – nacl](../../captures/m03/02-nacl.png)

**Journal des tests**

![Journal des tests](../../captures/m03/99-preuves-tests.png)


---

# Module 4 – Network Firewall

> Ce module a d'abord été refusé par l'organisation AWS (`network-firewall:*`). Ce blocage a été levé le 17/11/2026 (nous ne savons pas qui l’a levé) : nous avons alors réalisé et testé le module pour de vrai.

## Objectif
Filtrer ce qui sort du sous-réseau privé : n'autoriser que des dépôts de mises à jour, bloquer le reste du web et garder les alertes dans CloudWatch Logs.

## Ce qu'il faut savoir
Network Firewall est un pare-feu managé placé dans un sous-réseau à part. On y envoie le trafic avec des routes qui visent son endpoint. Il a un moteur sans état (par paquet) et un moteur avec état (domaines HTTP et TLS, règles Suricata). Il faut que le retour d'un flux repasse par le même endpoint, sinon le pare-feu perd l'état. Il coûte environ 0,40 USD de l'heure : on le supprime après les tests.

## Ce que nous avons fait
Le trafic de `app-01` passe par l'endpoint du pare-feu (`sub-fw-1a`, `10.20.2.0/28`), puis vers la NAT, puis vers Internet. Au retour, une route dans la table publique renvoie le trafic vers le pare-feu.

![Module 4](../images/m04-firewall.png)

Règles, en ordre strict :
1. laisser passer tout le trafic interne du VPC (`10.20.0.0/22`) pour ne pas casser les autres modules ;
2. autoriser seulement `.amazonlinux.com` et `.amazonaws.com` ;
3. par défaut, bloquer et journaliser (`drop_established` et `alert_established`) dans `/leman/nfw-alert-TP-AC`.

Les routes sont : `rt-prive` avec `0.0.0.0/0` vers l'endpoint ; `rt-fw` avec `0.0.0.0/0` vers la NAT ; `rt-public` avec `10.20.1.0/26` vers l'endpoint pour le retour.

Script : `scripts/m04-firewall.ps1`. Le template `cfn/optional-m04-network-firewall.yaml` reste une variante CloudFormation, non déployée.

## Résultats des tests
```
Module 4 - Network Firewall (17/11/2026, eu-north-1, depuis app-01-TP-AC via SSM)

Pare-feu : nfw-prod-leman-TP-AC, statut READY, endpoint vpce-08c28b6db9885db5b (sub-fw-1a-TP-AC, 10.20.2.0/28)
Routes : rt-prive 0.0.0.0/0 -> endpoint ; rt-public 10.20.1.0/26 -> endpoint ; rt-fw 0.0.0.0/0 -> NAT

[autorise] curl https://cdn.amazonlinux.com/             -> HTTP 403 (le serveur repond : la connexion passe)
[autorise] curl https://ssm.eu-north-1.amazonaws.com/    -> HTTP 400 (le serveur repond : la connexion passe)
[bloque]   curl https://example.com/                     -> Connection timed out after 15002 ms
[bloque]   curl https://www.wikipedia.org/               -> Connection timed out after 15003 ms

Journal /leman/nfw-alert-TP-AC (extrait) :
  "src_ip":"10.20.1.10","app_proto":"tls","alert":{"signature":"aws:alert_established action","action":"blocked"}
```

## Ce que nous avons vérifié
1. Le pare-feu passe à `Ready` et son endpoint apparaît dans la zone.
2. Depuis `app-01`, `curl https://cdn.amazonlinux.com` fonctionne, `curl https://example.com` échoue.
3. L'alerte du deuxième test apparaît dans les journaux.

## Ce qui a moins bien marché
Le script a créé le pare-feu mais a échoué sur trois étapes : le groupe de journaux (les étiquettes passées à la création), la journalisation qui en dépend, et les routes (l'identifiant d'endpoint n'avait pas été lu). Nous avons relu l'endpoint avec `describe-firewall`, créé le groupe sans étiquettes puis étiqueté à part, et posé les routes à la main. Les routes n'avaient pas été modifiées entre-temps.

## Nettoyage
Supprimer d'abord le pare-feu, puis la politique et les groupes de règles, et remettre `0.0.0.0/0` vers la NAT dans `rt-prive`.

## Captures

**Console AWS – paquets bloques**

![Console AWS – paquets bloques](../../captures/m04/00-console-paquets-bloques.png)

**Console AWS – pare feu details**

![Console AWS – pare feu details](../../captures/m04/00-console-pare-feu-details.png)

**Console AWS – pare feux**

![Console AWS – pare feux](../../captures/m04/00-console-pare-feux.png)

**Console AWS – politique regles**

![Console AWS – politique regles](../../captures/m04/00-console-politique-regles.png)

**Journal des tests**

![Journal des tests](../../captures/m04/99-preuves-tests.png)


---

# Module 5 – VPC Peering

## Objectif
Créer un VPC de développement, le relier à la production pour le seul port 8080, et comprendre les limites du peering.

## Ce qu'il faut savoir
Un peering relie deux VPC par le réseau privé d'AWS. Il faut faire la demande, l'accepter, ajouter les routes dans les deux sens et ouvrir ce qu'il faut dans les Security Groups. Les plages ne doivent pas se chevaucher (AWS accepte la demande, puis la met en échec à l'acceptation). Le peering n'est pas transitif : si A parle à B et B à C, A ne parle pas à C.

## Ce que nous avons fait
- Le VPC `vpc-dev-leman-TP-AC` en `10.21.0.0/24`, un sous-réseau `10.21.0.0/26`, une instance `dev-01` (`10.21.0.10`). Elle a une IP publique pour joindre SSM, et son groupe de sécurité n'autorise aucune entrée.
- Le peering `pcx-lab-TP-AC` entre la prod et le dev, les routes dans les deux tables, et le port 8080 ouvert dans `sg-app` pour `10.21.0.0/24`.
- Un VPC volontairement en `10.20.0.0/24` pour tenter un peering avec la prod : il passe en échec.
- Un troisième VPC `10.22.0.0/24` relié seulement à la prod : `app-01` le joint, `dev-01` non.

Scripts : `scripts/m05-peering.ps1` et `scripts/m05-tests.ps1`.

![Module 5](../images/m05-peering.png)

| Élément | Valeur |
|---|---|
| Peering | prod `10.20.0.0/22` avec dev `10.21.0.0/24` |
| Table du dev | `10.20.0.0/22` vers le peering, `0.0.0.0/0` vers l'IGW du dev |
| Table du privé (prod) | `10.21.0.0/24` vers le peering |
| sg-app | TCP 8080 depuis `10.21.0.0/24` |

## Comment nous testons
Depuis `dev-01`, un `curl` sur `app-01:8080` doit répondre et le port 22 doit rester fermé. Le peering avec la plage qui chevauche doit échouer. Et `dev-01` ne doit pas joindre le VPC relié seulement à la prod, alors qu'`app-01` le joint.

## Résultats des tests
```
dev-01 SSM en ligne : True
=== TP2 : peering pcx-lab (prod <-> dev) ===
dev-01 -> app-01:8080 : Success	app-01 TP-AC /api/health 	
dev-01 -> app-01:22 (non ouvert depuis dev) : Success	FERME 	

=== TP3 : limites du peering ===
Acceptation du peering avec un VPC en 10.20.0.0/24 (chevauche 10.20.0.0/22) -> aws: [ERROR]: An error occurred (InvalidStateTransition) when calling the AcceptVpcPeeringConnection operation: Invalid state transition for pcx-0b30499bae7844bdf, attempted to transition from failed to provisioning
app-01 (prod, peering direct) -> tiers-01 10.22.0.10 : Success	2 packets transmitted, 2 received, 0% packet loss, time 1002ms rtt min/avg/max/mdev = 0.170/0.294/0.419/0.124 ms 	
dev-01 (via prod = transit, NON transitif) -> tiers-01 10.22.0.10 : Success	2 packets transmitted, 0 received, 100% packet loss, time 1043ms  exit=0
```

## Nettoyage
Le sujet supprime le peering au module 6, mais le Transit Gateway est bloqué : nous gardons donc le peering pour relier prod et dev. `dev-01` est arrêtée après les tests, les VPC de test sont supprimés.

## Captures

**Console AWS – peering**

![Console AWS – peering](../../captures/m05/00-console-peering.png)

**Terminal – peering**

![Terminal – peering](../../captures/m05/01-peering.png)

**Terminal – routes dev**

![Terminal – routes dev](../../captures/m05/02-routes-dev.png)

**Journal des tests**

![Journal des tests](../../captures/m05/99-preuves-tests.png)


---

# Module 6 – Transit Gateway

> Nous n'avons pas pu faire ce module : la création d'un Transit Gateway (`ec2:CreateTransitGateway`) est refusée par l'organisation AWS du formateur. Rien n'a été déployé ni testé. Le template CloudFormation préparé a seulement passé `validate-template`. La liaison prod et dev reste assurée par le peering du module 5.

## Objectif
Remplacer les liaisons une à une par un point central : un Transit Gateway relie plusieurs VPC, avec une table de routage par environnement.

## Ce qu'il faut savoir
Chaque VPC se branche au Transit Gateway par un attachement. Avec le peering il faut un lien par paire de réseaux ; avec le Transit Gateway, un seul par réseau. Un attachement est associé à une table de routage (celle qui décide où il peut aller) et peut publier sa plage dans une autre table (propagation). En coupant l'association et la propagation par défaut, on décide à la main qui voit qui. Les routes dans les tables des VPC restent nécessaires. Il coûte environ 0,05 USD de l'heure par attachement.

## Ce que nous avons prévu
Un Transit Gateway `tgw-leman-TP-AC` (ASN 64512), deux attachements `tgwa-prod` et `tgwa-dev`, deux tables `tgw-rt-prod` et `tgw-rt-dev` avec propagation croisée, et des routes `10.21.0.0/24` et `10.20.0.0/22` dans les tables des deux VPC.

![Module 6](../images/m06-tgw.png)

Fichiers prêts : `cfn/optional-m06-m08-interconnexion.yaml` (template validé, jamais déployé) et `scripts/m06-tgw.ps1` (jamais exécuté avec succès).

## Ce que nous testerions
1. Les deux attachements passent à `available`.
2. `dev-01` joint `app-01` sur 8080 par le Transit Gateway.
3. On retire la propagation de `tgwa-dev` vers `tgw-rt-prod` : le `curl` échoue (le retour n'a plus de route). On la remet : il refonctionne.

## Ce que nous avons essayé
`aws ec2 create-transit-gateway` renvoie « explicit deny in a service control policy » (le détail est dans `01-services-bloques.md`). La lecture reste autorisée, pas la création.


---

# Module 7 – VPN site à site (siège et agence)

> Le VPN géré d'AWS est bloqué par l'organisation (`CreateCustomerGateway`, `CreateVpnGateway` et `CreateVpnConnection` sont refusés, le Transit Gateway aussi). Nous avons donc **simulé** les trois routeurs avec strongSwan sur des instances EC2 : le tunnel IPsec est réel, mais ce n'est pas le service VPN d'AWS.

## Objectif
Relier le siège (`192.168.10.0/24`) et l'agence (`192.168.20.0/24`) au VPC de production par des tunnels chiffrés. Le siège doit pouvoir joindre `app-01` (ping et 8080), l'agence seulement le port 8080.

## Ce qu'il faut savoir
IPsec en version 2 fonctionne en deux temps : une phase d'authentification (ici une clé partagée et un échange Diffie-Hellman), puis un tunnel ESP qui chiffre le trafic (nous utilisons `aes256-sha256-modp2048`). Le VPN d'AWS fournit deux tunnels par connexion et des adresses de tunnel en `169.254.x.x/30`. Nous avons fait du « route-based » : le tunnel est une interface et ce sont les routes qui décident ce qui y passe. La clé partagée ne doit jamais traîner dans un document : la nôtre est dans Secrets Manager (`Projet/SatomCloudNetwork/vpn`), les routeurs la lisent avec leur rôle IAM.

## Ce que nous avons fait
- `rtr-aws-TP-AC` dans le sous-réseau public 1b (`10.20.0.74`), qui joue la passerelle côté AWS.
- `rtr-siege-TP-AC` (`192.168.10.10`) et `rtr-agence-TP-AC` (`192.168.20.10`), chacun dans son propre petit VPC simulé.
- Des routes dans `rt-prive` vers `192.168.10.0/24` et `192.168.20.0/24` qui passent par le routeur AWS.
- Dans `sg-app`, le ping et le 8080 pour le siège, le 8080 seulement pour l'agence.

Script : `scripts/m07-ipsec-sim.ps1 -Site siege` ou `-Site agence`.

![Module 7](../images/m07-vpn.png)

| Élément | Valeur |
|---|---|
| IKE et ESP | `aes256-sha256-modp2048`, authentification par clé partagée |
| Interfaces de tunnel | `xfrm-siege` (`169.254.10.0/30`), `xfrm-agence` (`169.254.20.0/30`) |
| Adresses publiques | automatiques, car le quota d'Elastic IP du compte est plein |

## Si ça ne marche pas : quatre vérifications
1. L'état des tunnels : `swanctl --list-sas` doit afficher `ESTABLISHED`.
2. Les paramètres IPsec : mêmes propositions et même clé des deux côtés.
3. Les routes : `ip route get` côté site, et la route dans `rt-prive` côté AWS.
4. Les Security Groups : UDP 500 et 4500 et le protocole ESP doivent passer entre les routeurs, et `sg-app` doit autoriser la source.

## Résultats des tests
```
=== Module 7 - tunnel IPsec siege (simulation strongSwan) ===
rtr-aws : swanctl --list-sas (apres les tests)
Success  siege: #3, ESTABLISHED, IKEv2, 86ce1374cfee168c_i 4d3fa39eb5010b95_r*
  local  '16.171.33.204' @ 10.20.0.74[4500]
  remote '16.171.233.38' @ 16.171.233.38[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  established 49s ago, rekeying in 14332s
  siege: #2, reqid 1, INSTALLED, TUNNEL-in-UDP, ESP:AES_CBC-256/HMAC_SHA2_256_128
    installed 49s ago, rekeying in 3321s, expires in 3911s
    in  c4658670 (-|0x0000000b),      0 bytes,     0 packets
    out c84a9f39 (-|0x0000000b),      0 bytes,     0 packets
    local  0.0.0.0/0
    remote 0.0.0.0/0
siege: #1, ESTABLISHED, IKEv2, 539dbbd3258372a5_i* 3200bb556dbda525_r
  local  '16.171.33.204' @ 10.20.0.74[4500]
  remote '16.171.233.38' @ 16.171.233.38[4500]
xfrm-siege@ens5  UNKNOWN        169.254.10.1/30 fe80::fe5a:d22f:66df:1fa2/64 
192.168.10.0/24 dev xfrm-siege scope link metric 200 
  
rtr-siege : swanctl --list-sas
Success  siege: #2, ESTABLISHED, IKEv2, 539dbbd3258372a5_i 3200bb556dbda525_r*
  local  '16.171.233.38' @ 192.168.10.10[4500]
  remote '16.171.33.204' @ 16.171.33.204[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  established 9s ago, rekeying in 14382s
  siege: #2, reqid 1, INSTALLED, TUNNEL-in-UDP, ESP:AES_CBC-256/HMAC_SHA2_256_128
    installed 9s ago, rekeying in 3413s, expires in 3951s
    in  c957f44c (-|0x0000000b),      0 bytes,     0 packets
    out c7ad7116 (-|0x0000000b),      0 bytes,     0 packets
    local  0.0.0.0/0
    remote 0.0.0.0/0
siege: #1, ESTABLISHED, IKEv2, 86ce1374cfee168c_i* 4d3fa39eb5010b95_r
  local  '16.171.233.38' @ 192.168.10.10[4500]
  remote '16.171.33.204' @ 16.171.33.204[4500]

siege -> app-01 (10.20.1.10) ping : 
Success  --- 10.20.1.10 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 2.426/2.551/2.787/0.166 ms
  
siege -> app-01:8080 : Success  app-01 TP-AC /api/health
  
siege -> dev-01 : premier essai NON CONCLUANT (dev-01 etait arretee) ; refait plus bas avec dev-01 demarree
=== Module 7 - tunnel IPsec agence (simulation strongSwan) ===
rtr-aws : swanctl --list-sas
Success	siege: #2, CONNECTING, IKEv2, 46d24f38fb1cec9c_i* 0000000000000000_r
  local  '%any' @ 10.20.0.74[500]
  remote '%any' @ 16.171.233.38[500]
  active:  IKE_VENDOR IKE_INIT IKE_NATD IKE_CERT_PRE IKE_AUTH IKE_CERT_POST IKE_CONFIG IKE_AUTH_LIFETIME IKE_MOBIKE IKE_ESTABLISH CHILD_CREATE
agence: #1, CONNECTING, IKEv2, da793526fe55fb7b_i* 0000000000000000_r
  local  '%any' @ 10.20.0.74[500]
  remote '%any' @ 13.60.86.14[500]
  active:  IKE_VENDOR IKE_INIT IKE_NATD IKE_CERT_PRE IKE_AUTH IKE_CERT_POST IKE_CONFIG IKE_AUTH_LIFETIME IKE_MOBIKE IKE_ESTABLISH CHILD_CREATE

rtr-agence : swanctl --list-sas
Success	agence: #1, ESTABLISHED, IKEv2, 5fb2db85da6aec7a_i* afa4530cbd0d1f05_r
  local  '13.60.86.14' @ 192.168.20.10[4500]
  remote '16.171.33.204' @ 16.171.33.204[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  established 11s ago, rekeying in 13912s
  agence: #1, reqid 1, INSTALLED, TUNNEL-in-UDP, ESP:AES_CBC-256/HMAC_SHA2_256_128
    installed 11s ago, rekeying in 3390s, expires in 3949s
    in  cb7908ec (-|0x0000000c),      0 bytes,     0 packets
    out c082e22a (-|0x0000000c),      0 bytes,     0 packets
    local  0.0.0.0/0
    remote 0.0.0.0/0
	
agence -> app-01 ping (ICMP non autorise pour l'agence) : 
Success	2 packets transmitted, 0 received, 100% packet loss, time 1054ms

exit=0
	
agence -> app-01:8080 (seul flux autorise) : Success	app-01 TP-AC /api/health
	
agence -> dev-01 : premier essai NON CONCLUANT (dev-01 etait arretee) ; refait plus bas avec dev-01 demarree

=== Module 7 - tunnel IPsec siege (simulation strongSwan) ===
rtr-aws : swanctl --list-sas
Success	agence: #1, CONNECTING, IKEv2, 395d821a9697a878_i* 0000000000000000_r
  local  '%any' @ 10.20.0.74[500]
  remote '%any' @ 13.60.86.14[500]
  active:  IKE_VENDOR IKE_INIT IKE_NATD IKE_CERT_PRE IKE_AUTH IKE_CERT_POST IKE_CONFIG IKE_AUTH_LIFETIME IKE_MOBIKE IKE_ESTABLISH CHILD_CREATE
	plugin 'test-vectors': failed to load - test_vectors_plugin_create not found and no plugin file available
plugin 'ldap': failed to load - ldap_plugin_create not found and no plugin file available
plugin 'pkcs11': failed to load - pkcs11_plugin_create not found and no plugin file available
plugin 'rdrand': failed to load - rdrand_plugin_create not found and no plugin file available
plugin 'gcrypt': failed to load - gcrypt_plugin_create not found and no plugin file available
plugin 'af-alg': failed to load - af_alg_plugin_create not found and no plugin file available
plugin 'curve25519': failed to load - curve25519_plugin_create not found and no plugin file available
plugin 'chapoly': failed to load - chapoly_plugin_create not found and no plugin file available
plugin 'cmac': failed to load - cmac_plugin_create not found and no plugin file available
plugin 'ctr': failed to load - ctr_plugin_create not found and no plugin file available
plugin 'ccm': failed to load - ccm_plugin_create not found and no plugin file available
plugin 'ntru': failed to load - ntru_plugin_create not found and no plugin file available
plugin 'curl': failed to load - curl_plugin_create not found and no plugin file available

rtr-siege : swanctl --list-sas
Success	siege: #1, ESTABLISHED, IKEv2, b535252c8726a847_i* fdcc7f92d6069070_r
  local  '51.20.144.158' @ 192.168.10.10[4500]
  remote '16.171.171.189' @ 16.171.171.189[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  established 11s ago, rekeying in 14194s
  siege: #1, reqid 1, INSTALLED, TUNNEL-in-UDP, ESP:AES_CBC-256/HMAC_SHA2_256_128
    installed 11s ago, rekeying in 3286s, expires in 3949s
    in  c78f150b (-|0x0000000b),      0 bytes,     0 packets
    out c1856d9b (-|0x0000000b),      0 bytes,     0 packets
    local  0.0.0.0/0
    remote 0.0.0.0/0
	plugin 'test-vectors': failed to load - test_vectors_plugin_create not found and no plugin file available
plugin 'ldap': failed to load - ldap_plugin_create not found and no plugin file available
plugin 'pkcs11': failed to load - pkcs11_plugin_create not found and no plugin file available
plugin 'rdrand': failed to load - rdrand_plugin_create not found and no plugin file available
plugin 'gcrypt': failed to load - gcrypt_plugin_create not found and no plugin file available
plugin 'af-alg': failed to load - af_alg_plugin_create not found and no plugin file available
plugin 'curve25519': failed to load - curve25519_plugin_create not found and no plugin file available
plugin 'chapoly': failed to load - chapoly_plugin_create not found and no plugin file available
plugin 'cmac': failed to load - cmac_plugin_create not found and no plugin file available
plugin 'ctr': failed to load - ctr_plugin_create not found and no plugin file available
plugin 'ccm': failed to load - ccm_plugin_create not found and no plugin file available
plugin 'ntru': failed to load - ntru_plugin_create not found and no plugin file available
plugin 'curl': failed to load - curl_plugin_create not found and no plugin file available

(mode DevOnly : app-01 arretee, seuls l'etat du tunnel et le test dev-01 sont executes)
siege -> dev-01 (10.21.0.10), dev-01 en cours d'execution (SSM : Online) : Success	3 packets transmitted, 0 received, 100% packet loss, time 2061ms

code retour=0
	  (le tunnel ne contient que 10.20.0.0/22)
=== Module 7 - tunnel IPsec agence (simulation strongSwan) ===
rtr-aws : swanctl --list-sas
Success	siege: #2, CONNECTING, IKEv2, 7fadf2f20e07735e_i* 0000000000000000_r
  local  '%any' @ 10.20.0.74[500]
  remote '%any' @ 51.20.144.158[500]
  active:  IKE_VENDOR IKE_INIT IKE_NATD IKE_CERT_PRE IKE_AUTH IKE_CERT_POST IKE_CONFIG IKE_AUTH_LIFETIME IKE_MOBIKE IKE_ESTABLISH CHILD_CREATE
	plugin 'test-vectors': failed to load - test_vectors_plugin_create not found and no plugin file available
plugin 'ldap': failed to load - ldap_plugin_create not found and no plugin file available
plugin 'pkcs11': failed to load - pkcs11_plugin_create not found and no plugin file available
plugin 'rdrand': failed to load - rdrand_plugin_create not found and no plugin file available
plugin 'gcrypt': failed to load - gcrypt_plugin_create not found and no plugin file available
plugin 'af-alg': failed to load - af_alg_plugin_create not found and no plugin file available
plugin 'curve25519': failed to load - curve25519_plugin_create not found and no plugin file available
plugin 'chapoly': failed to load - chapoly_plugin_create not found and no plugin file available
plugin 'cmac': failed to load - cmac_plugin_create not found and no plugin file available
plugin 'ctr': failed to load - ctr_plugin_create not found and no plugin file available
plugin 'ccm': failed to load - ccm_plugin_create not found and no plugin file available
plugin 'ntru': failed to load - ntru_plugin_create not found and no plugin file available
plugin 'curl': failed to load - curl_plugin_create not found and no plugin file available

rtr-agence : swanctl --list-sas
Success	agence: #1, ESTABLISHED, IKEv2, 54b21ff5d5cbddfd_i* fb535af7b613e7e5_r
  local  '13.62.50.97' @ 192.168.20.10[4500]
  remote '16.171.171.189' @ 16.171.171.189[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  established 11s ago, rekeying in 13121s
  agence: #1, reqid 1, INSTALLED, TUNNEL-in-UDP, ESP:AES_CBC-256/HMAC_SHA2_256_128
    installed 11s ago, rekeying in 3449s, expires in 3949s
    in  c5ff0eeb (-|0x0000000c),      0 bytes,     0 packets
    out c468260c (-|0x0000000c),      0 bytes,     0 packets
    local  0.0.0.0/0
    remote 0.0.0.0/0
	plugin 'test-vectors': failed to load - test_vectors_plugin_create not found and no plugin file available
plugin 'ldap': failed to load - ldap_plugin_create not found and no plugin file available
plugin 'pkcs11': failed to load - pkcs11_plugin_create not found and no plugin file available
plugin 'rdrand': failed to load - rdrand_plugin_create not found and no plugin file available
plugin 'gcrypt': failed to load - gcrypt_plugin_create not found and no plugin file available
plugin 'af-alg': failed to load - af_alg_plugin_create not found and no plugin file available
plugin 'curve25519': failed to load - curve25519_plugin_create not found and no plugin file available
plugin 'chapoly': failed to load - chapoly_plugin_create not found and no plugin file available
plugin 'cmac': failed to load - cmac_plugin_create not found and no plugin file available
plugin 'ctr': failed to load - ctr_plugin_create not found and no plugin file available
plugin 'ccm': failed to load - ccm_plugin_create not found and no plugin file available
plugin 'ntru': failed to load - ntru_plugin_create not found and no plugin file available
plugin 'curl': failed to load - curl_plugin_create not found and no plugin file available

(mode DevOnly : app-01 arretee, seuls l'etat du tunnel et le test dev-01 sont executes)
agence -> dev-01 (10.21.0.10), dev-01 en cours d'execution (SSM : Online) : Success	3 packets transmitted, 0 received, 100% packet loss, time 2024ms

code retour=0
	  (le tunnel ne contient que 10.20.0.0/22)
```

## Limites de notre réalisation
- Un seul tunnel par site, alors que le VPN d'AWS en donne deux.
- Nous avons monté le siège puis l'agence l'un après l'autre : le compte est limité à 16 vCPU pour toute la classe.
- Pour vérifier que ni le siège ni l'agence ne voient `dev-01`, nous avons d'abord fait un test sans valeur (`dev-01` était arrêtée). Nous l'avons refait avec `dev-01` démarrée (SSM « Online ») : le ping vers `10.21.0.10` perd 100 % des paquets depuis le siège et depuis l'agence, car seule la plage `10.20.0.0/22` est dans les tunnels. Ces tests ont été faits un site à la fois, sans `app-01` allumée (manque de vCPU).

## Nettoyage
Le sujet est contradictoire sur ce point (garder ou supprimer le VPN). Nous gardons les routeurs jusqu'à la fin du cours, arrêtés quand nous ne les utilisons pas, et nous les supprimerons ensuite.


## Captures

**Console AWS – secret vpn**

![Console AWS – secret vpn](../../captures/m07/00-console-secret-vpn.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-1.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-2.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-3.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-4.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-5.png)

**Journal des tests**

![Journal des tests](../../captures/m07/99-preuves-tests-6.png)


---

# Module 8 – Direct Connect

> Direct Connect est bloqué par l'organisation : nous avons testé `CreateDirectConnectGateway` et `DescribeLocations`, les deux sont refusés. Nous n'avons donc pas créé `dxgw-leman` et nous n'avons pas pu choisir d'emplacement. La liaison dédiée est **simulée** par un tunnel GRE entre deux routeurs qui parlent BGP, le VPN du module 7 servant de secours.

## Objectif
Comprendre une liaison dédiée (dimensionnement, interface virtuelle, BGP) et la bascule entre une liaison principale et un secours.

## Ce qu'il faut savoir
Direct Connect est un lien physique entre le siège et un point de présence d'AWS (1, 10 ou 100 Gbit/s). Une interface virtuelle y porte la session BGP vers AWS. En BGP, le chemin avec la préférence locale (local-pref) la plus haute gagne ; pour décourager un chemin, on allonge son AS-path. Ici : local-pref 200 sur la liaison dédiée, et l'AS-path du VPN allongé de 3.

## Dimensionnement
Nous devons transférer 2 To en 8 heures : 16 000 Gbit sur 28 800 s, soit environ 0,56 Gbit/s. Une liaison de 1 Gbit/s suffit avec une marge d'environ 44 %.

## Ce que nous avons fait
- Un tunnel GRE `169.254.100.0/30` entre `rtr-siege` (AS 65010) et `rtr-aws` (AS 64513), qui joue la « fibre ».
- Deux sessions BGP, une sur le GRE et une dans le tunnel IPsec du module 7. Le siège annonce `192.168.10.0/24`, la prod annonce `10.20.0.0/22`.
- `local-pref 200` sur ce qui arrive par le GRE, et un AS-path allongé (`65010` trois fois de plus) sur le chemin VPN.
- Le GRE est coupé puis remis pendant un ping horodaté, pour mesurer la bascule.

Les routeurs tournent avec FRRouting sur Ubuntu. Le sujet propose GNS3 : nous ne l'avons pas utilisé.

Script : `scripts/m08-bgp-sim.ps1`.

![Module 8](../images/m08-dx.png)

| Élément | rtr-siege | rtr-aws |
|---|---|---|
| ASN | 65010 | 64513 |
| Tunnel GRE | `169.254.100.2/30` | `169.254.100.1/30` |
| Tunnel IPsec | `169.254.10.2/30` | `169.254.10.1/30` |
| Annonce | `192.168.10.0/24` | `10.20.0.0/22` |
| Timers BGP | 3 s / 9 s | 3 s / 9 s |

## Si ça ne marche pas : quatre vérifications
1. L'état de BGP : `show bgp summary` doit afficher `Established`.
2. Les préfixes annoncés et reçus.
3. La local-pref : `show ip bgp <préfixe>` montre quel chemin est le meilleur.
4. La route dans `rt-prive` vers le routeur, et `ip route get` sur le routeur.

## Résultats des tests
```
=== TP1 : dimensionnement (voir docs/modules/m08) ===
2 To en 8 h = 16 000 Gbit / 28 800 s = 0,556 Gbit/s -> liaison 1 Gbit/s (marge ~44 %)

=== TP2 : GRE + BGP ===
rtr-aws : show bgp summary
Success	
IPv4 Unicast Summary (VRF default):
BGP router identifier 10.20.0.74, local AS number 64513 vrf-id 0
BGP table version 2
RIB entries 3, using 576 bytes of memory
Peers 2, using 1448 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
169.254.10.2    4      65010        21        18        0    0    0 00:00:29            1        2 VPN-IPsec
169.254.100.2   4      65010        19        18        0    0    0 00:00:29            1        2 DX-simule-GRE

Total number of neighbors 2
	
rtr-aws : show ip bgp 192.168.10.0/24
Success	BGP routing table entry for 192.168.10.0/24, version 2
Paths: (2 available, best #1, table default)
  Advertised to non peer-group peers:
  169.254.10.2 169.254.100.2
  65010
    169.254.100.2 from 169.254.100.2 (192.168.10.10)
      Origin IGP, metric 0, localpref 200, valid, external, best (Local Pref)
      Last update: Mon Nov 16 12:54:16 2026
  65010 65010 65010 65010
    169.254.10.2 from 169.254.10.2 (192.168.10.10)
      Origin IGP, metric 0, valid, external
      Last update: Mon Nov 16 12:54:16 2026
	
rtr-siege : show ip route 10.20.0.0/22
Success	Routing entry for 10.20.0.0/22
  Known via "bgp", distance 20, metric 0, best
  Last update 00:00:39 ago
  * 169.254.100.1, via gre-dx, weight 1

	
siege -> app-01 (chemin DX) :
Success	10.20.1.10 from 192.168.10.10 via 169.254.100.1 dev gre-dx uid 0 
    cache 
--- 10.20.1.10 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 2.354/2.409/2.504/0.067 ms
	

=== TP3 : politique et bascule ===
rtr-siege : show ip bgp 10.20.0.0/22 (local-pref 200 sur DX, 100 sur VPN)
Success	BGP routing table entry for 10.20.0.0/22, version 2
Paths: (2 available, best #1, table default)
  Advertised to non peer-group peers:
  169.254.10.1 169.254.100.1
  64513
    169.254.100.1 from 169.254.100.1 (10.20.0.74)
      Origin IGP, metric 0, localpref 200, valid, external, best (Local Pref)
      Last update: Mon Nov 16 12:54:16 2026
  64513
    169.254.10.1 from 169.254.10.1 (10.20.0.74)
      Origin IGP, metric 0, valid, external
      Last update: Mon Nov 16 12:54:16 2026
	
rtr-aws : chemin VPN annonce par le siege avec AS-path prepend x3 (65010 65010 65010 65010) :
Success	BGP table version is 2, local router ID is 10.20.0.74, vrf id 0
Default local pref 100, local AS 64513
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*  192.168.10.0/24  169.254.10.2             0             0 65010 65010 65010 65010 i

Displayed  1 routes and 3 total paths
	
GRE coupe -> route apres bascule :
Success	10.20.1.10 from 192.168.10.10 via 169.254.10.1 dev xfrm-siege uid 0 
    cache 
Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
169.254.10.1    4      64513        48        51        0    0    0 00:01:54            1        2 VPN-IPsec
169.254.100.1   4      64513        35        36        0    0    0 00:00:36       Active        0 DX-simule-GRE
	
GRE retabli -> retour sur DX :
Success	10.20.1.10 from 192.168.10.10 via 169.254.100.1 dev gre-dx uid 0 
    cache 
	
Journal de continuite (pings toutes les 0,1 s ; KO = perdus) :
Success	    130 OK
      9 KO
    261 OK
---
9
pings_perdus_x0.1s
```

## Mesure de la bascule
Pendant la coupure du GRE, 9 sondes sur une série d'une sonde toutes les 0,1 s ont été perdues (chacune attend 1 s au plus) : l'interruption dure une dizaine de secondes, le temps que BGP détecte la perte (9 s). Le trafic passe alors par le VPN, et il revient sur la liaison principale quand le GRE est rétabli.

## Nettoyage
Rien n'est facturé à l'heure pour Direct Connect puisque nous n'avons rien commandé. Les routeurs sont des instances EC2 arrêtées après les tests.

## Captures

**Journal des tests**

![Journal des tests](../../captures/m08/99-preuves-tests-1.png)

**Journal des tests**

![Journal des tests](../../captures/m08/99-preuves-tests-2.png)

**Journal des tests**

![Journal des tests](../../captures/m08/99-preuves-tests-3.png)


---

# Module 9 – Load balancer

## Objectif
Publier le site derrière un Application Load Balancer en HTTPS sur deux zones, avec un chemin `/api/*` vers l'API, et savoir diagnostiquer une panne.

## Ce qu'il faut savoir
L'ALB travaille au niveau applicatif et a un nœud par zone de disponibilité : il faut donc deux sous-réseaux dans deux zones. Un listener (ici le 443) applique des règles (chemin, nom d'hôte) qui envoient vers des groupes cibles. Le contrôle de santé retire tout seul une cible qui ne répond plus ; sans cible saine, le client reçoit une erreur 502 ou 503. Les serveurs ne doivent accepter que l'ALB, pas Internet. L'ALB coûte environ 0,03 USD de l'heure.

## Ce que nous avons fait
- Un deuxième sous-réseau public `10.20.0.64/26` dans `eu-north-1b`.
- Deux groupes cibles : `tg-web` (HTTP 80, santé `/health`, cible `web-01`) et `tg-app` (HTTP 8080, santé `/api/health`, cible `app-01`).
- L'ALB `alb-prod-leman-TP-AC` sur les deux zones, avec son propre Security Group `sg-alb` (443 ouvert).
- Un listener HTTPS 443 avec un certificat auto-signé importé dans ACM, qui envoie par défaut vers `tg-web` ; une règle de priorité 10 envoie `/api/*` vers `tg-app`.
- Trois pannes : nginx arrêté sur `web-01`, port 443 fermé dans `sg-alb`, puis tout remis.

Script : `scripts/m09-alb.ps1`.

![Module 9](../images/m09-alb.png)

| Élément | Valeur |
|---|---|
| Listener | HTTPS 443, politique TLS 1.3/1.2, certificat auto-signé |
| Règle | priorité 10, chemin `/api/*` vers `tg-app` |
| Santé | 10 s d'intervalle, 2 échecs pour retirer, 2 réussites pour remettre |
| sg-web / sg-app | acceptent le 80 / le 8080 uniquement depuis `sg-alb` |

## Si ça ne marche pas : quatre vérifications
1. Le listener : bon port et bon certificat ?
2. La règle `/api/*` passe-t-elle avant la règle par défaut ?
3. L'état de la cible : `describe-target-health` donne `healthy` ou `unhealthy` avec la raison.
4. Le Security Group de la cible autorise-t-il l'ALB ?

## Résultats des tests
```
=== TP1/TP2 ===
tg-web : healthy   tg-app : healthy
curl https://ALB/            -> web-01 TP-AC  [HTTP 200]
curl https://ALB/api/health  -> app-01 TP-AC /api/health  [HTTP 200]

=== TP3 : pannes ===
nginx arrete sur web-01 : tg-web = unhealthy ; curl https://ALB/ -> <html> <head><title>502 Bad Gateway</title></head> <body> <center><h1>502 Bad Gateway</h1></center> </body> </html>  [HTTP 502]
nginx relance : tg-web = healthy
curl https://ALB/ -> web-01 TP-AC  [HTTP 200]
443 ferme dans sg-alb -> curl https://ALB/ -> ECHEC (curl 28)
443 retabli -> curl https://ALB/ -> web-01 TP-AC  [HTTP 200]
```

## Nettoyage
Nous gardons l'ALB et les groupes cibles pour les modules suivants, et nous supprimerons l'ALB à la fin du cours.

## Ce qui diffère du sujet
Nous n'avons pas de domaine, donc le certificat est auto-signé (nos tests utilisent `curl -k`). Le sujet réutilise `sg-web` pour l'ALB ; nous avons préféré un groupe séparé pour que les serveurs n'acceptent que l'ALB.

## Captures

**Console AWS – alb**

![Console AWS – alb](../../captures/m09/00-console-alb.png)

**Console AWS – groupes cibles**

![Console AWS – groupes cibles](../../captures/m09/00-console-groupes-cibles.png)

**Terminal – alb**

![Terminal – alb](../../captures/m09/01-alb.png)

**Terminal – targets web**

![Terminal – targets web](../../captures/m09/02-targets-web.png)

**Terminal – targets app**

![Terminal – targets app](../../captures/m09/03-targets-app.png)

**Terminal – rules**

![Terminal – rules](../../captures/m09/04-rules.png)

**Journal des tests**

![Journal des tests](../../captures/m09/99-preuves-tests.png)


---

# Module 10 – Route 53

## Objectif
Donner des noms à nos machines avec une zone privée, publier le site avec une zone publique, et prévoir une bascule automatique si le site tombe.

## Ce qu'il faut savoir
Une zone privée n'est visible que depuis les VPC auxquels on l'associe (le résolveur du VPC est à l'adresse base + 2, ici `10.20.0.2`). Une zone publique donne quatre serveurs de noms qu'il faut déclarer chez le bureau d'enregistrement du domaine. Un enregistrement « alias » pointe vers une ressource AWS. Pour le failover, on relie l'enregistrement principal à un contrôle de santé et on prévoit un enregistrement de secours.

## Ce que nous avons fait
- La zone privée `prod.leman.internal` associée au VPC de prod, avec `web.prod.leman.internal` (`10.20.0.10`) et `app.prod.leman.internal` (`10.20.1.10`).
- La zone publique `leman-finance.example`, et un alias `portefeuilles.leman-finance.example` vers l'ALB.
- Un contrôle de santé HTTPS sur `/health` (toutes les 10 s, 2 échecs), l'alias principal qui en dépend, et un enregistrement de secours vers `203.0.113.50`.

Scripts : `scripts/m10-route53.ps1` et `scripts/m10-tests.ps1`.

![Module 10](../images/m10-route53.png)

| Zone | Nom | Cible |
|---|---|---|
| privée | `web.prod.leman.internal` | `10.20.0.10` |
| privée | `app.prod.leman.internal` | `10.20.1.10` |
| publique | `portefeuilles` (principal) | alias ALB, plus tard CloudFront, avec contrôle de santé |
| publique | `portefeuilles` (secours) | `203.0.113.50` |

## Si ça ne marche pas : quatre vérifications
1. La délégation : les serveurs de noms du bureau d'enregistrement sont-ils ceux de la zone ?
2. L'enregistrement : nom, type, politique de routage, alias.
3. L'état du contrôle de santé (`get-health-check-status`).
4. La cible : les groupes cibles de l'ALB sont-ils sains ?

## Résultats des tests
```
=== TP1 : zone privee prod.leman.internal (resolveur 10.20.0.2) ===
web-01 : Success	app -> 10.20.1.10 web -> 10.20.0.10 	
web-01 : Success	serveur DNS utilise : nameserver 10.20.0.2 	

=== TP2 : zone publique leman-finance.example (domaine fictif : pas de delegation NS reelle) ===
Serveurs NS de la zone : ns-905.awsdns-49.net, ns-1255.awsdns-28.org, ns-345.awsdns-43.com, ns-1952.awsdns-52.co.uk
Interrogation directe de ns-905.awsdns-49.net -> 16.192.43.233, 13.62.193.147
curl https://portefeuilles.leman-finance.example/ (resolution forcee vers l'ALB) -> web-01 TP-AC

=== TP3 : health check + failover ===
Health check 85a1e433-8d08-5102-09a7-699b813f0412 : Success   | reponse DNS : 16.192.43.233	13.62.193.147  (primaire = ALB)
nginx arrete sur web-01 -> apres 34 s : health check = Failure, reponse DNS = 203.0.113.50 (secondaire statique)
nginx relance -> apres 23 s : health check = Success, reponse DNS = 16.192.43.233	13.62.193.147 (retour au primaire)
```

## Nettoyage
Nous gardons les zones et les enregistrements pour les modules 11 et 12. Le contrôle de santé (environ 0,50 USD par mois) sera supprimé à la fin du cours.

## Ce qui diffère du sujet
Nous n'avons pas acheté de domaine, donc la délégation réelle est impossible. Nous interrogeons directement un serveur de noms de la zone (`Resolve-DnsName -Server ns-…`) et nous utilisons `route53 test-dns-answer` pour voir la réponse que Route 53 donnerait. Le contrôle de santé vise le nom DNS de l'ALB (puis de CloudFront), car notre nom public n'est pas résolvable.

## Captures

**Console AWS – enregistrements**

![Console AWS – enregistrements](../../captures/m10/00-console-enregistrements.png)

**Console AWS – zones**

![Console AWS – zones](../../captures/m10/00-console-zones.png)

**Terminal – zones**

![Terminal – zones](../../captures/m10/01-zones.png)

**Terminal – records**

![Terminal – records](../../captures/m10/02-records.png)

**Terminal – records privee**

![Terminal – records privee](../../captures/m10/03-records-privee.png)

**Journal des tests**

![Journal des tests](../../captures/m10/99-preuves-tests.png)


---

# Module 11 – CloudFront

## Objectif
Mettre un CDN devant l'ALB : garder en cache le contenu statique, ne jamais mettre l'API en cache, et empêcher l'accès direct à l'ALB.

## Ce qu'il faut savoir
CloudFront sert le contenu depuis un point de présence proche du visiteur. Les en-têtes de la réponse le montrent : `x-amz-cf-pop` donne le point de présence, `x-cache` indique `Hit` ou `Miss`. Chaque chemin (`/static/*`, `/api/*`, le reste) a sa politique de cache. Pour changer un fichier avant la fin du délai de cache, on lance une invalidation. Pour fermer l'ALB au reste du monde, son Security Group n'accepte que la liste de préfixes gérée par AWS pour CloudFront.

## Ce que nous avons fait
- La distribution `d-leman-portail-TP-AC`, avec l'ALB comme origine.
- Trois comportements : le défaut (aucun cache, cookies transmis), `/static/*` (cache de 24 h, sans cookies, compression) et `/api/*` (aucun cache, tous les en-têtes et cookies, méthodes GET à DELETE).
- Un fichier `/static/logo.png` sur `web-01`, qu'on modifie ensuite pour tester l'invalidation.
- `sg-alb` limité à la liste de préfixes CloudFront, et l'alias Route 53 déplacé vers CloudFront.

Script : `scripts/m11-cloudfront.ps1` (tests : `m11-tests.ps1`).

![Module 11](../images/m11-cloudfront.png)

| Comportement | Chemin | Cache | Méthodes |
|---|---|---|---|
| défaut | `*` | aucun | GET à DELETE |
| statique | `/static/*` | 86 400 s | GET, HEAD |
| API | `/api/*` | aucun | GET à DELETE |

## Si ça ne marche pas : quatre vérifications
1. Une erreur 403 : le Security Group de l'ALB laisse-t-il passer CloudFront ?
2. Une erreur 502 : l'origine répond-elle (Security Group, protocole, certificat) ?
3. L'en-tête `x-cache` : `Hit` attendu sur le statique, jamais sur l'API.
4. Le certificat : il doit couvrir le nom utilisé.

## Résultats des tests
```
=== TP1 : distribution E3HM34P4WV8A3X (domaine d14byb6fexq6px.cloudfront.net) ===
GET / (comportement par defaut, TTL 0) :
   HTTP/1.1 200 OK
   X-Cache: Miss from cloudfront
   X-Amz-Cf-Pop: ZRH52-P1

=== TP2 : comportements ===
/static/logo.png 1re requete (apres invalidation initiale) :
   HTTP/1.1 200 OK
   X-Cache: Miss from cloudfront
   X-Amz-Cf-Pop: ZRH52-P1
/static/logo.png 2e requete :
   HTTP/1.1 200 OK
   X-Cache: Hit from cloudfront
   X-Amz-Cf-Pop: ZRH52-P1
/api/health 1re :
   HTTP/1.1 200 OK
   X-Cache: Miss from cloudfront
   X-Amz-Cf-Pop: ZRH52-P1
/api/health 2e (jamais servi depuis le cache) :
   HTTP/1.1 200 OK
   X-Cache: Miss from cloudfront
   X-Amz-Cf-Pop: ZRH52-P1

=== TP3 : verrouillage de l'origine et invalidation ===
acces direct a l'ALB depuis Internet : http -> HTTP 000 (bloque : timeout) ; https -> HTTP 000 (bloque : timeout)
via CloudFront : web-01 TP-AC
origine modifiee en 'v2', sans invalidation, CloudFront sert encore : logo v1
apres invalidation IE26QTNMXYDW4LNLD4T9LXYDBL : logo v2

Route 53 : alias primaire -> CloudFront ; reponse DNS : 3.171.102.185	3.171.102.186	3.171.102.187	3.171.102.43
```

## Nettoyage
Nous gardons la distribution pour le module 12 et la désactiverons puis supprimerons à la fin du cours.

## Ce qui diffère du sujet
Sans domaine, nous ne pouvons pas avoir de certificat ACM validé : les visiteurs voient le certificat `*.cloudfront.net`. Pour la même raison, CloudFront joint l'ALB en HTTP (port 80) : il refuserait le certificat auto-signé de l'ALB. L'ALB a donc aussi un listener 80, fermé à Internet. Le préfixe CloudFront compte pour environ 55 règles dans un Security Group (limite 60), nous n'avons pu l'utiliser qu'une fois (port 80).

## Captures

**Console AWS – cloudfront**

![Console AWS – cloudfront](../../captures/m11/00-console-cloudfront.png)

**Terminal – distribution**

![Terminal – distribution](../../captures/m11/01-distribution.png)

**Journal des tests**

![Journal des tests](../../captures/m11/99-preuves-tests.png)


---

# Module 12 – CloudWatch et Flow Logs

## Objectif
Surveiller le site avec un tableau de bord, être prévenu par une alarme, et garder la trace des flux réseau pour comprendre un rejet.

## Ce qu'il faut savoir
Chaque service envoie des métriques à CloudWatch. Une alarme regarde une statistique sur plusieurs périodes et passe de `OK` à `ALARM` quand le seuil est franchi ; SNS envoie alors le message à ses abonnés. Les Flow Logs enregistrent chaque connexion acceptée (`ACCEPT`) ou refusée (`REJECT`) avec la source, le port et le protocole, et Logs Insights permet de les interroger. Nous gardons les journaux 3 jours pour limiter les coûts.

## Ce que nous avons fait
- Le tableau de bord `db-portail-leman-TP-AC` : cibles saines et non saines, temps de réponse de l'ALB, erreurs 5xx des cibles, taux d'erreurs 5xx de CloudFront.
- Le topic SNS `sns-exploitation-leman-TP-AC`, avec deux abonnés : une adresse e-mail de l'équipe et une file SQS qui nous sert de preuve de réception.
- L'alarme `alarm-5xx-portail-TP-AC` : plus de 5 erreurs 5xx en 5 minutes, pendant 2 périodes de suite ; elle prévient en passant en alarme et en revenant à la normale. Pour la tester, notre API renvoie une erreur 500 sur `/api/error`.
- Le groupe de logs `/leman/vpc-prod/flow-TP-AC`, un rôle IAM d'écriture et le Flow Log `fl-vpc-prod-leman-TP-AC` (tout le trafic).
- Une sonde TCP sur le port 22 depuis une machine non autorisée, retrouvée dans les journaux avec Logs Insights.

Scripts : `scripts/m12-monitoring.ps1` (mise en place) et `m12-tests.ps1`, `m12-flowlogs3.ps1`, `m12-flowlogs4.ps1` (preuves).

![Module 12](../images/m12-monitoring.png)

| Élément | Réglage |
|---|---|
| Alarme | `HTTPCode_Target_5XX_Count` supérieur à 5, période de 5 min, 2 périodes |
| Action | message SNS en alarme et au retour à la normale |
| Flow Log | tout le trafic, vers CloudWatch Logs, rétention 3 jours |

## Si ça ne marche pas : quatre vérifications
1. Quelle métrique dérive : erreurs 5xx, lenteur, cibles saines ?
2. L'état et l'historique de l'alarme.
3. Les journaux de flux : `filter action="REJECT" | stats count(*) by srcAddr, dstPort`.
4. Quelle règle de Security Group ou de NACL a refusé, d'après le port et l'interface.

## Résultats des tests
```
=== TP1 : tableau de bord ===
Tableau de bord : db-portail-leman-TP-AC
HealthyHostCount tg-web (derniere minute) : 1.0

=== TP3 : Flow Logs (SSH non autorise vers web-01) ===
6 tentatives de connexion TCP sur le port 22 de web-01 depuis cette machine (refusees par sg-web)

=== TP2 : alarme ===
Etat initial : INSUFFICIENT_DATA
Trafic 5xx genere pendant 10 min -> etat de l'alarme : ALARM
Notification SNS recue dans sqs-exploitation-leman-TP-AC : { "Type" : "Notification", "MessageId" : "c384ef0a-2ba5-5287-897d-8c7edf73d6a8", "TopicArn" : "arn:aws:sns:eu-north-1:000000000000:sns-exploitation-leman-TP-AC", "Subject" : "OK: \"alarm-5xx-portail-TP-AC\" in EU (Stockholm)", "Message" : "{\"AlarmName\":\"alarm-5xx-portail-TP-AC\",\"AlarmDescription\":\"TP-AC : plus de 5 erreurs 5xx cibles sur 5 min, 2 periodes consecutives\",\"AWSAccountId\":\"0...
Apres arret des erreurs (18 min) -> etat de l'alarme : OK
Notification de retour a la normale presente : oui

=== TP3 (reel) : Flow Logs ===
Controle : port 22 sortant depuis ce poste (github.com:22) -> ouvert
8 tentatives TCP vers le port 22 de l'ALB (2 noeuds publics) depuis ce poste (84.226.x.x) -> 8 timeout : refusees par sg-alb (seul le port 80 est ouvert, au prefixe CloudFront)
Recherche dans /leman/vpc-prod/flow-TP-AC (source = ce poste, port 22, REJECT) :
  2 000000000000 eni-034bc06f123a72b63 84.226.x.x 10.20.0.115 61404 22 6 2 104 1794837701 1794837721 REJECT OK
  2 000000000000 eni-034bc06f123a72b63 84.226.x.x 10.20.0.115 60965 22 6 2 104 1794837701 1794837721 REJECT OK
  2 000000000000 eni-034bc06f123a72b63 84.226.x.x 10.20.0.115 63656 22 6 2 104 1794837701 1794837721 REJECT OK
  2 000000000000 eni-034bc06f123a72b63 84.226.x.x 10.20.0.115 59395 22 6 2 104 1794837701 1794837721 REJECT OK
  2 000000000000 eni-05458be49638c7015 84.226.x.x 10.20.0.7 62411 22 6 2 104 1794837702 1794837733 REJECT OK
  2 000000000000 eni-05458be49638c7015 84.226.x.x 10.20.0.7 63203 22 6 2 104 1794837702 1794837733 REJECT OK
  2 000000000000 eni-05458be49638c7015 84.226.x.x 10.20.0.7 64715 22 6 2 104 1794837702 1794837733 REJECT OK
  2 000000000000 eni-05458be49638c7015 84.226.x.x 10.20.0.7 63102 22 6 2 104 1794837702 1794837733 REJECT OK
Requete Logs Insights : filter action = "REJECT" and dstPort = 22 and srcAddr = <ce poste> | stats count(*) as n by srcAddr, dstAddr, dstPort | sort n desc
Resultat : srcAddr=84.226.x.x dstAddr=10.20.0.115 dstPort=22 n=4 | srcAddr=84.226.x.x dstAddr=10.20.0.7 dstPort=22 n=4
Diagnostic : le rejet vient du Security Group sg-alb (port 22 non ouvert) : source, ENI de l'ALB, port 22 et action REJECT le prouvent.

=== TP3 (web-01) : Flow Logs, sonde SSH vers web-01 ===
Controle : https vers web-01 (443 ouvert) -> HTTP 000 pendant le script (web-01 venait de demarrer) ; controle refait a part, web-01 demarree : HTTP 200
10 tentatives TCP vers web-01:22 depuis une machine non autorisee (84.226.x.x) -> 10 timeout (sg-web n'ouvre le 22 qu'a la salle d'exploitation)
Recherche dans /leman/vpc-prod/flow-TP-AC (source = ce poste, destination 10.20.0.10, port 22, REJECT) :
  aucune ligne livree dans le delai
Requete Logs Insights : filter action = "REJECT" and dstPort = 22 and srcAddr = <ce poste> and dstAddr = "10.20.0.10" | stats count(*) as n by srcAddr, dstAddr, dstPort
Resultat : srcAddr=84.226.x.x dstAddr=10.20.0.10 dstPort=22 n=1
Diagnostic : rejet par sg-web (port 22 non ouvert a cette source) ; ENI de web-01, port 22, action REJECT.
```

## Nettoyage
Nous gardons le tableau de bord, l'alarme et le groupe de logs pour le module 13, puis nous supprimerons le Flow Log et les journaux à la fin du cours.

## Problèmes rencontrés
- Notre premier groupe de logs n'avait pas été créé (une erreur de notre script) ; le Flow Log affichait `DeliverLogsStatus=FAILED`. Nous avons recréé le groupe puis le Flow Log.
- La livraison dans CloudWatch Logs prend plusieurs minutes.
- Une adresse e-mail d'abonné SNS doit être confirmée par un clic sur le message reçu : sans cela, l'abonnement reste en attente.

## Captures

**Console AWS – alarme**

![Console AWS – alarme](../../captures/m12/00-console-alarme.png)

**Console AWS – tableau de bord**

![Console AWS – tableau de bord](../../captures/m12/00-console-tableau-de-bord.png)

**Terminal – alarm**

![Terminal – alarm](../../captures/m12/01-alarm.png)

**Terminal – flowlog**

![Terminal – flowlog](../../captures/m12/02-flowlog.png)

**Terminal – sns**

![Terminal – sns](../../captures/m12/03-sns.png)

**Journal des tests**

![Journal des tests](../../captures/m12/99-preuves-tests-1.png)

**Journal des tests**

![Journal des tests](../../captures/m12/99-preuves-tests-2.png)

**Journal des tests**

![Journal des tests](../../captures/m12/99-preuves-tests.png)


---

# Module 13 – CloudFormation

## Objectif
Décrire le réseau dans un template, le déployer en stack, relire les changements avant de les appliquer, détecter les écarts avec la réalité (drift) et prouver qu'on peut tout supprimer puis tout recréer à l'identique.

## Ce qu'il faut savoir
Un template contient des ressources, des paramètres (`Environnement`, `CidrVpc`…) et des sorties. La stack est le template déployé ; CloudFormation calcule l'ordre de création et supprime dans l'ordre inverse. Un change set montre ce qui sera ajouté, modifié ou remplacé avant d'exécuter. Le drift est l'écart entre ce qui existe vraiment et le template, par exemple après une modification à la main dans la console.

## Ce que nous avons fait
- `cfn/reseau-leman-etape1.yaml` : le VPC, trois sous-réseaux, l'IGW, la table publique et les trois Security Groups, avec les paramètres `Environnement` (prod ou dev) et `CidrVpc`. Nous l'avons validé avec `validate-template`, puis créé la stack `stack-portail-leman-TP-AC`.
- `cfn/reseau-leman.yaml` : le template complet, avec en plus `web-01`, `app-01` (adresses fixes), les deux groupes cibles, l'ALB (HTTPS 443, règle `/api/*`) et le rôle IAM des instances. Nous l'avons appliqué avec un change set que nous avons relu avant de l'exécuter.
- Un test de drift : une règle SSH ajoutée à la main sur le Security Group web est détectée (`DRIFTED`). Nous retirons la règle manuelle (la pile est de nouveau `IN_SYNC`), puis nous la déclarons dans le template (paramètre `AdminCidr`) et nous redéployons par change set : la règle appartient maintenant à la pile et la pile reste `IN_SYNC`. Un premier essai, où nous déclarions la règle sans retirer la manuelle, laissait la pile en `DRIFTED` (la règle existante n'avait pas la même description).
- La stack est supprimée, puis recréée à l'identique.

Scripts : `scripts/m13-cfn.ps1` (le scénario complet) et `scripts/m13-deploy.ps1` (tout déployer en une commande, certificat compris).

![Module 13](../images/m13-cloudformation.png)

| Paramètre | Valeur par défaut |
|---|---|
| `Environnement` | `prod` (ou `dev`) |
| `CidrVpc` | `10.30.0.0/22` (nous avons gardé `10.20.0.0/22` pour le lab fait à la main) |
| `WebPrivateIp` / `AppPrivateIp` | `10.30.0.10` / `10.30.1.10` |
| `AdminCidr` | vide (pas de règle SSH) |
| `CertificateArn` | à fournir (le script de déploiement l'importe) |

Sorties : `VpcId`, `AlbDns` et `SgWebId`.

## Si ça ne marche pas : quatre vérifications
1. L'état de la stack (`*_COMPLETE`, `*_FAILED`, `ROLLBACK_*`).
2. Les événements : la première ressource en `CREATE_FAILED` donne la raison.
3. Le drift : `detect-stack-drift` puis `describe-stack-resource-drifts`.
4. Le rollback : on corrige le template, jamais la ressource à la main.

## Résultats des tests
```
=== TP1 : validation et creation de la stack (reseau seul) ===
validate-template : parametres = CidrVpc	WebPrivateIp	AppPrivateIp	AdminCidr	Environnement	InstanceType	CertificateArn	AmiId
Statut : CREATE_COMPLETE ; sorties : VpcId	vpc-03d732488a1659ebc SgWebId	sg-05ed3128c6be342bb

=== TP2 : change set (instances, groupes cibles, ALB) ===
Change set cs-ajouts-505498746 : 7 changements ; actions = Add
   Add  Alb  AWS::ElasticLoadBalancingV2::LoadBalancer
   Add  App01  AWS::EC2::Instance
   Add  ListenerHttps  AWS::ElasticLoadBalancingV2::Listener
   Add  RuleApi  AWS::ElasticLoadBalancingV2::ListenerRule
   Add  TgApp  AWS::ElasticLoadBalancingV2::TargetGroup
   Add  TgWeb  AWS::ElasticLoadBalancingV2::TargetGroup
   Add  Web01  AWS::EC2::Instance
Statut apres execution : UPDATE_COMPLETE
Cibles : tg-web=healthy  tg-app=healthy
curl -k https://alb-prod-leman-cfn-TP-AC-1713432283.eu-north-1.elb.amazonaws.com/api/health -> app-01 TP-AC (cfn) /api/health
curl -k https://alb-prod-leman-cfn-TP-AC-1713432283.eu-north-1.elb.amazonaws.com/ -> web-01 TP-AC (cfn)

=== TP3 : drift, suppression, redeploiement ===
Regle SSH ajoutee a la main sur sg-web-cfn -> drift stack : DETECTION_COMPLETE	DRIFTED
Detail : SgWeb	MODIFIED	/SecurityGroupIngress/1	ADD
Regle manuelle retiree -> drift stack : DETECTION_COMPLETE	IN_SYNC
Change set cs-declaration-template-1149632398 : 1 changements ; actions = Modify
   Modify  SgWeb  AWS::EC2::SecurityGroup
Regle declaree dans le template (AdminCidr) puis redeploiement -> statut : UPDATE_COMPLETE
Apres correction par le template -> drift stack : DETECTION_COMPLETE	IN_SYNC
Regles de sg-web-cfn : tcp	80	None	sg-018397dd4dbc1dd12 tcp	22	203.0.113.0/24	None
Suppression de la stack (ordre inverse des dependances) : 2 min -> DELETE_COMPLETE (stack disparue)
VPC restants avec le tag de la stack : 0
Change set cs-redeploiement-222070138 : 7 changements ; actions = Add
   Add  Alb  AWS::ElasticLoadBalancingV2::LoadBalancer
   Add  App01  AWS::EC2::Instance
   Add  ListenerHttps  AWS::ElasticLoadBalancingV2::Listener
   Add  RuleApi  AWS::ElasticLoadBalancingV2::ListenerRule
   Add  TgApp  AWS::ElasticLoadBalancingV2::TargetGroup
   Add  TgWeb  AWS::ElasticLoadBalancingV2::TargetGroup
   Add  Web01  AWS::EC2::Instance
Redeploiement : UPDATE_COMPLETE ; cibles tg-web=healthy tg-app=healthy ; curl -k https://alb-prod-leman-cfn-TP-AC-267212375.eu-north-1.elb.amazonaws.com/api/health -> app-01 TP-AC (cfn) /api/health
```

## Nettoyage
Nous gardons le template et la stack. La stack contient des instances et un ALB (facturés) : nous la supprimerons à la fin du cours avec `aws cloudformation delete-stack`.

## Problèmes rencontrés
Deux erreurs de notre part : les descriptions des Security Groups ne peuvent pas contenir d'apostrophes ni d'accents, et notre premier calcul des sous-réseaux avec `!Cidr` donnait au sous-réseau privé une plage qui ne contenait pas l'adresse fixe d'`app-01`. Nous n'avons pas mis de NAT dans la stack (coût) : `app-01` n'a pas besoin de paquets, mais elle n'est donc pas joignable par SSM.


## Captures

**Console AWS – piles cloudformation**

![Console AWS – piles cloudformation](../../captures/m13/00-console-piles-cloudformation.png)

**Terminal – stack**

![Terminal – stack](../../captures/m13/01-stack.png)

**Journal des tests**

![Journal des tests](../../captures/m13/99-preuves-tests-1.png)

**Journal des tests**

![Journal des tests](../../captures/m13/99-preuves-tests-2.png)
