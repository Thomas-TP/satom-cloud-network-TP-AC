# État du projet et historique

## En une phrase
Le TP réseau (treize modules) est **terminé, filmé et documenté**. Le TP final DevSecOps n'est **pas commencé** : il n'existe que l'analyse du sujet, les questions au formateur, l'estimation et un squelette de dépôt.

## Ce qui est livré (TP réseau)
| Livrable | Où |
|---|---|
| Vidéo complète avec voix (34 min, tout refait à la main dans la console) | https://youtu.be/emZqnBNtOjM (YouTube, non répertoriée) |
| Dossier en quatre notes HackMD (sommaire avec vidéo, trois parties) | `docs/hackmd/notes.json` donne les adresses ; sources : `docs/hackmd/*.md` |
| Dossier du même contenu, un fichier par module | `docs/DOSSIER.md`, `docs/modules/mNN.md`, sources dans `docs/src/` |
| Captures de la console, tirées des enregistrements | `docs/images/shots/` |
| Dossier de présentation client (et son PDF) | `docs/CLIENT.md`, `docs/CLIENT.pdf` |
| Écarts au sujet (pour le formateur) | `docs/02-ecarts-au-sujet.md` |
| Plan d'adressage, services bloqués, journal de nettoyage | `docs/00-plan-adressage.md`, `docs/01-services-bloques.md`, `docs/NETTOYAGE.md` |
| Modèles CloudFormation | `cfn/` |
| Scripts AWS CLI du TP réseau (première version) | `scripts/mNN-*.ps1` |

## Historique (ce qui s'est passé, dans l'ordre)
| Date | Événement |
|---|---|
| 16/11 | Début. Budget (100 USD par mois, alerte 80 %), plan d'adressage, premiers modules. Network Firewall, Transit Gateway, VPN et Direct Connect sont refusés par une règle de l'organisation. Nos instances sont arrêtées par une autre session du rôle partagé ; les 16 vCPU du compte sont saturés. |
| 17/11 | Le formateur lève le blocage. Nous faisons les modules 4, 6, 7 et 8 pour de vrai, en ligne de commande, et déployons tout par CloudFormation. |
| 18 et 19/11 | **Tout est refait à la main dans la console AWS et filmé** (outil de tournage maison, voir `06`). Il fallait une vraie démonstration : la vidéo sert de référence. |
| 19/11 | Montage muet de la vidéo (rythme, caméra de zoom, légendes). |
| 20/11 | Voix off (voix clonées de Thomas et d'Abderahmane). Domaine réel `leman.thomastp.ch` : modules 9 à 11 refaits avec un vrai certificat ACM, une vraie zone Route 53, CloudFront en HTTPS. Vidéo finale, mise en ligne sur YouTube. Dossier réécrit module par module avec de vraies captures. Nettoyage AWS (voir `docs/NETTOYAGE.md`). Les notes HackMD sont publiées. |
| 20/11 | Le formateur publie le TP final et décale la date du rendu (vendredi 27/11 à confirmer). Vous décidez qu'Abderahmane le porte. |

## Ce que la vidéo ne montre pas (honnêteté)
Deux scènes contredisent la voix et n'ont pas été refaites :
- **Module 3, panne du port 8080** : la console a refusé d'enregistrer la mauvaise règle supprimée ; aucun échec n'apparaît à l'écran alors que la voix dit « Échec ».
- **Module 10, zone privée** : `getent hosts` n'affiche rien à l'écran alors que la voix dit « se résout bien ».
Les chapitres du dossier le disent. Autres écarts mineurs : l'alarme du module 12 finit en « Données insuffisantes » (pas « OK ») ; la bascule Route 53 prend 33 s à l'aller et 141 s au retour dans la vidéo (70 s et 34 s à la première mesure).

## Ce qui est simulé (à ne pas présenter comme réel)
- Le siège et l'agence : deux instances Ubuntu avec strongSwan. Le VPN côté AWS est un vrai VPN site à site.
- La liaison Direct Connect : tunnel GRE et BGP (FRRouting) entre deux routeurs. La passerelle Direct Connect (DXGW) et son association au Transit Gateway sont réelles.
- Le secours du basculement Route 53 : l'adresse de documentation `203.0.113.50`, pas un second site.

## État d'AWS aujourd'hui
Voir `docs/NETTOYAGE.md` : seul un Network Firewall bloqué (erreur côté AWS, cas Support 179508151300233) est facturé (~0,40 USD/h), et quelques ressources gratuites restent. **Réessaie `DeleteFirewall`** de temps en temps : tant qu'il existe, quatre VPC vides ne peuvent pas partir.
