# Module 1 - VPC et sous-reseaux (equipe TP-AC) - region eu-north-1
# Usage : powershell -File scripts\m01-vpc.ps1   (profil AWS CLI : TP-AC)
$ErrorActionPreference = 'Stop'
$aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
$p = @('--profile','TP-AC','--region','eu-north-1','--output','text')
$state = Join-Path $PSScriptRoot 'state.json'
$s = if (Test-Path $state) { Get-Content $state | ConvertFrom-Json -AsHashtable } else { @{} }
function Tags($type,$name,$env='prod') { "ResourceType=$type,Tags=[{Key=Name,Value=$name},{Key=Projet,Value=SatomCloudNetwork},{Key=Equipe,Value=TP-AC},{Key=Environnement,Value=$env}]" }
function Save { $s | ConvertTo-Json | Set-Content $state }

# 1. VPC + sous-reseaux
$s.vpc = & $aws ec2 create-vpc --cidr-block 10.20.0.0/22 --tag-specifications (Tags 'vpc' 'vpc-prod-leman-TP-AC') @p --query Vpc.VpcId
& $aws ec2 modify-vpc-attribute --vpc-id $s.vpc --enable-dns-hostnames @p
$s.subPublic = & $aws ec2 create-subnet --vpc-id $s.vpc --cidr-block 10.20.0.0/26 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-public-1a-TP-AC') @p --query Subnet.SubnetId
$s.subPrive  = & $aws ec2 create-subnet --vpc-id $s.vpc --cidr-block 10.20.1.0/26 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-prive-1a-TP-AC') @p --query Subnet.SubnetId
Save

# 2. Role SSM pour administrer les instances sans SSH ni cle
$trust = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
$tf = Join-Path $env:TEMP 'trust-ec2-tpac.json'; [IO.File]::WriteAllText($tf,$trust)
& $aws iam create-role --role-name TP-AC-ec2-ssm-role --assume-role-policy-document "file://$tf" --tags Key=Equipe,Value=TP-AC @p | Out-Null
& $aws iam attach-role-policy --role-name TP-AC-ec2-ssm-role --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore @p
& $aws iam create-instance-profile --instance-profile-name TP-AC-ec2-ssm-profile @p | Out-Null
& $aws iam add-role-to-instance-profile --instance-profile-name TP-AC-ec2-ssm-profile --role-name TP-AC-ec2-ssm-role @p
Start-Sleep 15

# 3. Instances web-01 (public) et app-01 (prive), IP fixes
$ami = & $aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 @p --query Parameter.Value
$s.web = & $aws ec2 run-instances --image-id $ami --instance-type t3.micro --subnet-id $s.subPublic --private-ip-address 10.20.0.10 --iam-instance-profile Name=TP-AC-ec2-ssm-profile --tag-specifications (Tags 'instance' 'web-01-TP-AC') @p --query 'Instances[0].InstanceId'
$s.app = & $aws ec2 run-instances --image-id $ami --instance-type t3.micro --subnet-id $s.subPrive  --private-ip-address 10.20.1.10 --iam-instance-profile Name=TP-AC-ec2-ssm-profile --tag-specifications (Tags 'instance' 'app-01-TP-AC') @p --query 'Instances[0].InstanceId'
Save
& $aws ec2 wait instance-running --instance-ids $s.web $s.app @p
$s | ConvertTo-Json
