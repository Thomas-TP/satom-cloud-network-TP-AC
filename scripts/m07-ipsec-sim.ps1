# Module 7 - Site-to-Site VPN SIMULE (Site-to-Site VPN, TGW et CGW sont bloques par la SCP de l'organisation)
# Tunnel IPsec IKEv2 route-based (strongSwan, interfaces xfrm) entre rtr-aws (cote VPC prod, role de la passerelle VPN AWS)
# et rtr-siege (192.168.10.0/24) ou rtr-agence (192.168.20.0/24).
# Contraintes de la plateforme partagee : quota EIP atteint -> IP publiques automatiques ; 16 vCPU pour toute la classe -> un site a la fois.
# Usage : pwsh scripts\m07-ipsec-sim.ps1 -Site siege|agence
param([ValidateSet('siege','agence')][string]$Site = 'siege', [switch]$ConfigOnly, [switch]$DevOnly)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m07\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function J($name,$obj) { $f = Join-Path $env:TEMP "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 10 -Compress)); "file://$f" }
$ubuntu = Aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id --query Parameter.Value
$cfg = @{ siege=@{cidr='192.168.10.0/24';vpc='vpcSiege';sub='subSiege';ip='192.168.10.10';ifid=11;tun='169.254.10'}; agence=@{cidr='192.168.20.0/24';vpc='vpcAgence';sub='subAgence';ip='192.168.20.10';ifid=12;tun='169.254.20'} }
$c = $cfg[$Site]; $rk = "rtr$($Site.Substring(0,1).ToUpper())$($Site.Substring(1))"   # rtrSiege / rtrAgence

# --- reseaux simules (une fois) ---
function New-Site($name,$cidr,$subCidr) {
  $v = Aws ec2 create-vpc --cidr-block $cidr --tag-specifications (Tags 'vpc' "vpc-$name-sim-TP-AC" 'prod') --query Vpc.VpcId
  Aws ec2 modify-vpc-attribute --vpc-id $v --enable-dns-hostnames
  $sub = Aws ec2 create-subnet --vpc-id $v --cidr-block $subCidr --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' "sub-$name-sim-TP-AC") --query Subnet.SubnetId
  $igw = Aws ec2 create-internet-gateway --tag-specifications (Tags 'internet-gateway' "igw-$name-sim-TP-AC") --query InternetGateway.InternetGatewayId
  Aws ec2 attach-internet-gateway --internet-gateway-id $igw --vpc-id $v
  $rt = Aws ec2 create-route-table --vpc-id $v --tag-specifications (Tags 'route-table' "rt-$name-sim-TP-AC") --query RouteTable.RouteTableId
  Aws ec2 create-route --route-table-id $rt --destination-cidr-block 0.0.0.0/0 --gateway-id $igw | Out-Null
  Aws ec2 associate-route-table --route-table-id $rt --subnet-id $sub | Out-Null
  @{vpc=$v;sub=$sub;igw=$igw}
}
if (-not $s.vpcSiege) { $x = New-Site 'siege' 192.168.10.0/24 192.168.10.0/26; $s.vpcSiege=$x.vpc; $s.subSiege=$x.sub; $s.igwSiege=$x.igw; Save-State $s }
if (-not $s.vpcAgence) { $x = New-Site 'agence' 192.168.20.0/24 192.168.20.0/26; $s.vpcAgence=$x.vpc; $s.subAgence=$x.sub; $s.igwAgence=$x.igw; Save-State $s }

# --- secret : cles pre-partagees (jamais ecrites dans un fichier du depot) ---
if (-not $s.secretArn) {
  $rnd = { -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 40 | ForEach-Object { [char]$_ }) }
  $sf = Join-Path $env:TEMP 'tpac-psk.json'; [IO.File]::WriteAllText($sf, (@{siege=(& $rnd);agence=(& $rnd)} | ConvertTo-Json -Compress))
  $s.secretArn = Aws secretsmanager create-secret --name 'Projet/SatomCloudNetwork/vpn' --description 'TP-AC cles pre-partagees IPsec (simulation)' --secret-string "file://$sf" --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' --query ARN
  Remove-Item $sf -Force
  Aws iam put-role-policy --role-name TP-AC-ec2-ssm-role --policy-name read-vpn-secret --policy-document (J 'polsec' @{Version='2012-10-17';Statement=@(@{Effect='Allow';Action='secretsmanager:GetSecretValue';Resource=$s.secretArn})})
  Save-State $s
}

function New-Sg($vpc,$name) { Aws ec2 create-security-group --group-name $name --description "TP-AC $name" --vpc-id $vpc --tag-specifications (Tags 'security-group' "sg-$name") --query GroupId }
function New-Router($subnet,$sg,$ip,$name) {
  $ni = '[{"DeviceIndex":0,"SubnetId":"' + $subnet + '","Groups":["' + $sg + '"],"PrivateIpAddress":"' + $ip + '","AssociatePublicIpAddress":true}]'
  $f = Join-Path $env:TEMP "tpac-ni-$name.json"; [IO.File]::WriteAllText($f,$ni)
  $id = Aws ec2 run-instances --image-id $ubuntu --instance-type t3.micro --iam-instance-profile Name=TP-AC-ec2-ssm-profile --network-interfaces "file://$f" --tag-specifications (Tags 'instance' $name 'prod') --query 'Instances[0].InstanceId'
  Aws ec2 wait instance-running --instance-ids $id
  Aws ec2 modify-instance-attribute --instance-id $id --no-source-dest-check
  $id
}
function Pub($id) { Aws ec2 describe-instances --instance-ids $id --query 'Reservations[0].Instances[0].PublicIpAddress' }
function IpsecRules($ip) { @("IpProtocol=udp,FromPort=500,ToPort=500,IpRanges=[{CidrIp=$ip/32,Description=IKE}]","IpProtocol=udp,FromPort=4500,ToPort=4500,IpRanges=[{CidrIp=$ip/32,Description=NAT-T}]","IpProtocol=50,IpRanges=[{CidrIp=$ip/32,Description=ESP}]") }

function Reset-IpsecRules($sg, $ip) {
  $json = & $script:aws ec2 describe-security-groups --group-ids $sg --query 'SecurityGroups[0].IpPermissions' --output json --profile TP-AC --region eu-north-1
  $old = @(($json | ConvertFrom-Json) | Where-Object { $_.IpProtocol -eq '50' -or ($_.IpProtocol -eq 'udp' -and $_.FromPort -in 500,4500) })
  if ($old.Count) { $of = Join-Path $env:TEMP "tpac-old-ipsec-$sg.json"; [IO.File]::WriteAllText($of, ($old | ConvertTo-Json -Depth 6 -AsArray)); Aws ec2 revoke-security-group-ingress --group-id $sg --ip-permissions "file://$of" | Out-Null }
  Aws ec2 authorize-security-group-ingress --group-id $sg --ip-permissions (IpsecRules $ip) | Out-Null
}
# --- routeur cote AWS (une fois) ---
if (-not $s.rtrAws) {
  $s.sgRtrAws = New-Sg $s.vpc 'rtr-aws-TP-AC'
  Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrAws --ip-permissions 'IpProtocol=-1,IpRanges=[{CidrIp=10.20.0.0/22,Description=trafic VPC vers les sites}]' | Out-Null
  $s.rtrAws = New-Router $s.subPublic1b $s.sgRtrAws '10.20.0.74' 'rtr-aws-TP-AC'
  $s.eniRtrAws = Aws ec2 describe-instances --instance-ids $s.rtrAws --query 'Reservations[0].Instances[0].NetworkInterfaces[0].NetworkInterfaceId'
  Save-State $s
}
if ($ConfigOnly) {
  $startIds = @($s.rtrAws, $s[$rk]); if ($DevOnly) { $startIds += $s.dev }
  Aws ec2 start-instances --instance-ids $startIds | Out-Null
  Aws ec2 wait instance-running --instance-ids $startIds
}
$s.pubAws = Pub $s.rtrAws

# --- routeur du site demande ---
$sgKey = "sg$($rk.Substring(0,1).ToUpper())$($rk.Substring(1))"
if ($ConfigOnly) { $pubSite = Pub $s[$rk]; $s.pubSite = $pubSite; Reset-IpsecRules $s[$sgKey] $s.pubAws; Reset-IpsecRules $s.sgRtrAws $pubSite; Save-State $s } else {
$s[$sgKey] = New-Sg $s[$c.vpc] "rtr-$Site-TP-AC"
$s[$rk] = New-Router $s[$c.sub] $s[$sgKey] $c.ip "rtr-$Site-TP-AC"
$pubSite = Pub $s[$rk]
Aws ec2 authorize-security-group-ingress --group-id $s[$sgKey] --ip-permissions (IpsecRules $s.pubAws) | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgRtrAws --ip-permissions (IpsecRules $pubSite) | Out-Null
& $script:aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block $c.cidr --network-interface-id $s.eniRtrAws --profile TP-AC --region eu-north-1 2>&1 | Out-Null
if ($Site -eq 'siege') {
  Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions 'IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges=[{CidrIp=192.168.10.0/24,Description=ping siege}]' 'IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=192.168.10.0/24,Description=API siege}]' | Out-Null
} else {
  Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions 'IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=192.168.20.0/24,Description=API agence}]' | Out-Null
}
$s.pubSite = $pubSite; Save-State $s
}
foreach ($i in $s.rtrAws,$s[$rk]) { "$i SSM: $(Wait-Ssm $i 420)" }; if ($DevOnly) { "dev-01 SSM: $(Wait-Ssm $s.dev 420)" }

# --- configuration strongSwan (route-based, interfaces xfrm) ---
$common = @'
set -e
export PATH=$PATH:/snap/bin
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq strongswan-swanctl charon-systemd >/dev/null
snap list aws-cli >/dev/null 2>&1 || snap install aws-cli --classic >/dev/null
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-tpac.conf; sysctl -p /etc/sysctl.d/99-tpac.conf >/dev/null
PSK_JSON=$(aws secretsmanager get-secret-value --secret-id Projet/SatomCloudNetwork/vpn --region eu-north-1 --query SecretString --output text)
'@
function Conf($localId,$remoteId,$localPriv,$tunLocal,$route) {
@"
$common
PSK=`$(echo "`$PSK_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['$Site'])")
cat > /etc/swanctl/conf.d/$Site.conf <<EOC
connections {
  $Site {
    version = 2
    local_addrs = $localPriv
    remote_addrs = $remoteId
    local {
      auth = psk
      id = $localId
    }
    remote {
      auth = psk
      id = $remoteId
    }
    proposals = aes256-sha256-modp2048
    dpd_delay = 10s
    children {
      $Site {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        esp_proposals = aes256-sha256-modp2048
        if_id_in = $($c.ifid)
        if_id_out = $($c.ifid)
        start_action = start
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-$Site {
    id = $remoteId
    secret = "`$PSK"
  }
}
EOC
chmod 600 /etc/swanctl/conf.d/$Site.conf
ip link del xfrm-$Site 2>/dev/null || true
ip link add xfrm-$Site type xfrm dev `$(ip -o -4 route show to default | awk '{print `$5}') if_id $($c.ifid)
ip addr add $tunLocal/30 dev xfrm-$Site; ip link set xfrm-$Site up
systemctl enable --now strongswan >/dev/null 2>&1; systemctl restart strongswan; sleep 3; swanctl --load-all >/dev/null
ip route replace $route dev xfrm-$Site metric 200
sleep 8; swanctl --list-sas 2>/dev/null | head -14
"@
}
$t = $c.tun
$awsOut  = (Invoke-Ssm $s.rtrAws (Conf $s.pubAws $pubSite '10.20.0.74' "$t.1" $c.cidr) 360) -join "`n"
$siteOut = (Invoke-Ssm $s[$rk] (Conf $pubSite $s.pubAws $c.ip "$t.2" '10.20.0.0/22') 360) -join "`n"

L "=== Module 7 - tunnel IPsec $Site (simulation strongSwan) ==="
L "rtr-aws : swanctl --list-sas`n$awsOut"
L "rtr-${Site} : swanctl --list-sas`n$siteOut"
function Run($id,$cmd) { ((Invoke-Ssm $id $cmd 60) -join "`n") }
if ($DevOnly) { L "(mode DevOnly : app-01 arretee, seuls l'etat du tunnel et le test dev-01 sont executes)" } elseif ($Site -eq 'siege') {
  L "siege -> app-01 (10.20.1.10) ping : `n$(Run $s[$rk] 'ping -c 3 -I 192.168.10.10 10.20.1.10 | tail -3')"
  L "siege -> app-01:8080 : $(Run $s[$rk] 'curl -s -m 5 --interface 192.168.10.10 http://10.20.1.10:8080/api/health || echo ECHEC')"
} else {
  L "agence -> app-01 ping (ICMP non autorise pour l'agence) : `n$(Run $s[$rk] 'ping -c 2 -W 2 -I 192.168.20.10 10.20.1.10 | tail -2; echo exit=$?')"
  L "agence -> app-01:8080 (seul flux autorise) : $(Run $s[$rk] 'curl -s -m 5 --interface 192.168.20.10 http://10.20.1.10:8080/api/health || echo ECHEC')"
}
$devPing = if ($s.dev) { Aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$($s.dev)" --query 'InstanceInformationList[0].PingStatus' } else { 'inconnu' }
L "$Site -> dev-01 (10.21.0.10), dev-01 en cours d'execution (SSM : $devPing) : $(Run $s[$rk] "ping -c 3 -W 2 -I $($c.ip) 10.21.0.10 | tail -2; echo code retour=`$?")  (le tunnel ne contient que 10.20.0.0/22)"
$log | Add-Content $outFile -Encoding utf8
$s | ConvertTo-Json


