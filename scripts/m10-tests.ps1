# Module 10 - Tests Route 53 (preuves dans docs/modules/m10/tests.txt)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m10\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$fqdn = 'portefeuilles.leman-finance.example'
function Ans { Aws route53 test-dns-answer --hosted-zone-id $s.zonePub --record-name $fqdn --record-type A --query 'RecordData' }
function Hc { (Aws route53 get-health-check-status --health-check-id $s.hc --query 'HealthCheckObservations[].StatusReport.Status') -split "`t" | ForEach-Object { ($_ -split ':')[0] } | Sort-Object -Unique }

L "=== TP1 : zone privee prod.leman.internal (resolveur 10.20.0.2) ==="
L "web-01 : $((Invoke-Ssm $s.web 'dnf install -y -q bind-utils >/dev/null 2>&1; echo -n "app -> "; dig +short app.prod.leman.internal; echo -n "web -> "; dig +short web.prod.leman.internal' 120) -join ' ')"
L "web-01 : $((Invoke-Ssm $s.web 'echo -n "serveur DNS utilise : "; grep nameserver /etc/resolv.conf | head -1' 30) -join ' ')"

L "`n=== TP2 : zone publique leman-finance.example (domaine fictif : pas de delegation NS reelle) ==="
$ns = (Aws route53 get-hosted-zone --id $s.zonePub --query 'DelegationSet.NameServers') -split '\s+'
L "Serveurs NS de la zone : $($ns -join ', ')"
$ips = @(Resolve-DnsName $fqdn -Server $ns[0] -Type A -DnsOnly -ErrorAction SilentlyContinue | Where-Object Type -eq 'A' | ForEach-Object IPAddress)
L "Interrogation directe de $($ns[0]) -> $($ips -join ', ')"
if ($ips) { L "curl https://$fqdn/ (resolution forcee vers l'ALB) -> $(& curl.exe -sk --max-time 8 --resolve "${fqdn}:443:$($ips[0])" "https://$fqdn/")" }

L "`n=== TP3 : health check + failover ==="
L "Health check $($s.hc) : $(Hc)   | reponse DNS : $(Ans)  (primaire = ALB)"
Invoke-Ssm $s.web 'systemctl stop nginx' 30 | Out-Null
$t0 = Get-Date
do { Start-Sleep 10; $a = Ans } while ($a -notmatch '203\.0\.113\.50' -and ((Get-Date) - $t0).TotalSeconds -lt 300)
L "nginx arrete sur web-01 -> apres $([int]((Get-Date)-$t0).TotalSeconds) s : health check = $(Hc), reponse DNS = $a (secondaire statique)"
Invoke-Ssm $s.web 'systemctl start nginx' 30 | Out-Null
$t0 = Get-Date
do { Start-Sleep 10; $a = Ans } while ($a -match '203\.0\.113\.50' -and ((Get-Date) - $t0).TotalSeconds -lt 300)
L "nginx relance -> apres $([int]((Get-Date)-$t0).TotalSeconds) s : health check = $(Hc), reponse DNS = $a (retour au primaire)"
$log | Set-Content $outFile -Encoding utf8
