# Deploie cfn/interconnexion-leman.yaml : pare-feu (m4), Transit Gateway (m6), VPN siege et agence + Elastic IP (m7), Direct Connect Gateway (m8).
# Avant : retire les versions manuelles de ce que le modele va gerer (route par defaut de rt-prive, regles de sg-app pour les sites).
# Apres : importe les sorties de la stack dans scripts\state.json (memes cles que les scripts m06 a m08).
# Usage : pwsh scripts\m13-interconnexion.ps1 [-Delete]
param([switch]$Delete)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$stack = 'stack-interconnexion-leman-TP-AC'
function AwsJson { & $script:aws @args --profile TP-AC --region eu-north-1 --output json | ConvertFrom-Json }

if ($Delete) {
  Aws cloudformation delete-stack --stack-name $stack
  Aws cloudformation wait stack-delete-complete --stack-name $stack
  # le modele gerait la route par defaut de rt-prive (via le pare-feu) : on la remet vers la NAT
  & $script:aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $s.nat --profile TP-AC --region eu-north-1 2>&1 | Out-Null
  "stack supprimee, route par defaut de rt-prive remise vers la NAT"; return
}

# --- les routeurs doivent exister et tourner (les Elastic IP s'y associent)
Aws ec2 start-instances --instance-ids $s.rtrSiege $s.rtrAgence $s.rtrAws | Out-Null
Aws ec2 wait instance-running --instance-ids $s.rtrSiege $s.rtrAgence $s.rtrAws

# --- retirer ce que le modele va creer
& $script:aws ec2 delete-route --route-table-id $s.rtPrive --destination-cidr-block 0.0.0.0/0 --profile TP-AC --region eu-north-1 2>&1 | Out-Null
& $script:aws ec2 delete-route --route-table-id $s.rtPublic --destination-cidr-block 10.20.1.0/26 --profile TP-AC --region eu-north-1 2>&1 | Out-Null
$sg = AwsJson ec2 describe-security-groups --group-ids $s.sgApp
$n = 0
foreach ($perm in $sg.SecurityGroups[0].IpPermissions) {
  $proto = $perm.IpProtocol; $from = $perm.FromPort; $to = $perm.ToPort
  $ports = if ($proto -eq 'icmp') { @('--port', '-1') } else { @('--port', "$from") }
  foreach ($r in @($perm.IpRanges | Where-Object { $_.CidrIp -match '^192\.168\.' })) { & $script:aws ec2 revoke-security-group-ingress --group-id $s.sgApp --protocol $proto @ports --cidr $r.CidrIp --profile TP-AC --region eu-north-1 | Out-Null; $n++ }
  foreach ($g in @($perm.UserIdGroupPairs | Where-Object { $_.GroupId -eq $s.sgRtrAws })) { & $script:aws ec2 revoke-security-group-ingress --group-id $s.sgApp --protocol $proto @ports --source-group $g.GroupId --profile TP-AC --region eu-north-1 | Out-Null; $n++ }
}
"regles sg-app retirees : $n"
# groupes de journaux crees a la main lors du test du module 4 : le modele les cree lui-meme
foreach ($lg in '/leman/nfw-alert-TP-AC','/leman/nfw-flow-TP-AC') { & $script:aws logs delete-log-group --log-group-name $lg --profile TP-AC --region eu-north-1 2>&1 | Out-Null }
$prev = (& $script:aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].StackStatus' --output text --profile TP-AC --region eu-north-1 2>$null)
if ($prev -eq 'ROLLBACK_COMPLETE') { Aws cloudformation delete-stack --stack-name $stack; Aws cloudformation wait stack-delete-complete --stack-name $stack }

# --- parametres
$Prm = @{ VpcProdId = $s.vpc; VpcDevId = $s.vpcDev; SubPriveId = $s.subPrive; SubPublic1bId = $s.subPublic1b; SubDevId = $s.subDev
        RtPriveId = $s.rtPrive; RtPublicId = $s.rtPublic; RtDevId = $s.rtDev; SgAppId = $s.sgApp; SgRtrAwsId = $s.sgRtrAws; NatGatewayId = $s.nat
        RtrSiegeInstanceId = $s.rtrSiege; RtrAgenceInstanceId = $s.rtrAgence; RtrAwsInstanceId = $s.rtrAws }
$pf = Join-Path $env:TEMP 'tpac-interco-params.json'
[IO.File]::WriteAllText($pf, (($Prm.GetEnumerator() | ForEach-Object { @{ ParameterKey = $_.Key; ParameterValue = $_.Value } }) | ConvertTo-Json -AsArray))
$tpl = (Resolve-Path (Join-Path $PSScriptRoot '..\cfn\interconnexion-leman.yaml')).Path.Replace('\', '/')
Aws cloudformation validate-template --template-body "file://$tpl" | Out-Null
Aws cloudformation create-stack --stack-name $stack --template-body "file://$tpl" --parameters "file://$pf" --capabilities CAPABILITY_IAM --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' 'Key=Environnement,Value=prod' | Out-Null
"creation de la stack lancee ($stack)..."
$t0 = Get-Date
do { Start-Sleep 30; $st = Aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].StackStatus'; "{0:mm\:ss}  {1}" -f ((Get-Date) - $t0), $st } while ($st -eq 'CREATE_IN_PROGRESS')
if ($st -ne 'CREATE_COMPLETE') {
  Aws cloudformation describe-stack-events --stack-name $stack --query 'StackEvents[?contains(ResourceStatus,`FAILED`)].[LogicalResourceId,ResourceStatusReason]' --output text
  throw "stack en etat $st"
}

# --- sorties -> state.json
$o = @{}; (AwsJson cloudformation describe-stacks --stack-name $stack).Stacks[0].Outputs | ForEach-Object { $o[$_.OutputKey] = $_.OutputValue }
$map = @{ TgwId='tgw'; TgwRtProd='tgwRtProd'; TgwRtDev='tgwRtDev'; TgwRtSites='tgwRtSites'; AttachProd='tgwaProd'; AttachDev='tgwaDev'; VpnSiege='vpnSiege'; VpnAgence='vpnAgence'
          CgwSiege='cgwSiege'; CgwAgence='cgwAgence'; AttachVpnSiege='tgwaVpnSiege'; AttachVpnAgence='tgwaVpnAgence'; EipSiege='eipIpSiege'; EipAgence='eipIpAgence'
          EipRtrAws='eipIpRtrAws'; EipSiegeAlloc='eipSiege'; EipAgenceAlloc='eipAgence'; EipRtrAwsAlloc='eipRtrAws'; DxgwId='dxgw' }
foreach ($k in $map.Keys) { if ($o[$k]) { $s[$map[$k]] = $o[$k] } }
Save-State $s
"sorties importees : $($map.Keys.Count) cles ; TGW = $($s.tgw) ; DXGW = $($s.dxgw)"
# etat juste apres la creation, avant la configuration des routeurs (les tunnels doivent etre DOWN : normal tant que les sites ne sont pas configures)
$d = Join-Path $PSScriptRoot '..\docs\modules\m07'; New-Item -ItemType Directory -Force $d | Out-Null
$e1 = @('=== Module 7 - etape 1 : VPN crees par la stack, avant configuration des routeurs ===')
foreach ($n in 'Siege','Agence') { $e1 += "vpn-$($n.ToLower())-TP-AC : " + ((Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$n"] --query 'VpnConnections[0].[State,Type,Options.StaticRoutesOnly]') -join ' '); $e1 += '  tunnels (adresse AWS, etat) : ' + ((Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$n"] --query 'VpnConnections[0].VgwTelemetry[].[OutsideIpAddress,Status]') -join ' | ') }
$e1 += 'tgw-rt-prod : ' + ((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtProd --filters 'Name=state,Values=active,blackhole' --query 'Routes[].[DestinationCidrBlock,Type,State]') -join ' | ')
$e1 | Set-Content (Join-Path $d 'tests-etape1.txt') -Encoding utf8; $e1
