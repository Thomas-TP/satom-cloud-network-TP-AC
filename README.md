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
| Template CloudFormation (module 13) | [`cfn/reseau-leman.yaml`](cfn/reseau-leman.yaml) (+ `reseau-leman-etape1.yaml`, `optional-*.yaml`) |
| Procédures de test | section « Procédure de test / diagnostic » de chaque module |
| Services bloqués par l'organisation | [`docs/01-services-bloques.md`](docs/01-services-bloques.md) |
| Journal de projet et nettoyage | [`docs/NETTOYAGE.md`](docs/NETTOYAGE.md) |
| Captures (console AWS réelles, état CLI, preuves de tests) | [`captures/`](captures/) |
| Vidéo de rendu | [`video/satom-cloud-network-TP-AC.mp4`](video/satom-cloud-network-TP-AC.mp4) |

## Rejouer le projet
```powershell
aws login --region eu-north-1 --profile TP-AC          # connexion par navigateur, aucune clé à copier
pwsh scripts/m01-vpc.ps1; pwsh scripts/m02-routage.ps1; pwsh scripts/m03-securite.ps1   # puis m05, m09 ... m13
python scripts/build_docs.py && python scripts/diagrams/gen_m05_m13.py                   # documents et schémas
```
Chaque script de module écrit ses preuves dans `docs/modules/mNN/tests.txt`. Les ressources facturées à l'heure sont listées dans `docs/NETTOYAGE.md`.
