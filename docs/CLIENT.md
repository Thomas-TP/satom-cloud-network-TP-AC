# Groupe Léman Finance SA – Réseau cloud sécurisé sur AWS
**Dossier de présentation client** – Satom IT & Learning Solutions, équipe TP-AC – novembre 2026

---

## 1. Votre besoin
Un réseau AWS sécurisé qui sépare la production et le développement, relie le siège (Genève-Cornavin) et l'agence (Lausanne), journalise les accès et protège des données financières sensibles, avec un budget maîtrisé et une infrastructure reproductible.

## 2. Notre réponse en une page
| Objectif | Ce que nous avons livré | Preuve |
|---|---|---|
| Isoler prod / dev | Deux réseaux privés distincts (`10.20.0.0/22`, `10.21.0.0/24`) reliés par un Transit Gateway, avec une table de routage par environnement ; le dev n'atteint que le port 8080 de l'API | modules 5 et 6 |
| Relier siège et agence en chiffré | **VPN AWS site à site**, deux tunnels par site (IKEv2, AES-256, SHA-256) rattachés au Transit Gateway ; clés dans un coffre-fort de secrets ; le siège joint l'application, l'agence seulement l'API (8080) ; le réseau de développement n'est pas joignable depuis les sites | modules 7 et 8 |
| Filtrer et journaliser | Security Groups, NACL, pare-feu managé sur les domaines sortants, journaux de flux réseau, alarme sur erreurs applicatives | modules 3, 4 et 12 |
| Répartition de charge et DNS | Répartiteur HTTPS sur 2 zones, routage `/api/*`, DNS privé/public avec bascule automatique, CDN | modules 9 à 11 |
| Maîtriser les coûts | Instances arrêtées hors séance ; NAT et répartiteurs conservés jusqu'à la fin du cours ; budget de 100 USD par mois avec alerte à 80 % | section 7 |
| Reproductibilité | Template CloudFormation : suppression puis redéploiement identique, sans étape manuelle | module 13 |

![Architecture](../images/global.png)

## 3. Architecture
* **Production** `vpc-prod-leman` (`10.20.0.0/22`, 1 024 adresses – dimensionnée au besoin réel) : sous-réseaux **public** (serveur web, répartiteur), **privé** (application, aucune adresse publique) ; accès Internet sortant par NAT ; accès d'administration par **AWS Systems Manager** (aucun port SSH exposé, aucune clé à gérer).
* **Développement** `vpc-dev-leman` (`10.21.0.0/24`) : isolé ; il n'atteint la production que sur `app-01:8080`, par le Transit Gateway.
* **Filtrage sortant** : un Network Firewall n'autorise que les dépôts de mises à jour et les services AWS ; le reste est bloqué et journalisé.
* **Publication** : CloudFront (CDN) → ALB (HTTPS) → web et API ; l'ALB n'accepte **que** CloudFront.
* **Sites** : siège `192.168.10.0/24` et agence `192.168.20.0/24` reliés par deux VPN AWS (quatre tunnels). Les sites sont des routeurs simulés. Le Direct Connect Gateway est créé et associé au Transit Gateway ; la liaison dédiée est simulée (GRE et BGP) avec bascule vers le VPN.

## 4. Sécurité
| Mesure | Détail |
|---|---|
| Moindre privilège | Security Groups par rôle : le web n'accepte que l'ALB, l'application que le web (et les sites autorisés) |
| Défense en profondeur | NACL sans état sur le sous-réseau public, ordre des règles maîtrisé |
| Secrets | clés IPsec dans AWS Secrets Manager (`Projet/SatomCloudNetwork/vpn`), jamais dans un document ni un dépôt |
| Aucun accès SSH | administration par SSM Session Manager, traçable |
| Chiffrement | TLS 1.2/1.3 sur le répartiteur, IPsec entre sites (quatre tunnels) |
| Traçabilité | VPC Flow Logs (acceptés/rejetés), tags `Projet`, `Equipe`, `Environnement` sur toutes les ressources |
| Origine protégée | accès direct à l'ALB depuis Internet impossible (liste de préfixes CloudFront seulement) |

## 5. Résultats des tests (extraits)
| Test | Résultat |
|---|---|
| VPC : création d'un sous-réseau chevauchant | refusée par AWS (`InvalidSubnet.Conflict`) |
| Prod : route par défaut retirée | échec immédiat du trafic sortant (19 s), rétabli dès la route restaurée |
| NACL : règle de retour retirée | flux HTTPS coupé (comportement sans état démontré) |
| Peering : CIDR chevauchant | état `failed` ; 3ᵉ VPC non joignable depuis dev (non-transitivité) |
| Pare-feu : domaines sortants | les dépôts autorisés répondent, `example.com` est bloqué, l'alerte est journalisée |
| Transit Gateway : propagation retirée | le test dev vers prod échoue (pas de route retour), puis réussit une fois la propagation remise |
| VPN : quatre tunnels | tous à l'état haut ; le siège joint l'application ; l'agence seulement le port 8080 ; aucun site ne joint le dev |
| VPN : panne du tunnel 1 | le trafic reprend sur le tunnel 2 après 29 s (siège) et 34 s (agence), selon la détection d'AWS |
| Direct Connect (liaison simulée) : panne du DX | bascule vers le VPN en environ 8 s, retour automatique au rétablissement |
| ALB : serveur web arrêté | cible `unhealthy`, réponse 502, retour à `healthy` après redémarrage |
| Route 53 : serveur principal arrêté | bascule DNS vers le secours en **34 s**, retour au primaire en **23 s** |
| CloudFront | contenu statique `Hit` (mis en cache), API jamais mise en cache, accès direct à l'ALB bloqué, invalidation efficace |
| CloudFormation | dérive détectée (`DRIFTED`) puis corrigée ; stack supprimée et redéployée à l'identique |

## 6. Limites et écarts à connaître
| Sujet | Situation | Conséquence |
|---|---|---|
| Sites et liaison dédiée | les deux sites sont des routeurs strongSwan ; aucune fibre Direct Connect n'est commandée | le VPN et le Direct Connect Gateway sont ceux d'AWS ; la liaison dédiée est simulée en GRE et BGP. Bascule du VPN : 29 à 34 s (délai de détection d'AWS), pas « sans coupure » ; bascule liaison dédiée vers VPN : environ 10 s |
| Services refusés en début de semaine | Network Firewall, Transit Gateway, VPN, Direct Connect | levés le 17/11/2026 ; nous avons alors refait ces modules pour de vrai |
| Région | Stockholm (la région Zurich n'est pas activée sur la plateforme) | Pour la production réelle, Zurich/Francfort conviendrait à la localisation des données : il suffit de changer le paramètre de région |
| Domaine et certificats | domaine fictif | certificats auto-signés / CloudFront par défaut ; en production : domaine réel + ACM validé par DNS |
| Quotas du compte partagé | 16 vCPU au départ, 48 après demande | les deux sites et `app-01` ont pu fonctionner ensemble |

## 7. Coûts
| Poste | Ordre de grandeur |
|---|---|
| NAT Gateway | ~0,045 USD/h (supprimée hors usage) |
| ALB | ~0,03 USD/h |
| Instances `t3.micro` | ~0,01 USD/h chacune |
| CloudFront, Route 53, CloudWatch | négligeable à cette échelle |
| Network Firewall, Transit Gateway, VPN managé | ~0,40 USD/h, ~0,05 USD/h par attachement, ~0,05 USD/h par connexion : à budgéter en production (nous les avons supprimés après les tests) |

Estimation au 16/11 : de l'ordre de 2 à 4 USD pour la première journée (calcul par heures de ressources ; la facturation réelle n'était pas encore disponible, Cost Explorer a un retard d'environ 24 h). Les activités pédagogiques ont porté les crédits du compte à 180 USD.

## 8. Reproductibilité et exploitation
* **Code** : scripts PowerShell/AWS CLI (un par module), templates CloudFormation (`reseau-leman.yaml` pour le portail, `interconnexion-leman.yaml` pour le pare-feu, le Transit Gateway, les VPN et le Direct Connect Gateway), schémas et preuves dans le dépôt Git.
* **Déploiement complet** : une commande de création de stack (voir module 13) ; suppression propre en ordre inverse.
* **Exploitation** : tableau de bord CloudWatch, alarme 5xx → SNS, journaux de flux interrogeables avec Logs Insights, procédures de diagnostic en quatre étapes par module.

## 9. Recommandations
1. Raccorder le vrai matériel du siège et de l'agence aux Customer Gateways (les routeurs simulés disparaissent).
2. Commander la liaison Direct Connect (1 Gbit/s, marge ≈ 44 % pour 2 To transférés en 8 h) et créer l'interface virtuelle vers le Direct Connect Gateway déjà associé au Transit Gateway.
3. Acquérir le domaine, valider les certificats ACM par DNS, déléguer la zone Route 53.
4. Déployer en région Zurich ou Francfort (localisation des données), avec une deuxième zone de disponibilité pour l'application.
5. Mettre en place un budget AWS avec alerte à 80 % et un abonnement e-mail SNS pour l'équipe d'exploitation.

## 10. Prochaines étapes
Validation du dossier par Léman Finance → recette sur environnement de production → bascule des utilisateurs → transfert d'exploitation (procédures de diagnostic, tableau de bord, alarmes).



