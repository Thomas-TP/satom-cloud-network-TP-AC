# Fichiers, outils et gros fichiers laissés de côté

## Plan du dépôt
| Dossier / fichier | Contenu |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Contexte et règles pour les assistants IA (`CLAUDE.md` renvoie à `AGENTS.md`) |
| `README.md` | Page d'accueil du dépôt, liens des livrables |
| `docs/` | Documentation |
| `docs/passation/` | Ce dossier de passation |
| `docs/tp-final/` | Questions au formateur et plan du TP final |
| `docs/src/mNN.md` | **Sources** des chapitres du dossier (on les modifie ici) |
| `docs/modules/mNN.md`, `docs/DOSSIER.md` | Chapitres et dossier **générés** par `scripts/build_docs.py` (ne pas modifier à la main) |
| `docs/modules/mNN/tests.txt` | Sorties de test injectées dans les chapitres |
| `docs/hackmd/` | Les quatre notes HackMD générées, et `notes.json` (identifiants des notes) |
| `docs/images/` | Schémas et `shots/mNN/` (captures de la console tirées des rushs) |
| `cfn/` | Modèles CloudFormation (voir `04-carte-reutilisation-tp-final.md`) |
| `scripts/` | Scripts du TP réseau (`mNN-*.ps1`, AWS CLI), outils de documentation, `verif_vcpu.sh` |
| `captures/` | Anciennes captures de la première version (terminal et console). Les chapitres n'en utilisent plus |
| `video/shoot/` | **Une scène de tournage par fichier** (`mNNx.py`) : la suite exacte de clics dans la console. Précieux comme référence |
| `video/rig/` | Outil de tournage (Chrome piloté par Playwright : curseur visible, enregistrement 1080p) |
| `video/montage/`, `video/voix/` | Chaîne de montage de la vidéo et de la voix off |
| `tp-final/satom-leman-portail/` | Squelette du dépôt du TP final |

## Outils utiles pour le TP final
- `scripts/build_docs.py` (chapitres + dossier), `scripts/build_hackmd.py` puis `scripts/publish_hackmd.py` (notes HackMD ; jeton en variable d'environnement), `scripts/build_client_pdf.py` (PDF du dossier client).
- `scripts/shot.py` : extrait une capture de la console depuis un rush et masque le bandeau du compte. Pas utile sans rushs ; pour les captures du TP final, faire des captures normales en masquant l'identifiant de compte.
- `scripts/verif_vcpu.sh` : quota de vCPU, vCPU utilisés par la classe, et si l'on peut lancer 4 vCPU de plus.
- `scripts/prix_aws.py` : lecture de l'API de prix AWS (a servi pour l'estimation des coûts du module 0).

## Gros fichiers volontairement **laissés sur le PC de Thomas** (hors dépôt, inutiles pour le TP final)
| Quoi | Où (PC de Thomas) | Pourquoi on ne les transmet pas |
|---|---|---|
| Enregistrements bruts de la console (189 vidéos `.mp4`, leurs repères `.marks.json` et des captures d'échec non masquées : 382 fichiers, 0,6 Go) | `C:\Perso\AWS\video\raw\` | ne servent qu'à refaire la vidéo ou des captures ; les captures d'échec montrent le bandeau du compte |
| Vidéos de travail et montages intermédiaires | `video\work`, `video\work2`, `video\work3`, `video\clips`, `video\montage\work` | régénérables |
| Rendus de la vidéo (la v2 finale fait 931 Mo ; les versions précédentes sont aussi là) | `C:\Perso\AWS\video\*.mp4` | la vidéo finale est sur YouTube (`https://youtu.be/emZqnBNtOjM`) |
| Voix clonées, modèles et environnement Python de synthèse vocale (Qwen3-TTS) | `C:\Perso\voice\` | spécifique à la vidéo |
| Profil du Chrome de tournage (sessions AWS et Google, `psk.json` avec les clés pré-partagées des VPN) | `video\rig\profile\` | **contient des secrets : ne jamais le transmettre ni le versionner** |

Si un jour tu veux refaire une vidéo, la chaîne est décrite dans `video/montage/README.md` et `video/voix/README.md`, mais il faudra qu'Abderahmane se procure les rushs auprès de Thomas.

## Ce qu'il ne faut jamais mettre dans le dépôt
Clés pré-partagées des VPN, jetons (HackMD, GitHub), clés d'accès AWS, mots de passe, profil de navigateur, `psk.json`, identifiants de compte à 12 chiffres dans les textes. Pour AWS depuis GitHub : OIDC (sprint 13). Le `.gitignore` du dépôt exclut déjà `.env`, `*.pem`, `*.key`, `credentials`, `*.tfstate`, `video/rig/profile/`.
