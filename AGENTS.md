# AGENTS.md : contexte du projet pour les assistants IA (et pour les humains pressés)

Ce fichier est lu en premier par Claude Code (via `CLAUDE.md`) et par tout autre assistant. Lis-le en entier avant d'agir, puis ouvre `docs/passation/README.md`.

## 1. Le projet en dix lignes
- Formation AWS niveau 300 (Geneva Institute of Technology, promo E3). Client fictif : **Groupe Léman Finance SA**. Équipe **TP-AC** : Thomas Prud'homme et Abderahmane Chaouche.
- **Phase 1, terminée (16 au 20/11/2026) :** le « TP réseau » en treize modules (VPC, routage, sécurité, Network Firewall, peering, Transit Gateway, VPN, Direct Connect, ALB, Route 53, CloudFront, surveillance, CloudFormation). Tout a été refait à la main dans la console AWS, filmé (vidéo de 34 min : https://youtu.be/emZqnBNtOjM, non répertoriée), documenté (`docs/`, notes HackMD) et mesuré.
- **Phase 2, à faire : le « TP final DevSecOps »** : reconstruire tout le portail en infrastructure as code depuis GitHub, avec une pipeline de qualité et de sécurité, des tests de performance, du monitoring et une preuve de reprise. **Abderahmane en est responsable.** Sujet : https://hackmd.io/@Formateur/rJOiAHwCMg (version 2). Rendu prévu vendredi **27/11/2026** (à confirmer : le formateur a décalé la date).
- Dépôt public : https://github.com/Thomas-TP/satom-cloud-network-TP-AC (dossier local de Thomas : `C:\Perso\AWS`).

## 2. Où lire quoi
| Besoin | Fichier |
|---|---|
| Vue d'ensemble de la passation, ordre de lecture | `docs/passation/README.md` |
| État du projet et historique | `docs/passation/01-etat-et-historique.md` |
| Accès, comptes, actions que seul Thomas peut faire | `docs/passation/02-acces-et-actions-de-thomas.md` |
| Pièges rencontrés (AWS, console, outils) | `docs/passation/03-pieges-et-lecons.md` |
| **Carte de réutilisation : sprint du TP final -> ce qui existe déjà** | `docs/passation/04-carte-reutilisation-tp-final.md` |
| Domaine (réel) : comment l'utiliser | `docs/passation/05-domaine.md` |
| Plan du dépôt, outils, gros fichiers laissés de côté | `docs/passation/06-fichiers-et-outils.md` |
| Questions pour le formateur, coût et calendrier du TP final | `docs/tp-final/questions-formateur.md`, `docs/tp-final/plan-et-estimation.md` |
| Squelette du futur dépôt du TP final | `tp-final/satom-leman-portail/` |
| Dossier du TP réseau (module par module) | `docs/DOSSIER.md`, `docs/modules/`, `docs/src/` |

## 3. Règles non négociables
1. **Compte AWS partagé avec toute la classe.** On ne touche **jamais** aux ressources des autres équipes (suffixes vus : `_bko`, `-TM`, `_af`, `-MF`, `-AA`, `-AM`, `-LL`…). Nos ressources portent `-TP-AC` et le tag `Equipe=TP-AC`. **Supprimer uniquement par ce tag ou par l'identifiant exact**, après avoir regardé la ressource (jamais par motif de nom).
2. **Aucun secret** dans le dépôt, dans le chat, dans les captures ou à l'écran (clés pré-partagées VPN, jetons, mots de passe, clés d'accès). Les identifiants de compte à 12 chiffres ne vont pas dans les textes publiés. Pour GitHub vers AWS : OIDC, pas de clé longue durée.
3. **Demande avant toute action qui sort de la machine ou coûte** : publier, pousser dans le dépôt d'un autre, créer un compte, activer un service à l'échelle du compte (Security Hub, GuardDuty, Config, Access Analyzer), créer un fournisseur OIDC, lancer des ressources facturées à l'heure.
4. **Ressources facturées à l'heure** (Network Firewall ~0,40 USD/h, Transit Gateway ~0,05 USD/h par attachement, VPN ~0,05 USD/h par connexion, NAT ~0,045 USD/h, ALB ~0,03 USD/h) : les supprimer à la fin de chaque séance de travail. Budget du sujet : 150 CHF, alerte à 80 %.
5. **Quota de vCPU partagé : 48.** Une `t3.micro` compte 2 vCPU. Il a déjà été saturé par la classe : vérifie avant de lancer des instances (`verif_vcpu` : voir `03-pieges-et-lecons.md`).
6. **Honnêteté.** Écrire ce qui a été vraiment fait et mesuré. Dire ce qui est simulé (routeurs du siège et de l'agence, liaison Direct Connect, adresse de secours) et ce que les preuves ne montrent pas. Jamais de chiffre inventé.
7. **Ne casse pas le portfolio de Thomas** : le domaine `thomastp.ch` est son site personnel (hébergé chez Cloudflare). On n'y ajoute que ce qui est nécessaire (enregistrements NS du sous-domaine délégué), et on le retire après. Voir `docs/passation/05-domaine.md`.

## 4. Conventions
- Région **eu-north-1 (Stockholm)** (Zurich non activée, Francfort refusée par l'organisation). À confirmer avec le formateur pour le TP final.
- Profil CLI : `TP-AC` (`aws login --region eu-north-1 --profile TP-AC`, connexion par navigateur). Chacun se connecte avec son compte de formation.
- Noms : suffixe `-TP-AC` partout. Tags : `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=prod|dev` (le TP final ajoute `Module=<n>`).
- Plages d'adresses : prod `10.20.0.0/22`, dev `10.21.0.0/24`, siège `192.168.10.0/24`, agence `192.168.20.0/24` (voir `docs/00-plan-adressage.md`). Les plages du sujet (`10.0.0.0/16`, `10.1.0.0/16`) recouvrent celles des autres équipes.
- Accès aux machines : **Systems Manager Session Manager**, aucun port SSH ouvert, aucune clé.
- Texte écrit : français de Suisse, première personne du pluriel, phrases courtes et variées, concret. Pas de jargon de brochure, pas d'émojis. Les nombres écrits en toutes lettres se disent **septante, huitante, nonante**.
- Git : messages de commit clairs (le TP final impose Conventional Commits : `feat`, `fix`, `chore`, `docs`, `test`). Pas de commit direct sur `main` pour le TP final (pull requests relues par l'autre membre).
- Environnement de Thomas : Windows 11, PowerShell et Git Bash. Dans Git Bash, `MSYS_NO_PATHCONV=1` devant les commandes `aws` qui contiennent des chemins commençant par `/`. Fins de ligne : les fichiers sont en CRLF dans le dépôt.

## 5. Ce qui est déjà prêt pour le TP final
- Modèles CloudFormation de départ : `cfn/reseau-leman-etape1.yaml` (15 ressources : VPC, 3 sous-réseaux, IGW, tables, 3 Security Groups, rôle SSM), `cfn/reseau-leman.yaml` (réseau + `web-01`, `app-01`, ALB, groupes cibles, règle `/api/*`), `cfn/interconnexion-leman.yaml` (Network Firewall, Transit Gateway, VPN, Direct Connect Gateway par ressource personnalisée Lambda).
- Scripts du TP réseau (première version en AWS CLI) : `scripts/m01-*.ps1` à `m13-*.ps1`. Les scènes de tournage `video/shoot/mNN*.py` décrivent **clic par clic** ce qui a été fait dans la console, avec les valeurs exactes.
- Mesures et preuves : `docs/modules/mNN/tests.txt`, `docs/modules/m10/tests-domaine-reel.txt`, captures dans `docs/images/shots/`.
- Domaine réel : `thomastp.ch` ; sous-domaine `leman.thomastp.ch` (délégation chez Cloudflare, retirée à la fin du TP réseau). **Pour le TP final, préférer un sous-domaine d'un domaine d'Abderahmane** : voir `docs/passation/05-domaine.md`.
- Squelette du dépôt du TP final : `tp-final/satom-leman-portail/`.

## 6. État d'AWS à la passation (20/11/2026)
Rien de facturé à l'heure ne tourne, **sauf** un Network Firewall `nfw-prod-leman-TP-AC` bloqué par une erreur côté AWS (cas Support 179508151300233). Il reste en plus des ressources gratuites : quatre VPC vides, deux Customer Gateways, un rôle IAM, un secret `Projet/SatomCloudNetwork/vpn` et des groupes de journaux. Détail et suite à donner : `docs/NETTOYAGE.md`.

## 7. Comment travailler sur le TP final (méthode)
1. Lire la carte `docs/passation/04-carte-reutilisation-tp-final.md` et les questions du formateur.
2. Ne rien déployer avant le point de contrôle **G0** (dépôt créé, branche protégée, OIDC configuré, budget et alertes actifs).
3. Avancer sprint par sprint : un template, un contrôle de sécurité, une mesure, une preuve. Une pull request par sprint. Un ADR par décision importante. Un point dans `docs/journal.md` avec les indicateurs DORA.
4. Tout ce qui est facturé à l'heure est détruit en fin de séance (et recréé depuis le dépôt : c'est justement la démonstration finale).
5. Documenter honnêtement, dans le style décrit en 4.
