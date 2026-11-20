# Journal de projet et nettoyage (équipe TP-AC)

Le compte AWS est partagé avec toute la classe : nous ne touchons jamais aux ressources des autres équipes (suffixes `_bko`, `-TM`, `_af`, `-MF`, `-AA`, `-AM`, `-LL`…). Toutes nos ressources portent `-TP-AC` et le tag `Equipe=TP-AC`. Chaque suppression a été faite par ce tag ou par l'identifiant exact de la ressource, jamais par un nom approximatif.

## Où nous en sommes (20/11/2026)
Le TP est terminé et filmé. Tout ce qui était facturé à l'heure est supprimé, **sauf un Network Firewall que nous n'arrivons pas à supprimer** (voir plus bas). Il reste aussi quelques ressources gratuites ou presque.

### Ce qui reste, et pourquoi
| Ressource | Coût | Pourquoi elle reste |
|---|---|---|
| Network Firewall `nfw-prod-leman-TP-AC` | ~0,40 USD/h | `DeleteFirewall` répond `InternalServerError: Internal failure` : état bloqué côté AWS. Cas AWS Support n° 179508151300233 ouvert. |
| VPC `vpc-prod-leman-ancien-TP-AC` et le sous-réseau du pare-feu | gratuit | le point d'accès du pare-feu est dans `sub-public-1b-TP-AC` : ce sous-réseau et son VPC ne peuvent partir qu'avec lui |
| VPC `vpc-siege-TP-AC`, `vpc-agence-TP-AC`, `vpc-dev-leman-TP-AC` et leurs sous-réseaux | gratuit | vides ; supprimés avec le reste quand le pare-feu sera débloqué |
| 2 Customer Gateways | gratuit | idem |
| Rôle IAM `TP-AC-ec2-ssm-role` (accès Systems Manager des instances) | gratuit | pas facturé ; supprimé avec le reste |
| Secret `Projet/SatomCloudNetwork/vpn` | ~0,40 USD/mois | contient les clés des VPN (jamais copiées dans le dépôt) |
| Groupes de journaux CloudWatch (`/leman/vpc-prod/flow-TP-AC`, journaux du pare-feu) | négligeable | conservés tant que le pare-feu existe |

La politique `policy-prod-leman-TP-AC` et le groupe de règles `rg-depots-autorises-TP-AC` sont rattachés au pare-feu et partiront avec lui.

### Le Network Firewall bloqué
La suppression échoue depuis la console et depuis la CLI. Nous avons vérifié et écarté les causes habituelles : protection contre la suppression désactivée, plus aucune route vers l'endpoint, journalisation retirée, tag `AWSNetworkFirewallManaged` absent, rôle lié au service en place. Nous avons aussi essayé un contournement (ajouter un second sous-réseau, retirer le premier) : l'ancien endpoint disparaît d'EC2, mais l'attachement reste en `DELETING` côté Network Firewall et l'erreur revient. Le pare-feu est maintenant rattaché à `sub-public-1b-TP-AC`. Le cas AWS Support (Compte et facturation, plan Basic) demande la suppression et l'arrêt de la facturation. Dès qu'il est supprimé, il faut supprimer la politique et le groupe de règles, puis les VPC et les Customer Gateways de la liste ci-dessus.

## Ce qui a été supprimé à la fin du tournage (20/11/2026)
Pour les modules 9 à 11, refaits avec le vrai domaine `leman.thomastp.ch`, tout ce que nous avions créé a été supprimé, dans cet ordre :
1. Distribution CloudFront : alias et certificat retirés, désactivée, puis supprimée.
2. Zones Route 53 `leman.thomastp.ch` (avec `origin`, `portefeuilles` principal et secours, `cdn`, CNAME de validation ACM) et `prod.leman.internal`, puis la surveillance de l'état `hc-portail-TP-AC`.
3. ALB `alb-prod-leman-TP-AC`, groupes cibles `tg-web-TP-AC` et `tg-app-TP-AC`, Security Group `alb-TP-AC` (et la règle 8080 qui y faisait référence).
4. Pile CloudFormation de tournage `env-m9-m11-TP-AC` (VPC, sous-réseaux, passerelle Internet, `web-01-TP-AC`, `app-01-TP-AC`, rôle SSM).
5. Certificats ACM `leman.thomastp.ch` d'`eu-north-1` et d'`us-east-1`.
6. Chez Cloudflare : les quatre enregistrements NS du sous-domaine `leman` ont été retirés. Le reste de la zone `thomastp.ch` (le portfolio de Thomas) n'a jamais été modifié.

Avant cela, après la vidéo des modules 0 à 8 et 12 à 13 (journal du 19/11 ci-dessous), les instances, Elastic IP, NAT, VPN, Transit Gateway, Direct Connect Gateway, SNS/SQS, tableau de bord, alarme et Flow Log avaient déjà été supprimés. Nous avons vérifié le 20/11 qu'il ne reste aucune instance, NAT, Elastic IP, Transit Gateway, connexion VPN ni Direct Connect Gateway à notre nom.

## Journal des suppressions
| Date | Ressource | Justification |
|---|---|---|
| 16/11/2026 | Quêtes de crédits : instance EC2 de test, fonction Lambda + rôle + logs, table DynamoDB, base RDS `tp-ac-quest-db` | supprimées dès la quête validée (consigne) |
| 16/11/2026 | `sub-fw-1a`, `rt-fw-leman` | module 4 impossible (SCP), ressources inutiles |
| 16/11/2026 | VPC de test (chevauchement, tiers), peering de test, instance `tiers-01` | ressources de test supprimées après mesure |
| 16/11/2026 | Tentatives `m07` (routeur, groupes de sécurité) | échec quota Elastic IP / vCPU : recréé autrement |
| 17/11/2026 | Pare-feu `nfw-prod-leman-TP-AC`, sa politique, ses 2 groupes de règles, `sub-fw-1a`, `rt-fw-leman`, groupe de journaux conservé | tests du module 4 terminés (facturé à l'heure) |
| 17/11/2026 | 2e Transit Gateway créé par erreur par notre script (+ 2 attachements) | doublon, supprimé |
| 17/11/2026 | Direct Connect Gateway de test (ASN 64512) | mauvais ASN (même ASN que le Transit Gateway), recréé avec 64513 |
| 17/11/2026 | Peering `pcx-lab-TP-AC` | supprimé au module 6, comme demandé par le sujet |
| 17/11/2026 (nuit) | Stack `stack-interconnexion-leman-TP-AC` (pare-feu, Transit Gateway, 2 VPN, 2 Customer Gateways, DX Gateway, Elastic IP des routeurs), stack `stack-portail-leman-TP-AC` (instances + ALB), ALB `alb-prod-leman-TP-AC` et ses listeners, NAT Gateway + Elastic IP, Elastic IP de `web-01`, health check Route 53 | vidéo et dossier validés par Thomas ; plus aucune ressource facturée à l'heure |
| 19/11/2026 | Tout le TP refait à la main en console puis filmé : instances (6), Elastic IP (3), NAT, 2 VPN, Transit Gateway et attachements, ALB et groupes cibles, CloudFront, zones Route 53 et health check, DX Gateway, secret, SNS/SQS, tableau de bord, alarme, Flow Log, groupes de journaux | vidéo validée par Thomas, plus rien à filmer |
| 20/11/2026 | Distribution CloudFront, zones Route 53 (publique `leman.thomastp.ch` et privée `prod.leman.internal`), surveillance de l'état, ALB, groupes cibles, Security Group `alb-TP-AC`, pile `env-m9-m11-TP-AC`, certificats ACM, 4 enregistrements NS chez Cloudflare | fin du tournage des modules 9 à 11 avec le vrai domaine |

## Événements du 16/11/2026 à retenir
| Heure | Événement |
|---|---|
| 14:28 | `web-01-TP-AC` et `app-01-TP-AC` arrêtés par une autre session du rôle partagé (visible dans CloudTrail) ; les 16 vCPU du compte sont ensuite saturés par 8 instances de la classe : impossible de redémarrer nos instances tant que de la place n'est pas libérée |
| fin de journée | Instances TP-AC toutes à l'état `stopped` |

Le quota de vCPU du compte partagé est de 48. Une demande d'augmentation à 64 est restée ouverte, sans effet utile.

## Rejouer le projet
Pour rejouer le TP, il faudrait recréer l'environnement : les scripts `scripts/mNN-*.ps1` et les modèles `cfn/*.yaml` datent de notre première exécution en ligne de commande. Les scènes de tournage `video/shoot/*.py` décrivent, clic par clic, ce que nous avons fait dans la console.
