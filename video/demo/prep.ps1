# Mise en etat des routeurs du siege avant l'enregistrement d'un module (hors fenetre filmee).
param([ValidateSet('m07','m08','m11')][string]$Module)
. C:\Perso\AWS\scripts\lib.ps1; $s = Get-State
if ($Module -eq 'm07') {   # siege en VPN seul : FRR arrete, GRE coupes, routes statiques par les tunnels
  $c = 'systemctl stop frr; ip link set gre-dx down; ip link set gre-vpn down; ip route replace 10.20.0.0/22 dev xfrm-siege1 metric 100; ip route replace 10.20.0.0/22 dev xfrm-siege2 metric 200; for i in $(seq 1 30); do ping -c 1 -W 1 -I 192.168.10.10 10.20.1.10 >/dev/null 2>&1 && break; sleep 2; done; ip route get 10.20.1.10 from 192.168.10.10 | head -1'
} else {                   # retour a la configuration du module 8 : GRE montes, BGP en marche
  $c = 'ip route del 10.20.0.0/22 dev xfrm-siege1 2>/dev/null; ip route del 10.20.0.0/22 dev xfrm-siege2 2>/dev/null; ip link set gre-dx up; ip link set gre-vpn up; systemctl start frr; sleep 25; vtysh -c "show bgp summary" | grep -E "^169"'
}
if ($Module -eq 'm11') {   # cache vide : la 1re requete de la demo sera un Miss
  $id = Aws cloudfront create-invalidation --distribution-id $s.cfId --paths '/static/logo.png' --query Invalidation.Id
  Aws cloudfront wait invalidation-completed --distribution-id $s.cfId --id $id
  'cache vide' } else { Invoke-Ssm $s.rtrSiege $c 120 }
