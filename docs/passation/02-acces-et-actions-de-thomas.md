# Accès, comptes et actions de Thomas

## 1. Dépôt GitHub : ajouter Abderahmane comme collaborateur (recommandé)
On garde le dépôt chez Thomas (`Thomas-TP/satom-cloud-network-TP-AC`) et on invite Abderahmane en écriture. Un transfert complet casserait des liens (HackMD, README, YouTube) pour rien.

**Thomas, avec l'interface web :**
1. Ouvrir https://github.com/Thomas-TP/satom-cloud-network-TP-AC
2. **Settings** (onglet en haut à droite) -> **Collaborators** (menu de gauche, rubrique « Access »).
3. **Add people**, taper le pseudo GitHub (ou l'e-mail) d'Abderahmane, le choisir dans la liste.
4. Choisir le rôle **Write** (lire, écrire, ouvrir des pull requests). **Maintain** si Abderahmane doit aussi gérer les paramètres.
5. **Add**. GitHub envoie une invitation.

**Thomas, avec la ligne de commande** (déjà connecté avec `gh`) :
```powershell
gh api -X PUT repos/Thomas-TP/satom-cloud-network-TP-AC/collaborators/<PSEUDO_ABDERAHMANE> -f permission=push
```
(`permission` accepte `pull`, `triage`, `push`, `maintain`, `admin`.)

**Abderahmane :** accepter l'invitation par e-mail, ou sur https://github.com/Thomas-TP/satom-cloud-network-TP-AC/invitations. Puis :
```powershell
git clone https://github.com/Thomas-TP/satom-cloud-network-TP-AC.git
```
**Vérification :** Abderahmane peut pousser une petite branche ; Thomas voit son nom dans Settings -> Collaborators.

*(Transférer entièrement : Settings -> General -> Danger Zone -> Transfer ownership. Pas recommandé ici.)*

### Le dépôt du TP final
Le sujet impose l'organisation `Morrad-Satom-IT` et le dépôt `satom-leman-portail`. C'est le **formateur** qui doit inviter Abderahmane dans cette organisation (question 14). En attendant, le squelette est prêt dans `tp-final/satom-leman-portail/` : à copier tel quel dans le nouveau dépôt.

## 2. AWS
Tout le monde utilise le **même compte partagé** de la classe, région `eu-north-1`. Il n'y a rien à transférer.
```powershell
aws login --region eu-north-1 --profile TP-AC      # connexion par navigateur, aucune clé à copier
aws sts get-caller-identity --profile TP-AC        # vérifie l'accès ; ne publie jamais le résultat
aws ec2 describe-vpcs --filters Name=tag:Equipe,Values=TP-AC --profile TP-AC --region eu-north-1
```
La dernière commande liste nos VPC (il en reste quatre, vides : voir `docs/NETTOYAGE.md`). Rappel : nous ne touchons qu'aux ressources `Equipe=TP-AC`.

## 3. Claude Code
Voir `README.md` de ce dossier : `git clone`, puis `claude` à la racine. `CLAUDE.md` renvoie vers `AGENTS.md`.

## 4. Notes HackMD du TP réseau
Elles appartiennent au compte de Thomas (`ThomasTP`). Les liens sont dans `docs/hackmd/notes.json` et le README. Abderahmane les lit sans compte. Pour les modifier, Thomas l'invite sur chaque note (bouton **Invite**), ou Abderahmane fait une copie. Les notes se régénèrent avec `scripts/build_hackmd.py` puis `scripts/publish_hackmd.py` : il faut alors un **jeton d'API HackMD** (HackMD -> Settings -> API), passé en variable d'environnement `HACKMD_TOKEN`, **jamais** écrit dans un fichier. Ce n'est pas nécessaire pour le TP final.

## 5. Vidéo YouTube
Elle est sur la chaîne de Thomas, en non répertoriée : le lien suffit pour la voir. Rien à transférer.

## 6. Domaine
Voir `05-domaine.md`. Choix recommandé : Abderahmane utilise un sous-domaine de **son propre** domaine. Le domaine `thomastp.ch` (portfolio de Thomas, chez Cloudflare) n'est qu'une solution de repli, et seul Thomas peut y ajouter les enregistrements.

## Liste de ce que Thomas doit faire (checklist)
- [ ] Inviter Abderahmane sur le dépôt (section 1) et vérifier qu'il a accepté.
- [ ] Donner à Abderahmane ces fichiers par message : le lien du dépôt, ce dossier `docs/passation/`, le sujet du TP final.
- [ ] Révoquer les jetons HackMD donnés dans le chat (HackMD -> Settings -> API). Vérifier aussi qu'aucun autre jeton ou clé n'a été partagé.
- [ ] Si Abderahmane choisit finalement `leman.thomastp.ch` : ajouter les enregistrements NS chez Cloudflare quand il le demande (voir `05`), et les retirer ensuite.
- [ ] Relancer `DeleteFirewall` (ou le cas Support 179508151300233) tant que le pare-feu n'est pas supprimé ; ensuite supprimer la politique, le groupe de règles, les VPC et les Customer Gateways restants (`docs/NETTOYAGE.md`).
- [ ] Décider si la note HackMD « questions du formateur » (https://hackmd.io/@ThomasTP/B1kkt7A0fl, créée par erreur) doit être supprimée.
- [ ] Transmettre à Abderahmane la réponse du formateur aux questions dès qu'elle arrive.

## Ce qui reste hors du dépôt, sur le PC de Thomas (volontairement)
Rien de tout cela n'est utile au TP final : voir `06-fichiers-et-outils.md`. Si Abderahmane en a besoin un jour, Thomas peut les lui transmettre séparément.
