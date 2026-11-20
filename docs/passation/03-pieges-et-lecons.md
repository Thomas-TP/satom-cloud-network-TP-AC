# Pièges rencontrés et leçons

Tout ce qui nous a fait perdre du temps, classé par sujet. Chaque point vient de ce que nous avons réellement vécu (voir aussi le chapitre du module concerné dans `docs/modules/`).

## Compte AWS partagé et organisation
- **Quota de vCPU : 48 pour toute la classe** (16 au départ ; une demande à 64 est restée ouverte). Une `t3.micro` compte 2 vCPU. Le quota a été saturé plusieurs fois par la classe : des instances ne démarraient plus, et des piles CloudFormation échouaient pour cette raison. `scripts/verif_vcpu.sh` affiche le quota, les vCPU utilisés et dit si 4 vCPU de plus passent. Éteins tout hors séance.
- **Instances arrêtées par quelqu'un d'autre.** Le 16/11 à 14:28, `web-01` et `app-01` ont été arrêtés par une autre session du rôle partagé (CloudTrail le montre). Toujours vérifier l'état des instances avant un test.
- **Services refusés par l'organisation (SCP)** jusqu'au 17/11 : Network Firewall, Transit Gateway, VPN, Direct Connect. Le message AWS parle de « explicit deny in a service control policy ». Un refus peut revenir : **teste chaque service tôt** (surtout Security Hub, GuardDuty, Config, WAF, Synthetics, KMS, OIDC pour le TP final). Voir `docs/01-services-bloques.md`.
- **Régions.** Zurich (`eu-central-2`) n'est pas activée (`AuthFailure`), Francfort est refusée. On travaille en Stockholm (`eu-north-1`).
- **Bandeau rouge `DescribeLocations`** dans la console Direct Connect : la liste des emplacements est refusée, mais la création de la passerelle marche.
- **Quota de NAT : 5 par zone** sur le compte partagé. Atteint en zone A : notre NAT est en zone B (`sub-public-1b`).
- **Les plages d'adresses du sujet** (`10.0.0.0/16`, `10.1.0.0/16`) recouvrent celles des autres équipes. Nous avons pris `10.20.0.0/22` et `10.21.0.0/24`.

## Réseau
- **Pare-feu et Security Groups.** Si seul le trafic aller passe par le pare-feu (la route de retour manque dans la table publique), `web-01` ne joint plus `app-01`. Il faut des routes symétriques, et des règles de `sg-app` par **plage d'adresses**, pas « depuis un groupe » : les groupes ne correspondent plus au trafic qui sort d'un point d'accès de pare-feu.
- **Network Firewall : la suppression peut se bloquer** (`InternalServerError: Internal failure`). C'est arrivé chez nous (cas Support 179508151300233) et le pare-feu est toujours facturé. Garde-fou : ne le garde allumé que pendant les séances, **vérifie la suppression dès la première fois**, et ne retire pas ses sous-réseaux à la main.
- **Direct Connect Gateway :** son ASN doit être différent de celui du Transit Gateway (64512 pour le TGW, 64513 pour le DXGW). Même ASN = rejeté.
- **VPN rattaché à un Transit Gateway :** on ne déclare pas de routes statiques sur la connexion ; elles vont dans la table de routage du TGW. Les adresses « de documentation » du sujet (`203.0.113.x`, `198.51.100.x`) ne permettent aucun tunnel : il faut une adresse IP publique réelle par routeur de site.
- **Un VPN ne bascule pas « sans coupure ».** Mesure : environ 29 s avant que le trafic reprenne sur le deuxième tunnel (AWS détecte la panne). La bascule de la liaison dédiée simulée vers le VPN : environ 7 à 10 s.
- **Peering avec CIDR chevauchant :** en ligne de commande AWS acceptait puis faisait échouer ; dans la console le formulaire refuse tout de suite.
- **Zone privée Route 53 :** le VPC doit avoir les noms d'hôte DNS activés (`enableDnsHostnames`). Sinon rien ne se résout. (Dans notre vidéo, `getent hosts` n'a rien affiché malgré cela : cause non établie.)

## Certificats, domaine, CloudFront
- **Un certificat ACM par région :** celui de l'ALB dans la région de l'ALB, celui de CloudFront en **`us-east-1`** obligatoirement.
- **Un nom pour l'ALB.** Le nom DNS d'un ALB (`….elb.amazonaws.com`) ne figure pas sur le certificat : il faut un enregistrement alias dans notre domaine (`origin.leman.thomastp.ch`) pour que le certificat corresponde.
- **Validation DNS :** le domaine nu et le joker `*.domaine` partagent un seul CNAME de validation. Le bouton « Créer des enregistrements dans Route 53 » le crée en un clic. Un essai « à blanc » a créé un vrai certificat : pense à le supprimer.
- **La console Route 53 masque NS, SOA et le CNAME de validation** dans la liste des enregistrements. Le compteur dit « (4) » mais la liste n'en montre qu'un. Les serveurs de noms se lisent dans « Détails de la zone hébergée ».
- **La console CloudFront n'a pas proposé notre certificat** de `us-east-1` dans la liste. Nous avons posé le nom alternatif et le certificat avec `aws cloudfront update-distribution`.
- **Supprimer une distribution :** il faut d'abord retirer l'alias, remettre un certificat par défaut avec une `MinimumProtocolVersion`, la désactiver, attendre « Deployed », puis supprimer.
- **OAC (Origin Access Control)** ne s'applique qu'aux origines S3, pas à un ALB. Pour protéger un ALB : liste de préfixes gérée `com.amazonaws.global.cloudfront.origin-facing` dans le Security Group.
- **nginx renvoie `application/octet-stream`** pour un `return 200 "texte"` : le navigateur télécharge au lieu d'afficher. Ajouter `default_type text/plain;`.

## Console AWS
- **La session de la console expire** : on tombe sur une page de connexion blanche. Se reconnecter, puis relancer l'étape.
- **Supprimer une règle de Security Group dans la console** : on peut supprimer la **mauvaise** (c'est arrivé : la source de la règle SSH a été vidée, la console a refusé d'enregistrer et la règle voulue est restée). Vérifier à l'écran avant d'enregistrer.
- **Session Manager :** l'erreur « instance non configurée pour SSM » est apparue à deux reprises alors que les instances étaient `Online` ; cause inconnue, un nouvel essai a suffi.
- **Menus « Actions » parfois non cliquables** : cliquer par coordonnées de page.

## CloudFormation
- Les créations de pile échouent si le quota de vCPU est plein (`VcpuLimitExceeded`) : relancer quand de la place se libère.
- La détection de dérive ne couvre pas tous les types de ressource ; elle a bien vu une règle de Security Group ajoutée à la main.
- Un modèle qui crée un rôle IAM oblige à cocher la case `CAPABILITY_IAM` dans la console.

## Outils et poste de Thomas (Windows)
- **Git Bash et chemins :** une commande `aws ... /health` est transformée en `C:/Program Files/Git/health`. Mets `MSYS_NO_PATHCONV=1` devant.
- **Encodages :** écrire en UTF-8 explicite (JSON, fichiers texte), sinon cp1252 corrompt les accents. Fins de ligne CRLF dans le dépôt.
- **ffmpeg** : installé par WinGet, mais le lien `…\WinGet\Links\ffmpeg.exe` a disparu une fois (mise à jour) : recopier l'exécutable depuis `…\WinGet\Packages\Gyan.FFmpeg_…\bin\` si besoin.
- **Écrire des scripts avec des `\n` dans des commandes passées à l'outil** : les antislashs peuvent être mangés ; écrire le fichier directement plutôt que par un `python -` en ligne.
- **Fenêtres natives (sélecteur de fichier, « Actualiser le site ? »)** bloquent le pilotage du navigateur : les fermer à la main.
- **HackMD :** une note est limitée à environ 100 000 caractères (d'où les quatre notes). L'API (`/v1/notes`) accepte la création et la mise à jour avec un jeton ; `/v1/history` liste les notes consultées.
