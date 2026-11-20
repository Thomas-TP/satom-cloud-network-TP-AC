# ADR 0001 : région et domaine (brouillon, à valider avec le formateur)

- **Date :** à compléter
- **Statut :** proposé
- **Propriétaire :** Abderahmane

## Contexte
Le sujet demande la région `eu-central-2` (Zurich) et le domaine fictif `portefeuilles.leman-finance.example`. Zurich n'est pas activée sur le compte (`AuthFailure`), Francfort est refusée par l'organisation. Un nom en `.example` ne peut pas être délégué : pas de certificat ACM validé par DNS, pas de DNSSEC.

## Décision proposée
- Région **`eu-north-1` (Stockholm)** ; certificats CloudFront en `us-east-1`.
- Un **vrai sous-domaine** délégué à une zone publique Route 53 (voir `docs/passation/05-domaine.md` du dépôt du TP réseau).

## Conséquences et risques
- Les mesures de latence sont prises depuis Stockholm, pas Zurich : à indiquer dans le rapport.
- Le DNSSEC demande un enregistrement DS chez le fournisseur du domaine parent, à retirer à la fin.
- Dépend de la réponse du formateur (questions 5 et 18).
