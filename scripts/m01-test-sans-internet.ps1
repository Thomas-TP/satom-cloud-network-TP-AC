# Module 1 - Test reel : une instance d'un sous-reseau prive SANS route par defaut ne joint pas Internet.
# Pas d'acces SSM possible sans Internet : le resultat est lu dans la console serie de l'instance (user-data -> /dev/console).
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m01\tests.txt'
$ami = Aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value
$sub = Aws ec2 create-subnet --vpc-id $s.vpc --cidr-block 10.20.3.0/26 --availability-zone eu-north-1a --tag-specifications (Tags 'subnet' 'sub-test-isole-TP-AC') --query Subnet.SubnetId
$rt  = Aws ec2 create-route-table --vpc-id $s.vpc --tag-specifications (Tags 'route-table' 'rt-test-isole-TP-AC') --query RouteTable.RouteTableId
Aws ec2 associate-route-table --route-table-id $rt --subnet-id $sub | Out-Null
$ud = @'
#!/bin/bash
exec > /dev/console 2>&1
sleep 25
echo "TPAC-TEST table de routage :"; ip route
echo "TPAC-TEST ping 8.8.8.8 :"; ping -c 3 -W 2 8.8.8.8; echo "code retour ping = $?"
echo "TPAC-TEST curl :"; curl -s -m 6 https://checkip.amazonaws.com; echo "code retour curl = $?"
echo "TPAC-TEST-FIN"
'@
$udf = Join-Path $env:TEMP 'tpac-ud.sh'; [IO.File]::WriteAllText($udf, $ud.Replace("`r`n","`n"))
$id = Aws ec2 run-instances --image-id $ami --instance-type t3.micro --subnet-id $sub --user-data "file://$udf" --tag-specifications (Tags 'instance' 'test-isole-TP-AC') --query 'Instances[0].InstanceId'
Aws ec2 wait instance-running --instance-ids $id
$out = ''
for ($i = 0; $i -lt 24; $i++) { Start-Sleep 10; $out = Aws ec2 get-console-output --instance-id $id --latest --query Output; if ($out -match 'TPAC-TEST-FIN') { break } }
$res = ($out -split "`n" | Where-Object { $_ -match 'TPAC-TEST|^default|^10\.|packet loss|exit|retour|^From|ping:|curl' } | ForEach-Object { ($_ -replace '^\S*\[\s*[\d\.]+\]\s*','').Trim() }) -join "`n  "
Aws ec2 terminate-instances --instance-ids $id | Out-Null
Aws ec2 wait instance-terminated --instance-ids $id
Aws ec2 disassociate-route-table --association-id (Aws ec2 describe-route-tables --route-table-ids $rt --query 'RouteTables[0].Associations[0].RouteTableAssociationId') | Out-Null
Aws ec2 delete-route-table --route-table-id $rt | Out-Null; Aws ec2 delete-subnet --subnet-id $sub | Out-Null
$t = Get-Content $outFile -Raw
$new = "TEST REEL (instance de test sans route par defaut, sous-reseau prive 10.20.3.0/26, resultat lu dans la console serie) :`n  $res"
$t = $t -replace "(?m)^app-01 -> Internet avant IGW/NAT : NON TESTE.*$", $new
Set-Content $outFile $t -Encoding utf8
$res
