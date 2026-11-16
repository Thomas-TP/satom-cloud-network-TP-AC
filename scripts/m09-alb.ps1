# Module 9 - Elastic Load Balancing (TP-AC)  [ALB facture a l'heure]
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m09\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }

# TP1 : 2e sous-reseau public (eu-north-1b), groupes cibles, enregistrement des cibles
if (-not $s.sgAlb) {
$s.subPublic1b = Aws ec2 create-subnet --vpc-id $s.vpc --cidr-block 10.20.0.64/26 --availability-zone eu-north-1b --tag-specifications (Tags 'subnet' 'sub-public-1b-TP-AC') --query Subnet.SubnetId
Aws ec2 associate-route-table --route-table-id $s.rtPublic --subnet-id $s.subPublic1b | Out-Null
$s.sgAlb = Aws ec2 create-security-group --group-name alb-TP-AC --description 'TP-AC ALB' --vpc-id $s.vpc --tag-specifications (Tags 'security-group' 'sg-alb-TP-AC') --query GroupId
Aws ec2 authorize-security-group-ingress --group-id $s.sgAlb --ip-permissions 'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTPS public}]' | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgWeb --ip-permissions "IpProtocol=tcp,FromPort=80,ToPort=80,UserIdGroupPairs=[{GroupId=$($s.sgAlb),Description=HTTP depuis ALB}]" | Out-Null
Aws ec2 authorize-security-group-ingress --group-id $s.sgApp --ip-permissions "IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=$($s.sgAlb),Description=API depuis ALB}]" | Out-Null
}
$s.tgWeb = Aws elbv2 create-target-group --name tg-web-TP-AC --protocol HTTP --port 80 --vpc-id $s.vpc --health-check-path /health --health-check-interval-seconds 10 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' --query 'TargetGroups[0].TargetGroupArn'
$s.tgApp = Aws elbv2 create-target-group --name tg-app-TP-AC --protocol HTTP --port 8080 --vpc-id $s.vpc --health-check-path /api/health --health-check-interval-seconds 10 --healthy-threshold-count 2 --unhealthy-threshold-count 2 --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' --query 'TargetGroups[0].TargetGroupArn'
Aws elbv2 register-targets --target-group-arn $s.tgWeb --targets "Id=$($s.web)"
Aws elbv2 register-targets --target-group-arn $s.tgApp --targets "Id=$($s.app)"
Save-State $s

# Certificat auto-signe importe dans ACM (pas de domaine reel : on n'achete rien)
$ossl = 'C:\Program Files\Git\usr\bin\openssl.exe'
$cd = Join-Path $env:TEMP 'tpac-cert'; New-Item -ItemType Directory -Force $cd | Out-Null
& $ossl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout "$cd\k.pem" -out "$cd\c.pem" -subj '/CN=portefeuilles.leman-finance.example' -addext 'subjectAltName=DNS:portefeuilles.leman-finance.example' 2>$null
$s.cert = Aws acm import-certificate --certificate "fileb://$cd\c.pem" --private-key "fileb://$cd\k.pem" --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' 'Key=Name,Value=cert-autosigne-TP-AC' --query CertificateArn
Remove-Item $cd -Recurse -Force   # la cle privee ne reste jamais sur le disque

# TP2 : ALB + listener HTTPS + regle /api/*
$s.alb = Aws elbv2 create-load-balancer --name alb-prod-leman-TP-AC --type application --scheme internet-facing --subnets $s.subPublic $s.subPublic1b --security-groups $s.sgAlb --tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC' --query 'LoadBalancers[0].LoadBalancerArn'
Aws elbv2 wait load-balancer-available --load-balancer-arns $s.alb
$s.albDns = Aws elbv2 describe-load-balancers --load-balancer-arns $s.alb --query 'LoadBalancers[0].DNSName'
$s.listener = Aws elbv2 create-listener --load-balancer-arn $s.alb --protocol HTTPS --port 443 --certificates "CertificateArn=$($s.cert)" --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 --default-actions "Type=forward,TargetGroupArn=$($s.tgWeb)" --query 'Listeners[0].ListenerArn'
Aws elbv2 create-rule --listener-arn $s.listener --priority 10 --conditions 'Field=path-pattern,Values=/api/*' --actions "Type=forward,TargetGroupArn=$($s.tgApp)" | Out-Null
Save-State $s

function Health($arn) { Aws elbv2 describe-target-health --target-group-arn $arn --query 'TargetHealthDescriptions[0].TargetHealth.State' }
function WaitHealthy($arn,$t=180) { for($i=0;$i -lt $t/5;$i++){ if((Health $arn) -eq 'healthy'){return 'healthy'}; Start-Sleep 5 }; Health $arn }
function Curl($path) { $o = & curl.exe -sk --max-time 8 -w ' [HTTP %{http_code}]' "https://$($s.albDns)$path" 2>&1; if ($LASTEXITCODE -ne 0) { "ECHEC (curl $LASTEXITCODE)" } else { ($o -join ' ').Trim() } }

L "=== TP1/TP2 ==="
L "tg-web : $(WaitHealthy $s.tgWeb)   tg-app : $(WaitHealthy $s.tgApp)"
Start-Sleep 20
L "curl https://ALB/            -> $(Curl '/')"
L "curl https://ALB/api/health  -> $(Curl '/api/health')"

L "`n=== TP3 : pannes ==="
Invoke-Ssm $s.web 'systemctl stop nginx' 30 | Out-Null
Start-Sleep 35
L "nginx arrete sur web-01 : tg-web = $(Health $s.tgWeb) ; curl https://ALB/ -> $(Curl '/')"
Invoke-Ssm $s.web 'systemctl start nginx' 30 | Out-Null
L "nginx relance : tg-web = $(WaitHealthy $s.tgWeb)"
Start-Sleep 10
L "curl https://ALB/ -> $(Curl '/')"
Aws ec2 revoke-security-group-ingress --group-id $s.sgAlb --protocol tcp --port 443 --cidr 0.0.0.0/0 | Out-Null
Start-Sleep 5
L "443 ferme dans sg-alb -> curl https://ALB/ -> $(Curl '/')"
Aws ec2 authorize-security-group-ingress --group-id $s.sgAlb --ip-permissions 'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTPS public}]' | Out-Null
Start-Sleep 5
L "443 retabli -> curl https://ALB/ -> $(Curl '/')"
$log | Set-Content $outFile -Encoding utf8
$s | ConvertTo-Json

