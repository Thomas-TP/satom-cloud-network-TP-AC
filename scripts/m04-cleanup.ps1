# Module 4 - Nettoyage : supprime le pare-feu (facture a l'heure) et restaure le routage vers la NAT
$ErrorActionPreference = 'Continue'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
Aws ec2 replace-route --route-table-id $s.rtPrive --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $s.nat
Aws ec2 delete-route --route-table-id $s.rtPublic --destination-cidr-block 10.20.1.0/26
# AWS refuse de supprimer un pare-feu qui a une configuration de journalisation : on la retire d'abord
[IO.File]::WriteAllText("$env:TEMP	pac-nolog.json", '{"LogDestinationConfigs":[]}')
Aws network-firewall update-logging-configuration --firewall-name nfw-prod-leman-TP-AC --logging-configuration "file://$env:TEMP/tpac-nolog.json" | Out-Null
Aws network-firewall delete-firewall --firewall-name nfw-prod-leman-TP-AC | Out-Null
Write-Host 'Suppression du pare-feu...'
do { Start-Sleep 15; $r = Aws network-firewall describe-firewall --firewall-name nfw-prod-leman-TP-AC --query FirewallStatus.Status 2>&1 } while ($r -notmatch 'ResourceNotFound')
Aws network-firewall delete-firewall-policy --firewall-policy-name policy-prod-leman-TP-AC
Aws network-firewall delete-rule-group --rule-group-name rg-vpc-pass-TP-AC --type STATEFUL
Aws network-firewall delete-rule-group --rule-group-name rg-depots-autorises-TP-AC --type STATEFUL
$assoc = Aws ec2 describe-route-tables --route-table-ids $s.rtFw --query 'RouteTables[0].Associations[0].RouteTableAssociationId'
Aws ec2 disassociate-route-table --association-id $assoc
Aws ec2 delete-route-table --route-table-id $s.rtFw
Aws ec2 delete-subnet --subnet-id $s.subFw
foreach ($k in 'nfwEndpoint','subFw','rtFw','rgVpc','rgDom','nfwPolicy') { if ($s -is [hashtable]) { $s.Remove($k) } else { $s.PSObject.Properties.Remove($k) } }
Save-State $s
'Nettoyage termine (le groupe de logs /leman/nfw-alert-TP-AC est conserve, retention 3 j)'
