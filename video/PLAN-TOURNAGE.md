# Plan de tournage : tutoriel vidéo, tout dans la console AWS (équipe TP-AC)

Tout est supprimé côté AWS (vérifié : 0 VPC, 0 instance, 0 zone, 0 CloudFront, 0 rôle, 0 pile, 0 secret, 0 budget `TP-AC` ; les 16 VPC des autres élèves sont intacts). On repart de zéro, et **chaque ressource est créée à la main dans la console**, devant la caméra.

## Règles de tournage
- **Image** : Chrome dédié, 1920×1080, 30 i/s, curseur visible, clic animé, texte tapé comme un humain. Interface en français, région Stockholm.
- **Vie privée** : les lignes d'autres élèves sont masquées pendant le tournage ; le coin haut droit (compte) est flouté au montage ; pas de mot de passe ni de clé à l'écran.
- **Aucun terminal local** : pour les routeurs, seulement Session Manager ou CloudShell, ouverts dans la console.
- **Attentes** (NAT, pare-feu, Transit Gateway, VPN, CloudFront…) : accélérées au montage avec une pastille « accéléré ×N ».
- **Voix** : Thomas (intro, modules 0–3, 7, 8, fin) et Abderahmane (modules 4–6, 9–13), sous-titres synchronisés.
- **Coût** : le tournage garde les ressources chères le moins longtemps possible (NAT 0,045 USD/h, pare-feu 0,40 USD/h, Transit Gateway, VPN et ALB en bloc). Budget total estimé : moins de 20 USD sur les 180 USD de crédits.

## Déroulé par module (ce qui sera filmé)
| Module | Ce qu'on crée dans la console | Preuve montrée à l'écran |
|---|---|---|
| 0 Cadrage | Budget `budget-TP-AC-satom` (100 USD, alerte à 80 %), balises de coûts ; plan d'adressage affiché | Page Budgets, ligne d'alerte |
| 1 Réseaux | VPC `vpc-prod-leman-TP-AC` (10.20.0.0/22), sous-réseaux public 10.20.0.0/26 et privé 10.20.1.0/26, rôle IAM SSM + profil, instances `web-01` et `app-01` (t3.micro, AL2023), test de chevauchement refusé | Liste des sous-réseaux, instances en cours d'exécution |
| 2 Routage | Internet Gateway, table `rt-public` (0.0.0.0/0 → IGW), NAT Gateway + Elastic IP, table `rt-prive` (0.0.0.0/0 → NAT), test de panne en retirant la route | Tables de routage, `curl checkip` dans Session Manager |
| 3 Sécurité | Security Groups web / app / alb / dev, NACL publique, test 8080 ouvert et 22 fermé | Règles des groupes, résultat des tests |
| 4 Network Firewall | Sous-réseau pare-feu, groupes de règles (VPC autorisé, domaines `.amazonlinux.com` et `.amazonaws.com`), politique en ordre strict, pare-feu, routes, journaux d'alertes et de flux | Journaux CloudWatch du flux bloqué et du flux autorisé |
| 5 Peering | VPC dev (10.21.0.0/24), peering, routes, test du chevauchement refusé et de la non-transitivité, puis suppression | Connexion active puis supprimée |
| 6 Transit Gateway | TGW, 2 attachements, 2 tables (prod / dev), associations et propagations, routes dans les VPC | Tables et routes du TGW, curl dev-01 → app-01 |
| 7 VPN | Customer Gateways, 2 VPN statiques sur le TGW (2 tunnels chacun), secret des clés, 2 routeurs strongSwan (VPC simulés siège et agence), routes TGW | Tunnels « Haut », ping et curl depuis les sites |
| 8 Direct Connect | Direct Connect Gateway (ASN 64513) associée au TGW ; routeurs FRRouting, GRE et BGP simulés | Associations, sessions BGP, bascule |
| 9 ALB | 2 groupes cibles, ALB, listeners (HTTPS 443 avec certificat importé, règle `/api/*`), test de panne d'une cible | Cibles « healthy » puis « unhealthy » |
| 10 Route 53 | Zone privée `prod.leman.internal`, zone publique `leman-finance.example`, enregistrements, health check, basculement | Réponses DNS, état du health check |
| 11 CloudFront | Distribution (origine ALB, 2 comportements), politique de cache, ALB limité à CloudFront | En-têtes Miss puis Hit |
| 12 Surveillance | Tableau de bord, alarme 5xx, SNS + SQS, Flow Logs, Logs Insights | Alarme en alerte puis OK, requête Logs Insights |
| 13 CloudFormation | Pile du portail (téléversement du modèle), change set, détection de dérive | Événements de la pile, dérive détectée puis corrigée |

## Ce qui reste simulé, dit à l'écran
Les deux sites (siège et agence) sont des instances EC2 dans des VPC séparés ; la liaison « Direct Connect » est un tunnel GRE avec BGP ; pas de domaine réel ; pas de bascule VPN « sans coupure » (voir `docs/02-ecarts-au-sujet.md`).

## Calendrier (avec ta validation à la fin de chaque bloc)
1. **Bloc A** : modules 0 à 3 (créés puis arrêtés si besoin : NAT dès le module 2) → je te montre l'extrait.
2. **Bloc B** : modules 4 à 6.
3. **Bloc C** : modules 7 et 8 (le plus long : VPN, routeurs, BGP).
4. **Bloc D** : modules 9 à 13.
5. **Montage** : version complète d'environ 30 minutes, puis version courte de 7 à 8 minutes, voix, sous-titres, floutage.

## Texte de narration du bloc A (à valider)
Les textes suivants sont lus par Thomas. Les nombres suisses (septante, huitante, nonante) sont respectés.

**Introduction** : « Bonjour, nous sommes Thomas et Abderahmane. Pour le groupe Léman Finance, nous construisons sur AWS un réseau complet, qui relie un siège, une agence et le cloud. Dans cette vidéo, nous le créons de A à Z dans la console, et nous le testons à chaque étape. »

**Module 0, le cadrage** : « Avant de créer quoi que ce soit, nous fixons les règles. Chaque ressource porte le suffixe T-P-A-C et trois étiquettes : projet, équipe et environnement. Le plan d'adressage est écrit à l'avance : dix point vingt pour la production, dix point vingt et un pour le développement. Dernier garde-fou : un budget de cent dollars, avec une alerte à huitante pour cent. »

**Module 1, les réseaux** : « Nous créons le V-P-C de production avec la plage dix point vingt point zéro barre vingt-deux. Le sujet propose un barre seize, mais c'est beaucoup trop grand pour deux serveurs. Dedans, un sous-réseau public et un sous-réseau privé, tous deux dans la zone A. AWS garde cinq adresses par sous-réseau : un barre vingt-six offre donc cinquante-neuf adresses utilisables. Nous essayons ensuite de créer un sous-réseau qui chevauche le premier : AWS le refuse, comme prévu. Puis le rôle I-A-M qui permet d'administrer les machines sans S-S-H, et les deux instances : web zéro un dans le public, app zéro un dans le privé. »

**Module 2, le routage** : « Pour l'instant, rien ne sort du réseau. Nous créons une passerelle Internet, et une table de routage publique dont la route par défaut vise cette passerelle. Pour le sous-réseau privé, nous plaçons une passerelle N-A-T dans le public : les serveurs privés pourront sortir, mais personne ne pourra entrer. La preuve : depuis app zéro un, qui n'a pas d'adresse publique, Internet nous voit avec l'adresse de la N-A-T. Puis un test de panne : nous retirons la route par défaut, la sortie s'arrête, nous la remettons et tout repart. »

**Module 3, la sécurité** : « Les Security Groups retiennent l'état des connexions : une réponse est autorisée sans règle de retour. Nous créons un groupe par rôle, avec le minimum de règles : web, application, load balancer et développement. La liste de contrôle d'accès du réseau, elle, filtre dans les deux sens et sans mémoire. Le test : depuis dev zéro un, le port huit mille huitante de app zéro un répond, et le port vingt-deux reste fermé. »

## Questions encore ouvertes pour toi
- Veux-tu garder les phrases d'introduction ci-dessus, ou en changer le ton ?
- Pour le module 0, as-tu des précisions sur les rôles du client (je les ai supposés) ?
