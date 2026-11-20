# satom-leman-portail

Squelette du dépôt du **TP final DevSecOps** (portail Groupe Léman Finance SA), équipe TP-AC. Il suit la structure demandée par le sujet (https://hackmd.io/@Formateur/rJOiAHwCMg). À copier dans le dépôt `Morrad-Satom-IT/satom-leman-portail` dès que l'organisation GitHub l'accepte.

```
satom-leman-portail/
├── templates/          # un YAML par domaine (réseau, sécurité, calcul, edge, supervision)
│   └── _depart/        # modèles du TP réseau, à découper (voir templates/README.md)
├── parameters/         # dev.json, prod.json (aucun secret)
├── policies/           # règles cfn-guard / checkov, règles Sonar
├── app/                # petite application (Python) et ses tests unitaires
├── tests/              # tests de connectivité, de charge (k6) et de DAST (ZAP)
├── sbom/               # inventaire des dépendances généré par la pipeline
├── docs/               # journal.md, ADR, schémas, rapports
└── .github/workflows/  # pipeline (ci.yml : étapes 1 et 2 prêtes, la suite en commentaire)
```

## Premiers pas (point de contrôle G0)
1. Créer le dépôt, **protéger `main`** (pull request obligatoire, une revue, pas de commit direct), activer GitHub Actions.
2. Configurer l'**OIDC GitHub vers AWS** (un seul fournisseur `token.actions.githubusercontent.com` par compte : vérifier s'il existe déjà) et un rôle de déploiement au moindre privilège, avec une condition sur ce dépôt. **Aucune clé d'accès** dans le dépôt.
3. Budget et alertes actifs (150 CHF, alerte à 80 %).
4. Tester les services possiblement bloqués par l'organisation (Security Hub, GuardDuty, Config, WAF, KMS, Synthetics, X-Ray) et noter les refus dans un ADR.
5. Pipeline minimale verte : `cfn-lint`, `gitleaks`, tests unitaires (voir `.github/workflows/ci.yml`).

## Règles du projet
- Aucun commit direct sur `main`, une pull request par sprint relue par l'autre membre, messages au format Conventional Commits.
- Un ADR par décision importante (`docs/adr/`).
- Tout ce qui est facturé à l'heure est détruit en fin de séance et recréé depuis ce dépôt.
- Tags de toutes les ressources : `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=<dev|prod>`, `Module=<n>`.
- Voir `AGENTS.md` du dépôt du TP réseau pour le contexte complet.
