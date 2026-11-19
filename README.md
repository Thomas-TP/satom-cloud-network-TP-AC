# TP-AC – Satom Cloud Network (Groupe Léman Finance SA)

Équipe **TP-AC** : Thomas Prud'homme, Abderahmane Chaouche – Formation AWS niveau 300 (Geneva Institute of Technology, promo E3, 16-20 novembre 2026).
Région : **eu-north-1 (Stockholm)** – tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=prod|dev`. **Aucun secret dans ce dépôt.**

## Livrables
| Livrable | Fichier |
|---|---|
| Dossier complet (modules 0 à 13, cours, schémas, tableaux, procédures, preuves) | [`docs/DOSSIER.md`](docs/DOSSIER.md) (un fichier par module dans `docs/modules/`) |
| Schéma réseau final (WAN) | [`docs/images/global.png`](docs/images/global.png) |
| Plan d'adressage | [`docs/00-plan-adressage.md`](docs/00-plan-adressage.md) |
| Dossier client (10 pages max) | [`docs/CLIENT.md`](docs/CLIENT.md) |
| Template CloudFormation (module 13) | [`cfn/reseau-leman.yaml`](cfn/reseau-leman.yaml) (+ `reseau-leman-etape1.yaml`) et [`cfn/interconnexion-leman.yaml`](cfn/interconnexion-leman.yaml) (pare-feu, Transit Gateway, VPN, DX Gateway) |
| Procédures de test | section « Procédure de test / diagnostic » de chaque module |
| Services bloqués par l'organisation | [`docs/01-services-bloques.md`](docs/01-services-bloques.md) |
| Points du sujet impossibles ou incohérents (pour le formateur) | [`docs/02-ecarts-au-sujet.md`](docs/02-ecarts-au-sujet.md) |
| Journal de projet et nettoyage | [`docs/NETTOYAGE.md`](docs/NETTOYAGE.md) |
| Captures (console AWS réelles, état CLI, preuves de tests) | [`captures/`](captures/) |
| Vidéo de rendu v2 (environ 8 min, captures et terminaux) | [`video/satom-cloud-network-TP-AC.mp4`](video/satom-cloud-network-TP-AC.mp4) |
| Vidéo tutoriel refaite à la main dans la console AWS (version complète d'environ 38 min, version courte de 6 min 30) | fichiers locaux `video/satom-cloud-network-TP-AC-gui.mp4` et `…-court.mp4` (trop lourds pour le dépôt) ; outils de tournage et de montage : [`video/rig/`](video/rig/), [`video/shoot/`](video/shoot/), [`video/scenario2.py`](video/scenario2.py), [`video/build_video.py`](video/build_video.py) |

## Rejouer le projet
```powershell
aws login --region eu-north-1 --profile TP-AC          # connexion par navigateur, aucune clé à copier
pwsh scripts/m01-vpc.ps1; pwsh scripts/m02-routage.ps1; pwsh scripts/m03-securite.ps1   # puis m05, m09 ... m13
python scripts/build_docs.py && python scripts/diagrams/gen_m05_m13.py                   # documents et schémas
```
Chaque script de module écrit ses preuves dans `docs/modules/mNN/tests.txt`. Les ressources facturées à l'heure sont listées dans `docs/NETTOYAGE.md`.

