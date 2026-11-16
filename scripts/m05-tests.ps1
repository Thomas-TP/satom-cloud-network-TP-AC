# Module 5 - Tests du peering (preuves dans docs/modules/m05/tests.txt)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m05\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$ami = Aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value
if (-not $s.dev) { $s.dev = Aws ec2 describe-instances --filters "Name=tag:Name,Values=dev-01-TP-AC" "Name=instance-state-name,Values=running,pending" --query 'Reservations[0].Instances[0].InstanceId'; Save-State $s }
L "dev-01 SSM en ligne : $(Wait-Ssm $s.dev 300)"

L "=== TP2 : peering pcx-lab (prod <-> dev) ==="
L "dev-01 -> app-01:8080 : $((Invoke-Ssm $s.dev 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
L "dev-01 -> app-01:22 (non ouvert depuis dev) : $((Invoke-Ssm $s.dev 'timeout 4 bash -c ''</dev/tcp/10.20.1.10/22'' && echo OUVERT || echo FERME' 20) -join ' ')"

L "`n=== TP3 : limites du peering ==="
# 1. CIDR chevauchant : la demande est creee puis refusee a l'acceptation
$ov = Aws ec2 create-vpc --cidr-block 10.20.0.0/24 --tag-specifications (Tags 'vpc' 'vpc-test-chevauchement-TP-AC' 'dev') --query Vpc.VpcId
$pc = Aws ec2 create-vpc-peering-connection --vpc-id $ov --peer-vpc-id $s.vpc --query VpcPeeringConnection.VpcPeeringConnectionId
$r = & $script:aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $pc --profile TP-AC --region eu-north-1 2>&1 | Out-String
L "Acceptation du peering avec un VPC en 10.20.0.0/24 (chevauche 10.20.0.0/22) -> $($r.Trim() -replace '\s+',' ')"
Aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $pc 2>&1 | Out-Null
Start-Sleep 5; Aws ec2 delete-vpc --vpc-id $ov

# 2. Non-transitivite
$v3 = Aws ec2 create-vpc --cidr-block 10.22.0.0/24 --tag-specifications (Tags 'vpc' 'vpc-test-tiers-TP-AC' 'dev') --query Vpc.VpcId
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
Aws ec2 wait instance-running --instance-ids $i3; Start-Sleep 20
L "app-01 (prod, peering direct) -> tiers-01 10.22.0.10 : $((Invoke-Ssm $s.app 'ping -c 2 -W 2 10.22.0.10 | tail -2' 30) -join ' ')"
L "dev-01 (via prod = transit, NON transitif) -> tiers-01 10.22.0.10 : $((Invoke-Ssm $s.dev 'ping -c 2 -W 2 10.22.0.10 | tail -2; echo exit=$?' 30) -join ' ')"
$log | Set-Content $outFile -Encoding utf8
# nettoyage des ressources de test
Aws ec2 terminate-instances --instance-ids $i3 | Out-Null; Aws ec2 wait instance-terminated --instance-ids $i3
Aws ec2 delete-route --route-table-id $s.rtPrive --destination-cidr-block 10.22.0.0/24
Aws ec2 delete-route --route-table-id $s.rtDev --destination-cidr-block 10.22.0.0/24
Aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $pcx3 | Out-Null
Start-Sleep 5; Aws ec2 delete-subnet --subnet-id $sub3; Aws ec2 delete-security-group --group-id $sg3; Aws ec2 delete-vpc --vpc-id $v3
"tests termines"
