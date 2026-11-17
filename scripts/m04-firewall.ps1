# Module 4 - AWS Network Firewall (TP-AC)  [facture a l'heure : a supprimer apres les tests -> m04-cleanup.ps1]
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$tmp = $env:TEMP
function J($name,$obj) { $f = Join-Path $tmp "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 10 -Compress)); "file://$f" }
$tags = @(@{Key='Projet';Value='SatomCloudNetwork'},@{Key='Equipe';Value='TP-AC'},@{Key='Environnement';Value='prod'}) | ForEach-Object { "Key=$($_.Key),Value=$($_.Value)" }

# TP1 : sous-reseau pare-feu + table dediee
$s.subFw = Aws ec2 create-subnet --vpc-id $s.vpc --cidr-block 10.20.2.0/28 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-fw-1a-TP-AC') --query Subnet.SubnetId
$s.rtFw  = Aws ec2 create-route-table --vpc-id $s.vpc --tag-specifications (Tags 'route-table' 'rt-fw-leman-TP-AC') --query RouteTable.RouteTableId
Aws ec2 associate-route-table --route-table-id $s.rtFw --subnet-id $s.subFw | Out-Null
Aws ec2 create-route --route-table-id $s.rtFw --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $s.nat | Out-Null
Save-State $s

# Groupes de regles (ordre strict)
$strict = @{ RuleOrder = 'STRICT_ORDER' }
$rgVpc = @{ RulesSource = @{ RulesString = 'pass ip 10.20.0.0/22 any -> 10.20.0.0/22 any (msg:"intra-VPC TP-AC"; sid:100001; rev:1;)' }; StatefulRuleOptions = $strict }
$s.rgVpc = Aws network-firewall create-rule-group --rule-group-name rg-vpc-pass-TP-AC --type STATEFUL --capacity 10 --rule-group (J 'rgvpc' $rgVpc) --tags $tags --query RuleGroupResponse.RuleGroupArn
$rgDom = @{ RulesSource = @{ RulesSourceList = @{ Targets = @('.amazonlinux.com','.amazonaws.com'); TargetTypes = @('HTTP_HOST','TLS_SNI'); GeneratedRulesType = 'ALLOWLIST' } }; StatefulRuleOptions = $strict }
$s.rgDom = Aws network-firewall create-rule-group --rule-group-name rg-depots-autorises-TP-AC --type STATEFUL --capacity 100 --rule-group (J 'rgdom' $rgDom) --tags $tags --query RuleGroupResponse.RuleGroupArn

$pol = @{ StatelessDefaultActions = @('aws:forward_to_sfe'); StatelessFragmentDefaultActions = @('aws:forward_to_sfe');
  StatefulEngineOptions = $strict; StatefulDefaultActions = @('aws:drop_established','aws:alert_established');
  StatefulRuleGroupReferences = @(@{ResourceArn=$s.rgVpc;Priority=1}, @{ResourceArn=$s.rgDom;Priority=2}) }
$s.nfwPolicy = Aws network-firewall create-firewall-policy --firewall-policy-name policy-prod-leman-TP-AC --firewall-policy (J 'pol' $pol) --tags $tags --query FirewallPolicyResponse.FirewallPolicyArn
Save-State $s

# Pare-feu
Aws network-firewall create-firewall --firewall-name nfw-prod-leman-TP-AC --firewall-policy-arn $s.nfwPolicy --vpc-id $s.vpc --subnet-mappings "SubnetId=$($s.subFw)" --tags $tags | Out-Null
Write-Host 'Attente du pare-feu (5-10 min)...'
do { Start-Sleep 20; $st = Aws network-firewall describe-firewall --firewall-name nfw-prod-leman-TP-AC --query FirewallStatus.Status } while ($st -ne 'READY')
# l'endpoint se lit en JSON (la fonction Aws force --output text)
$fw = & $script:aws network-firewall describe-firewall --firewall-name nfw-prod-leman-TP-AC --profile TP-AC --region eu-north-1 --output json | ConvertFrom-Json
$s | Add-Member -NotePropertyName nfwEndpoint -NotePropertyValue (($fw.FirewallStatus.SyncStates.PSObject.Properties | Select-Object -First 1).Value.Attachment.EndpointId) -Force
Save-State $s

# Journalisation des alertes -> CloudWatch Logs
Aws logs create-log-group --log-group-name /leman/nfw-alert-TP-AC
Aws logs tag-log-group --log-group-name /leman/nfw-alert-TP-AC --tags "Equipe=TP-AC,Projet=SatomCloudNetwork"
Aws logs put-retention-policy --log-group-name /leman/nfw-alert-TP-AC --retention-in-days 3
$log = @{ LogDestinationConfigs = @(@{ LogType='ALERT'; LogDestinationType='CloudWatchLogs'; LogDestination=@{ logGroup='/leman/nfw-alert-TP-AC' } }) }
Aws network-firewall update-logging-configuration --firewall-name nfw-prod-leman-TP-AC --logging-configuration (J 'log' $log) | Out-Null

# TP3 : routage via le pare-feu (retour symetrique pour la NAT)
Aws ec2 replace-route --route-table-id $s.rtPrive --destination-cidr-block 0.0.0.0/0 --vpc-endpoint-id $s.nfwEndpoint
Aws ec2 create-route --route-table-id $s.rtPublic --destination-cidr-block 10.20.1.0/26 --vpc-endpoint-id $s.nfwEndpoint | Out-Null
Save-State $s
"Pare-feu pret, endpoint = $($s.nfwEndpoint)"
