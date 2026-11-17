# Module 7 - VPN site a site AWS (service gere) attache au Transit Gateway tgw-leman (TP-AC)  [facture a l'heure : voir m07-vpn-cleanup.ps1]
# Les "sites" siege et agence sont deux routeurs strongSwan (EC2) qui jouent l'equipement client (Customer Gateway).
# Etape 1 : Elastic IP, Customer Gateways, connexions VPN (routage statique, 2 tunnels chacune), tables et routes du TGW, Security Groups.
# Etape 2 : configuration strongSwan des deux tunnels de chaque site, attente de l'etat UP, tests (flux, segmentation).
# Etape 3 : coupure du premier tunnel du siege pendant un ping horodate (bascule), puis retablissement.
# Usage : pwsh scripts\m07-vpn-aws.ps1 -Stage 1|2|3
param([ValidateSet(1,2,3)][int]$Stage = 1)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$out = Join-Path $PSScriptRoot '..\docs\modules\m07'; New-Item -ItemType Directory -Force $out | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function J($name,$obj) { $f = Join-Path $env:TEMP "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 10 -Compress)); "file://$f" }
function AwsJson { & $script:aws @args --profile TP-AC --region eu-north-1 --output json | ConvertFrom-Json }
$sites = @(
  @{ n='siege';  cidr='192.168.10.0/24'; sg='sgRtrSiege';  rtr='rtrSiege';  priv='192.168.10.10'; ifid=@(11,12) },
  @{ n='agence'; cidr='192.168.20.0/24'; sg='sgRtrAgence'; rtr='rtrAgence'; priv='192.168.20.10'; ifid=@(21,22) } )

if ($Stage -eq 1) {
  # --- instances des routeurs demarrees ---
  Aws ec2 start-instances --instance-ids $s.rtrSiege $s.rtrAgence | Out-Null
  Aws ec2 wait instance-running --instance-ids $s.rtrSiege $s.rtrAgence

  # --- cles pre-partagees : 4 cles (une par tunnel), uniquement dans Secrets Manager ---
  $rnd = { 'k' + (-join ((48..57)+(65..90)+(97..122) | Get-Random -Count 39 | ForEach-Object { [char]$_ })) }
  $sf = Join-Path $env:TEMP 'tpac-psk.json'
  [IO.File]::WriteAllText($sf, (@{siege1=(& $rnd);siege2=(& $rnd);agence1=(& $rnd);agence2=(& $rnd)} | ConvertTo-Json -Compress))
  Aws secretsmanager put-secret-value --secret-id Projet/SatomCloudNetwork/vpn --secret-string "file://$sf" | Out-Null
  $psk = Get-Content $sf -Raw | ConvertFrom-Json; Remove-Item $sf -Force

  foreach ($x in $sites) {
    $n = $x.n; $N = $n.Substring(0,1).ToUpper() + $n.Substring(1)
    # Elastic IP fixe pour le routeur (adresse du Customer Gateway)
    if (-not $s["eip$N"]) {
      $a = AwsJson ec2 allocate-address --domain vpc --tag-specifications (Tags 'elastic-ip' "eip-rtr-$n-TP-AC" 'prod')
      $s["eip$N"] = $a.AllocationId; $s["eipIp$N"] = $a.PublicIp; Save-State $s
    }
    Aws ec2 associate-address --instance-id $s[$x.rtr] --allocation-id $s["eip$N"] | Out-Null
    $ip = $s["eipIp$N"]
    # Customer Gateway (routage statique : l'ASN est obligatoire mais sans effet)
    if (-not $s["cgw$N"]) { $s["cgw$N"] = Aws ec2 create-customer-gateway --type ipsec.1 --ip-address $ip --bgp-asn 65000 --tag-specifications (Tags 'customer-gateway' "cgw-$n-TP-AC" 'prod') --query CustomerGateway.CustomerGatewayId; Save-State $s }
    # Connexion VPN attachee au Transit Gateway, 2 tunnels, IKEv2, AES-256 / SHA-256 / DH 14
    if (-not $s["vpn$N"]) {
      $to = @(1,2) | ForEach-Object { @{ PreSharedKey = $psk."$n$_"; IKEVersions=@(@{Value='ikev2'}); Phase1EncryptionAlgorithms=@(@{Value='AES256'}); Phase2EncryptionAlgorithms=@(@{Value='AES256'});
          Phase1IntegrityAlgorithms=@(@{Value='SHA2-256'}); Phase2IntegrityAlgorithms=@(@{Value='SHA2-256'}); Phase1DHGroupNumbers=@(@{Value=14}); Phase2DHGroupNumbers=@(@{Value=14}); DPDTimeoutSeconds=30 } }
      $opt = @{ StaticRoutesOnly = $true; TunnelOptions = @($to) }
      $s["vpn$N"] = Aws ec2 create-vpn-connection --type ipsec.1 --customer-gateway-id $s["cgw$N"] --transit-gateway-id $s.tgw --options (J "vpnopt$n" $opt) --tag-specifications (Tags 'vpn-connection' "vpn-$n-TP-AC" 'prod') --query VpnConnection.VpnConnectionId
      Save-State $s
    }
  }
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    do { Start-Sleep 15; $st = Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"] --query 'VpnConnections[0].State' } while ($st -ne 'available') }
  # (les routes statiques d'un VPN attache a un TGW se declarent dans la table du TGW : voir plus bas)

  # --- attachements VPN du TGW : association a une table "sites" dediee (voient la prod, pas le dev) ---
  if (-not $s.tgwRtSites) { $s.tgwRtSites = Aws ec2 create-transit-gateway-route-table --transit-gateway-id $s.tgw --tag-specifications (Tags 'transit-gateway-route-table' 'tgw-rt-sites-TP-AC' 'prod') --query TransitGatewayRouteTable.TransitGatewayRouteTableId; Save-State $s; Start-Sleep 20 }
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    for ($i=0; $i -lt 30 -and -not $s["tgwaVpn$N"]; $i++) {
      $att = Aws ec2 describe-transit-gateway-attachments --filters "Name=resource-id,Values=$($s["vpn$N"])" "Name=resource-type,Values=vpn" --query 'TransitGatewayAttachments[0].TransitGatewayAttachmentId'
      if ($att -and $att -ne 'None') { $s["tgwaVpn$N"] = $att } else { Start-Sleep 10 } }
    Aws ec2 create-tags --resources $s["tgwaVpn$N"] --tags "Key=Name,Value=tgwa-vpn-$($x.n)-TP-AC" 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' 'Key=Environnement,Value=prod' | Out-Null
    do { Start-Sleep 10; $st = Aws ec2 describe-transit-gateway-attachments --transit-gateway-attachment-ids $s["tgwaVpn$N"] --query 'TransitGatewayAttachments[0].State' } while ($st -ne 'available')
    Aws ec2 associate-transit-gateway-route-table --transit-gateway-route-table-id $s.tgwRtSites --transit-gateway-attachment-id $s["tgwaVpn$N"] 2>&1 | Out-Null
  }
  Save-State $s; Start-Sleep 20
  Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtSites --transit-gateway-attachment-id $s.tgwaProd 2>&1 | Out-Null   # les sites apprennent la prod
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    Aws ec2 enable-transit-gateway-route-table-propagation --transit-gateway-route-table-id $s.tgwRtProd --transit-gateway-attachment-id $s["tgwaVpn$N"] 2>&1 | Out-Null }  # la prod apprend les sites (pas le dev)
  # routes statiques des sites dans tgw-rt-prod (cible = attachement VPN)
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    Aws ec2 create-transit-gateway-route --transit-gateway-route-table-id $s.tgwRtProd --destination-cidr-block $x.cidr --transit-gateway-attachment-id $s["tgwaVpn$N"] 2>&1 | Out-Null }
  # routes VPC : la prod renvoie les sites vers le TGW (remplace les routes de la simulation)
  foreach ($x in $sites) { & $script:aws ec2 replace-route --route-table-id $s.rtPrive --destination-cidr-block $x.cidr --transit-gateway-id $s.tgw --profile TP-AC --region eu-north-1 2>&1 | Out-Null
    if ($LASTEXITCODE) { Aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block $x.cidr --transit-gateway-id $s.tgw | Out-Null } }

  # --- Security Groups : routeurs (IKE depuis les 4 adresses AWS) et sg-app (siege : ping + 8080, agence : 8080) ---
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    $v = AwsJson ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"]
    $topts = $v.VpnConnections[0].Options.TunnelOptions
    $perm = @(); foreach ($t in $topts) { $o = $t.OutsideIpAddress
      $perm += "IpProtocol=udp,FromPort=500,ToPort=500,IpRanges=[{CidrIp=$o/32,Description=IKE}]"; $perm += "IpProtocol=udp,FromPort=4500,ToPort=4500,IpRanges=[{CidrIp=$o/32,Description=NAT-T}]"; $perm += "IpProtocol=50,IpRanges=[{CidrIp=$o/32,Description=ESP}]" }
    Aws ec2 authorize-security-group-ingress --group-id $s[$x.sg] --ip-permissions $perm 2>&1 | Out-Null
  }
  Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions 'IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges=[{CidrIp=192.168.10.0/24,Description=ping siege}]' 'IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=192.168.10.0/24,Description=API siege}]' 2>&1 | Out-Null
  Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions 'IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=192.168.20.0/24,Description=API agence}]' 2>&1 | Out-Null

  L "=== Module 7 - etape 1 : etat des VPN avant configuration des routeurs ==="
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    L "vpn-$($x.n)-TP-AC : $(Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"] --query 'VpnConnections[0].[State,Type,Options.StaticRoutesOnly]')"
    L "  tunnels (adresse AWS, etat) : $((Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"] --query 'VpnConnections[0].VgwTelemetry[].[OutsideIpAddress,Status]') -join ' | ')"
  }
  $log | Set-Content (Join-Path $out 'tests-etape1.txt') -Encoding utf8
  Save-State $s; return
}

# ------------------------------------------------------------------ etape 2 / 3
function Run($id,$cmd,$t=90) { ((Invoke-Ssm $id ($cmd -replace "`r","") $t) -join "`n") }
function Tun($N) { $v = AwsJson ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"]; @($v.VpnConnections[0].Options.TunnelOptions) }
function Conf($x,$N) {
  $topts = Tun $N
  $tpl = @'
set -e
export PATH=$PATH:/snap/bin DEBIAN_FRONTEND=noninteractive
apt-get update -qq; apt-get install -y -qq strongswan-swanctl charon-systemd python3 >/dev/null
snap list aws-cli >/dev/null 2>&1 || snap install aws-cli --classic >/dev/null
printf 'net.ipv4.ip_forward=1\nnet.ipv4.conf.all.rp_filter=0\nnet.ipv4.conf.default.rp_filter=0\n' > /etc/sysctl.d/99-tpac.conf; sysctl --system >/dev/null
PSK_JSON=$(aws secretsmanager get-secret-value --secret-id Projet/SatomCloudNetwork/vpn --region eu-north-1 --query SecretString --output text)
P1=$(echo "$PSK_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['@@S@@1'])")
P2=$(echo "$PSK_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['@@S@@2'])")
rm -f /etc/swanctl/conf.d/*.conf
cat > /etc/swanctl/conf.d/@@S@@.conf <<EOC
connections {
  @@S@@-t1 {
    version = 2
    local_addrs = @@PRIV@@
    remote_addrs = @@O1@@
    local {
      auth = psk
      id = @@PUB@@
    }
    remote {
      auth = psk
      id = @@O1@@
    }
    proposals = aes256-sha256-modp2048
    dpd_delay = 10s
    children {
      @@S@@-t1 {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        esp_proposals = aes256-sha256-modp2048
        if_id_in = @@IF1@@
        if_id_out = @@IF1@@
        start_action = start
        dpd_action = restart
      }
    }
  }
  @@S@@-t2 {
    version = 2
    local_addrs = @@PRIV@@
    remote_addrs = @@O2@@
    local {
      auth = psk
      id = @@PUB@@
    }
    remote {
      auth = psk
      id = @@O2@@
    }
    proposals = aes256-sha256-modp2048
    dpd_delay = 10s
    children {
      @@S@@-t2 {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        esp_proposals = aes256-sha256-modp2048
        if_id_in = @@IF2@@
        if_id_out = @@IF2@@
        start_action = start
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-@@S@@-t1 {
    id = @@O1@@
    secret = "$P1"
  }
  ike-@@S@@-t2 {
    id = @@O2@@
    secret = "$P2"
  }
}
EOC
chmod 600 /etc/swanctl/conf.d/@@S@@.conf
DEV=$(ip -o -4 route show to default | awk '{print $5}')
for i in 1 2; do ip link del xfrm-@@S@@$i 2>/dev/null || true; done
ip link add xfrm-@@S@@1 type xfrm dev $DEV if_id @@IF1@@; ip addr add @@I1@@/30 dev xfrm-@@S@@1; ip link set xfrm-@@S@@1 up
ip link add xfrm-@@S@@2 type xfrm dev $DEV if_id @@IF2@@; ip addr add @@I2@@/30 dev xfrm-@@S@@2; ip link set xfrm-@@S@@2 up
ip route replace 10.20.0.0/22 dev xfrm-@@S@@1 metric 100
ip route replace 10.20.0.0/22 dev xfrm-@@S@@2 metric 200
systemctl enable --now strongswan >/dev/null 2>&1; systemctl restart strongswan; sleep 4; swanctl --load-all >/dev/null
sleep 12; swanctl --list-sas 2>/dev/null | grep -E "^ *@@S@@-t[12]|ESTABLISHED|INSTALLED" | head -12
'@
  # adresses internes : le /30 AWS donne .1 cote AWS et .2 cote client
  function Ins($cidr) { $b = $cidr.Split('/')[0].Split('.'); "$($b[0]).$($b[1]).$($b[2]).$([int]$b[3] + 2)" }
  $tpl.Replace('@@S@@',$x.n).Replace('@@PRIV@@',$x.priv).Replace('@@PUB@@',$s["eipIp$N"]).Replace('@@O1@@',$topts[0].OutsideIpAddress).Replace('@@O2@@',$topts[1].OutsideIpAddress).Replace('@@IF1@@',[string]$x.ifid[0]).Replace('@@IF2@@',[string]$x.ifid[1]).Replace('@@I1@@',(Ins $topts[0].TunnelInsideCidr)).Replace('@@I2@@',(Ins $topts[1].TunnelInsideCidr))
}

if ($Stage -eq 2) {
  Aws ec2 start-instances --instance-ids $s.app $s.dev | Out-Null
  foreach ($i in $s.rtrSiege,$s.rtrAgence,$s.app,$s.dev) { "$i SSM: $(Wait-Ssm $i 300)" }
  L "=== Module 7 - etape 2 : tunnels, flux et segmentation ==="
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    $r = Run $s[$x.rtr] (Conf $x $N) 400
    L "$($x.n) : swanctl --list-sas (cote routeur)`n$r"
  }
  Start-Sleep 20
  foreach ($x in $sites) { $N = $x.n.Substring(0,1).ToUpper() + $x.n.Substring(1)
    L "vpn-$($x.n)-TP-AC, etat des tunnels vu par AWS : $((Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"] --query 'VpnConnections[0].VgwTelemetry[].[OutsideIpAddress,Status,StatusMessage]') -join ' | ')" }
  L "tgw-rt-prod (routes actives) : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtProd --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type,TransitGatewayAttachments[0].ResourceType]') -join ' | ')"
  L "tgw-rt-dev  (routes actives) : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtDev --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
  L "tgw-rt-sites (routes actives) : $((Aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $s.tgwRtSites --filters 'Name=state,Values=active' --query 'Routes[].[DestinationCidrBlock,Type]') -join ' | ')"
  L "`n-- siege -> app-01 (10.20.1.10)"
  L "ping : $(Run $s.rtrSiege 'ping -c 3 -W 2 -I 192.168.10.10 10.20.1.10 | tail -3')"
  L "8080 : $(Run $s.rtrSiege 'curl -s -m 6 --interface 192.168.10.10 http://10.20.1.10:8080/api/health || echo ECHEC')"
  L "`n-- agence -> app-01 (seul le 8080 est autorise)"
  L "8080 : $(Run $s.rtrAgence 'curl -s -m 6 --interface 192.168.20.10 http://10.20.1.10:8080/api/health || echo ECHEC')"
  L "ping (doit echouer) : $(Run $s.rtrAgence 'ping -c 2 -W 2 -I 192.168.20.10 10.20.1.10 | tail -2')"
  L "`n-- segmentation : aucun site ne joint dev-01 (10.21.0.10), dev-01 ne joint pas les sites (dev-01 SSM : $(Aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$($s.dev)" --query 'InstanceInformationList[0].PingStatus'))"
  L "siege -> dev-01 : $(Run $s.rtrSiege 'ping -c 3 -W 2 -I 192.168.10.10 10.21.0.10 | tail -2')"
  L "agence -> dev-01 : $(Run $s.rtrAgence 'ping -c 3 -W 2 -I 192.168.20.10 10.21.0.10 2>&1 | tail -2')"
  L "dev-01 -> siege : $(Run $s.dev 'ping -c 3 -W 2 192.168.10.10 | tail -2')"
  L "dev-01 -> agence : $(Run $s.dev 'ping -c 3 -W 2 192.168.20.10 | tail -2')"
  $log | Set-Content (Join-Path $out 'tests-etape2.txt') -Encoding utf8
  Save-State $s; return
}

# etape 3 : bascule des tunnels du siege
$N = 'Siege'
L "=== Module 7 - etape 3 : bascule entre les deux tunnels du siege ==="
$cmd = @'
rm -f /tmp/fo.txt
( ping -D -i 0.5 -c 200 -I 192.168.10.10 10.20.1.10 > /tmp/fo.txt 2>&1 & )
sleep 10
echo "T+10 s : coupure du tunnel 1 (siege-t1)"; swanctl --terminate --ike siege-t1 >/dev/null 2>&1; ip link set xfrm-siege1 down
sleep 60
echo "T+70 s : tunnel 1 retabli"; ip link set xfrm-siege1 up; swanctl --initiate --child siege-t1 >/dev/null 2>&1
sleep 35
echo "--- resultat du ping horodate (une sonde toutes les 0,5 s, 200 sondes)"
tail -3 /tmp/fo.txt | grep -E "transmitted|rtt"
grep "bytes from" /tmp/fo.txt | sed 's/^\[\([0-9.]*\)\].*icmp_seq=\([0-9]*\).*/\1 \2/' | awk 'NR==1{t0=$1} NR>1 && $1-p>1.2 {printf "interruption de %.1f s, de T+%.1f s a T+%.1f s (sondes %d a %d perdues)\n", $1-p, p-t0, $1-t0, q+1, $2-1} {p=$1; q=$2}'
echo "sessions IKE etablies : $(swanctl --list-sas 2>/dev/null | grep -cE 'ESTABLISHED')"
'@
L ((Run $s.rtrSiege $cmd 240) -split "`n" | Where-Object { $_ -notmatch "^plugin '" } | Out-String)
L "etat vu par AWS : $((Aws ec2 describe-vpn-connections --vpn-connection-ids $s["vpn$N"] --query 'VpnConnections[0].VgwTelemetry[].[OutsideIpAddress,Status]') -join ' | ')"
$log | Set-Content (Join-Path $out 'tests-etape3.txt') -Encoding utf8
