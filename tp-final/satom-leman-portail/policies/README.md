# policies/

Règles de sécurité appliquées par la pipeline (étape 2).

À écrire, sprint par sprint :
- `cfn-guard` : aucun port d'administration (22, 3389) ouvert à `0.0.0.0/0` ; route par défaut d'un sous-réseau privé vers la NAT jamais vers l'IGW ; chiffrement KMS des journaux, volumes et compartiments ; tags obligatoires.
- `checkov` : configuration (par exemple `.checkov.yaml`) ; chaque exception passe par un ADR (risque, propriétaire, date de revue).
- Règles Sonar personnalisées si besoin.

Test à prévoir : un modèle volontairement fautif doit **échouer** à la pipeline (preuve que la règle fonctionne).
