# Module 6 - Transit Gateway tgw-leman (TP-AC)  [attachements factures a l'heure]
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m06\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function Wait-State($cmd, $want) { do { Start-Sleep 10; $st = ((Invoke-Expression $cmd) -join ',') -replace '\s+', ',' } while ($st -ne $want); }
function Find-Id($cmd) { $r = Invoke-Expression $cmd; if ($r -and $r -ne 'None') { $r } else { $null } }

# TP1 : TGW (association et propagation par defaut desactivees) + 2 attachements
$s.tgw = Find-Id "Aws ec2 describe-transit-gateways --filters 'Name=tag:Name,Values=tgw-leman-TP-AC' 'Name=state,Values=available,pending' --query 'TransitGateways[0].TransitGatewayId'"
if (-not $s.tgw) { $s.tgw = Aws ec2 create-transit-gateway --description 'tgw-leman TP-AC' --options 'AmazonSideAsn=64512,DefaultRouteTableAssociation=disable,DefaultRouteTablePropagation=disable,DnsSupport=enable,VpnEcmpSupport=enable' --tag-specifications (Tags 'transit-gateway' 'tgw-leman-TP-AC') --query TransitGateway.TransitGatewayId }
Wait-State "Aws ec2 describe-transit-gateways --transit-gateway-ids $($s.tgw) --query 'TransitGateways[0].State'" 'available'
$s.tgwaProd = Find-Id "Aws ec2 describe-transit-gateway-vpc-attachments --filters 'Name=tag:Name,Values=tgwa-prod-TP-AC' 'Name=state,Values=available,pending' --query 'TransitGatewayVpcAttachments[0].TransitGatewayAttachmentId'"
if (-not $s.tgwaProd) { $s.tgwaProd = Aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id $s.tgw --vpc-id $s.vpc --subnet-ids $s.subPrive --tag-specifications (Tags 'transit-gateway-attachment' 'tgwa-prod-TP-AC') --query TransitGatewayVpcAttachment.TransitGatewayAttachmentId }
$s.tgwaDev = Find-Id "Aws ec2 describe-transit-gateway-vpc-attachments --filters 'Name=tag:Name,Values=tgwa-dev-TP-AC' 'Name=state,Values=available,pending' --query 'TransitGatewayVpcAttachments[0].TransitGatewayAttachmentId'"
if (-not $s.tgwaDev) { $s.tgwaDev = Aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id $s.tgw --vpc-id $s.vpcDev --subnet-ids $s.subDev --tag-specifications (Tags 'transit-gateway-attachment' 'tgwa-dev-TP-AC' 'dev') --query TransitGatewayVpcAttachment.TransitGatewayAttachmentId }
Wait-State "Aws ec2 describe-transit-gateway-vpc-attachments --transit-gateway-attachment-ids $($s.tgwaProd) $($s.tgwaDev) --query 'TransitGatewayVpcAttachments[].State'" 'available,available'
Save-State $s

# TP2 : tables TGW dediees + propagation croisee
$s.tgwRtProd = Aws ec2 create-transit-gateway-route-table --transit-gateway-id $s.tgw --tag-specifications (Tags 'transit-gateway-route-table' 'tgw-rt-prod-TP-AC') --query TransitGatewayRouteTable.TransitGatewayRouteTableId
$s.tgwRtDev  = Aws ec2 create-transit-gateway-route-table --transit-gateway-id $s.tgw --tag-specifications (Tags 'transit-gateway-route-table' 'tgw-rt-dev-TP-AC' 'dev') --query TransitGatewayRouteTable.TransitGatewayRouteTableId
Wait-State "Aws ec2 describe-transit-gateway-route-tables --transit-gateway-route-table-ids $($s.tgwRtProd) $($s.tgwRtDev) --query 'TransitGatewayRouteTables[].State'" 'available,available'
Aws ec2 associate-transit-gateway-route-table --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaProd | Out-Null
Aws ec2 associate-transit-gateway-route-table --transit-gateway-route-table-id $s.tgwRtDev  --transit-gateway-attachment-id $s.tgwaDev | Out-Null
Start-Sleep 20
Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaDev | Out-Null   # la prod apprend le CIDR dev
Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtDev  --transit-gateway-attachment-id $s.tgwaProd | Out-Null  # le dev apprend le CIDR prod
# routes VPC -> TGW (remplacent le peering), puis suppression de pcx-lab
Aws ec2 replace-route --route-table-id $s.rtPrive --destination-cidr-block 10.21.0.0/24 --transit-gateway-id $s.tgw
Aws ec2 replace-route --route-table-id $s.rtDev   --destination-cidr-block 10.20.0.0/22 --transit-gateway-id $s.tgw
Aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $s.pcx | Out-Null
$s.Remove('pcx'); Save-State $s
Start-Sleep 15

L "=== TP1/TP2 : tgw-leman ==="
L "Attachements : $(Aws ec2 describe-transit-gateway-attachments --filters "Name=transit-gateway-id,Values=$($s.tgw)" --query 'TransitGatewayAttachments[].[Tags[?Key==`Name`]|[0].Value,State]')"
L "pcx-lab present ? : $(Aws ec2 describe-vpc-peering-connections --filters 'Name=status-code,Values=active' 'Name=tag:Equipe,Values=TP-AC' --query 'length(VpcPeeringConnections)') (0 = supprime)"
L "Routes tgw-rt-prod : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtProd --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
L "Routes tgw-rt-dev  : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtDev --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
L "dev-01 -> app-01:8080 via TGW : $((Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"

# TP3 : retrait de la propagation -> trafic asymetrique
L "`n=== TP3 : propagation retiree ==="
Aws ec2 disable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaDev | Out-Null
Start-Sleep 15
L "Propagation tgwa-dev -> tgw-rt-prod retiree (la prod ne sait plus repondre au dev) : $((Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s.tgwaDev | Out-Null
Start-Sleep 15
L "Propagation retablie : $((Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
$log | Set-Content $outFile -Encoding utf8
$s | ConvertTo-Json
