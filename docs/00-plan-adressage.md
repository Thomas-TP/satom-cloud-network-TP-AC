# Plan d'adressage - TP-AC (Satom Cloud Network)

Region : eu-north-1 (Stockholm) - seule region autorisee sur le compte (Zurich/Francfort bloquees).
Convention : suffixe `-TP-AC` sur les noms, tags `Projet=SatomCloudNetwork`, `Equipe=TP-AC`, `Environnement=prod|dev`.

| Reseau | CIDR | Remarque |
|---|---|---|
| vpc-prod-leman-TP-AC | 10.20.0.0/22 | 1024 adresses, suffisant (les camarades utilisent 10.0.0.0/16) |
| sub-public-1a | 10.20.0.0/26 | web-01 = 10.20.0.10 |
| sub-public-1b | 10.20.0.64/26 | ALB (2e zone) |
| sub-prive-1a | 10.20.1.0/26 | app-01 = 10.20.1.10 |
| sub-fw-1a | 10.20.2.0/28 | endpoint Network Firewall |
| reserve BDD | 10.20.3.0/26 | non cree |
| vpc-dev-leman-TP-AC | 10.21.0.0/24 | dev, sub-dev-1a 10.21.0.0/26 |
| Siege (simule) | 192.168.10.0/24 | selon HackMD |
| Agence (simulee) | 192.168.20.0/24 | selon HackMD |

Contraintes : quota VPC = 5/region sur le compte partage (hausse a 15 demandee).
