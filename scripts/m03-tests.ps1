# Module 3 - Tests (preuves enregistrees dans docs/modules/m03/tests.txt)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$out = Join-Path $PSScriptRoot '..\docs\modules\m03\tests.txt'
New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null
$log = New-Object System.Collections.Generic.List[string]
function L($t) { $log.Add($t); Write-Host $t }
$ip = Aws ec2 describe-addresses --allocation-ids $s.eipWeb --query 'Addresses[0].PublicIp'
$curl = 'curl.exe'
function Ext { & $curl -sk --max-time 6 -o NUL -w "HTTP %{http_code}" "https://$ip/" 2>&1; if ($LASTEXITCODE -ne 0) { "ECHEC (code curl $LASTEXITCODE : timeout/refus)" } }

L "=== TP1 : Security Groups ==="
L "curl https depuis Internet vers web-01 : $(Ext)"
L "ping depuis Internet vers web-01 (ICMP non autorise) : $(if (Test-Connection $ip -Count 2 -Quiet -TimeoutSeconds 2) {'repond'} else {'pas de reponse (attendu)'})"
L "app-01 n'a pas d'IP publique : $(Aws ec2 describe-instances --instance-ids $($s.app) --query 'Reservations[0].Instances[0].PublicIpAddress')"

L "`n=== TP2 : SG (avec etat) vs NACL (sans etat) ==="
L "web-01 -> app-01:8080 : $((Invoke-Ssm $s.web 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
Aws ec2 delete-network-acl-entry --network-acl-id $s.naclPublic --egress --rule-number 110
Start-Sleep 5
L "NACL : regle de retour (sortie ephemere 1024-65535) retiree -> curl externe : $(Ext)"
Aws ec2 create-network-acl-entry --network-acl-id $s.naclPublic --egress --rule-number 110 --protocol 6 --cidr-block 0.0.0.0/0 --port-range "From=1024,To=65535" --rule-action allow
Start-Sleep 5
L "NACL : regle de retour retablie -> curl externe : $(Ext)"

L "`n=== TP3 : diagnostic ==="
Aws ec2 revoke-security-group-ingress --group-id $s.sgApp --protocol tcp --port 8080 --source-group $s.sgWeb | Out-Null
Start-Sleep 3
L "8080 retire de sg-app -> web-01 -> app-01:8080 : $((Invoke-Ssm $s.web 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions "IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=$($s.sgWeb),Description=API depuis sg-web}]" | Out-Null
Start-Sleep 3
L "8080 retabli -> web-01 -> app-01:8080 : $((Invoke-Ssm $s.web 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
Aws ec2 create-network-acl-entry --network-acl-id $s.naclPublic --ingress --rule-number 50 --protocol 6 --cidr-block 0.0.0.0/0 --port-range "From=443,To=443" --rule-action deny
Start-Sleep 5
L "NACL : refus explicite regle 50 (avant l'autorisation 100) -> curl externe : $(Ext)  [la regle au numero le plus bas gagne]"
Aws ec2 delete-network-acl-entry --network-acl-id $s.naclPublic --ingress --rule-number 50
Start-Sleep 5
L "refus supprime -> curl externe : $(Ext)"
$log | Set-Content $out -Encoding utf8

