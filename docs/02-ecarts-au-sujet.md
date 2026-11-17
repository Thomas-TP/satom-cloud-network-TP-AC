# Points du sujet impossibles, incohérents ou réalisés autrement

Le sujet a été rédigé avec l'aide d'une IA : certaines consignes ne peuvent pas être suivies à la lettre, ou se contredisent. Cette liste dit, pour chacune, ce que nous avons fait à la place et pourquoi. Elle est destinée au formateur.

| # | Module | Ce que dit le sujet | Pourquoi ce n'est pas possible tel quel | Ce que nous avons fait |
|---|---|---|---|---|
| 1 | 8 | Une liaison Direct Connect près de Genève | Il n'existe aucun emplacement Direct Connect près de Genève dans la région de Stockholm (Zurich n'est pas activée sur le compte, Francfort est refusée). Et nous ne commandons pas de fibre. | Emplacement retenu sur le papier : EQSK1 (Equinix Sweden SK1, 1 Gbit/s). Direct Connect Gateway réel et associé au Transit Gateway ; la liaison est simulée par un tunnel GRE et BGP (FRRouting). |
| 2 | 7 | Une bascule entre deux tunnels VPN « sans coupure » | Un VPN IPsec ne peut pas basculer sans coupure : AWS met un certain temps à constater qu'un tunnel est mort avant d'utiliser l'autre. Nous avons mesuré entre 26 et 34 secondes (valeurs exactes au module 7). | Mesure honnête, avec une vraie panne silencieuse (paquets perdus, sans couper l'interface). |
| 3 | 8 | Une bascule Direct Connect vers VPN en quelques secondes, avec un prepend | Un VPN statique ne parle pas BGP : le prepend n'aurait aucun effet. | Le BGP du chemin « VPN » passe dans un tunnel GRE à l'intérieur du vrai VPN. Bascule mesurée au module 8. |
| 4 | 7 | Customer Gateways en `203.0.113.10` et `198.51.100.10` | Ce sont des adresses réservées à la documentation : aucun tunnel ne s'établit vers elles. | Une Elastic IP par routeur de site (`rtr-siege-TP-AC`, `rtr-agence-TP-AC`). |
| 5 | 6, 7 | Plages `10.0.0.0/16` et `10.1.0.0/16` | Le compte est partagé par toute la classe : ces plages recouvrent celles des autres. | `10.20.0.0/22` (prod) et `10.21.0.0/24` (dev). |
| 6 | 7 | Déclarer les routes statiques sur la connexion VPN | Pour un VPN rattaché à un Transit Gateway, AWS refuse : les routes se déclarent dans la table de routage du Transit Gateway. | Routes dans `tgw-rt-prod-TP-AC`. |
| 7 | 4 | Ne mettre que la route de retour `10.20.1.0/26` dans la table publique | Cela casse `web-01` vers `app-01` : la requête passe par le pare-feu, pas la réponse, et le pare-feu perd l'état. Les Security Groups « depuis un groupe » ne correspondent plus au trafic qui sort d'un endpoint de pare-feu. | Routes symétriques, et règles de `sg-app` par plage d'adresses (module 4). |
| 8 | 4 | Le flux autorisé doit apparaître dans les journaux | Un journal d'alertes ne contient que ce qui est bloqué. | Second journal, de type flux (`/leman/nfw-flow-TP-AC`). |
| 9 | 10, 11 | Zone publique et certificat ACM validé par DNS pour `leman-finance.example` | Nous n'avons pas de domaine (et n'en achetons pas) : la délégation DNS réelle et la validation ACM sont impossibles. | La zone existe, et nous interrogeons directement un de ses serveurs de noms ainsi que `route53 test-dns-answer`. Les visiteurs voient le certificat `*.cloudfront.net` ; CloudFront joint l'ALB en HTTP (il refuserait le certificat auto-signé de l'ALB). |
| 10 | 0 | Un module « cadrage » sans client joignable | Nous ne pouvons pas poser nos questions au client. | Questions et budget rédigés par nos soins, à relire (module 0). |
| 11 | 1 | Région Zurich | `eu-central-2` n'est pas activée (`AuthFailure`), Francfort est refusée par l'organisation. | Stockholm (`eu-north-1`), acceptée avec le formateur. |
| 12 | 8 | Console Direct Connect | La console affiche une erreur `DescribeLocations` : elle appelle un point d'accès global situé dans une région interdite. | Le service est utilisé par la ligne de commande. |
| 13 | 4, 6, 7, 8 | Services autorisés | L'organisation refusait Network Firewall, Transit Gateway, VPN et Direct Connect jusqu'au 17/11/2026 (voir `01-services-bloques.md`). | Modules refaits en réel après la levée, et redéployés depuis un modèle CloudFormation. |

## Ce qui reste simulé malgré tout
- Les deux sites (siège, agence) sont des instances EC2 avec strongSwan, pas du matériel réel.
- La « fibre » Direct Connect est un tunnel GRE sur Internet : il n'y a pas d'interface virtuelle physique.
- Il n'y a pas de domaine réel : certificat auto-signé.
- GNS3 n'est pas utilisé : les routeurs sont des instances EC2 avec FRRouting.
