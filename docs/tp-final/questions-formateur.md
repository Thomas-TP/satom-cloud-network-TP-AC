# TP final DevSecOps : questions pour le formateur (équipe TP-AC)

Thomas Prud'homme et Abderahmane Chaouche. Nous avons lu la version 2 du sujet en entier. Avant de commencer, nous avons besoin de quelques réponses, surtout sur ce que le compte partagé permet. Pour chaque question, nous écrivons ce que nous ferons **par défaut** : un simple « oui » ou « non » nous suffit.

Les questions marquées **[bloquante]** nous empêchent de démarrer ou changent l'architecture : une réponse rapide nous ferait gagner plusieurs jours.

## A. Rendu et démonstration

1. **Date et heure exactes du rendu.** Nous comprenons vendredi 27 novembre 2026 : à quelle heure, et où rendons-nous (dépôt GitHub, HackMD, les deux) ? *Par défaut : dépôt GitHub et HackMD le vendredi matin.*
2. **La démonstration de 15 minutes** (suppression de `dev`, recréation depuis le dépôt, mesures) : en direct devant vous, ou enregistrée ? Le même jour que le rendu ? *Par défaut : en direct, avec une vidéo de secours.*
3. **Rapport de trois pages.** Pouvons-nous mettre les preuves (captures, rapports de charge, SonarQube, Security Hub) en annexe, sans les compter dans les trois pages ? *Par défaut : oui, en annexe.*
4. **Réutilisation.** Pouvons-nous partir de ce que nous avons déjà fait pour le TP précédent (modèles CloudFormation, scripts, mesures) et le reprendre dans le dépôt du TP final ? *Par défaut : oui.*

## B. Compte AWS partagé, région, budget

5. **[bloquante] Région.** Le sujet demande `eu-central-2` (Zurich). Zurich n'est pas activée sur le compte (`AuthFailure`) et Francfort est refusée par l'organisation. Pouvons-nous rester sur Stockholm (`eu-north-1`), comme au TP précédent ? Sinon, pouvez-vous activer Zurich ? *Par défaut : Stockholm.*
6. **Plages d'adresses.** Le sujet donne `10.0.0.0/16` et `10.1.0.0/16`, déjà utilisées par d'autres équipes. Pouvons-nous garder nos plages (`10.20.0.0/22` pour la production, `10.21.0.0/24` pour le développement) ? *Par défaut : nos plages.*
7. **[bloquante] Quota de vCPU.** Le compte est limité à 48 vCPU pour toute la classe, et il a été saturé plus d'une fois. Pour ce TP, il nous faut en même temps : un runner GitHub dans le VPC, deux routeurs de site simulés, un routeur côté AWS, `web-01`, `app-01` et `dev-01`. Combien de vCPU pouvons-nous utiliser, et à quels moments ? *Par défaut : une dizaine de vCPU, arrêtés en dehors des séances.*
8. **Budget.** Le sujet parle de 150 CHF par équipe, mais le compte dispose de crédits partagés (100 USD au départ). Comment est mesurée notre consommation, et existe-t-il un plafond par équipe ? *Par défaut : nous restons sous 80 % de 150 CHF et nous supprimons les ressources facturées à l'heure après chaque séance.*
9. **[bloquante] Services possiblement bloqués.** Certains services étaient refusés par une règle de l'organisation jusqu'au 17/11. Pouvez-vous confirmer que nous pouvons créer : AWS Security Hub, GuardDuty, AWS Config (règles et enregistreur), IAM Access Analyzer, X-Ray, CloudWatch Synthetics, AWS WAF, des clés KMS, un fournisseur d'identité OIDC IAM, et DNSSEC sur Route 53 ? Sinon, une dérogation documentée par ADR convient-elle ? *Par défaut : nous testons chaque service dès le point de contrôle G0 et nous documentons les refus en ADR.*

## C. Services qui valent pour tout le compte

10. **[bloquante] Score Security Hub (≥ 90 %).** Security Hub évalue tout le compte, donc aussi les ressources des autres équipes. Comment notre score est-il calculé : sur les seules ressources avec le tag `Equipe=TP-AC`, ou sur le compte entier ? *Par défaut : nous filtrons sur notre tag et nous documentons les écarts.*
11. **Activation de Security Hub, GuardDuty et Config.** Ces services sont-ils déjà activés au niveau de l'organisation ? Si non, pouvons-nous les activer nous-mêmes, sachant que cela concerne et coûte pour toute la classe, ou préférez-vous le faire ? *Par défaut : nous demandons avant d'activer.*
12. **[bloquante] Fournisseur OIDC de GitHub.** Un seul fournisseur `token.actions.githubusercontent.com` peut exister par compte. Existe-t-il déjà ? Si oui, pouvons-nous créer notre propre rôle de déploiement qui l'utilise, avec une condition sur notre dépôt ? *Par défaut : nous réutilisons le fournisseur existant, ou nous le créons s'il n'existe pas.*
13. **Nom et permissions du rôle de déploiement.** Pouvons-nous créer des rôles IAM nommés `TP-AC-*` ? Le rôle partagé que nous utilisons peut-il créer des rôles et des politiques ? *Par défaut : nous préfixons tout par `TP-AC-` et nous appliquons le moindre privilège.*

## D. GitHub et outils d'analyse

14. **Organisation `Morrad-Satom-IT`.** Pouvez-vous nous inviter avec les droits nécessaires pour créer le dépôt `satom-leman-portail`, protéger `main`, configurer des environnements avec approbation manuelle, des secrets et des variables, et utiliser GitHub Actions ? *Par défaut : nous attendons votre invitation, sinon nous créons le dépôt dans notre compte personnel.*
15. **Dépôt public ou privé.** Un runner auto-hébergé sur un dépôt public peut exécuter du code venant d'une pull request externe. Le dépôt peut-il être privé, avec l'accès donné à vous seul ? *Par défaut : privé.*
16. **Revue des pull requests.** Nous sommes deux : chacun relit les pull requests de l'autre. Cela suffit-il pour le critère de gouvernance ? *Par défaut : oui.*
17. **SonarQube.** Une instance est-elle fournie ? Sinon, pouvons-nous utiliser SonarCloud (gratuit pour un dépôt public), ou devons-nous héberger SonarQube Community sur une instance AWS ? Savez-vous que l'affichage dans la pull request demande une édition Developer ? *Par défaut : SonarCloud si le dépôt est public, SonarQube Community sur EC2 s'il est privé.*

## E. Points techniques du sujet

18. **[bloquante] Domaine.** Le sujet utilise `portefeuilles.leman-finance.example` : ce nom ne peut pas être délégué, donc ni certificat ACM validé ni DNSSEC. Pouvons-nous utiliser notre vrai sous-domaine `leman.thomastp.ch` (déjà délégué à Route 53 pendant le TP précédent, sans toucher au reste du domaine) ? *Par défaut : oui.*
19. **DNSSEC.** Pour activer DNSSEC sur la zone publique, il faut ajouter un enregistrement DS dans la zone parente (chez nous, `thomastp.ch`, hébergée chez un autre fournisseur) et une clé KMS en `us-east-1`. Cela vous convient-il ? *Par défaut : oui, en retirant le DS à la fin.*
20. **[bloquante] VPN du sprint 7.** Les adresses `203.0.113.10` et `198.51.100.20` sont réservées à la documentation : aucun tunnel ne peut monter vers elles, donc l'alarme `TunnelState` ne peut pas se tester. Pouvons-nous les remplacer par deux routeurs simulés (instances avec strongSwan et une adresse IP publique), comme au TP précédent ? *Par défaut : oui.*
21. **Direct Connect (sprint 8).** Nous ne pouvons pas commander de liaison. Une passerelle Direct Connect réelle associée à la Transit Gateway, plus une liaison simulée (tunnel GRE et BGP entre deux routeurs) et un ADR sur le choix de la voie principale, convient-il ? *Par défaut : oui.*
22. **CloudFront (sprint 11).** OAC (Origin Access Control) ne s'applique qu'aux origines S3 et pas à un ALB. Pour protéger l'ALB, pouvons-nous utiliser la liste de préfixes gérée de CloudFront et un en-tête secret ? *Par défaut : oui, sans OAC.*
23. **Traces X-Ray « sur l'ALB ».** L'ALB ne produit pas de segments X-Ray lui-même. Pouvons-nous instrumenter l'application (SDK X-Ray) et considérer la trace complète comme remplissant l'exigence ? *Par défaut : oui.*
24. **Disponibilité mensuelle de 99,5 %.** Elle ne peut pas se mesurer sur un mois. Pouvons-nous la mesurer sur la période de test (quelques jours, avec CloudWatch Synthetics) et le dire dans le rapport ? *Par défaut : oui.*
25. **Taux de cache supérieur à 80 % et Lighthouse.** Sur quel scénario de charge mesure-t-on le taux de cache ? Faut-il une page d'accueil statique pour Lighthouse CI ? *Par défaut : une petite page d'accueil statique, et un scénario k6 avec 80 % de requêtes statiques.*
26. **RTO et RPO.** Le portail n'a pas de base de données : le RPO est donc nul par construction. Pouvons-nous le justifier ainsi, et ne mesurer que le RTO (suppression et recréation de `dev`) ? *Par défaut : oui.*
27. **Tags.** Le tag `Module=<n>` s'ajoute à nos trois tags habituels. Quand un modèle regroupe plusieurs modules, quel numéro mettons-nous ? *Par défaut : le module principal du modèle.*

## F. Évaluation

28. **Minimum par critère.** En cas de service refusé par l'organisation (voir la question 9), la dérogation par ADR compte-t-elle comme critère satisfait ? *Par défaut : oui, avec le risque, le propriétaire et la date de revue.*
29. **Métriques DORA.** Sur une semaine de travail, nous mesurerons les quatre indicateurs de chaque sprint dans `docs/journal.md`. Cette période courte est-elle acceptable ? *Par défaut : oui.*
30. **Points de contrôle (gates).** Les validez-vous vous-même, ou les validons-nous seuls avec preuve dans `docs/` ? *Par défaut : nous les consignons avec preuve.*

Merci d'avance. Les questions bloquantes sont les n° 5, 7, 9, 10, 12, 18 et 20.
