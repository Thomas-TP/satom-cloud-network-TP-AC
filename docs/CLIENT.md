# Groupe Léman Finance SA – Réseau cloud sécurisé sur AWS
**Dossier de présentation client** – Satom IT & Learning Solutions, équipe TP-AC – novembre 2026

---

## 1. Votre besoin
Un réseau AWS sécurisé qui sépare la production et le développement, relie le siège (Genève-Cornavin) et l'agence (Lausanne), journalise les accès et protège des données financières sensibles, avec un budget maîtrisé et une infrastructure reproductible.

## 2. Notre réponse en une page
| Objectif | Ce que nous avons livré | Preuve |
|---|---|---|
| Isoler prod / dev | Deux réseaux privés distincts (`10.20.0.0/22`, `10.21.0.0/24`) reliés par un lien contrôlé limité au port 8080 de l'API | tests du module 5 |
| Relier siège et agence en chiffré | Tunnels **IPsec IKEv2 (AES-256, SHA-256, PFS)** ; clés dans un coffre-fort de secrets ; le siège joint l'application, l'agence seulement l'API (8080), aucun site ne voit le développement | modules 7 et 8 |
| Filtrer et journaliser | Pare-feux à deux niveaux (Security Groups, NACL), journaux de flux réseau, alarme sur erreurs applicatives | modules 3 et 12 |
| Répartition de charge et DNS | Répartiteur HTTPS sur 2 zones, routage `/api/*`, DNS privé/public avec bascule automatique, CDN | modules 9 à 11 |
| Maîtriser les coûts | Ressources facturées à l'heure supprimées après usage ; coût total du projet très inférieur au budget | section 7 |
| Reproductibilité | Template CloudFormation : suppression puis redéploiement identique, sans étape manuelle | module 13 |

![Architecture](../images/global.png)

## 3. Architecture
* **Production** `vpc-prod-leman` (`10.20.0.0/22`, 1 024 adresses – dimensionnée au besoin réel) : sous-réseaux **public** (serveur web, répartiteur), **privé** (application, aucune adresse publique) ; accès Internet sortant par NAT ; accès d'administration par **AWS Systems Manager** (aucun port SSH exposé, aucune clé à gérer).
* **Développement** `vpc-dev-leman` (`10.21.0.0/24`) : isolé ; il n'atteint la production que sur `app-01:8080`.
* **Publication** : CloudFront (CDN) → ALB (HTTPS) → web et API ; l'ALB n'accepte **que** CloudFront.
* **Sites** : siège `192.168.10.0/24` et agence `192.168.20.0/24` reliés par IPsec ; liaison dédiée simulée en GRE/BGP avec bascule automatique vers le VPN.

## 4. Sécurité
| Mesure | Détail |
|---|---|
| Moindre privilège | Security Groups par rôle : le web n'accepte que l'ALB, l'application que le web (et les sites autorisés) |
| Défense en profondeur | NACL sans état sur le sous-réseau public, ordre des règles maîtrisé |
| Secrets | clés IPsec dans AWS Secrets Manager (`Projet/SatomCloudNetwork/vpn`), jamais dans un document ni un dépôt |
| Aucun accès SSH | administration par SSM Session Manager, traçable |
| Chiffrement | TLS 1.2/1.3 sur le répartiteur, IPsec entre sites |
| Traçabilité | VPC Flow Logs (acceptés/rejetés), tags `Projet`, `Equipe`, `Environnement` sur toutes les ressources |
| Origine protégée | accès direct à l'ALB depuis Internet impossible (liste de préfixes CloudFront seulement) |

## 5. Résultats des tests (extraits)
| Test | Résultat |
|---|---|
| VPC : création d'un sous-réseau chevauchant | refusée par AWS (`InvalidSubnet.Conflict`) |
| Prod : route par défaut retirée | échec immédiat du trafic sortant (19 s), rétabli dès la route restaurée |
| NACL : règle de retour retirée | flux HTTPS coupé (comportement sans état démontré) |
| Peering : CIDR chevauchant | état `failed` ; 3ᵉ VPC non joignable depuis dev (non-transitivité) |
| ALB : serveur web arrêté | cible `unhealthy`, réponse 502, retour à `healthy` après redémarrage |
| Route 53 : serveur principal arrêté | bascule DNS vers le secours en **34 s**, retour au primaire en **23 s** |
| CloudFront | contenu statique `Hit` (mis en cache), API jamais mise en cache, accès direct à l'ALB bloqué, invalidation efficace |
| CloudFormation | dérive détectée (`DRIFTED`) puis corrigée ; stack supprimée et redéployée à l'identique |

## 6. Limites et écarts à connaître
| Sujet | Situation | Conséquence |
|---|---|---|
| Services bloqués sur la plateforme de formation | Network Firewall, Transit Gateway, VPN managé, Direct Connect | Architecture, templates validés et procédures fournis ; VPN et Direct Connect **simulés** avec de vrais protocoles (strongSwan, FRRouting) |
| Région | Stockholm (la région Zurich n'est pas activée sur la plateforme) | Pour la production réelle, Zurich/Francfort conviendrait à la localisation des données : il suffit de changer le paramètre de région |
| Domaine et certificats | domaine fictif | certificats auto-signés / CloudFront par défaut ; en production : domaine réel + ACM validé par DNS |
| Quotas du compte partagé | 16 vCPU, 5 Elastic IP pour toute la classe | un site simulé à la fois |

## 7. Coûts
| Poste | Ordre de grandeur |
|---|---|
| NAT Gateway | ~0,045 USD/h (supprimée hors usage) |
| ALB | ~0,03 USD/h |
| Instances `t3.micro` | ~0,01 USD/h chacune |
| CloudFront, Route 53, CloudWatch | négligeable à cette échelle |
| Network Firewall, Transit Gateway, VPN managé (cibles) | ~0,40 USD/h, ~0,05 USD/h par attachement, ~0,05 USD/h par connexion : à budgéter en production |

Les crédits du compte ont été augmentés par les activités pédagogiques (120 → 180 USD) ; l'ensemble du projet consomme une très faible partie du budget.

## 8. Reproductibilité et exploitation
* **Code** : scripts PowerShell/AWS CLI (un par module), templates CloudFormation (`reseau-leman.yaml`, `optional-*.yaml`), schémas et preuves dans le dépôt Git.
* **Déploiement complet** : une commande de création de stack (voir module 13) ; suppression propre en ordre inverse.
* **Exploitation** : tableau de bord CloudWatch, alarme 5xx → SNS, journaux de flux interrogeables avec Logs Insights, procédures de diagnostic en quatre étapes par module.

## 9. Recommandations
1. Lever la restriction sur Network Firewall et Transit Gateway pour la production et rejouer les modules 4 et 6 avec les templates fournis.
2. Remplacer la simulation du lien siège/agence par deux tunnels Site-to-Site VPN managés (templates prêts) et commander la liaison Direct Connect (1 Gbit/s, marge ≈ 44 % pour 2 To transférés en 8 h).
3. Acquérir le domaine, valider les certificats ACM par DNS, déléguer la zone Route 53.
4. Déployer en région Zurich ou Francfort (localisation des données), avec une deuxième zone de disponibilité pour l'application.
5. Mettre en place un budget AWS avec alerte à 80 % et un abonnement e-mail SNS pour l'équipe d'exploitation.

## 10. Prochaines étapes
Validation du dossier par Léman Finance → recette sur environnement de production → bascule des utilisateurs → transfert d'exploitation (procédures de diagnostic, tableau de bord, alarmes).
