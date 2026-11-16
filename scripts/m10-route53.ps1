# Module 10 - Route 53 : zone privee, zone publique, failover (TP-AC)
# NB : pas de domaine reel -> pas de delegation NS. Les reponses DNS sont verifiees avec "test-dns-answer"
#      et avec dig directement sur les serveurs de noms de la zone.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m10\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function J($name,$obj) { $f = Join-Path $env:TEMP "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 10 -Compress)); "file://$f" }
function Rec($name,$ip) { @{Action='UPSERT';ResourceRecordSet=@{Name=$name;Type='A';TTL=60;ResourceRecords=@(@{Value=$ip})}} }

# TP1 : zone privee
$s.zonePriv = (Aws route53 create-hosted-zone --name prod.leman.internal --caller-reference "tpac-priv-$(Get-Random)" --vpc "VPCRegion=eu-north-1,VPCId=$($s.vpc)" --hosted-zone-config 'Comment=TP-AC zone privee,PrivateZone=true' --query 'HostedZone.Id').Split('/')[-1]
Aws route53 change-tags-for-resource --resource-type hostedzone --resource-id $s.zonePriv --add-tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC'
Aws route53 change-resource-record-sets --hosted-zone-id $s.zonePriv --change-batch (J 'priv' @{Changes=@((Rec 'web.prod.leman.internal' '10.20.0.10'),(Rec 'app.prod.leman.internal' '10.20.1.10'))}) | Out-Null
Save-State $s
L "=== TP1 : zone privee prod.leman.internal ==="
L "dig web-01 -> app.prod.leman.internal : $((Invoke-Ssm $s.web 'getent hosts app.prod.leman.internal; getent hosts web.prod.leman.internal' 40) -join ' ')"

# TP2 : zone publique + alias vers l'ALB
$s.zonePub = (Aws route53 create-hosted-zone --name leman-finance.example --caller-reference "tpac-pub-$(Get-Random)" --hosted-zone-config 'Comment=TP-AC zone publique (domaine fictif)' --query 'HostedZone.Id').Split('/')[-1]
Aws route53 change-tags-for-resource --resource-type hostedzone --resource-id $s.zonePub --add-tags 'Key=Projet,Value=SatomCloudNetwork' 'Key=Equipe,Value=TP-AC'
$albZone = Aws elbv2 describe-load-balancers --load-balancer-arns $s.alb --query 'LoadBalancers[0].CanonicalHostedZoneId'
$alias = @{Action='UPSERT';ResourceRecordSet=@{Name='portefeuilles.leman-finance.example';Type='A';AliasTarget=@{HostedZoneId=$albZone;DNSName=$s.albDns;EvaluateTargetHealth=$true}}}
Aws route53 change-resource-record-sets --hosted-zone-id $s.zonePub --change-batch (J 'pub' @{Changes=@($alias)}) | Out-Null
Save-State $s
$ns = (Aws route53 get-hosted-zone --id $s.zonePub --query 'DelegationSet.NameServers') -split '\s+'
L "`n=== TP2 : zone publique leman-finance.example ==="
L "Serveurs NS a reporter chez le bureau d'enregistrement : $($ns -join ', ')"
$ans = Aws route53 test-dns-answer --hosted-zone-id $s.zonePub --record-name portefeuilles.leman-finance.example --record-type A --query '[ResponseCode,RecordData]'
L "test-dns-answer portefeuilles.leman-finance.example -> $ans"
# dig direct sur un serveur de noms de la zone (Resolve-DnsName, sans delegation)
$ips = @(Resolve-DnsName portefeuilles.leman-finance.example -Server $ns[0] -Type A -DnsOnly -ErrorAction SilentlyContinue | Where-Object Type -eq 'A' | ForEach-Object IPAddress)
L "Resolve-DnsName @$($ns[0]) -> $($ips -join ', ')"
if ($ips) { L "curl https://portefeuilles.leman-finance.example/ (resolution forcee vers l'ALB) -> $(& curl.exe -sk --max-time 8 --resolve "portefeuilles.leman-finance.example:443:$($ips[0])" https://portefeuilles.leman-finance.example/)" }

# TP3 : health check + failover
$hc = @{Type='HTTPS';FullyQualifiedDomainName=$s.albDns;Port=443;ResourcePath='/health';RequestInterval=10;FailureThreshold=2;EnableSNI=$true}
$s.hc = Aws route53 create-health-check --caller-reference "tpac-hc-$(Get-Random)" --health-check-config (J 'hc' $hc) --query 'HealthCheck.Id'
Aws route53 change-tags-for-resource --resource-type healthcheck --resource-id $s.hc --add-tags 'Key=Name,Value=hc-portail-TP-AC' 'Key=Equipe,Value=TP-AC'
$prim = @{Action='UPSERT';ResourceRecordSet=@{Name='portefeuilles.leman-finance.example';Type='A';SetIdentifier='primaire-alb';Failover='PRIMARY';HealthCheckId=$s.hc;AliasTarget=@{HostedZoneId=$albZone;DNSName=$s.albDns;EvaluateTargetHealth=$true}}}
$sec  = @{Action='UPSERT';ResourceRecordSet=@{Name='portefeuilles.leman-finance.example';Type='A';SetIdentifier='secondaire-statique';Failover='SECONDARY';TTL=60;ResourceRecords=@(@{Value='203.0.113.50'})}}
$del  = @{Action='DELETE';ResourceRecordSet=$alias.ResourceRecordSet}
Aws route53 change-resource-record-sets --hosted-zone-id $s.zonePub --change-batch (J 'fo' @{Changes=@($del,$prim,$sec)}) | Out-Null
Save-State $s
function HcState { Aws route53 get-health-check-status --health-check-id $s.hc --query 'HealthCheckObservations[].StatusReport.Status' | ForEach-Object { ($_ -split '\s+' | Select-Object -First 1) } }
function Ans { Aws route53 test-dns-answer --hosted-zone-id $s.zonePub --record-name portefeuilles.leman-finance.example --record-type A --query 'RecordData' }
Start-Sleep 60
L "`n=== TP3 : failover ==="
L "Etat nominal -> reponse DNS : $(Ans)  (ALB = primaire)"
Invoke-Ssm $s.web 'systemctl stop nginx' 30 | Out-Null
$t0 = Get-Date
do { Start-Sleep 10; $a = Ans } while ($a -match 'ALB|elb|\d+\.\d+\.\d+\.\d+' -and $a -notmatch '203\.0\.113\.50' -and ((Get-Date) - $t0).TotalSeconds -lt 240)
L "nginx arrete -> reponse DNS apres $([int]((Get-Date)-$t0).TotalSeconds) s : $a  (secondaire 203.0.113.50 attendu)"
Invoke-Ssm $s.web 'systemctl start nginx' 30 | Out-Null
$t0 = Get-Date
do { Start-Sleep 10; $a = Ans } while ($a -match '203\.0\.113\.50' -and ((Get-Date) - $t0).TotalSeconds -lt 240)
L "nginx relance -> reponse DNS apres $([int]((Get-Date)-$t0).TotalSeconds) s : $a  (retour au primaire)"
$log | Set-Content $outFile -Encoding utf8
$s | ConvertTo-Json
