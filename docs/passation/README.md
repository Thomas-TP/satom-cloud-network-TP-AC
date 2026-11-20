# Passation du projet à Abderahmane

Ce dossier rassemble **tout** ce qu'il faut pour reprendre le projet : ce qui a été fait, comment, avec quels pièges, et ce qui t'attend pour le TP final. Thomas a décidé avec toi que tu portes le TP final ; il reste disponible pour les actions qui dépendent de son compte (voir `02`).

## Ordre de lecture (environ 45 minutes)
1. **Ce fichier**, puis `AGENTS.md` à la racine (les règles et le contexte, que ton Claude Code lira tout seul).
2. `01-etat-et-historique.md` : où nous en sommes, ce qui a été fait, par jour.
3. `02-acces-et-actions-de-thomas.md` : comment tu obtiens l'accès au dépôt et à AWS, et la liste de ce que Thomas doit encore faire.
4. `03-pieges-et-lecons.md` : tout ce qui nous a fait perdre du temps. À lire avant de lancer quoi que ce soit.
5. `04-carte-reutilisation-tp-final.md` : **le plus utile pour gagner du temps** : les treize sprints du TP final, avec ce qui existe déjà pour chacun.
6. `05-domaine.md` : comment utiliser un vrai domaine (le tien, de préférence).
7. `06-fichiers-et-outils.md` : plan du dépôt, scripts, outils, et les gros fichiers volontairement laissés sur le PC de Thomas.
8. Puis `docs/tp-final/questions-formateur.md` (les questions à poser) et `docs/tp-final/plan-et-estimation.md` (coût et calendrier). Le sujet : https://hackmd.io/@Formateur/rJOiAHwCMg

## Gagner du temps : CloudFormation existe déjà

Le sujet demande de tout décrire en CloudFormation. **Nous avons déjà trois modèles, déployés et testés.** Pars de là au lieu de repartir de zéro : ils couvrent une grande partie des sprints 1 à 9.

| Modèle (`cfn/`, copié dans `tp-final/satom-leman-portail/templates/_depart/`) | Ce qu'il crée | Ce qui a été vraiment fait avec |
|---|---|---|
| `reseau-leman-etape1.yaml` | VPC, trois sous-réseaux, IGW, table publique, trois Security Groups, rôle SSM (15 ressources) | déployé **dans la console** pendant le tournage (module 13) : `CREATE_COMPLETE` en environ 2 min 30, dérive détectée puis corrigée, suppression propre |
| `reseau-leman.yaml` | le précédent + `web-01`, `app-01`, ALB, deux groupes cibles, listener HTTPS, règle `/api/*` | déployé en ligne de commande lors de la première exécution (17/11), avec un jeu de modifications et un redéploiement |
| `interconnexion-leman.yaml` | Network Firewall, Transit Gateway et tables de routage, deux VPN, Direct Connect Gateway (Lambda), routes | déployé en ligne de commande le 17/11 (`scripts/m13-interconnexion.ps1`, `tests-interconnexion.ps1`) |

**Limites à connaître avant de t'y fier :**
- Ils ont été écrits pour le TP réseau : noms en `-TP-AC`, région `eu-north-1`, plages `10.20.0.0/22` et `10.21.0.0/24`. Les plages et les noms sont des paramètres ou se changent facilement, mais vérifie-les.
- `interconnexion-leman.yaml` suppose que le réseau existe déjà (les identifiants des VPC et sous-réseaux sont des paramètres) et que le secret `Projet/SatomCloudNetwork/vpn` (clés des VPN) existe dans Secrets Manager. Il existe encore, mais vérifie son contenu.
- **Il leur manque** ce que le sujet ajoute : la NAT et la table privée, les NACL, le peering et le VPC dev, l'alarme `TunnelState`, KMS, WAF, X-Ray, Security Hub, GuardDuty, Config, les routeurs de site (strongSwan, simulés, hors modèle). La carte `04` dit sprint par sprint ce qui existe et ce qui reste.
- Nous n'avons **pas lancé `cfn-lint`, `cfn-guard` ni `checkov`** dessus : il est probable qu'ils réclament des corrections (chiffrement, tags `Module`, ports ouverts).
- Ils ne sont pas découpés « un fichier par domaine » comme le demande le sujet : c'est la première chose à faire (voir `tp-final/satom-leman-portail/templates/README.md`).

## Démarrer avec Claude Code
```powershell
git clone https://github.com/Thomas-TP/satom-cloud-network-TP-AC.git   # après avoir accepté l'invitation (voir 02)
cd satom-cloud-network-TP-AC
claude
```
`CLAUDE.md` renvoie vers `AGENTS.md` : ton assistant connaît dès le départ le projet, les règles (aucun secret, ne supprimer que nos ressources, nombres à la suisse) et où se trouve chaque chose. Premier message conseillé :

> Lis AGENTS.md puis docs/passation/README.md et docs/passation/04-carte-reutilisation-tp-final.md. Résume-moi l'état du projet et propose-moi le plan pour le point de contrôle G0 du TP final. Ne déploie rien et n'active aucun service avant mon accord.

## Les trois choses à faire dès aujourd'hui
1. Accepter l'invitation GitHub de Thomas (`02`, section 1).
2. Te connecter à AWS et vérifier ton accès (`02`, section 2).
3. Envoyer les questions au formateur (`docs/tp-final/questions-formateur.md`) : sept d'entre elles bloquent le démarrage.
