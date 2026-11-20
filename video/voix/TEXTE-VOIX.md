# Texte de voix off - Satom Cloud Network (TP-AC)

Durée estimée avec la voix : **34.4 min** (montage muet : 32 min ; les cartes de titre, de schéma et de chapitre sont allongées pour laisser parler).
Répartition : Thomas **1865 mots** (50 %), Abderahmane **1873 mots** (50 %).

Chaque phrase est calée sur un geste précis à l’écran (repère entre crochets : minute:seconde dans la vidéo avec voix). Les nombres sont écrits comme ils seront prononcés (septante, huitante, nonante).

## Ouverture

- [0:00.5] **Thomas** : Bonjour à tous, c'est Thomas.
- [0:03.0] **Abderahmane** : Et moi, Abderahmane.

*Schéma global*
- [0:05.2] **Thomas** : Pour le Groupe Léman Finance, nous avons construit sur AWS un réseau complet : un siège à Genève, une agence à Lausanne, et le cloud au milieu.
- [0:14.6] **Abderahmane** : Au centre, le Transit Gateway sert de carrefour. À droite, la production, avec son pare-feu et son équilibreur. En dessous, le développement, bien isolé.
- [0:23.8] **Thomas** : Les sites sont reliés par des tunnels chiffrés, et en pointillé, par une liaison Direct Connect que nous simulons.
- [0:30.3] **Abderahmane** : Tout est refait en direct, à la souris, et testé à chaque étape, pannes comprises. Quand l'attente est longue, on accélère : un badge vous prévient.
- [0:38.2] **Thomas** : Quatorze modules, du budget jusqu'à CloudFormation. C'est parti.


## Module 0 - Cadrage

- [0:43.1] **Thomas** : Module zéro, le cadrage. Avant le moindre serveur, on fixe un budget, pour éviter toute mauvaise surprise.

*Fixer un budget* (m00)
- [0:50.4] **Thomas** : On crée un budget de coûts, mensuel, de cent dollars.
- [0:55.2] **Abderahmane** : Avec une alerte à huitante pour cent, vers une adresse fictive.


## Module 1 - Réseaux

- [0:59.5] **Thomas** : Le cadre est posé. Abderahmane, le réseau, c'est pour toi !
- [1:04.1] **Abderahmane** : Merci. Module un : un VPC, deux sous-réseaux, et deux serveurs qui doivent déjà se parler.

*VPC de production* (m01a)
- [1:10.9] **Abderahmane** : Le VPC de production : une plage en slash vingt-deux, soit mille vingt-quatre adresses.

*Deux sous-réseaux* (m01b)
- [1:19.5] **Thomas** : Pourquoi pas un slash seize, comme dans le sujet ?
- [1:23.0] **Abderahmane** : Parce que le compte est partagé avec la classe : il faut rester petit.
- [1:28.4] **Abderahmane** : Deux sous-réseaux, le public d'abord : slash vingt-six, soixante-quatre adresses.
- [1:32.7] **Thomas** : Dont cinq que AWS garde pour lui.

*Test de chevauchement* (m01c)
- [1:35.8] **Thomas** : Test : un sous-réseau qui en recouvre un autre.
- [1:39.2] **Thomas** : AWS refuse.

*Rôle IAM pour SSM* (m01d)
- [1:41.4] **Abderahmane** : Un rôle pour les serveurs : avec SSM, on les administre sans SSH, ni clé.

*Serveur web-01* (m01e)
- [1:48.0] **Abderahmane** : Premier serveur, web zéro un : son nom, et les balises.
- [1:56.6] **Abderahmane** : Amazon Linux, t trois point micro, sans paire de clés : Session Manager suffira.
- [2:01.8] **Abderahmane** : Réseau : VPC de production, sous-réseau public, adresse publique.
- [2:06.7] **Abderahmane** : Adresse privée fixe, puis le rôle SSM.

*Serveur app-01* (m01f)
- [2:10.2] **Thomas** : À moi le second serveur, app zéro un. Même recette, avec deux différences.
- [2:22.3] **Thomas** : Il va dans le sous-réseau privé, sans adresse publique : personne ne l'atteint depuis Internet.
- [2:27.9] **Thomas** : Et dans les données utilisateur, une mini API sur le port huit mille huitante.


## Module 2 - Routage

- [2:34.3] **Abderahmane** : Nos deux serveurs sont là. À toi, Thomas.
- [2:36.6] **Thomas** : Module deux, le routage : on branche Internet, et une NAT fait sortir le serveur privé.

*Passerelle Internet* (m02a)
- [2:42.6] **Thomas** : D'abord la passerelle Internet, avec ses balises. Une fois créée, il faut encore l'attacher au VPC.
- [2:50.3] **Thomas** : Sans cela, elle ne sert à rien.

*Table de routage publique* (m02b)
- [2:53.6] **Thomas** : Ensuite, la table de routage du sous-réseau public.
- [3:01.9] **Thomas** : Dans cette table, une route par défaut : tout ce qui n'est pas local part vers la passerelle Internet.
- [3:12.0] **Thomas** : Puis on l'associe au sous-réseau public : c'est ce qui le rend public.

*Table de routage privée* (m02c)
- [3:16.2] **Abderahmane** : Même chose pour le privé, avec sa propre table.
- [3:21.9] **Abderahmane** : Elle ne contient que la route locale : rien ne sort.

*Sous-réseau de la zone B* (m02c2)
- [3:26.1] **Abderahmane** : Un deuxième sous-réseau public, en zone B ? Pourquoi ?
- [3:29.4] **Thomas** : Parce que la zone A a déjà atteint sa limite de passerelles NAT : le compte est partagé avec toute la classe.

*Passerelle NAT* (m02d)
- [3:38.7] **Thomas** : La passerelle NAT, avec une adresse IP Elastic.
- [3:46.7] **Thomas** : Zone A : refusé, quota atteint.
- [3:49.2] **Thomas** : Zone B : ça passe.
- [3:51.1] **Abderahmane** : Un peu plus d'une minute d'attente : on accélère.

*NAT disponible* (m02d2)
- [3:55.7] **Thomas** : Et voilà, elle est disponible.

*Route privée vers la NAT* (m02e)
- [3:59.5] **Abderahmane** : Maintenant, la table du sous-réseau privé : sa route par défaut pointe vers la NAT.
- [4:05.6] **Abderahmane** : Le serveur privé peut sortir, sans jamais être joignable de l'extérieur.

*Preuve par Session Manager* (m02f)
- [4:11.1] **Thomas** : La preuve, par Session Manager : depuis app zéro un, on interroge Internet.
- [4:16.1] **Abderahmane** : C'est l'adresse de la NAT.

*Test de panne* (m02g)
- [4:18.8] **Abderahmane** : Et maintenant, une panne volontaire.
- [4:21.5] **Thomas** : Une boucle interroge Internet chaque seconde.
- [4:24.1] **Thomas** : On retire la route par défaut du privé.
- [4:27.6] **Thomas** : Et les requêtes échouent aussitôt.
- [4:30.7] **Abderahmane** : Quand une sortie Internet tombe, on vérifie dans l'ordre : la table associée, la route par défaut, sa cible, et l'état de cette cible.
- [4:40.0] **Thomas** : On remet la route, et l'adresse de la NAT revient.


## Module 3 - Sécurité

- [4:44.9] **Thomas** : Le routage tient. Abderahmane, la sécurité ?
- [4:48.5] **Abderahmane** : Module trois : les Security Groups retiennent l'état des connexions, les NACL n'ont aucune mémoire.

*Security Group « web »* (m03a)
- [4:55.4] **Abderahmane** : Premier groupe, pour le web : le port quatre cent quarante-trois, ouvert à tous.
- [5:00.6] **Abderahmane** : Le port vingt-deux, lui, est limité à une plage d'adresses précise.
- [5:06.3] **Abderahmane** : Et on étiquette, comme toujours.

*Security Group « app »* (m03b)
- [5:10.0] **Abderahmane** : Pour l'application, on est plus strict : la source des règles n'est pas une adresse.
- [5:15.8] **Thomas** : C'est quoi, alors ?
- [5:17.8] **Abderahmane** : Le groupe web lui-même. Seuls les serveurs web peuvent parler à l'application : le port huit mille huitante, le SSH, et le ping.

*Associer les groupes* (m03c)
- [5:30.6] **Thomas** : Il faut maintenant brancher ces groupes sur les instances, à la place du groupe par défaut.
- [5:37.5] **Thomas** : Web zéro un reçoit le groupe web, app zéro un le groupe application.

*Tests entre les serveurs* (m03d)
- [5:44.2] **Abderahmane** : Depuis web zéro un : le ping passe, et l'API aussi.
- [5:48.7] **Thomas** : On installe nginx, avec un certificat auto-signé, pour répondre en HTTPS.
- [5:56.5] **Thomas** : Une page à la racine, et un relais vers l'API sous slash api.

*NACL du sous-réseau public* (m03e)
- [6:01.6] **Abderahmane** : La NACL filtre au niveau du sous-réseau, et elle ne retient rien.
- [6:10.3] **Thomas** : Donc il faut tout autoriser, dans les deux sens ?
- [6:14.5] **Abderahmane** : Oui. Le quatre cent quarante-trois, les ports éphémères pour les réponses, et le trafic interne du VPC.
- [6:21.2] **Abderahmane** : Et la même chose en sortie.

*Test de panne* (m03f)
- [6:26.0] **Abderahmane** : Dernière vérification : web zéro un interroge l'API en boucle.
- [6:32.9] **Abderahmane** : On retire le huit mille huitante du groupe application.
- [6:36.3] **Thomas** : Échec : c'est bien ce groupe qui décide.
- [6:40.0] **Abderahmane** : On remet la règle, et tout repart.


## Module 4 - Pare-feu

- [6:44.4] **Abderahmane** : Notre réseau est filtré de l'intérieur. Thomas, tu nous mets un pare-feu ?
- [6:48.0] **Thomas** : Module quatre : Network Firewall. Tout ce qui sort du serveur privé passera par lui.

*Sous-réseau du pare-feu* (m04a)
- [6:53.4] **Thomas** : Le pare-feu a son propre sous-réseau, tout petit : seize adresses, le minimum accepté.

*Tables de routage* (m04b)
- [7:02.0] **Thomas** : Pour que le trafic passe au bon endroit : des tables de routage.
- [7:06.8] **Thomas** : La première, pour le sous-réseau du pare-feu : tout part vers la NAT.
- [7:13.0] **Abderahmane** : Le chemin sera donc : serveur privé, pare-feu, NAT, puis Internet.
- [7:20.4] **Thomas** : On l'associe au sous-réseau du pare-feu.
- [7:26.3] **Thomas** : La seconde est pour le sous-réseau de la NAT, en zone B : tout part vers la passerelle Internet.
- [7:35.2] **Thomas** : Avec ces deux tables, le chemin de sortie est prêt, à un maillon près.

*Groupe de règles* (m04c)
- [7:41.6] **Abderahmane** : Ensuite, les règles : un groupe de règles avec état, de type liste de domaines, en autorisation.
- [7:50.3] **Abderahmane** : Deux domaines seulement : les dépôts Amazon Linux, et les services AWS.

*Politique du pare-feu* (m04d)
- [7:56.4] **Thomas** : Puis la politique : elle décide quoi faire de ce que les règles ne couvrent pas.
- [8:03.5] **Thomas** : Ordre strict, et tout ce qui n'est pas autorisé est abandonné, avec une alerte.

*Créer le pare-feu* (m04e)
- [8:10.7] **Abderahmane** : Toutes les pièces sont là : on crée le pare-feu ?
- [8:14.3] **Thomas** : Oui : le VPC, le sous-réseau dédié, et notre politique.
- [8:19.4] **Thomas** : AWS y déploie un point de terminaison.

*Groupes de journaux* (m04f0)
- [8:24.5] **Abderahmane** : Deux groupes de journaux : les alertes d'un côté, les flux de l'autre.

*Activer la journalisation* (m04f)
- [8:30.1] **Abderahmane** : On les branche sur le pare-feu : les alertes ici, les flux là.

*Route privée vers le pare-feu* (m04g)
- [8:37.2] **Thomas** : Pare-feu prêt : la route par défaut du privé vise maintenant son point de terminaison.

*Route de retour* (m04h)
- [8:43.7] **Abderahmane** : Et une route de retour, pour que la réponse revienne par le même chemin.

*Test du pare-feu* (m04i)
- [8:50.2] **Thomas** : Le test, depuis app zéro un : d'abord un domaine autorisé.
- [8:54.5] **Thomas** : Ça aboutit : le quatre cent trois, c'est la réponse du site.
- [8:58.6] **Abderahmane** : Example point com ? Pas dans la liste : ça expire.

*Alertes et flux* (m04j)
- [9:02.7] **Abderahmane** : CloudWatch a tout enregistré : l'alerte, et les flux.


## Module 5 - Appairage

- [9:07.3] **Thomas** : Le pare-feu filtre bien. Je te passe la main, Abderahmane.
- [9:11.1] **Abderahmane** : Module cinq : un VPC de développement, relié à la production par un appairage.

*VPC de développement* (m05a1)
- [9:16.0] **Abderahmane** : Le VPC de développement : sa plage ne doit surtout pas chevaucher celle de la production.

*Sous-réseau de développement* (m05a2)
- [9:25.0] **Thomas** : Dedans, un petit sous-réseau en slash vingt-six.
- [9:29.5] **Thomas** : Une plage modeste suffit : un seul serveur y vivra.

*Passerelle Internet dev* (m05b1)
- [9:34.0] **Thomas** : Comme avant, une passerelle Internet, créée puis attachée.
- [9:39.1] **Thomas** : Elle donnera au développement sa sortie vers Internet.

*Table de routage dev* (m05b2)
- [9:44.6] **Thomas** : Les mêmes gestes qu'au module deux ?
- [9:48.7] **Abderahmane** : Exactement : une table, une route par défaut vers la passerelle, et l'association au sous-réseau.

*Security Group dev* (m05c1)
- [10:07.1] **Abderahmane** : Pour le développement, un Security Group sans aucune règle entrante : personne ne peut y entrer.

*Serveur dev-01* (m05c2)
- [10:16.8] **Abderahmane** : Puis le serveur dev zéro un, dans ce VPC, avec le même rôle pour Session Manager.
- [10:30.7] **Abderahmane** : Avec le groupe sans règle entrante.
- [10:33.0] **Abderahmane** : Adresse fixe, elle aussi.

*Appairage de VPC* (m05d)
- [10:37.3] **Thomas** : Maintenant, l'appairage : on demande la connexion de la production vers le développement.
- [10:46.2] **Thomas** : Même compte : on l'accepte nous-mêmes.

*Routes des deux côtés* (m05e)
- [10:49.4] **Abderahmane** : Chaque côté a besoin de sa route vers l'autre : d'abord dans le privé de la production, puis dans le développement.

*Autoriser le port 8080* (m05f)
- [10:59.1] **Thomas** : Le port huit mille huitante s'ouvre au développement, et à lui seul.

*Test depuis dev-01* (m05g)
- [11:04.1] **Abderahmane** : Test depuis dev zéro un.
- [11:08.7] **Thomas** : L'API répond.
- [11:10.7] **Abderahmane** : Ping refusé.
- [11:11.8] **Thomas** : SSH aussi : seul ce qu'on ouvre passe.

*Plages qui se chevauchent* (m05h)
- [11:15.0] **Abderahmane** : Dernier test : deux VPC aux plages qui se chevauchent ne s'apparient pas.
- [11:20.1] **Thomas** : AWS refuse.


## Module 6 - Transit Gateway

- [11:21.7] **Abderahmane** : L'appairage ne passe pas à l'échelle. Thomas, tu as mieux ?
- [11:24.7] **Thomas** : Module six : le Transit Gateway, un carrefour unique, avec une table de routage par environnement.

*Transit Gateway* (m06a)
- [11:30.9] **Thomas** : Avec l'appairage, chaque nouveau VPC demande une connexion de plus. Ici, un seul Transit Gateway.
- [11:37.9] **Thomas** : On désactive l'association et la propagation par défaut : on veut tout piloter nous-mêmes.

*Attachement de la production* (m06b)
- [11:44.6] **Abderahmane** : Premier attachement : le VPC de production, avec un sous-réseau par zone.

*Attachement du développement* (m06c)
- [11:53.8] **Abderahmane** : Deuxième attachement : le développement, avec son propre sous-réseau.

*Deux tables de routage* (m06d)
- [12:02.2] **Thomas** : Deux tables de routage : une pour la production, une pour le développement.
- [12:08.0] **Abderahmane** : Pourquoi deux ?
- [12:09.6] **Thomas** : Pour contrôler qui peut parler à qui. Chaque environnement ne verra que ce qu'on décide.

*Associations et propagations* (m06e)
- [12:16.5] **Thomas** : On associe chaque attachement à sa table. Puis on croise les propagations : la production apprend les routes du développement, et inversement.

*Routes apprises* (m06i)
- [12:26.8] **Abderahmane** : Chaque table ne connaît que l'autre côté.

*Routes des VPC* (m06f)
- [12:30.8] **Thomas** : Dans les VPC, les routes visent désormais le Transit Gateway, plus l'appairage.

*Supprimer l'appairage* (m06g)
- [12:39.0] **Abderahmane** : L'appairage ne sert plus : on le supprime.

*Test et panne contrôlée* (m06h)
- [12:45.5] **Thomas** : Depuis dev zéro un, l'API répond, cette fois par le Transit Gateway.
- [12:50.8] **Abderahmane** : Maintenant, on casse quelque chose. Une boucle d'appels, et on retire la propagation du développement dans la table de production.
- [12:57.9] **Thomas** : Plus de route : les requêtes échouent.
- [13:01.6] **Abderahmane** : On remet la propagation, et tout repart.


## Module 7 - VPN site à site

- [13:07.4] **Thomas** : Le carrefour est en place. Abderahmane, on y raccorde les sites ?
- [13:11.2] **Abderahmane** : Module sept : le VPN site à site. Deux sites simulés par des serveurs Linux, mais des tunnels IPsec bien réels.

*Clés des tunnels VPN* (m07a)
- [13:17.8] **Abderahmane** : Avant de créer les tunnels, les clés partagées : elles ne doivent jamais traîner dans un fichier. On les range dans Secrets Manager.
- [13:26.1] **Abderahmane** : Elles sont saisies masquées : elles n'apparaissent nulle part.

*Politique du rôle* (m07b)
- [13:33.6] **Abderahmane** : Le rôle des serveurs reçoit le droit de lire ce secret, et rien d'autre.

*VPC du siège* (m07c)
- [13:40.0] **Abderahmane** : Le siège et l'agence sont simulés par deux VPC séparés, chacun avec un slash vingt-quatre d'adresses d'entreprise.
- [13:46.9] **Thomas** : On refait les gestes des modules un et deux, mais en accéléré.
- [13:54.7] **Abderahmane** : Un VPC, un sous-réseau, une passerelle Internet, une table de routage : rien de nouveau.
- [14:03.3] **Thomas** : Pas de siège réel dans notre salle de cours : ces VPC jouent le rôle des sites.
- [14:12.6] **Thomas** : Celui-ci joue le siège, à Genève.
- [14:20.0] **Abderahmane** : Dernier geste : on associe la table au sous-réseau.

*VPC de l'agence* (m07c2)
- [14:23.9] **Thomas** : Même chose pour l'agence, à Lausanne, avec sa propre plage d'adresses.
- [14:38.5] **Abderahmane** : Les deux sites ne se recouvrent ni entre eux, ni avec nos VPC AWS : c'est indispensable pour qu'un VPN route correctement.
- [14:54.0] **Thomas** : Les gestes sont les mêmes, simplement accélérés.
- [15:04.5] **Abderahmane** : Et la table de routage, associée au sous-réseau.

*Security Groups des routeurs* (m07d)
- [15:08.7] **Thomas** : Un Security Group par routeur, et pour l'instant, aucune règle entrante.
- [15:17.8] **Abderahmane** : Les règles IPsec viendront quand on connaîtra les adresses des tunnels.

*Routeur du siège* (m07e)
- [15:27.7] **Abderahmane** : Le routeur du siège : une instance Ubuntu, dans le VPC du siège.
- [15:39.8] **Abderahmane** : Avec son Security Group, une adresse privée fixe, et le rôle pour Session Manager.

*Routeur de l'agence* (m07e2)
- [15:48.1] **Thomas** : Même recette pour le routeur de l'agence.
- [15:56.7] **Abderahmane** : Ubuntu encore, avec son Security Group, son adresse privée fixe, et le rôle pour Session Manager.

*Adresses IP Elastic* (m07f)
- [16:07.6] **Thomas** : Chaque routeur reçoit une adresse IP Elastic : une adresse publique fixe, celle que la passerelle cliente décrira.
- [16:15.9] **Abderahmane** : On l'alloue, puis on l'associe à l'instance.
- [16:26.0] **Thomas** : Et pareil pour l'agence.

*Passerelles clientes* (m07g)
- [16:31.9] **Abderahmane** : Les passerelles clientes : une par site. Chacune décrit le routeur par son adresse publique.
- [16:40.2] **Thomas** : Le numéro d'AS est obligatoire, mais sans effet en routage statique.

*Connexions VPN* (m07h)
- [16:47.0] **Thomas** : Les connexions VPN : cible, le Transit Gateway, routage statique.
- [16:52.2] **Thomas** : Deux tunnels par connexion, chacun avec sa clé, saisie masquée.
- [16:57.3] **Abderahmane** : Au total, AWS prépare quatre tunnels : deux par site.
- [17:02.1] **Thomas** : Même chose pour l'agence.
- [17:06.4] **Abderahmane** : Deux tunnels, deux clés, comme pour le siège.
- [17:13.4] **Thomas** : La création prend quelques minutes : on accélère.

*Table de routage des sites* (m07i)
- [17:18.4] **Thomas** : Sur le Transit Gateway, une troisième table, réservée aux sites.
- [17:26.8] **Thomas** : Les deux VPN y sont associés, et seule la production s'y propage.
- [17:32.1] **Abderahmane** : Les sites ne verront donc jamais le développement.

*Routes statiques* (m07j)
- [17:35.0] **Thomas** : Dans la table de la production, une route statique par site, vers son VPN.

*Routes du VPC de production* (m07k)
- [17:41.6] **Thomas** : Et côté VPC de production, la table privée envoie les deux plages des sites vers le Transit Gateway.

*Autoriser le port 8080* (m07l)
- [17:50.5] **Abderahmane** : Le port huit mille huitante s'ouvre au siège et à l'agence, à eux seuls.

*Pare-feu des routeurs* (m07m)
- [17:57.2] **Abderahmane** : Chaque routeur n'accepte que le trafic venant des deux adresses publiques de ses tunnels AWS.
- [18:04.3] **Thomas** : Toute autre adresse est simplement ignorée.

*Routeur du siège* (m07n)
- [18:12.7] **Abderahmane** : Place à la configuration du routeur du siège, par Session Manager.
- [18:17.1] **Abderahmane** : On installe strongSwan, puis on lit les clés dans Secrets Manager, sans jamais les afficher.
- [18:23.5] **Thomas** : Un petit script Python lit la description du VPN et écrit la configuration : deux tunnels IPsec.
- [18:29.6] **Abderahmane** : En IKE version deux, avec du chiffrement AES deux cent cinquante-six.
- [18:35.1] **Thomas** : Puis une interface par tunnel, et un suivi qui ne garde la route que sur un tunnel établi.
- [18:43.1] **Abderahmane** : Deux sessions établies.

*Routeur de l'agence* (m07n2)
- [18:44.8] **Thomas** : Même configuration pour l'agence : on installe, on récupère les clés et la description, on génère.
- [18:54.4] **Thomas** : Les clés sont lues à la volée dans Secrets Manager, jamais écrites en clair.
- [19:03.3] **Abderahmane** : Rien de nouveau : seules les adresses changent.
- [19:11.4] **Thomas** : On attend la négociation des tunnels.

*Tunnels VPN* (m07o)
- [19:20.1] **Thomas** : Dans la console, les quatre tunnels sont hauts, et les routes sont là.

*Tests depuis les sites* (m07p)
- [19:26.1] **Thomas** : Les tests, d'abord depuis le siège.
- [19:32.3] **Thomas** : L'API répond.
- [19:34.5] **Abderahmane** : Ping refusé : seul le huit mille huitante passe.
- [19:37.9] **Thomas** : Le développement reste injoignable.
- [19:40.7] **Abderahmane** : Même scénario depuis l'agence.
- [19:44.4] **Thomas** : L'API répond ici aussi, et le développement reste hors de portée.

*Panne d'un tunnel* (m07q)
- [19:49.8] **Abderahmane** : Dernier test du module : la panne d'un tunnel. D'abord, on règle IKE pour que la détection soit la plus rapide possible.
- [20:04.6] **Thomas** : Une boucle interroge l'API pendant qu'on coupe le tunnel un du siège.
- [20:12.2] **Abderahmane** : Les requêtes échouent le temps de la détection, environ une trentaine de secondes : ce n'est pas une bascule sans coupure, et on préfère le dire.
- [20:22.7] **Thomas** : Puis tout passe par le tunnel deux, et on rétablit le tunnel un.


## Module 8 - Direct Connect

- [20:34.1] **Abderahmane** : Les sites sont connectés. Thomas, Direct Connect est pour toi.
- [20:37.6] **Thomas** : Module huit : la passerelle est réelle, la liaison est simulée par un tunnel GRE avec du BGP, et le VPN reste en secours.

*Direct Connect Gateway* (m08a)
- [20:46.3] **Thomas** : Une Direct Connect Gateway, bien réelle, avec son propre numéro d'AS.
- [20:51.0] **Thomas** : Le bandeau rouge, c'est l'organisation qui bloque les emplacements.

*Association au Transit Gateway* (m08b)
- [20:56.3] **Abderahmane** : On l'associe au Transit Gateway, en limitant les préfixes à la production et au siège.
- [21:03.1] **Abderahmane** : L'association devient active après quelques minutes.

*Route côté AWS* (m08c)
- [21:06.9] **Thomas** : Côté AWS, un routeur aura besoin d'une route vers le siège, par le Transit Gateway.
- [21:16.5] **Thomas** : Et son propre Security Group.

*Table du sous-réseau de la zone B* (m08j)
- [21:23.8] **Abderahmane** : La même route dans la table du sous-réseau de la zone B.

*Routeur côté AWS* (m08d)
- [21:30.8] **Thomas** : Le routeur côté AWS : une instance Ubuntu, dans le sous-réseau public de la zone B, avec une adresse fixe.
- [21:41.9] **Thomas** : Son adresse fixe servira de point d'extrémité aux tunnels GRE.
- [21:48.8] **Thomas** : Refusé : limite de vCPU atteinte.

*Libérer des vCPU* (m08e)
- [21:52.3] **Thomas** : On arrête dev zéro un, inutile pour l'instant.

*Relancer le routeur* (m08f)
- [21:55.9] **Abderahmane** : On relance le routeur : cette fois, le quota le permet.
- [22:03.9] **Abderahmane** : Toujours Ubuntu, toujours dans le sous-réseau public de la zone B.
- [22:14.4] **Abderahmane** : Cette fois, il démarre.

*Attachement multi-zones* (m08k)
- [22:16.3] **Abderahmane** : Un attachement ne couvre que les zones déclarées : on ajoute la zone B, celle du routeur.

*Règles de sécurité* (m08g)
- [22:24.3] **Abderahmane** : Les règles de sécurité : entre les deux routeurs, le protocole GRE, numéro quarante-sept.
- [22:30.2] **Abderahmane** : Et le port huit mille huitante d'app zéro un, ouvert à ce routeur.
- [22:35.4] **Abderahmane** : Sans ces règles, les tunnels GRE ne monteraient jamais.

*Routeur côté AWS* (m08h)
- [22:46.7] **Thomas** : Sur le routeur côté AWS : FRRouting, un logiciel de routage libre.
- [23:00.4] **Thomas** : Deux tunnels GRE : l'un pour la liaison simulée, via Internet, l'autre à l'intérieur du VPN.
- [23:06.9] **Thomas** : Et BGP par-dessus.

*Routeur du siège* (m08i)
- [23:12.4] **Abderahmane** : Le routeur du siège reçoit les mêmes tunnels.
- [23:20.2] **Thomas** : Un VPN statique ne parle pas BGP : comment le secours peut-il fonctionner ?
- [23:25.4] **Abderahmane** : Le BGP du secours circule dans un tunnel GRE, à l'intérieur du VPN : c'est ce tunnel-là qui fait le travail.
- [23:35.9] **Abderahmane** : Liaison d'abord, VPN en secours.

*Sessions BGP établies* (m08l)
- [23:42.5] **Thomas** : Deux sessions BGP établies.
- [23:44.8] **Thomas** : Le meilleur chemin passe par la liaison : préférence locale deux cents.
- [23:49.2] **Abderahmane** : L'API répond par la liaison simulée.
- [23:53.6] **Abderahmane** : Côté AWS, le chemin du VPN arrive allongé.

*Panne de la liaison dédiée* (m08m)
- [23:57.2] **Thomas** : Le test décisif : on coupe la liaison dédiée. D'abord, une boucle qui affiche par où passe le trafic.
- [24:05.1] **Abderahmane** : Pour l'instant, tout passe par la liaison.
- [24:10.5] **Thomas** : On coupe le GRE avec une règle iptables : en silence, sans toucher à l'interface.
- [24:18.5] **Abderahmane** : BGP s'en aperçoit, et le trafic bascule sur le chemin du VPN, en quelques secondes.
- [24:25.4] **Thomas** : Maintenant, on rétablit la liaison.
- [24:33.6] **Abderahmane** : Et dès qu'elle revient, BGP la préfère de nouveau.

*Vue d'ensemble dans la console* (m08n)
- [24:39.9] **Thomas** : Et dans la console, l'association est active.


## Module 9 - Load balancer

- [24:44.6] **Thomas** : Direct Connect est validé. Abderahmane, on passe aux applications ?
- [24:49.6] **Abderahmane** : Module neuf : l'équilibreur de charge, en HTTPS, vers deux groupes cibles : le web, et l'application.

*Certificat public ACM* (m09a)
- [24:56.3] **Abderahmane** : Un vrai certificat public ACM, pour leman point thomastp point ch.
- [25:01.5] **Abderahmane** : Validation par DNS : on prouve que le domaine est à nous.
- [25:10.4] **Abderahmane** : La console crée l'enregistrement dans Route cinquante-trois.
- [25:16.0] **Abderahmane** : Le certificat est émis.

*Deux groupes cibles* (m09b)
- [25:17.6] **Abderahmane** : Deux groupes cibles. D'abord le web : HTTPS, port quatre cent quarante-trois.
- [25:22.6] **Abderahmane** : Avec son contrôle de santé, puis web zéro un comme cible.
- [25:32.9] **Thomas** : Le second pour l'application, en HTTP sur le port huit mille huitante, avec le même principe.
- [25:40.5] **Thomas** : Cible : app zéro un.

*Security Group de l'ALB* (m09c)
- [25:43.5] **Abderahmane** : Le Security Group de l'équilibreur : le port quatre cent quarante-trois, ouvert à tous.
- [25:52.1] **Abderahmane** : Il laisse entrer les clients, et rien d'autre.

*Équilibreur de charge* (m09d)
- [25:56.5] **Thomas** : L'équilibreur lui-même, sur deux zones de disponibilité.
- [26:03.4] **Thomas** : Un listener HTTPS sur le port quatre cent quarante-trois, qui envoie par défaut vers le groupe web, avec le vrai certificat ACM.
- [26:14.0] **Abderahmane** : Il se déploie en quelques minutes : on accélère.

*Nom de l'ALB* (m09d2)
- [26:20.2] **Abderahmane** : On crée un alias : origin point leman point thomastp point ch, vers l'équilibreur.

*Autoriser l'ALB* (m09e)
- [26:28.3] **Abderahmane** : Le groupe application accepte l'équilibreur, sur le port huit mille huitante.

*Règle du listener* (m09f)
- [26:32.8] **Abderahmane** : Une règle sur le listener : tout ce qui commence par slash api part vers le groupe de l'application.

*Santé des cibles* (m09g)
- [26:41.8] **Thomas** : Les deux groupes sont sains.
- [26:46.7] **Thomas** : L'API répond par son vrai nom.

*Test de panne* (m09h)
- [26:49.2] **Thomas** : La panne : on arrête nginx sur web zéro un.
- [26:56.9] **Abderahmane** : L'équilibreur renvoie une erreur cinq cent deux, et la cible passe à non saine.
- [27:03.7] **Thomas** : On relance nginx : après quelques contrôles réussis, la cible redevient saine.


## Module 10 - Route 53

- [27:09.6] **Abderahmane** : Le trafic est équilibré. Thomas, on s'occupe des noms ?
- [27:12.7] **Thomas** : Module dix, Route cinquante-trois : une zone privée, une zone publique, et un basculement automatique.

*Zone privée Route 53* (m10a)
- [27:18.7] **Thomas** : D'abord une zone privée : prod point leman point internal, rattachée au VPC de production.
- [27:24.8] **Thomas** : Elle n'est visible que de l'intérieur.

*Enregistrements* (m10b)
- [27:29.8] **Thomas** : Deux enregistrements : web et app.

*Noms d'hôte DNS* (m10f0)
- [27:34.6] **Thomas** : Il faut activer les noms d'hôte DNS sur le VPC.

*Résolution depuis web-01* (m10f)
- [27:40.0] **Thomas** : Depuis web zéro un, le nom se résout bien : c'est le résolveur du VPC qui répond.

*Zone publique* (m10c)
- [27:48.9] **Abderahmane** : La zone publique réelle : leman point thomastp point ch.
- [27:53.3] **Abderahmane** : Voici ses quatre serveurs de noms.

*Surveillance de l'état* (m10d)
- [27:56.3] **Abderahmane** : On surveille l'équilibreur en HTTPS, toutes les dix secondes.
- [28:01.0] **Abderahmane** : Deux échecs, et il est déclaré en panne.

*Enregistrements de basculement* (m10e)
- [28:05.4] **Abderahmane** : Les enregistrements de basculement. Le nom portefeuilles pointe d'abord vers l'équilibreur : c'est le principal, lié à la surveillance.
- [28:17.4] **Thomas** : Et le secours : une adresse statique de documentation.

*Test de basculement* (m10g)
- [28:23.1] **Thomas** : On interroge directement un serveur de noms d'AWS, depuis web zéro un. D'abord, on installe l'outil dig.
- [28:32.7] **Abderahmane** : On interroge la vraie zone : la réponse est l'adresse de l'équilibreur.
- [28:38.2] **Thomas** : Une boucle demande la réponse toutes les trois secondes : c'est l'adresse de l'équilibreur.
- [28:43.5] **Abderahmane** : Maintenant, on arrête nginx sur web zéro un.
- [28:47.2] **Abderahmane** : Il faut patienter : la surveillance doit constater la panne.
- [28:58.8] **Thomas** : La réponse change : adresse de secours.
- [29:01.5] **Abderahmane** : On relance nginx, et la réponse revient à l'équilibreur.


## Module 11 - CloudFront

- [29:05.3] **Thomas** : Le basculement fonctionne. Abderahmane, la vitrine, c'est CloudFront.
- [29:09.6] **Abderahmane** : Module onze : un cache devant l'équilibreur, qui ne sera plus joignable en direct.

*Fichier statique* (m11a)
- [29:15.1] **Abderahmane** : Un petit fichier statique sur web zéro un : un logo, servi sous slash static.

*Distribution CloudFront* (m11d)
- [29:24.8] **Thomas** : La distribution CloudFront, avec le paiement à l'utilisation.
- [29:32.1] **Abderahmane** : L'origine : l'équilibreur, par son vrai nom, en HTTPS seulement, sans pare-feu applicatif.

*Nom de domaine alternatif* (m11d2)
- [29:38.8] **Thomas** : La distribution porte le nom cdn point leman point thomastp point ch, avec un certificat ACM.

*Alias DNS* (m11d3)
- [29:46.0] **Abderahmane** : Dans Route cinquante-trois, un alias : cdn vers CloudFront.

*Comportement /static/** (m11e)
- [29:51.1] **Thomas** : Un comportement pour slash static : cache optimisé.

*Comportement /api/** (m11e2)
- [29:55.6] **Abderahmane** : Et pour slash api : jamais de cache, tous les en-têtes transmis.

*Verrouiller l'ALB* (m11f)
- [30:01.1] **Thomas** : On verrouille l'équilibreur : seul CloudFront y accède, grâce à la liste de préfixes d'AWS.

*Tests CloudFront* (m11g)
- [30:08.5] **Abderahmane** : Les tests. On appelle le fichier statique.
- [30:18.4] **Thomas** : Premier appel : Miss, la réponse vient de l'origine.
- [30:21.6] **Abderahmane** : Deuxième appel : Hit, depuis le cache.
- [30:26.0] **Thomas** : Pour l'API, jamais de cache : Miss à chaque fois.
- [30:29.5] **Abderahmane** : On modifie le fichier : le cache sert encore l'ancienne version.
- [30:33.6] **Thomas** : Une invalidation vide son cache.
- [30:35.8] **Abderahmane** : Quelques minutes d'attente, accélérées.
- [30:41.7] **Thomas** : Et la nouvelle version apparaît.
- [30:45.8] **Abderahmane** : Accès direct : bloqué.


## Module 12 - Surveillance

- [30:46.7] **Abderahmane** : Le site est en ligne. Thomas, comment sait-on qu'il va bien ?
- [30:50.1] **Thomas** : Module douze : la surveillance. Un tableau de bord, une alarme SNS, et les journaux de flux.

*Rubrique SNS* (m12a)
- [30:57.0] **Thomas** : D'abord une rubrique SNS, qui servira aux notifications d'alarme.
- [31:06.0] **Thomas** : Abonné par e-mail, avec une adresse fictive.

*File SQS* (m12b)
- [31:10.4] **Thomas** : Une file SQS, qui nous servira de preuve de réception.

*Abonnement* (m12b2)
- [31:19.4] **Thomas** : Et on l'abonne à la rubrique.

*Alarme CloudWatch* (m12c)
- [31:24.3] **Abderahmane** : L'alarme : on surveille les erreurs HTTP cinq cents de l'équilibreur.
- [31:29.8] **Abderahmane** : Au-delà de cinq erreurs, elle se déclenche.
- [31:32.3] **Thomas** : Elle prévient la rubrique en passant en alarme, et en revenant à la normale.

*Tableau de bord* (m12d)
- [31:40.4] **Thomas** : Le tableau de bord : cibles saines, temps de réponse, erreurs cinq cents, décrits par une source JSON.

*Journaux de flux du VPC* (m12e)
- [31:47.4] **Thomas** : Les journaux de flux du VPC de production : tout le trafic part vers CloudWatch Logs.
- [31:53.7] **Thomas** : Avec un rôle de service, créé par la console.

*Sonde SSH non autorisée* (m12f)
- [31:57.3] **Abderahmane** : Pour générer du trafic refusé, une sonde SSH non autorisée, depuis l'agence vers web zéro un.
- [32:04.0] **Abderahmane** : Le Security Group la refuse.

*Logs Insights* (m12g)
- [32:06.8] **Abderahmane** : Logs Insights : une requête compte les connexions refusées.

*Test de l'alarme* (m12h)
- [32:11.4] **Thomas** : Le test de l'alarme. Pour la déclencher, on commence par arrêter nginx.
- [32:17.3] **Abderahmane** : Puis on envoie soixante requêtes par CloudFront : elles reviendront toutes en erreur cinq cent deux.
- [32:24.5] **Thomas** : CloudWatch évalue par périodes : il faut un peu de patience avant que l'alarme bascule.
- [32:33.5] **Abderahmane** : Chaque requête traverse CloudFront et l'équilibreur, puis tombe sur une cible arrêtée.
- [32:41.9] **Abderahmane** : On accélère l'attente.
- [32:44.0] **Thomas** : L'alarme se déclenche.
- [32:48.0] **Abderahmane** : On relance nginx : sans nouvelles erreurs, l'alarme finit par se calmer.

*Messages reçus* (m12i)
- [32:53.5] **Abderahmane** : La file SQS a bien reçu les notifications : voilà notre preuve.


## Module 13 - CloudFormation

- [32:59.7] **Thomas** : Tout est surveillé. Il reste à tout automatiser, Abderahmane.
- [33:03.9] **Abderahmane** : Module treize : CloudFormation. Le réseau décrit dans un modèle, avec détection de dérive.

*Pile CloudFormation* (m13a)
- [33:10.2] **Abderahmane** : On téléverse le modèle, on nomme la pile, et on renseigne les paramètres.
- [33:19.3] **Abderahmane** : Le certificat est masqué, les balises sont posées, et on autorise la pile à créer un rôle IAM.

*Événements de la pile* (m13b)
- [33:27.7] **Abderahmane** : Les événements montrent l'ordre de création des ressources.

*Créer une dérive* (m13c)
- [33:32.3] **Thomas** : Maintenant, une dérive : on ajoute une règle SSH à la main sur le groupe web.

*Détection de dérive* (m13d)
- [33:38.2] **Abderahmane** : On lance la détection : la pile est en dérive, et la règle ajoutée est visible.

*Corriger la dérive* (m13e)
- [33:45.2] **Abderahmane** : On retire la règle manuelle : la pile est de nouveau en phase.

*Suppression de la pile* (m13f)
- [33:52.6] **Thomas** : Dernier geste : supprimer la pile. CloudFormation défait tout, dans l'ordre inverse de la création.


## Conclusion

- [34:00.1] **Thomas** : Voilà, c'est la fin du parcours : quatorze modules, tous réalisés à la main dans la console AWS.
- [34:06.4] **Abderahmane** : Un réseau sur trois sites, cloisonné, surveillé, et reproductible grâce à CloudFormation.
- [34:11.2] **Thomas** : On est restés honnêtes sur les limites : les sites sont simulés, la liaison Direct Connect aussi. Le domaine, lui, est réel. Tous les écarts avec le sujet sont expliqués dans le dossier.
- [34:20.5] **Abderahmane** : Merci de nous avoir suivis.
- [34:22.0] **Thomas** : À bientôt !
