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
| 4 | Network Firewall | déployé et testé (service débloqué le 17/11) |
| 5 | VPC Peering | déployé et testé, puis remplacé par le Transit Gateway au module 6 |
| 6 | Transit Gateway | déployé et testé |
| 7 | VPN site à site | vrai VPN AWS, 2 tunnels par site ; les deux sites sont des routeurs strongSwan simulés |
| 8 | Direct Connect | vrai Direct Connect Gateway associé au Transit Gateway ; la liaison dédiée est simulée (GRE et BGP) |
| 9 | Load balancer | déployé et testé |
| 10 | Route 53 | déployé et testé |
| 11 | CloudFront | déployé et testé |
| 12 | CloudWatch et Flow Logs | déployé et testé |
| 13 | CloudFormation | déployé et testé |

Au début de la semaine, Network Firewall, Transit Gateway, VPN et Direct Connect étaient refusés par une règle de l'organisation AWS du formateur. Cette règle a été levée le 17/11/2026, et nous avons alors fait les modules 4, 6, 7 et 8 pour de vrai. Les erreurs relevées avant cette date sont dans le fichier `docs/01-services-bloques.md` du dépôt.

![Schéma réseau final](../images/global.png)

Tout le code (scripts AWS CLI, templates CloudFormation), les preuves et les captures sont dans le dépôt GitHub public `Thomas-TP/satom-cloud-network-TP-AC`.
