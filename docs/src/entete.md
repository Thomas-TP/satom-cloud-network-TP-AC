# Satom Cloud Network – Dossier du binôme TP-AC

Projet réalisé par Thomas Prud'homme et Abderahmane Chaouche pour le client fictif Groupe Léman Finance SA (formation AWS niveau 300, Geneva Institute of Technology, promo E3, semaine du 16 au 20 novembre 2026).

Tout le TP a été refait à la main dans la console AWS, puis filmé : les captures de ce dossier sont tirées de ces enregistrements (le bandeau avec le compte et le rôle est masqué, comme les identifiants de compte). Une première version avait été faite en ligne de commande (scripts du dépôt) ; quand un chapitre cite une mesure de cette première version, il le dit.

Tout est fait dans la région de Stockholm (`eu-north-1`). Nos ressources portent le suffixe `-TP-AC` et les tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC` et `Environnement=prod` ou `dev`.

Les modules 9, 10 et 11 utilisent un domaine réel : le sous-domaine `leman.thomastp.ch`, délégué à Route 53, avec des certificats publics ACM validés par DNS.

## Vidéo
{%youtube emZqnBNtOjM %}

Vidéo complète du tutoriel (34 minutes, voix de Thomas et d'Abderahmane), refaite à la main dans la console AWS, modules 0 à 13, avec un vrai domaine pour les modules 9 à 11 : [https://youtu.be/emZqnBNtOjM](https://youtu.be/emZqnBNtOjM) (non répertoriée : seules les personnes qui ont le lien peuvent la voir).

## Où nous en sommes

Tout est fait : les modules 0 à 13 sont réalisés, testés et filmés.

![Schéma réseau final](../images/global.png)

Tout le code (scripts AWS CLI, templates CloudFormation), les preuves et les captures sont dans le dépôt GitHub public `Thomas-TP/satom-cloud-network-TP-AC`.
