# Services refusés par l'organisation AWS (Service Control Policy) : historique

Le compte de formation est rattaché à une AWS Organization dont des règles (SCP) refusent certaines actions. Le message AWS est : `... with an explicit deny in a service control policy`. Ces refus ne viennent pas des droits de notre rôle (`AccountFullAccessRole`) : ils sont posés au niveau de l'organisation, dans le compte de gestion du formateur.

## Relevé du 16/11/2026 (région eu-north-1, appels réels ou `--dry-run`)
| Module | Service / action | Résultat |
|---|---|---|
| 4 | AWS Network Firewall (`network-firewall:*`) | refusé |
| 6 | Transit Gateway (`ec2:CreateTransitGateway`) | refusé (lecture autorisée) |
| 7 | VPN site à site (`CreateCustomerGateway`, `CreateVpnGateway`, `CreateVpnConnection`) | refusé |
| 8 | AWS Direct Connect (`directconnect:*`) | refusé |
| 1-3, 5, 9-13 | VPC, EC2, SG, NACL, peering, ELB, Route 53, CloudFront, ACM, CloudWatch, SNS, Flow Logs, CloudFormation | autorisé |
| - | Région eu-central-1 (Francfort) | refusée |
| - | Région eu-central-2 (Zurich) | non activée (`AuthFailure`) |

À ce moment-là, nous avions fait les modules 4, 6, 7 et 8 en documentation et en simulation seulement.

## Levée du blocage le 17/11/2026
Nous avons demandé au formateur de retirer ces actions de la règle (liste de `network-firewall:*`, `ec2:*TransitGateway*`, `ec2:*Vpn*`, `ec2:*CustomerGateway*`, `directconnect:*`, `ec2:*NetworkInsights*`) et d'augmenter le quota de vCPU de 16 à 48. Le 17/11/2026, nos tests montrent :

| Service | Résultat |
|---|---|
| Network Firewall (création d'un groupe de règles, puis du pare-feu) | autorisé |
| Reachability Analyzer (`CreateNetworkInsightsPath` en simulation) | autorisé |
| Customer Gateway, VPN Gateway, Transit Gateway (simulation) | autorisé |
| Direct Connect Gateway (création et association) | autorisé |
| Quota de vCPU | 48 (demande approuvée) |

Nous ne savons pas quelle règle exacte a été modifiée. Il reste un refus : la page *Passerelles Direct Connect* de la **console** affiche un bandeau rouge, `AccessDeniedException ... directconnect:DescribeLocations with an explicit deny in a service control policy`. C'est la liste des emplacements Direct Connect qui est refusée par l'organisation. La page reste utilisable : nous avons créé et associé la passerelle Direct Connect directement dans la console.

Nous avons donc refait pour de vrai les modules 4, 6, 7 et 8. Une première fois le 17/11 avec des scripts (`scripts/`, `docs/modules/`), puis une seconde fois à la main dans la console du 18 au 20/11, filmée : c'est la version décrite dans le dossier.
