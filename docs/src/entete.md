# Satom Cloud Network – Dossier de réalisation (équipe TP-AC)

**Client** : Groupe Léman Finance SA – **Intégrateur** : Satom IT & Learning Solutions – **Équipe** : TP-AC (Thomas Prud'homme, Abderahmane Chaouche)
**Formation** : AWS niveau 300 « Intégrer des services réseau multiplateformes » – Geneva Institute of Technology, promotion E3 – semaine du 16 au 20 novembre 2026
**Région de travail** : Europe (Stockholm) `eu-north-1` – **Tags** : `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=prod|dev`

## Vidéo de rendu
<video controls preload="metadata" width="100%" src="https://raw.githubusercontent.com/Thomas-TP/satom-cloud-network-TP-AC/main/video/satom-cloud-network-TP-AC.mp4"></video>

Si le lecteur ne s'affiche pas : [voir la vidéo sur GitHub](https://github.com/Thomas-TP/satom-cloud-network-TP-AC/blob/main/video/satom-cloud-network-TP-AC.mp4) (durée environ 8 min : schémas, captures de la console AWS et preuves de tests, module par module).
## Sommaire
| Module | Sujet | Statut |
|---|---|---|
| 0 | Cadrage, mandat, équipe, plan d'adressage | ✔ |
| 1 | VPC et sous-réseaux | ✔ déployé et testé |
| 2 | Routage : IGW et NAT | ✔ déployé et testé |
| 3 | Security Groups et NACL | ✔ déployé et testé |
| 4 | Network Firewall | ◐ bloqué par l'organisation : architecture, template validé, procédure |
| 5 | VPC Peering | ✔ déployé et testé |
| 6 | Transit Gateway | ◐ bloqué par l'organisation : architecture, template validé, procédure |
| 7 | VPN site à site | ✔ simulé (IPsec strongSwan réel) |
| 8 | Direct Connect | ✔ simulé (GRE + BGP FRRouting) |
| 9 | Elastic Load Balancing | ✔ déployé et testé |
| 10 | Route 53 | ✔ déployé et testé |
| 11 | CloudFront | ✔ déployé et testé |
| 12 | CloudWatch et Flow Logs | ✔ déployé et testé |
| 13 | CloudFormation | ✔ déployé, drift, suppression/redéploiement testés |

![Schéma réseau final](../images/global.png)

Dépôt du code, des scripts et des preuves : dépôt GitHub public `Thomas-TP/satom-cloud-network-TP-AC`. Les captures de preuve sont dans `captures/mNN/` : captures **réelles de la console AWS** (fichiers `00-console-*.png`, l'identifiant de compte est masqué), tableaux d'état issus de l'AWS CLI et journaux de tests (`99-preuves-tests.png`).




