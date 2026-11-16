# Module 8 - Direct Connect SIMULE : tunnel GRE + BGP (FRRouting) entre rtr-siege (AS 65010) et rtr-aws (AS 64513)
# Direct Connect est bloque par la SCP : le tunnel GRE remplace la fibre, le VPN IPsec du module 7 sert de secours.
#  - Sessions BGP : via GRE (169.254.100.0/30, "DX") et via IPsec (169.254.10.0/30, VPN)
#  - local-pref 200 sur les routes recues par la liaison DX ; AS-path prepend x3 sur le chemin VPN
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m08\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function Run($id,$cmd,$t=120) { ((Invoke-Ssm $id $cmd $t) -join "`n") }

# GRE (protocole 47) autorise entre les deux routeurs
Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrAws --ip-permissions "IpProtocol=47,IpRanges=[{CidrIp=$($s.pubSite)/32,Description=GRE DX simule}]" | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrSiege --ip-permissions "IpProtocol=47,IpRanges=[{CidrIp=$($s.pubAws)/32,Description=GRE DX simule}]" | Out-Null

$frrInstall = @'
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq frr >/dev/null
sed -i 's/^bgpd=no/bgpd=yes/' /etc/frr/daemons
systemctl enable frr >/dev/null 2>&1; systemctl restart frr; sleep 3
'@
# --- routeur AWS (AS 64513) ---
$awsCmd = $frrInstall + @"
ip tunnel del gre-dx 2>/dev/null || true
ip tunnel add gre-dx mode gre local 10.20.0.74 remote $($s.pubSite) ttl 255
ip addr add 169.254.100.1/30 dev gre-dx; ip link set gre-dx up
ip route del 192.168.10.0/24 dev xfrm-siege 2>/dev/null || true
ip route replace 10.20.0.0/22 via 10.20.0.65 dev `$(ip -o -4 route show to default | awk '{print `$5}') metric 100
vtysh <<'EOV'
configure terminal
route-map DX-IN permit 10
 set local-preference 200
route-map VPN-IN permit 10
route-map ANNOUNCE permit 10
router bgp 64513
 bgp router-id 10.20.0.74
 no bgp ebgp-requires-policy
 neighbor 169.254.100.2 remote-as 65010
 neighbor 169.254.100.2 description DX-simule-GRE
 neighbor 169.254.100.2 timers 3 9
 neighbor 169.254.10.2 remote-as 65010
 neighbor 169.254.10.2 description VPN-IPsec
 neighbor 169.254.10.2 timers 3 9
 address-family ipv4 unicast
  network 10.20.0.0/22
  neighbor 169.254.100.2 route-map DX-IN in
  neighbor 169.254.10.2 route-map VPN-IN in
 exit-address-family
end
write memory
EOV
"@
# --- routeur siege (AS 65010) ---
$siegeCmd = $frrInstall + @"
ip tunnel del gre-dx 2>/dev/null || true
ip tunnel add gre-dx mode gre local 192.168.10.10 remote $($s.pubAws) ttl 255
ip addr add 169.254.100.2/30 dev gre-dx; ip link set gre-dx up
ip route del 10.20.0.0/22 dev xfrm-siege 2>/dev/null || true
ip route replace 192.168.10.0/24 via 192.168.10.1 dev `$(ip -o -4 route show to default | awk '{print `$5}') metric 100
vtysh <<'EOV'
configure terminal
route-map DX-IN permit 10
 set local-preference 200
route-map VPN-OUT permit 10
 set as-path prepend 65010 65010 65010
route-map VPN-IN permit 10
router bgp 65010
 bgp router-id 192.168.10.10
 no bgp ebgp-requires-policy
 neighbor 169.254.100.1 remote-as 64513
 neighbor 169.254.100.1 description DX-simule-GRE
 neighbor 169.254.100.1 timers 3 9
 neighbor 169.254.10.1 remote-as 64513
 neighbor 169.254.10.1 description VPN-IPsec
 neighbor 169.254.10.1 timers 3 9
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.100.1 route-map DX-IN in
  neighbor 169.254.10.1 route-map VPN-IN in
  neighbor 169.254.10.1 route-map VPN-OUT out
 exit-address-family
end
write memory
EOV
"@
Run $s.rtrAws $awsCmd 300 | Out-Null
Run $s.rtrSiege $siegeCmd 300 | Out-Null
Start-Sleep 25

L "=== TP1 : dimensionnement (voir docs/modules/m08) ==="
L "2 To en 8 h = 16 000 Gbit / 28 800 s = 0,556 Gbit/s -> liaison 1 Gbit/s (marge ~44 %)"
L "`n=== TP2 : GRE + BGP ==="
L "rtr-aws : show bgp summary`n$(Run $s.rtrAws 'vtysh -c "show bgp summary"' 40)"
L "rtr-aws : show ip bgp 192.168.10.0/24`n$(Run $s.rtrAws 'vtysh -c "show ip bgp 192.168.10.0/24"' 40)"
L "rtr-siege : show ip route 10.20.0.0/22`n$(Run $s.rtrSiege 'vtysh -c "show ip route 10.20.0.0/22"' 40)"
L "siege -> app-01 (chemin DX) :`n$(Run $s.rtrSiege 'ip route get 10.20.1.10 from 192.168.10.10; ping -c 3 -I 192.168.10.10 10.20.1.10 | tail -3' 40)"

L "`n=== TP3 : politique et bascule ==="
L "rtr-siege : show ip bgp 10.20.0.0/22 (local-pref 200 sur DX, 100 sur VPN)`n$(Run $s.rtrSiege 'vtysh -c "show ip bgp 10.20.0.0/22"' 40)"
L "rtr-aws : chemin VPN annonce par le siege avec AS-path prepend x3 (65010 65010 65010 65010) :`n$(Run $s.rtrAws 'vtysh -c "show ip bgp neighbors 169.254.10.2 routes"' 40)"
# bascule : ping continu horodate, coupure du GRE, mesure du delai
Run $s.rtrSiege 'rm -f /tmp/fo.log; nohup bash -c "for i in \$(seq 1 400); do if ping -c1 -W1 -I 192.168.10.10 10.20.1.10 >/dev/null 2>&1; then echo \$(date +%s.%N) OK; else echo \$(date +%s.%N) KO; fi; sleep 0.1; done" >/tmp/fo.log 2>&1 &' 20 | Out-Null
Start-Sleep 8
$tCut = Get-Date
Run $s.rtrSiege 'ip link set gre-dx down; date +%s.%N' 20 | Out-Null
Start-Sleep 30
L "GRE coupe -> route apres bascule :`n$(Run $s.rtrSiege 'ip route get 10.20.1.10 from 192.168.10.10; vtysh -c "show bgp summary" | grep -E "Neighbor|169.254"' 40)"
Run $s.rtrSiege 'ip link set gre-dx up' 20 | Out-Null
Start-Sleep 40
L "GRE retabli -> retour sur DX :`n$(Run $s.rtrSiege 'ip route get 10.20.1.10 from 192.168.10.10' 40)"
Start-Sleep 20
$fo = Run $s.rtrSiege 'awk "{print \$2}" /tmp/fo.log | uniq -c | head -20; echo ---; grep -c KO /tmp/fo.log; echo pings_perdus_x0.1s' 40
L "Journal de continuite (pings toutes les 0,1 s ; KO = perdus) :`n$fo"
$log | Set-Content $outFile -Encoding utf8

