# Module 6 - tests sur le Transit Gateway deploye par le modele CloudFormation (interconnexion-leman.yaml)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m06\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function Curl { (Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ' }
Aws ec2 start-instances --instance-ids $s.app $s.dev | Out-Null
"SSM : app $(Wait-Ssm $s.app 240) / dev $(Wait-Ssm $s.dev 240)" | Out-Null
L "=== Module 6 : Transit Gateway deploye par la stack stack-interconnexion-leman-TP-AC ==="
L "Attachements : $((Aws ec2 describe-transit-gateway-attachments --filters "Name=transit-gateway-id,Values=$($s.tgw)" 'Name=state,Values=available' --query 'TransitGatewayAttachments[].[Tags[?Key==`Name`]|[0].Value,ResourceType,State]') -join ' | ')"
L "Peering pcx-lab encore actif ? : $(Aws ec2 describe-vpc-peering-connections --filters 'Name=status-code,Values=active' 'Name=tag:Equipe,Values=TP-AC' --query 'length(VpcPeeringConnections)') (0 = supprime)"
L "Tables : $((Aws ec2 describe-transit-gateway-route-tables --filters "Name=transit-gateway-id,Values=$($s.tgw)" --query 'TransitGatewayRouteTables[].[Tags[?Key==`Name`]|[0].Value,State]') -join ' | ')"
L "Routes tgw-rt-prod : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtProd --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
L "Routes tgw-rt-dev  : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtDev --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
L "dev-01 -> app-01:8080 par le Transit Gateway : $(Curl)"
L "`n=== TP3 : propagation de tgwa-dev vers tgw-rt-prod retiree ==="
Aws ec2 disable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaDev | Out-Null
Start-Sleep 20
L "Routes tgw-rt-prod apres retrait : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtProd --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
L "dev-01 -> app-01:8080 (la reponse n'a plus de route) : $(Curl)"
Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaDev | Out-Null
Start-Sleep 20
L "Propagation retablie : $(Curl)"
$log | Set-Content $outFile -Encoding utf8
