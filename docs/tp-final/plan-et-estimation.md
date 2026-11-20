# TP final : estimation du coût et plan jusqu'à vendredi 27/11/2026

Document interne (équipe TP-AC). Les prix sont des tarifs publics approximatifs (ordre de grandeur, à plus ou moins 30 %), à confirmer sur la page de tarification AWS ; je n'ai pas pu les vérifier en direct.

## 1. Coût AWS estimé

### Ressources facturées à l'heure, seulement pendant les séances
| Ressource | Quantité | Coût approximatif par heure |
|---|---|---|
| Network Firewall (un point d'accès) | 1 | 0,40 USD |
| Transit Gateway (4 attachements : prod, dev, 2 VPN) | 4 | 0,20 USD |
| Connexions VPN | 2 | 0,10 USD |
| NAT Gateway | 1 | 0,045 USD |
| ALB | 1 | 0,03 USD |
| Instances (`web-01`, `app-01`, `dev-01`, 3 routeurs, runner) | 7 | 0,08 USD |
| Adresses IPv4 publiques | environ 10 | 0,05 USD |
| **Total, environnement complet** | | **environ 0,90 USD par heure** |

Hypothèse : 35 heures d'environnement complet sur la semaine (par exemple cinq séances de sept heures), le reste du temps tout est supprimé. Cela donne environ **31 USD**.

### Ressources qui courent toute la semaine
| Ressource | Coût sur 7 jours |
|---|---|
| Tableaux de bord CloudWatch (3) | environ 2 USD |
| AWS WAF (une ACL, quelques règles) | environ 2 USD |
| Clés KMS (3 : journaux, DNSSEC, chiffrement) | environ 1 USD |
| Secrets Manager (clés VPN) | environ 0,10 USD |
| Route 53 (zones, vérifications de santé) | environ 1 USD |
| CloudWatch Synthetics (une sonde toutes les 5 minutes) | environ 2,50 USD |
| Config (règles, éléments enregistrés) | 1 à 3 USD |
| Journaux CloudWatch, X-Ray, CloudFront | moins de 2 USD |
| SonarQube sur EC2, si hébergé (`t3.medium`) | environ 2,50 USD |
| Security Hub et GuardDuty | 0 USD pendant l'essai de 30 jours s'il est disponible, sinon quelques USD |
| **Total** | **environ 12 à 20 USD** |

### Synthèse
| Scénario | USD | CHF (à 0,80) |
|---|---|---|
| Bas (séances courtes, tout supprimé à chaque fois) | 25 | 20 |
| **Probable** | **45** | **36** |
| Haut (oublis, séances longues, tests de charge répétés, Security Hub payant) | 70 | 56 |

Le budget du sujet est de 150 CHF par équipe, alerte à 80 % (120 CHF) : nous restons largement dessous. Mais le plafond réel est celui des **crédits partagés du compte** (100 USD au départ, relevés plus tard) : nous ne savons pas combien en ont déjà consommé les autres équipes. C'est la question 8 du formateur.

Deux coûts qui font basculer l'estimation : laisser le pare-feu allumé la nuit (environ 9,50 USD par nuit de 24 h, tout compris environ 22 USD) et oublier un Transit Gateway.

## 2. Coût en crédit pour moi (Claude)

Je ne connais pas le prix de ton abonnement, donc je ne peux pas le chiffrer en francs. Ordre de grandeur relatif : ce TP final représente **deux à trois fois** ce que nous avons consommé aujourd'hui pour la vidéo, le dossier et les notes HackMD, parce qu'il y a treize sprints à écrire, tester et documenter, plus la pipeline et les mesures.

Ce qui le réduit : travailler par sprint avec des agents qui se partagent des fichiers distincts ; éviter les captures d'écran et les vidéos (le TP final est surtout du code et des rapports) ; ne pas refaire de rendu vidéo.

## 3. Calendrier jusqu'à vendredi

Aujourd'hui, vendredi 20/11. Rendu vendredi 27/11. Les temps d'attente d'AWS (pare-feu, tunnels VPN, CloudFront, DNSSEC) sont le vrai chemin critique, pas l'écriture.

| Jour | Contenu | Point de contrôle |
|---|---|---|
| Ven 20 et sam 21 | Envoi des questions au formateur. Dépôt, branche protégée, OIDC, budget et alertes, pipeline minimale (cfn-lint, gitleaks), petite application avec tests pour SonarQube | G0 |
| Dim 22 et lun 23 | Sprints 1 à 3 : réseau, routage, groupes de sécurité, NACL. Étapes 1 à 3 de la pipeline (qualité, sécurité statique, SBOM), premier déploiement `dev` | G1 |
| Mar 24 | Sprints 4 à 8 : pare-feu, peering, Transit Gateway, VPN avec routeurs simulés, Direct Connect (passerelle, liaison simulée, ADR) | G2 |
| Mer 25 | Sprints 9 à 11 : ALB, Route 53 avec DNSSEC, CloudFront avec WAF. Tests k6 et ZAP, mesures de cache et de bascule | G3 |
| Jeu 26 | Sprints 12 et 13 : tableaux de bord, alarmes, Security Hub, Config, X-Ray ; suppression et recréation de `dev` avec RTO ; journal et indicateurs DORA ; rapport de trois pages | G4 et G5 |
| Ven 27 matin | Répétition de la démonstration, corrections, rendu | |

C'est serré. Je l'estime faisable pour un résultat qui passe le seuil de 70 sur 100, **à condition que les réponses aux questions bloquantes arrivent avant dimanche**.

## 4. Ce que nous coupons si le temps manque (par ordre)
1. Lighthouse CI et CloudWatch Synthetics (moins de points).
2. Une partie des traces X-Ray (une application instrumentée suffit).
3. Le score Security Hub à 90 % : nous documentons les findings par ADR.
4. Les tests de charge répétés : un seul rapport propre par palier.

Ce que nous ne coupons pas : le dépôt propre avec pull requests et ADR (15 points), la sécurité IaC, SAST, SCA et secrets (20 points), la connectivité (15 points), et la démonstration de reprise.

## 5. Risques principaux
| Risque | Effet | Parade |
|---|---|---|
| Quota de vCPU saturé par la classe | impossible de lancer routeurs ou runner | questions 7, arrêter tout hors séance, ordre de lancement |
| Service bloqué par l'organisation | un critère sans preuve | tester dès G0, dérogation par ADR |
| Security Hub pollué par les autres équipes | score impossible à 90 % | filtrer par tag, question 10 |
| Fournisseur OIDC déjà créé par une autre équipe | pipeline bloquée | question 12 |
| DNSSEC : délai de propagation du DS | mesure en retard | l'activer dès le sprint 10 le mardi |
| Runner auto-hébergé exposé | exécution de code non voulue | dépôt privé, question 15 |
