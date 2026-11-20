# Satom Cloud Network – Dossier du binôme TP-AC

Projet réalisé par Thomas Prud'homme et Abderahmane Chaouche pour le client fictif Groupe Léman Finance SA (formation AWS niveau 300, Geneva Institute of Technology, promo E3, semaine du 16 au 20 novembre 2026).

## Lire le dossier

| [Partie 1]({{URL_partie1}}) | [Partie 2]({{URL_partie2}}) | [Partie 3]({{URL_partie3}}) |
|:---:|:---:|:---:|
| **[modules 0 à 4]({{URL_partie1}})**<br>cadrage, réseaux, routage, sécurité, pare-feu | **[modules 5 à 8]({{URL_partie2}})**<br>peering, Transit Gateway, VPN, Direct Connect | **[modules 9 à 13]({{URL_partie3}})**<br>ALB, Route 53, CloudFront, surveillance, CloudFormation |

Tout le TP a été fait à la main dans la console AWS, puis filmé : les captures de ce dossier viennent de ces enregistrements.

Tout est fait dans la région de Stockholm (`eu-north-1`). Nos ressources portent le suffixe `-TP-AC` et les tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC` et `Environnement=prod` ou `dev`.

Les modules 9, 10 et 11 utilisent un domaine réel : le sous-domaine `leman.thomastp.ch`, délégué à Route 53, avec des certificats publics ACM validés par DNS.

## Vidéo
{%youtube emZqnBNtOjM %}

Vidéo complète du tutoriel (34 minutes, voix de Thomas et d'Abderahmane), refaite à la main dans la console AWS, modules 0 à 13, avec un vrai domaine pour les modules 9 à 11 : [https://youtu.be/emZqnBNtOjM](https://youtu.be/emZqnBNtOjM) (non répertoriée : seules les personnes qui ont le lien peuvent la voir).

## Où nous en sommes

| Module | Sujet | État | Lire |
|---|---|---|---|
| 0 | Cadrage et plan d'adressage | terminé | **[Partie 1]({{URL_partie1}})** |
| 1 | VPC et sous-réseaux | terminé | **[Partie 1]({{URL_partie1}})** |
| 2 | Routage, IGW et NAT | terminé | **[Partie 1]({{URL_partie1}})** |
| 3 | Security Groups et NACL | terminé | **[Partie 1]({{URL_partie1}})** |
| 4 | Network Firewall | terminé | **[Partie 1]({{URL_partie1}})** |
| 5 | VPC Peering | terminé | **[Partie 2]({{URL_partie2}})** |
| 6 | Transit Gateway | terminé | **[Partie 2]({{URL_partie2}})** |
| 7 | VPN site à site | terminé | **[Partie 2]({{URL_partie2}})** |
| 8 | Direct Connect | terminé | **[Partie 2]({{URL_partie2}})** |
| 9 | Load balancer | terminé | **[Partie 3]({{URL_partie3}})** |
| 10 | Route 53 | terminé | **[Partie 3]({{URL_partie3}})** |
| 11 | CloudFront | terminé | **[Partie 3]({{URL_partie3}})** |
| 12 | CloudWatch et Flow Logs | terminé | **[Partie 3]({{URL_partie3}})** |
| 13 | CloudFormation | terminé | **[Partie 3]({{URL_partie3}})** |

![Schéma réseau final](https://raw.githubusercontent.com/Thomas-TP/satom-cloud-network-TP-AC/main/docs/images/global.png)

Tout le code (scripts AWS CLI, templates CloudFormation), les preuves et les captures sont dans le dépôt GitHub public `Thomas-TP/satom-cloud-network-TP-AC`.
