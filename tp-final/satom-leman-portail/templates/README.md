# templates/

Un fichier CloudFormation par domaine, comme le demande le sujet : `reseau.yaml`, `securite.yaml`, `calcul.yaml`, `edge.yaml`, `supervision.yaml` (et d'autres si utile : `interconnexion.yaml`).

## `_depart/` : ce qu'on reprend du TP réseau
| Fichier | Contenu | À faire |
|---|---|---|
| `reseau-leman-etape1.yaml` | VPC, trois sous-réseaux, IGW, table publique, trois Security Groups, rôle et profil SSM (15 ressources) | découper en `reseau.yaml` et `securite.yaml` ; ajouter NAT, table privée, NACL ; tag `Module` |
| `reseau-leman.yaml` | le précédent + `web-01`, `app-01`, ALB, groupes cibles, listener HTTPS, règle `/api/*` | `calcul.yaml` (instances) et un modèle ALB ; politique TLS 1.2 minimum ; journaux d'accès |
| `interconnexion-leman.yaml` | Network Firewall, Transit Gateway et tables, deux VPN, Direct Connect Gateway (ressource personnalisée Lambda), routes | `interconnexion.yaml` découpé par sprint (4, 6, 7, 8) ; alarme `TunnelState` ; routeurs de site hors modèle à écrire |

Ils ont été écrits pour le TP réseau (noms `-TP-AC`, région `eu-north-1`). Les paramètres de ces modèles sont déjà des valeurs à passer, jamais des secrets : les clés des VPN se lisent dans Secrets Manager par référence dynamique.

## Règles pour chaque modèle
- Passe `cfn-lint` et `cfn-guard` (ou `checkov`) sans échec critique.
- Aucun port d'administration ouvert à `0.0.0.0/0`.
- Chiffrement (KMS) des journaux, volumes et compartiments.
- Tags obligatoires sur chaque ressource.
- Déploiement par **change set**, jamais de suppression non confirmée.
