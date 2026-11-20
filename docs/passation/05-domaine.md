# Domaine : comment l'utiliser (pour toi et pour ton assistant IA)

Le sujet du TP final utilise `portefeuilles.leman-finance.example`. Ce nom est **fictif et ne peut pas être délégué** : avec lui, pas de certificat ACM validé par DNS, pas de DNSSEC, pas de vraie résolution publique. Il faut un vrai domaine. Nous avons déjà prouvé que la démarche marche (modules 9 à 11 du TP réseau).

## Principe (pour ne rien casser)
On ne branche jamais un domaine entier sur AWS. On **délègue un sous-domaine** à une zone publique Route 53 : au fournisseur DNS du domaine on ajoute seulement quatre enregistrements `NS` pour ce sous-domaine. Tout le reste du domaine (site web, courrier, etc.) n'est pas touché. À la fin, on retire ces quatre enregistrements.

## Option A (recommandée) : un sous-domaine du domaine d'Abderahmane
Exemple : tu possèdes `exemple.ch` et tu choisis le sous-domaine `portail`.
1. **Route 53** (console) -> « Créer une zone hébergée » -> nom `portail.exemple.ch`, type **publique**, balises du projet. Noter les **quatre serveurs de noms** (visibles dans « Détails de la zone hébergée » : la liste des enregistrements masque NS et SOA).
2. **Chez le fournisseur DNS de `exemple.ch`** (Cloudflare, Infomaniak, OVH, etc.) : ajouter quatre enregistrements de type **NS**, nom `portail`, valeur = chacun des quatre serveurs de noms. Rien d'autre.
3. **Vérifier** : `nslookup -type=NS portail.exemple.ch` doit renvoyer les quatre serveurs d'AWS (quelques minutes).
4. **Certificat ACM** (une fois dans la région de l'ALB, une fois en **`us-east-1`** pour CloudFront) : demander `portail.exemple.ch` et `*.portail.exemple.ch`, validation **DNS** ; dans la console, le bouton « Créer des enregistrements dans Route 53 » crée le CNAME de validation. Compter une à deux minutes.
5. **Noms à créer dans la zone** : `origin.portail.exemple.ch` (alias vers l'ALB), `portefeuilles.portail.exemple.ch` (basculement, principal alias vers l'ALB), `cdn.portail.exemple.ch` (alias vers CloudFront).
6. **DNSSEC (sprint 10)** : créer une clé KMS asymétrique **en `us-east-1`** (ECC_NIST_P256, signature), activer DNSSEC dans Route 53, puis ajouter l'enregistrement **DS** (fourni par Route 53) dans la zone **parente** chez ton fournisseur, au nom du sous-domaine. Vérifie que ton fournisseur accepte les DS d'un sous-domaine délégué (Cloudflare : oui). Retire le DS à la fin, avant de supprimer la zone, sinon le sous-domaine ne se résout plus.
7. **À la fin** : supprimer d'abord les enregistrements propres à la zone, la zone, puis (chez ton fournisseur) les quatre NS (et le DS).

## Option B (repli) : `leman.thomastp.ch`, le sous-domaine de Thomas
C'est le domaine que nous avons déjà utilisé. `thomastp.ch` est le **portfolio de Thomas** (hébergé chez Cloudflare) : on n'y touche **que** pour les quatre NS de `leman` (et un DS éventuel). Seul Thomas peut le faire. Marche à suivre :
1. Abderahmane crée la zone publique `leman.thomastp.ch` dans Route 53 et envoie les quatre serveurs de noms à Thomas.
2. Thomas, dans Cloudflare : `thomastp.ch` -> DNS -> Enregistrements -> **Ajouter un enregistrement**, type **NS**, nom `leman`, valeur = un serveur de noms, un enregistrement par serveur (quatre en tout). Le menu « Type » demande de cliquer sur l'option « NS » (la saisie ne filtre pas).
3. À la fin du travail, Thomas supprime ces quatre enregistrements (et le DS si DNSSEC a été activé) : **uniquement ceux dont le nom est `leman`**.

> **Règle pour l'assistant IA :** ne modifie jamais le DNS de `thomastp.ch` toi-même et ne demande jamais d'accès au compte Cloudflare de Thomas. Prépare les valeurs (les quatre serveurs de noms) et demande à Thomas de les ajouter. Ne touche à aucun autre enregistrement de cette zone (MX, SPF, DMARC, Workers du portfolio).

## Ce que le domaine apporte au TP final
Il rend réalisables : un certificat ACM public validé par DNS (ALB et CloudFront), un vrai basculement Route 53 mesurable de l'extérieur (`dig` vers un serveur de noms AWS), DNSSEC, un test OWASP ZAP sur un vrai nom, Lighthouse sur la page d'accueil, et une démonstration crédible. À valider avec le formateur (question 18 de `docs/tp-final/questions-formateur.md`).

## Mesures de référence (TP réseau, domaine réel)
- Bascule DNS vers le secours : 33 s dans la vidéo (70 s à la première mesure). Retour au principal : 141 s dans la vidéo (34 s à la première mesure). Le sujet demande moins de 60 s : à régler en abaissant l'intervalle de surveillance et en réduisant le TTL.
- Détails : `docs/modules/m10.md` et `docs/modules/m10/tests-domaine-reel.txt`.
