# Chronologie du montage v3 (sans voix)

Début · durée (s) · scène · module · légende — base pour écrire les textes de voix adaptés à chaque plan.

| Début | Durée s | Type | Scène | Module | Légende |
|---|---|---|---|---|---|
| 0:00.0 | 4.0 | title | title |  | Titre  |
| 0:03.7 | 7.0 | intro | intro |  | Schéma global  |
| 0:10.4 | 5.0 | chapter | chapter | 0 | Cadrage  |
| 0:15.1 | 10.0 | gui | m00 | 0 | Fixer un budget — Budget mensuel de 100 $ avec alerte de dépassement |
| 0:24.8 | 5.0 | chapter | chapter | 1 | Réseaux  |
| 0:29.6 | 8.8 | gui | m01a | 1 | VPC de production — vpc-prod-leman-TP-AC · 10.20.0.0/22 |
| 0:38.1 | 16.7 | gui | m01b | 1 | Deux sous-réseaux — Public 10.20.0.0/26 · privé 10.20.1.0/26 |
| 0:54.6 | 5.8 | gui | m01c | 1 | Test de chevauchement — AWS refuse un CIDR qui recouvre un sous-réseau existant |
| 1:00.1 | 6.9 | gui | m01d | 1 | Rôle IAM pour SSM — Administrer les serveurs sans SSH ni clé |
| 1:06.7 | 22.4 | gui | m01e | 1 | Serveur web-01 — Sous-réseau public · t3.micro · Amazon Linux 2023 |
| 1:28.8 | 24.3 | gui | m01f | 1 | Serveur app-01 — Sous-réseau privé · IP fixe 10.20.1.10 · mini API sur 8080 |
| 1:52.8 | 5.0 | chapter | chapter | 2 | Routage  |
| 1:57.5 | 11.7 | gui | m02a | 2 | Passerelle Internet — Créée puis attachée au VPC de production |
| 2:09.0 | 22.8 | gui | m02b | 2 | Table de routage publique — 0.0.0.0/0 → passerelle Internet |
| 2:31.5 | 10.3 | gui | m02c | 2 | Table de routage privée — Pour l'instant : route locale uniquement |
| 2:41.6 | 12.9 | gui | m02c2 | 2 | Sous-réseau de la zone B — Pour héberger la NAT |
| 2:54.2 | 17.3 | gui | m02d | 2 | Passerelle NAT — Quota atteint en zone A : on bascule en zone B |
| 3:11.3 | 3.8 | gui | m02d2 | 2 | NAT disponible — L'état passe à « disponible » |
| 3:14.8 | 12.1 | gui | m02e | 2 | Route privée vers la NAT — 0.0.0.0/0 → passerelle NAT |
| 3:26.7 | 6.6 | gui | m02f | 2 | Preuve par Session Manager — app-01 sort sur Internet avec l'IP de la NAT |
| 3:33.0 | 27.4 | gui | m02g | 2 | Test de panne — On retire la route NAT, puis on la remet |
| 4:00.1 | 5.0 | chapter | chapter | 3 | Sécurité  |
| 4:04.9 | 14.7 | gui | m03a | 3 | Security Group « web » — 443 ouvert à Internet · SSH restreint |
| 4:19.3 | 21.0 | gui | m03b | 3 | Security Group « app » — Source = le groupe web, pas une adresse |
| 4:40.1 | 11.7 | gui | m03c | 3 | Associer les groupes — web-01 → sg-web · app-01 → sg-app |
| 4:51.5 | 19.7 | gui | m03d | 3 | Tests entre les serveurs — Ping, API 8080, nginx en HTTPS |
| 5:11.0 | 24.6 | gui | m03e | 3 | NACL du sous-réseau public — Sans état : il faut autoriser l'aller et le retour |
| 5:35.3 | 18.6 | gui | m03f | 3 | Test de panne — On retire le port 8080 du groupe app |
| 5:53.6 | 5.0 | chapter | chapter | 4 | Pare-feu  |
| 5:58.4 | 8.8 | gui | m04a | 4 | Sous-réseau du pare-feu — 10.20.2.0/28 en zone A |
| 6:06.9 | 40.0 | gui | m04b | 4 | Tables de routage — Faire passer le trafic au bon endroit |
| 6:46.6 | 15.1 | gui | m04c | 4 | Groupe de règles — Liste de domaines autorisés |
| 7:01.4 | 14.6 | gui | m04d | 4 | Politique du pare-feu — Ordre strict · tout le reste est abandonné |
| 7:15.8 | 14.1 | gui | m04e | 4 | Créer le pare-feu — AWS Network Firewall · point de terminaison dédié |
| 7:29.6 | 5.7 | gui | m04f0 | 4 | Groupes de journaux — Un pour les alertes, un pour les flux |
| 7:35.1 | 7.5 | gui | m04f | 4 | Activer la journalisation — Alertes et flux vers CloudWatch |
| 7:42.3 | 6.8 | gui | m04g | 4 | Route privée vers le pare-feu — 0.0.0.0/0 → point de terminaison |
| 7:48.8 | 6.6 | gui | m04h | 4 | Route de retour — La réponse revient par le même chemin |
| 7:55.2 | 12.9 | gui | m04i | 4 | Test du pare-feu — Domaine autorisé : OK · domaine bloqué : délai dépassé |
| 8:07.8 | 4.6 | gui | m04j | 4 | Alertes et flux — Le pare-feu a tout vu dans CloudWatch |
| 8:12.2 | 5.0 | chapter | chapter | 5 | Appairage  |
| 8:16.9 | 9.0 | gui | m05a1 | 5 | VPC de développement — vpc-dev-leman-TP-AC · 10.21.0.0/22 |
| 8:25.7 | 9.3 | gui | m05a2 | 5 | Sous-réseau de développement — 10.21.0.0/26 |
| 8:34.7 | 10.9 | gui | m05b1 | 5 | Passerelle Internet dev — Créée puis attachée |
| 8:45.4 | 22.7 | gui | m05b2 | 5 | Table de routage dev — 0.0.0.0/0 → passerelle Internet |
| 9:07.8 | 10.0 | gui | m05c1 | 5 | Security Group dev — Aucune règle entrante |
| 9:17.6 | 20.8 | gui | m05c2 | 5 | Serveur dev-01 — IP fixe 10.21.0.10 |
| 9:38.1 | 12.5 | gui | m05d | 5 | Appairage de VPC — Demande de prod vers dev, puis acceptation |
| 9:50.3 | 10.1 | gui | m05e | 5 | Routes des deux côtés — Chaque VPC a besoin de sa route |
| 10:00.1 | 5.2 | gui | m05f | 5 | Autoriser le port 8080 — Depuis le sous-réseau de développement |
| 10:05.0 | 11.2 | gui | m05g | 5 | Test depuis dev-01 — L'API répond ; ping et SSH restent fermés |
| 10:15.9 | 6.7 | gui | m05h | 5 | Plages qui se chevauchent — L'appairage est refusé |
| 10:22.4 | 5.0 | chapter | chapter | 6 | Transit Gateway  |
| 10:27.1 | 13.9 | gui | m06a | 6 | Transit Gateway — Un hub unique au lieu de l'appairage |
| 10:40.7 | 9.5 | gui | m06b | 6 | Attachement de la production  |
| 10:50.0 | 8.7 | gui | m06c | 6 | Attachement du développement  |
| 10:58.3 | 14.5 | gui | m06d | 6 | Deux tables de routage — Une pour la prod, une pour le dev |
| 11:12.6 | 10.8 | gui | m06e | 6 | Associations et propagations — On croise les propagations |
| 11:23.2 | 4.1 | gui | m06i | 6 | Routes apprises — Chaque table ne connaît que l'autre côté |
| 11:27.0 | 8.5 | gui | m06f | 6 | Routes des VPC — Vers le Transit Gateway |
| 11:35.3 | 4.5 | gui | m06g | 6 | Supprimer l'appairage — Il ne sert plus |
| 11:39.5 | 24.2 | gui | m06h | 6 | Test et panne contrôlée — L'API répond via le Transit Gateway |
| 12:03.4 | 5.0 | chapter | chapter | 7 | VPN site à site  |
| 12:08.2 | 16.1 | gui | m07a | 7 | Clés des tunnels VPN — Dans Secrets Manager, jamais en clair |
| 12:24.0 | 6.6 | gui | m07b | 7 | Politique du rôle — Lire ce secret |
| 12:30.2 | 44.1 | gui | m07c | 7 | VPC du siège — 192.168.10.0/24 |
| 13:14.1 | 45.1 | gui | m07c2 | 7 | VPC de l'agence — 192.168.20.0/24 |
| 13:58.9 | 19.3 | gui | m07d | 7 | Security Groups des routeurs — Aucune règle entrante par défaut |
| 14:17.9 | 20.6 | gui | m07e | 7 | Routeur du siège — Ubuntu · t3.micro · IP fixe |
| 14:38.3 | 19.8 | gui | m07e2 | 7 | Routeur de l'agence  |
| 14:57.8 | 24.6 | gui | m07f | 7 | Adresses IP Elastic — Une par routeur |
| 15:22.1 | 15.4 | gui | m07g | 7 | Passerelles clientes — Une par site |
| 15:37.2 | 31.7 | gui | m07h | 7 | Connexions VPN — Cible : le Transit Gateway · routage statique |
| 16:08.6 | 16.9 | gui | m07i | 7 | Table de routage des sites — Associations et propagations |
| 16:25.2 | 6.9 | gui | m07j | 7 | Routes statiques — Une route par site dans la table de la prod |
| 16:31.8 | 9.2 | gui | m07k | 7 | Routes du VPC de production — Vers les deux sites |
| 16:40.8 | 6.9 | gui | m07l | 7 | Autoriser le port 8080 — Siège et agence uniquement |
| 16:47.4 | 13.6 | gui | m07m | 7 | Pare-feu des routeurs — Seulement les adresses d'AWS |
| 17:00.7 | 34.5 | gui | m07n | 7 | Routeur du siège — strongSwan installé et configuré |
| 17:35.0 | 35.8 | gui | m07n2 | 7 | Routeur de l'agence — Même configuration |
| 18:10.5 | 6.0 | gui | m07o | 7 | Tunnels VPN — Les deux tunnels de chaque connexion |
| 18:16.3 | 24.0 | gui | m07p | 7 | Tests depuis les sites — L'API d'app-01 répond |
| 18:40.0 | 44.4 | gui | m07q | 7 | Panne d'un tunnel — Détection puis reprise automatique |
| 19:24.2 | 5.0 | chapter | chapter | 8 | Direct Connect  |
| 19:29.0 | 10.2 | gui | m08a | 8 | Direct Connect Gateway — ASN 64513 |
| 19:38.9 | 10.9 | gui | m08b | 8 | Association au Transit Gateway — Préfixes autorisés |
| 19:49.5 | 17.1 | gui | m08c | 8 | Route côté AWS — Vers le routeur |
| 20:06.4 | 7.3 | gui | m08j | 8 | Table du sous-réseau de la zone B — La même route |
| 20:13.4 | 20.7 | gui | m08d | 8 | Routeur côté AWS — Ubuntu · sous-réseau public |
| 20:33.8 | 4.9 | gui | m08e | 8 | Libérer des vCPU — On arrête dev-01 |
| 20:38.5 | 20.6 | gui | m08f | 8 | Relancer le routeur — Cette fois, il démarre |
| 20:58.9 | 8.3 | gui | m08k | 8 | Attachement multi-zones — Il faut couvrir la zone du routeur |
| 21:06.9 | 20.0 | gui | m08g | 8 | Règles de sécurité — GRE (protocole 47) entre les routeurs |
| 21:26.5 | 26.1 | gui | m08h | 8 | Routeur côté AWS — FRRouting · deux tunnels GRE · BGP |
| 21:52.4 | 28.6 | gui | m08i | 8 | Routeur du siège — Mêmes tunnels · BGP |
| 22:20.7 | 19.1 | gui | m08l | 8 | Sessions BGP établies — Le meilleur chemin passe par la liaison dédiée |
| 22:39.5 | 43.3 | gui | m08m | 8 | Panne de la liaison dédiée — BGP bascule sur le VPN, puis revient |
| 23:22.6 | 4.7 | gui | m08n | 8 | Vue d'ensemble dans la console — Association active |
| 23:27.0 | 5.0 | chapter | chapter | 9 | Load balancer  |
| 23:31.7 | 10.4 | gui | m09a | 9 | Certificat pour l'ALB — Importé dans ACM · clé masquée |
| 23:41.9 | 27.2 | gui | m09b | 9 | Deux groupes cibles — Web (HTTPS) et application (8080) |
| 24:08.8 | 13.6 | gui | m09c | 9 | Security Group de l'ALB — 443 depuis Internet |
| 24:22.2 | 24.3 | gui | m09d | 9 | Équilibreur de charge — Application Load Balancer sur deux zones |
| 24:46.2 | 5.0 | gui | m09e | 9 | Autoriser l'ALB — Port 8080 pour le groupe de l'application |
| 24:51.0 | 8.6 | gui | m09f | 9 | Règle du listener — /api/* → groupe cible de l'application |
| 24:59.4 | 5.9 | gui | m09g | 9 | Santé des cibles — Les deux groupes sont sains |
| 25:05.0 | 19.9 | gui | m09h | 9 | Test de panne — nginx arrêté : l'ALB renvoie 502 puis reprend |
| 25:24.6 | 5.0 | chapter | chapter | 10 | Route 53  |
| 25:29.3 | 11.3 | gui | m10a | 10 | Zone privée Route 53 — prod.leman.internal |
| 25:40.4 | 5.4 | gui | m10b | 10 | Enregistrements — web et app |
| 25:45.5 | 5.0 | gui | m10f0 | 10 | Noms d'hôte DNS — Activés pour la résolution privée |
| 25:50.2 | 7.7 | gui | m10f | 10 | Résolution depuis web-01 — Le nom se résout par le résolveur du VPC |
| 25:57.7 | 8.2 | gui | m10c | 10 | Zone publique — Domaine fictif leman-finance.example |
| 26:05.7 | 7.6 | gui | m10d | 10 | Surveillance de l'état — HTTPS sur l'équilibreur |
| 26:13.0 | 17.9 | gui | m10e | 10 | Enregistrements de basculement — Principal : ALB · secours : secondaire |
| 26:30.7 | 41.4 | gui | m10g | 10 | Test de basculement — Réponse du serveur de noms AWS en direct |
| 27:11.9 | 5.0 | chapter | chapter | 11 | CloudFront  |
| 27:16.6 | 9.3 | gui | m11a | 11 | Fichier statique — Servi par web-01 |
| 27:25.6 | 4.9 | gui | m11b | 11 | Cible de l'ALB — Certificat auto-signé : HTTP en origine |
| 27:30.3 | 9.2 | gui | m11c | 11 | Règle /api/* — Vers le groupe de l'application |
| 27:39.2 | 14.0 | gui | m11d | 11 | Distribution CloudFront — L'ALB en origine |
| 27:53.0 | 6.0 | gui | m11e | 11 | Comportement /static/* — Cache optimisé |
| 27:58.7 | 7.7 | gui | m11e2 | 11 | Comportement /api/* — Jamais de cache |
| 28:06.2 | 7.3 | gui | m11f | 11 | Verrouiller l'ALB — Joignable seulement par CloudFront |
| 28:13.2 | 5.4 | gui | m11f2 | 11 | NACL du sous-réseau public — Règle 105 pour le port 80 |
| 28:18.3 | 35.0 | gui | m11g | 11 | Tests CloudFront — Miss puis Hit · invalidation du cache |
| 28:53.0 | 5.0 | chapter | chapter | 12 | Surveillance  |
| 28:57.7 | 13.7 | gui | m12a | 12 | Rubrique SNS — Notifications d'alarme |
| 29:11.2 | 9.3 | gui | m12b | 12 | File SQS — Preuve de réception |
| 29:20.2 | 5.0 | gui | m12b2 | 12 | Abonnement — La file reçoit la rubrique |
| 29:25.0 | 16.4 | gui | m12c | 12 | Alarme CloudWatch — Erreurs 5xx de l'équilibreur |
| 29:41.1 | 7.3 | gui | m12d | 12 | Tableau de bord — Santé des cibles et temps de réponse |
| 29:48.2 | 10.2 | gui | m12e | 12 | Journaux de flux du VPC — Vers CloudWatch Logs |
| 29:58.0 | 9.8 | gui | m12f | 12 | Sonde SSH non autorisée — Depuis l'agence vers web-01 |
| 30:07.6 | 4.7 | gui | m12g | 12 | Logs Insights — Requête sur les flux rejetés |
| 30:12.0 | 42.5 | gui | m12h | 12 | Test de l'alarme — nginx arrêté, 60 requêtes, alarme déclenchée |
| 30:54.2 | 6.3 | gui | m12i | 12 | Messages reçus — La file SQS a reçu les notifications |
| 31:00.2 | 5.0 | chapter | chapter | 13 | CloudFormation  |
| 31:05.0 | 17.9 | gui | m13a | 13 | Pile CloudFormation — Téléverser le modèle et créer la pile |
| 31:22.5 | 4.8 | gui | m13b | 13 | Événements de la pile — Ressources créées dans l'ordre |
| 31:27.1 | 6.1 | gui | m13c | 13 | Créer une dérive — Règle SSH ajoutée à la main |
| 31:32.9 | 7.3 | gui | m13d | 13 | Détection de dérive — La pile est en dérive |
| 31:39.9 | 7.6 | gui | m13e | 13 | Corriger la dérive — On retire la règle : la pile est en phase |
| 31:47.3 | 7.6 | gui | m13f | 13 | Suppression de la pile — CloudFormation supprime tout |
| 31:54.6 | 8.0 | end | end |  | Conclusion  |
