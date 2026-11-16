# Services bloques par l'organisation AWS (Service Control Policy)

Le compte de formation est rattache a une AWS Organization dont une SCP refuse certaines actions (message AWS :
`... with an explicit deny in a service control policy`). Ces refus ne sont pas un probleme de droits de notre role
(`AccountFullAccessRole`) : ils sont poses au niveau de l'organisation (compte de gestion du formateur).
Releve effectue le 16/11/2026 (region eu-north-1, test par appel reel ou `--dry-run`).

| Module | Service / action | Resultat | Preuve |
|---|---|---|---|
| 4 | AWS Network Firewall (`network-firewall:*`) | **Bloque** | `ListFirewalls`, `DescribeFirewall`, `ListRuleGroups` : explicit deny (SCP) |
| 6 | Transit Gateway (`ec2:CreateTransitGateway`) | **Bloque** (lecture autorisee) | `UnauthorizedOperation ... explicit deny in a service control policy` |
| 7 | Site-to-Site VPN (`CreateCustomerGateway`, `CreateVpnGateway`, `CreateVpnConnection`) | **Bloque** | `--dry-run` : explicit deny (SCP) |
| 8 | AWS Direct Connect (`directconnect:*`) | **Bloque** | `DescribeConnections`, `DescribeLocations` et `CreateDirectConnectGateway` : explicit deny (SCP), testes le 16/11 |
| 1-3, 5, 9-13 | VPC, EC2, SG, NACL, peering, ELB, Route 53, CloudFront, ACM, CloudWatch, SNS, Flow Logs, CloudFormation | Autorise | tests des modules |
| - | Region eu-central-1 (Francfort) | Bloquee | explicit deny (SCP) |
| - | Region eu-central-2 (Zurich) | Non activee | `AuthFailure` |

Consequences pour le projet :
* Region de travail : **Stockholm (eu-north-1)** uniquement (le HackMD annonce Zurich/Francfort).
* Modules 4, 6, 7, 8 : realisation par **simulation** quand c'est possible (routeurs strongSwan / FRRouting sur EC2 pour
  l'IPsec et le BGP), sinon documentation complete + **template CloudFormation pret a deployer** (`cfn/`) valide par
  `aws cloudformation validate-template`, non deployable tant que la SCP n'est pas levee. Chaque ecart est justifie dans le module concerne.
* Si le formateur leve la SCP, les templates `cfn/optional-*.yaml` permettent un deploiement immediat.

