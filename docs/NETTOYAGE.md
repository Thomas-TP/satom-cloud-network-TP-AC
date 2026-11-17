# Journal de projet et plan de nettoyage (équipe TP-AC)

Le compte AWS est **partagé** : on ne touche jamais aux ressources des autres équipes (suffixes `_bko`, `-TM`, `_af`, `-MF`, `-AA`…). Toutes nos ressources portent `-TP-AC` et le tag `Equipe=TP-AC` ; la suppression se fait **uniquement** par ce tag ou par les identifiants du fichier d'état local.

## Ressources facturées à l'heure (à supprimer en premier)
| Ressource | Coût approximatif | Quand supprimer |
|---|---|---|
| NAT Gateway `nat-prod-leman-TP-AC` + Elastic IP | ~0,045 USD/h + IP | dès que SSM sur `app-01` n'est plus nécessaire |
| ALB `alb-prod-leman-TP-AC` | ~0,03 USD/h | fin du projet |
| Instances EC2 (`web-01`, `app-01`, `dev-01`, routeurs) | ~0,01 USD/h chacune | arrêtées hors séance, supprimées en fin de projet |
| Stack `stack-portail-leman-TP-AC` (instances + ALB) | ~0,04 USD/h | fin du projet |
| Health check Route 53 | ~0,50 USD/mois | fin du projet |
| Transit Gateway : 4 attachements (prod, dev, 2 VPN) + 1 association DX Gateway | ~0,05 USD/h chacun | après les captures et la vidéo (`scripts/m06-m08-cleanup.ps1`) |
| 2 connexions VPN (siège, agence) | ~0,05 USD/h chacune | idem |
| 3 Elastic IP (`rtr-siege`, `rtr-agence`, `rtr-aws`) | ~0,005 USD/h chacune | idem |
| Network Firewall | ~0,40 USD/h | déjà supprimé après les tests du 17/11 |

## Ordre de suppression en fin de projet
0. Modules 6 à 8 : `scripts/m06-m08-cleanup.ps1` (routes, DX Gateway, VPN, Customer Gateways, attachements, tables, Transit Gateway, Elastic IP).
1. Stack CloudFormation : `aws cloudformation delete-stack --stack-name stack-portail-leman-TP-AC`.
2. Alarme, tableau de bord, topic SNS + file SQS, Flow Log, groupes de logs.
3. CloudFront : désactiver puis supprimer `d-leman-portail-TP-AC` (+ politique de cache).
4. Route 53 : health check, enregistrements puis zones.
5. ALB, listeners, groupes cibles ; certificat ACM importé.
6. Routeurs simulés, VPC `siege`/`agence`, secret `Projet/SatomCloudNetwork/vpn`.
7. Peering, VPC dev, instances, NAT + Elastic IP, IGW, sous-réseaux, tables, Security Groups, NACL, VPC prod.
8. Rôles IAM `TP-AC-*` et profil d'instance.

## Journal des suppressions déjà effectuées
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

## Ressources actuellement conservées
VPC prod + dev, sous-réseaux, IGW, tables, SG, NACL, NAT, Transit Gateway (3 tables, 4 attachements), 2 VPN, 2 Customer Gateways, DX Gateway, 3 Elastic IP, ALB, groupes cibles, zones Route 53, CloudFront, tableau de bord, alarme, SNS/SQS, Flow Logs, secret VPN, rôles IAM `TP-AC-*`.

## Événements du 16/11/2026 à retenir
| Heure | Événement |
|---|---|
| 14:28 | `web-01-TP-AC` et `app-01-TP-AC` arrêtés par une autre session du rôle partagé (voir CloudTrail) ; les 16 vCPU du compte sont ensuite saturés par 8 instances de la classe : impossible de redémarrer nos instances tant que de la place n'est pas libérée |
| fin de journée | Instances TP-AC toutes à l'état `stopped` ; routeurs simulés, instances CloudFormation et dev arrêtés |

## Coût actuel (ressources facturées même instances arrêtées)
NAT Gateway (~1,1 USD/jour), 2 ALB (manuel + stack, ~1,3 USD/jour), health check Route 53, 2 Elastic IP, volumes EBS, CloudFront et SNS/SQS négligeables. Le coût cumulé du projet reste très inférieur aux crédits du compte (180 USD).

