# Plan d'adressage - TP-AC (Satom Cloud Network)

Region : eu-north-1 (Stockholm) - seule region utilisable sur le compte (Zurich non activee, Francfort refusee).
Convention : suffixe `-TP-AC` sur les noms, tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=prod|dev`.

| Reseau | CIDR | Remarque |
|---|---|---|
| vpc-prod-leman-TP-AC | 10.20.0.0/22 | 1024 adresses, suffisant (les camarades utilisent 10.0.0.0/16) |
| sub-public-1a-TP-AC | 10.20.0.0/26 | web-01-TP-AC = 10.20.0.10 |
| sub-public-1b-TP-AC | 10.20.0.64/26 | NAT (module 2, 10.20.0.101), rtr-aws-TP-AC = 10.20.0.74, 2e zone de l'ALB |
| sub-prive-1a-TP-AC | 10.20.1.0/26 | app-01-TP-AC = 10.20.1.10 |
| sub-fw-1a-TP-AC | 10.20.2.0/28 | endpoint Network Firewall (module 4) |
| reserve BDD | 10.20.3.0/26 | jamais cree |
| vpc-dev-leman-TP-AC | 10.21.0.0/24 | dev, sub-dev-1a-TP-AC 10.21.0.0/26, dev-01-TP-AC = 10.21.0.10 |
| Siege (simule) | 192.168.10.0/24 | plage donnee par le sujet |
| Agence (simulee) | 192.168.20.0/24 | plage donnee par le sujet |

Un /26 compte 64 adresses, dont 5 reservees par AWS : 59 utilisables.

Contraintes : quota de 5 passerelles NAT par zone de disponibilite sur le compte partage (atteint en zone A : la NAT est en zone B).
