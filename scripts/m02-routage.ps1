# Module 2 - Routage : IGW, NAT, tables de routage (TP-AC)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State

# TP1 : IGW + table publique + IP publique pour web-01
$s.igw = Aws ec2 create-internet-gateway --tag-specifications (Tags 'internet-gateway' 'igw-prod-leman-TP-AC') --query InternetGateway.InternetGatewayId
Aws ec2 attach-internet-gateway --internet-gateway-id $s.igw --vpc-id $s.vpc
$s.rtPublic = Aws ec2 create-route-table --vpc-id $s.vpc --tag-specifications (Tags 'route-table' 'rt-public-leman-TP-AC') --query RouteTable.RouteTableId
Aws ec2 create-route --route-table-id $s.rtPublic --destination-cidr-block 0.0.0.0/0 --gateway-id $s.igw | Out-Null
Aws ec2 associate-route-table --route-table-id $s.rtPublic --subnet-id $s.subPublic | Out-Null
$s.eipWeb = Aws ec2 allocate-address --domain vpc --tag-specifications (Tags 'elastic-ip' 'eip-web-01-TP-AC') --query AllocationId
Aws ec2 associate-address --allocation-id $s.eipWeb --instance-id $s.web | Out-Null
Save-State $s

# TP2 : EIP + NAT + table privee
$s.eipNat = Aws ec2 allocate-address --domain vpc --tag-specifications (Tags 'elastic-ip' 'eip-nat-TP-AC') --query AllocationId
$s.nat = Aws ec2 create-nat-gateway --subnet-id $s.subPublic --allocation-id $s.eipNat --tag-specifications (Tags 'natgateway' 'nat-prod-leman-TP-AC') --query NatGateway.NatGatewayId
Aws ec2 wait nat-gateway-available --nat-gateway-ids $s.nat
$s.rtPrive = Aws ec2 create-route-table --vpc-id $s.vpc --tag-specifications (Tags 'route-table' 'rt-prive-leman-TP-AC') --query RouteTable.RouteTableId
Aws ec2 create-route --route-table-id $s.rtPrive --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $s.nat | Out-Null
Aws ec2 associate-route-table --route-table-id $s.rtPrive --subnet-id $s.subPrive | Out-Null
Save-State $s
$s | ConvertTo-Json
