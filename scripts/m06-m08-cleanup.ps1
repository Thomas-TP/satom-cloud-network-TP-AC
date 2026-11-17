# Nettoyage des modules 6, 7 et 8 (TP-AC) : tout ce qui est facture a l'heure (VPN, attachements TGW, Elastic IP) puis le TGW et le DXGW.
# Ne touche qu'aux ressources de notre fichier d'etat (state.json). Les routeurs EC2 sont seulement arretes.
$ErrorActionPreference = 'Continue'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
function Try($label, $sb) { try { & $sb | Out-Null; "ok    : $label" } catch { "echec : $label ($($_.Exception.Message))" } }
function Wait-Gone($cmd, $pattern) { for ($i=0; $i -lt 60; $i++) { $r = (Invoke-Expression $cmd 2>&1 | Out-String); if ($r -match $pattern) { return }; Start-Sleep 10 } }

# 1. routes qui visent le TGW (on remet les tables en ordre avant de supprimer la cible)
foreach ($c in '192.168.10.0/24','192.168.20.0/24','10.21.0.0/24') { Try "rt-prive $c" { Aws ec2 delete-route --route-table-id $s.rtPrive --destination-cidr-block $c } }
Try 'rt-dev 10.20.0.0/22' { Aws ec2 delete-route --route-table-id $s.rtDev --destination-cidr-block 10.20.0.0/22 }
Try 'rt-public 192.168.10.0/24' { Aws ec2 delete-route --route-table-id $s.rtPublic --destination-cidr-block 192.168.10.0/24 }

# 2. Direct Connect Gateway : association puis passerelle
$assoc = Aws directconnect describe-direct-connect-gateway-associations --direct-connect-gateway-id $s.dxgw --query 'directConnectGatewayAssociations[0].associationId' 2>$null
if ($assoc -and $assoc -ne 'None') { Try 'association DXGW-TGW' { Aws directconnect delete-direct-connect-gateway-association --association-id $assoc }
  Wait-Gone "Aws directconnect describe-direct-connect-gateway-associations --direct-connect-gateway-id $($s.dxgw) --query 'directConnectGatewayAssociations[0].associationState'" 'None|disassociated' }
Try 'DXGW' { Aws directconnect delete-direct-connect-gateway --direct-connect-gateway-id $s.dxgw }

# 3. VPN (facture a l'heure) puis Customer Gateways
foreach ($n in 'Siege','Agence') { if ($s["vpn$n"]) { Try "vpn $n" { Aws ec2 delete-vpn-connection --vpn-connection-id $s["vpn$n"] } } }
foreach ($n in 'Siege','Agence') { if ($s["vpn$n"]) { Wait-Gone "Aws ec2 describe-vpn-connections --vpn-connection-ids $($s["vpn$n"]) --query 'VpnConnections[0].State'" 'deleted' } }
foreach ($n in 'Siege','Agence') { if ($s["cgw$n"]) { Try "cgw $n" { Aws ec2 delete-customer-gateway --customer-gateway-id $s["cgw$n"] } } }

# 4. attachements VPC, tables du TGW, TGW
foreach ($a in $s.tgwaProd,$s.tgwaDev) { if ($a) { Try "attachement $a" { Aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $a } } }
Wait-Gone "Aws ec2 describe-transit-gateway-attachments --filters Name=transit-gateway-id,Values=$($s.tgw) Name=state,Values=available,deleting --query 'length(TransitGatewayAttachments)'" '^0'
foreach ($rt in $s.tgwRtProd,$s.tgwRtDev,$s.tgwRtSites) { if ($rt) { Try "table $rt" { Aws ec2 delete-transit-gateway-route-table --transit-gateway-route-table-id $rt } } }
Start-Sleep 20
Try 'TGW' { Aws ec2 delete-transit-gateway --transit-gateway-id $s.tgw }

# 5. Elastic IP (facturees si non utilisees)
foreach ($k in 'eipSiege','eipAgence','eipRtrAws') { if ($s[$k]) { Try "EIP $k" { Aws ec2 release-address --allocation-id $s[$k] } } }

# 6. routeurs arretes
Try 'routeurs arretes' { Aws ec2 stop-instances --instance-ids $s.rtrSiege $s.rtrAgence $s.rtrAws }
foreach ($k in 'tgw','tgwaProd','tgwaDev','tgwRtProd','tgwRtDev','tgwRtSites','tgwaVpnSiege','tgwaVpnAgence','vpnSiege','vpnAgence','cgwSiege','cgwAgence','eipSiege','eipAgence','eipRtrAws','dxgw') { if ($s -is [hashtable]) { $s.Remove($k) } else { $s.PSObject.Properties.Remove($k) } }
Save-State $s
'Nettoyage des modules 6 a 8 termine.'
