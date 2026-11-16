# Module 5 - VPC Peering prod <-> dev (TP-AC)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m05\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$tmpDir = $env:TEMP
$ami = Aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value

function New-LabVpc($cidr, $name, $env) {
  $v = Aws ec2 create-vpc --cidr-block $cidr --tag-specifications (Tags 'vpc' $name $env) --query Vpc.VpcId
  Aws ec2 modify-vpc-attribute --vpc-id $v --enable-dns-hostnames
  $v
}

# TP1 : VPC dev, sous-reseau, IGW (acces SSM sans NAT), dev-01
$s.vpcDev = New-LabVpc 10.21.0.0/24 'vpc-dev-leman-TP-AC' 'dev'
$s.subDev = Aws ec2 create-subnet --vpc-id $s.vpcDev --cidr-block 10.21.0.0/26 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-dev-1a-TP-AC' 'dev') --query Subnet.SubnetId
$s.igwDev = Aws ec2 create-internet-gateway --tag-specifications (Tags 'internet-gateway' 'igw-dev-leman-TP-AC' 'dev') --query InternetGateway.InternetGatewayId
Aws ec2 attach-internet-gateway --internet-gateway-id $s.igwDev --vpc-id $s.vpcDev
$s.rtDev = Aws ec2 create-route-table --vpc-id $s.vpcDev --tag-specifications (Tags 'route-table' 'rt-dev-leman-TP-AC' 'dev') --query RouteTable.RouteTableId
Aws ec2 create-route --route-table-id $s.rtDev --destination-cidr-block 0.0.0.0/0 --gateway-id $s.igwDev | Out-Null
Aws ec2 associate-route-table --route-table-id $s.rtDev --subnet-id $s.subDev | Out-Null
$s.sgDev = Aws ec2 create-security-group --group-name dev-TP-AC --description 'TP-AC dev (aucune entree)' --vpc-id $s.vpcDev --tag-specifications (Tags 'security-group' 'sg-dev-TP-AC' 'dev') --query GroupId
$ni = '[{"DeviceIndex":0,"SubnetId":"' + $s.subDev + '","Groups":["' + $s.sgDev + '"],"PrivateIpAddress":"10.21.0.10","AssociatePublicIpAddress":true}]'
$nif = Join-Path $tmpDir 'ni-tpac.json'; [IO.File]::WriteAllText($nif, $ni)
$s.dev = Aws ec2 run-instances --image-id $ami --instance-type t3.micro --iam-instance-profile Name=TP-AC-ec2-ssm-profile --network-interfaces "file://$nif" --tag-specifications (Tags 'instance' 'dev-01-TP-AC' 'dev') --query 'Instances[0].InstanceId'
Save-State $s

# TP2 : peering pcx-lab
$s.pcx = Aws ec2 create-vpc-peering-connection --vpc-id $s.vpc --peer-vpc-id $s.vpcDev --tag-specifications (Tags 'vpc-peering-connection' 'pcx-lab-TP-AC') --query VpcPeeringConnection.VpcPeeringConnectionId
Aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $s.pcx | Out-Null
Aws ec2 create-route --route-table-id $s.rtDev   --destination-cidr-block 10.20.0.0/22 --vpc-peering-connection-id $s.pcx | Out-Null
Aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block 10.21.0.0/24 --vpc-peering-connection-id $s.pcx | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions 'IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=10.21.0.0/24,Description=API depuis dev}]' | Out-Null
Save-State $s
Aws ec2 wait instance-running --instance-ids $s.dev
"dev-01 SSM: $(Wait-Ssm $s.dev 300)"
L "=== TP2 : peering ==="
L "dev-01 -> app-01:8080 : $((Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
L "dev-01 -> app-01:22 (non ouvert depuis dev) : $((Invoke-Ssm $s.dev 'timeout 4 bash -c ''</dev/tcp/10.20.1.10/22'' && echo OUVERT || echo FERME' 20) -join ' ')"

# TP3 : refus attendus
L "`n=== TP3 : limites du peering ==="
$ov = New-LabVpc 10.20.0.0/24 'vpc-test-chevauchement-TP-AC' 'dev'
$r = & $script:aws ec2 create-vpc-peering-connection --vpc-id $ov --peer-vpc-id $s.vpc --profile TP-AC --region eu-north-1 2>&1 | Out-String
L "Peering avec un VPC au CIDR chevauchant 10.20.0.0/22 -> $($r.Trim())"
Aws ec2 delete-vpc --vpc-id $ov

# non-transitivite : 3e VPC relie uniquement a la prod
$v3 = New-LabVpc 10.22.0.0/24 'vpc-test-tiers-TP-AC' 'dev'
$sub3 = Aws ec2 create-subnet --vpc-id $v3 --cidr-block 10.22.0.0/26 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-test-tiers-TP-AC' 'dev') --query Subnet.SubnetId
$sg3 = Aws ec2 create-security-group --group-name tiers-TP-AC --description 'TP-AC tiers' --vpc-id $v3 --query GroupId
Aws ec2 authorize-security-group-ingress --group-id $sg3 --ip-permissions 'IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges=[{CidrIp=10.0.0.0/8}]' | Out-Null
$i3 = Aws ec2 run-instances --image-id $ami --instance-type t3.micro --subnet-id $sub3 --private-ip-address 10.22.0.10 --security-group-ids $sg3 --tag-specifications (Tags 'instance' 'tiers-01-TP-AC' 'dev') --query 'Instances[0].InstanceId'
$pcx3 = Aws ec2 create-vpc-peering-connection --vpc-id $s.vpc --peer-vpc-id $v3 --query VpcPeeringConnection.VpcPeeringConnectionId
Aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $pcx3 | Out-Null
$rt3 = Aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$v3" --query 'RouteTables[0].RouteTableId'
Aws ec2 create-route --route-table-id $rt3 --destination-cidr-block 10.20.0.0/22 --vpc-peering-connection-id $pcx3 | Out-Null
Aws ec2 create-route --route-table-id $rt3 --destination-cidr-block 10.21.0.0/24 --vpc-peering-connection-id $pcx3 | Out-Null
Aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block 10.22.0.0/24 --vpc-peering-connection-id $pcx3 | Out-Null
Aws ec2 create-route --route-table-id $s.rtDev   --destination-cidr-block 10.22.0.0/24 --vpc-peering-connection-id $s.pcx | Out-Null
Aws ec2 wait instance-running --instance-ids $i3
Start-Sleep 20
L "app-01 (prod, peering direct) -> tiers-01 10.22.0.10 : $((Invoke-Ssm $s.app 'ping -c 2 -W 2 10.22.0.10 | tail -2' 30) -join ' ')"
L "dev-01 (via prod, NON transitif) -> tiers-01 10.22.0.10 : $((Invoke-Ssm $s.dev 'ping -c 2 -W 2 10.22.0.10 | tail -2' 30) -join ' ')"
$log | Set-Content $outFile -Encoding utf8
# nettoyage des ressources de test
Aws ec2 terminate-instances --instance-ids $i3 | Out-Null
Aws ec2 wait instance-terminated --instance-ids $i3
Aws ec2 delete-route --route-table-id $s.rtPrive --destination-cidr-block 10.22.0.0/24
Aws ec2 delete-route --route-table-id $s.rtDev --destination-cidr-block 10.22.0.0/24
Aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $pcx3 | Out-Null
Start-Sleep 5
Aws ec2 delete-subnet --subnet-id $sub3; Aws ec2 delete-security-group --group-id $sg3; Aws ec2 delete-vpc --vpc-id $v3
$s | ConvertTo-Json
