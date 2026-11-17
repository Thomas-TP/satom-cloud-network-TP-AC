# Module 8 - Direct Connect : partie simulee (liaison dedicee, TP2 et TP3). La partie reelle (dxgw-leman-TP-AC + association au TGW) est faite par la CLI.
# Pas de fibre commandee : un tunnel GRE entre rtr-siege (AS 65010) et rtr-aws (AS 64513, joue l'equipement cote AWS) remplace la liaison.
#   chemin "DX"  : GRE gre-dx sur Internet (EIP) ................ 169.254.100.0/30, local-pref 200 cote siege
#   chemin "VPN" : GRE gre-vpn a l'interieur du VRAI VPN du module 7 .. 169.254.101.0/30, AS-path prepend x3 cote siege
# Prerequis : module 7 en place (tunnels UP). Usage : pwsh scripts\m08-dx-sim.ps1
param([switch]$TestOnly)   # -TestOnly : rejoue les tests sans reconfigurer les routeurs
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$out = Join-Path $PSScriptRoot '..\docs\modules\m08'; New-Item -ItemType Directory -Force $out | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function Run($id,$cmd,$t=120) { ((Invoke-Ssm $id ($cmd -replace "`r","") $t) -join "`n") -split "`n" | Where-Object { $_ -notmatch "^plugin '" } | Out-String }
function AwsJson { & $script:aws @args --profile TP-AC --region eu-north-1 --output json | ConvertFrom-Json }

# --- instances, Elastic IP du routeur AWS, groupes de securite, routes ---
Aws ec2 start-instances --instance-ids $s.rtrAws $s.rtrSiege $s.app | Out-Null
Aws ec2 wait instance-running --instance-ids $s.rtrAws $s.rtrSiege $s.app
if (-not $s.eipRtrAws) { $a = AwsJson ec2 allocate-address --domain vpc --tag-specifications (Tags 'elastic-ip' 'eip-rtr-aws-TP-AC' 'prod'); $s.eipRtrAws = $a.AllocationId; $s.eipIpRtrAws = $a.PublicIp; Save-State $s }
Aws ec2 associate-address --instance-id $s.rtrAws --allocation-id $s.eipRtrAws | Out-Null
$pubAws = $s.eipIpRtrAws; $pubSiege = $s.eipIpSiege
Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrAws --ip-permissions "IpProtocol=47,IpRanges=[{CidrIp=$pubSiege/32,Description=GRE DX simule},{CidrIp=192.168.10.0/24,Description=GRE dans le VPN}]" 2>&1 | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrSiege --ip-permissions "IpProtocol=47,IpRanges=[{CidrIp=$pubAws/32,Description=GRE DX simule},{CidrIp=10.20.0.74/32,Description=GRE dans le VPN}]" 2>&1 | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions "IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=$($s.sgRtrAws),Description=API via DX simule}]" "IpProtocol=icmp,FromPort=-1,ToPort=-1,UserIdGroupPairs=[{GroupId=$($s.sgRtrAws),Description=ping via DX simule}]" 2>&1 | Out-Null
# route du sous-reseau public (ou vit rtr-aws) vers le siege par le TGW (necessaire pour le GRE dans le VPN)
& $script:aws ec2 create-route --route-table-id $s.rtPublic --destination-cidr-block 192.168.10.0/24 --transit-gateway-id $s.tgw --profile TP-AC --region eu-north-1 2>&1 | Out-Null
$sub = Aws ec2 describe-transit-gateway-vpc-attachments --transit-gateway-attachment-ids $s.tgwaProd --query 'TransitGatewayVpcAttachments[0].SubnetIds'
if ($sub -notmatch $s.subPublic1b) {
  Aws ec2 modify-transit-gateway-vpc-attachment --transit-gateway-attachment-id $s.tgwaProd --add-subnet-ids $s.subPublic1b | Out-Null
  do { Start-Sleep 10; $st = Aws ec2 describe-transit-gateway-vpc-attachments --transit-gateway-attachment-ids $s.tgwaProd --query 'TransitGatewayVpcAttachments[0].State' } while ($st -ne 'available')
}
foreach ($i in $s.rtrAws,$s.rtrSiege,$s.app) { "$i SSM: $(Wait-Ssm $i 300)" }

$frrInstall = @'
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq; apt-get install -y -qq frr iptables >/dev/null
sed -i 's/^bgpd=no/bgpd=yes/' /etc/frr/daemons
printf 'net.ipv4.ip_forward=1\nnet.ipv4.conf.all.rp_filter=0\nnet.ipv4.conf.default.rp_filter=0\n' > /etc/sysctl.d/99-tpac.conf; sysctl --system >/dev/null
systemctl stop frr; printf 'frr defaults traditional
log syslog informational
' > /etc/frr/frr.conf; chown frr:frr /etc/frr/frr.conf
systemctl enable frr >/dev/null 2>&1; systemctl start frr; sleep 3
DEV=$(ip -o -4 route show to default | awk '{print $5}')
'@
# --- routeur AWS (AS 64513) ---
$awsCmd = $frrInstall + @"
ip tunnel del gre-dx 2>/dev/null || true; ip tunnel del gre-vpn 2>/dev/null || true
ip tunnel add gre-dx mode gre local 10.20.0.74 remote $pubSiege ttl 255
ip addr add 169.254.100.1/30 dev gre-dx; ip link set gre-dx up
ip tunnel add gre-vpn mode gre local 10.20.0.74 remote 192.168.10.10 ttl 255
ip addr add 169.254.101.1/30 dev gre-vpn; ip link set gre-vpn up
ip route replace 192.168.10.10/32 via 10.20.0.65 dev `$DEV
iptables -t nat -C POSTROUTING -s 192.168.10.0/24 -o `$DEV -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o `$DEV -j MASQUERADE
vtysh <<'EOV'
configure terminal
ip route 10.20.0.0/22 10.20.0.65
ip route 192.168.10.10/32 10.20.0.65
router bgp 64513
 bgp router-id 10.20.0.74
 no bgp ebgp-requires-policy
 neighbor 169.254.100.2 remote-as 65010
 neighbor 169.254.100.2 description DX-simule-GRE
 neighbor 169.254.100.2 timers 3 9
 neighbor 169.254.101.2 remote-as 65010
 neighbor 169.254.101.2 description VPN-GRE-dans-IPsec
 neighbor 169.254.101.2 timers 3 9
 address-family ipv4 unicast
  network 10.20.0.0/22
 exit-address-family
end
write memory
EOV
"@
# --- routeur siege (AS 65010) ---
$siegeCmd = $frrInstall + @"
ip tunnel del gre-dx 2>/dev/null || true; ip tunnel del gre-vpn 2>/dev/null || true
ip tunnel add gre-dx mode gre local 192.168.10.10 remote $pubAws ttl 255
ip addr add 169.254.100.2/30 dev gre-dx; ip link set gre-dx up
ip tunnel add gre-vpn mode gre local 192.168.10.10 remote 10.20.0.74 ttl 255
ip addr add 169.254.101.2/30 dev gre-vpn; ip link set gre-vpn up
pkill -f tpac-watch.sh 2>/dev/null || true      # le suivi du module 7 gere la route 10.20.0.0/22 : ici c'est FRR (BGP) qui la gere
for n in 1 2; do swanctl --terminate --ike siege-t`$n >/dev/null 2>&1; done; sleep 3; iptables -F INPUT 2>/dev/null; iptables -F OUTPUT 2>/dev/null
for n in 1 2; do swanctl --initiate --child siege-t`$n >/dev/null 2>&1; done; sleep 15
ip route del 10.20.0.0/22 dev xfrm-siege1 2>/dev/null || true; ip route del 10.20.0.0/22 dev xfrm-siege2 2>/dev/null || true   # secours = routes statiques FRR de distance elevee (voir vtysh)
cat > /usr/local/bin/tpac-watch32.sh <<'EOW'
#!/bin/bash
# le GRE dans le VPN a besoin d'une route vers rtr-aws (10.20.0.74) par un tunnel etabli
while true; do
  for n in 1 2; do
    if swanctl --list-sas 2>/dev/null | grep -q "^siege-t`$n: .*ESTABLISHED"; then ip route replace 10.20.0.74/32 dev xfrm-siege`$n metric `$((n*100)) 2>/dev/null
    else ip route del 10.20.0.74/32 dev xfrm-siege`$n 2>/dev/null; fi
  done
  sleep 1
done
EOW
chmod +x /usr/local/bin/tpac-watch32.sh; pkill -f tpac-watch32.sh 2>/dev/null || true; setsid nohup /usr/local/bin/tpac-watch32.sh >/dev/null 2>&1 < /dev/null &
vtysh <<'EOV'
configure terminal
ip route 192.168.10.0/24 192.168.10.1
ip route 10.20.0.0/22 xfrm-siege1 150
ip route 10.20.0.0/22 xfrm-siege2 160
route-map DX-IN permit 10
 set local-preference 200
route-map VPN-IN permit 10
route-map VPN-OUT permit 10
 set as-path prepend 65010 65010 65010
router bgp 65010
 bgp router-id 192.168.10.10
 no bgp ebgp-requires-policy
 neighbor 169.254.100.1 remote-as 64513
 neighbor 169.254.100.1 description DX-simule-GRE
 neighbor 169.254.100.1 timers 3 9
 neighbor 169.254.101.1 remote-as 64513
 neighbor 169.254.101.1 description VPN-GRE-dans-IPsec
 neighbor 169.254.101.1 timers 3 9
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.100.1 route-map DX-IN in
  neighbor 169.254.101.1 route-map VPN-IN in
  neighbor 169.254.101.1 route-map VPN-OUT out
 exit-address-family
end
write memory
EOV
"@
if (-not $TestOnly) {
  Run $s.rtrAws $awsCmd 400 | Out-Null
  Run $s.rtrSiege $siegeCmd 400 | Out-Null
  Start-Sleep 25
}

L "=== TP1 : dimensionnement et Direct Connect Gateway (reel) ==="
L "2 To en 8 h = 16 000 Gbit / 28 800 s = 0,556 Gbit/s -> liaison 1 Gbit/s (marge ~44 %)"
L "Emplacement retenu (non commande) : EQSK1, Equinix Sweden SK1 (vitesses 1G / 10G / 100G), le plus proche disponible dans la region eu-north-1"
L "dxgw : $(Aws directconnect describe-direct-connect-gateways --direct-connect-gateway-id $($s.dxgw) --query 'directConnectGateways[0].[directConnectGatewayName,amazonSideAsn,directConnectGatewayState]')"
L "association avec tgw-leman : $(Aws directconnect describe-direct-connect-gateway-associations --direct-connect-gateway-id $($s.dxgw) --query 'directConnectGatewayAssociations[0].[associationState,allowedPrefixesToDirectConnectGateway[].cidr]')"
L "`n=== TP2 : GRE + BGP ==="
L "rtr-aws : traduction d'adresse (NAT) pour app-01 :`n$(Run $s.rtrAws 'iptables -t nat -S POSTROUTING | tail -2' 40)"
L "rtr-siege : show bgp summary`n$(Run $s.rtrSiege 'vtysh -c "show bgp summary"' 40)"
L "rtr-aws : show ip bgp (prefixes recus du siege)`n$(Run $s.rtrAws 'vtysh -c "show ip bgp"' 40)"
L "siege -> app-01 (chemin choisi) :`n$(Run $s.rtrSiege 'ip addr add 192.168.10.50/32 dev lo 2>/dev/null; ip route get 10.20.1.10 from 192.168.10.50; ping -c 3 -I 192.168.10.50 10.20.1.10 | tail -3; curl -s -m 5 --interface 192.168.10.50 http://10.20.1.10:8080/api/health' 60)"
L "`n=== TP3 : politique et bascule ==="
L "rtr-siege : show ip bgp 10.20.0.0/22 (local-pref 200 sur DX, 100 sur VPN)`n$(Run $s.rtrSiege 'vtysh -c "show ip bgp 10.20.0.0/22"' 40)"
L "rtr-aws : show ip bgp 192.168.10.0/24 (le chemin VPN arrive avec AS-path prepend x3)`n$(Run $s.rtrAws 'vtysh -c "show ip bgp 192.168.10.0/24"' 40)"
$cmd = @'
ip addr add 192.168.10.50/32 dev lo 2>/dev/null || true     # un poste du LAN du siege (192.168.10.50)
AWSIP=$(ip tunnel show gre-dx | sed 's/.*remote \([0-9.]*\).*/\1/')
iptables -D OUTPUT -p gre -d $AWSIP -j DROP 2>/dev/null; iptables -D INPUT -p gre -s $AWSIP -j DROP 2>/dev/null
rm -f /tmp/fo.txt
( ping -D -i 0.5 -c 180 -I 192.168.10.50 10.20.1.10 > /tmp/fo.txt 2>&1 & )
sleep 10
echo "T+10 s : panne de la liaison DX (le GRE vers $AWSIP est perdu, sans coupure de l'interface)"
echo "route : $(ip route get 10.20.1.10 from 192.168.10.50 | head -1)"
iptables -I OUTPUT -p gre -d $AWSIP -j DROP; iptables -I INPUT -p gre -s $AWSIP -j DROP
sleep 30
echo "T+40 s (DX en panne) route : $(ip route get 10.20.1.10 from 192.168.10.50 | head -1)"
vtysh -c "show bgp summary" | grep -E "^169|^Neighbor"
echo "T+40 s : liaison DX retablie"; iptables -D OUTPUT -p gre -d $AWSIP -j DROP; iptables -D INPUT -p gre -s $AWSIP -j DROP
sleep 30
echo "T+70 s (DX retablie) route : $(ip route get 10.20.1.10 from 192.168.10.50 | head -1)"
sleep 22
echo "--- ping horodate depuis 192.168.10.50 (une sonde toutes les 0,5 s, 180 sondes)"
tail -3 /tmp/fo.txt | grep -E "transmitted|rtt"
grep "bytes from" /tmp/fo.txt | sed 's/^\[\([0-9.]*\)\].*icmp_seq=\([0-9]*\).*/\1 \2/' | awk 'NR==1{t0=$1} NR>1 && $1-p>1.2 {printf "interruption de %.1f s, de T+%.1f s a T+%.1f s (sondes %d a %d perdues)\n", $1-p, p-t0, $1-t0, q+1, $2-1} {p=$1; q=$2}'
'@
L ((Run $s.rtrSiege $cmd 300))
$log | Set-Content (Join-Path $out 'tests.txt') -Encoding utf8
