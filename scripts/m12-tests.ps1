# Module 12 - Tests : alarme 5xx -> SNS et Flow Logs REJECT (preuves dans docs/modules/m12/tests.txt)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m12\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$alarm = 'alarm-5xx-portail-TP-AC'
function AlarmState { Aws cloudwatch describe-alarms --alarm-names $alarm --query 'MetricAlarms[0].StateValue' }

L "=== TP1 : tableau de bord ==="
L "Tableau de bord : $(Aws cloudwatch list-dashboards --dashboard-name-prefix db-portail-leman-TP-AC --query 'DashboardEntries[0].DashboardName')"
L "HealthyHostCount tg-web (derniere minute) : $(Aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name HealthyHostCount --dimensions "Name=TargetGroup,Value=$($s.tgWebDim)" "Name=LoadBalancer,Value=$($s.albDim)" --start-time (Get-Date).AddMinutes(-10).ToUniversalTime().ToString('s') --end-time (Get-Date).ToUniversalTime().ToString('s') --period 60 --statistics Average --query 'sort_by(Datapoints,&Timestamp)[-1].Average')"

L "`n=== TP3 : Flow Logs (SSH non autorise vers web-01) ==="
$ip = Aws ec2 describe-addresses --allocation-ids $s.eipWeb --query 'Addresses[0].PublicIp'
for ($i = 0; $i -lt 6; $i++) { & curl.exe -s --max-time 2 -o NUL "telnet://${ip}:22" 2>&1 | Out-Null }
L "6 tentatives de connexion TCP sur le port 22 de web-01 depuis cette machine (refusees par sg-web)"

L "`n=== TP2 : alarme ==="
L "Etat initial : $(AlarmState)"
# genere des 5xx via CloudFront -> ALB -> app-01 (/api/error) : > 5 par periode de 5 min pendant 2 periodes
$t0 = Get-Date; $reached = $false
$cf = "https://$($s.cfDomain)/api/error"
while (((Get-Date) - $t0).TotalMinutes -lt 22) {
  1..30 | ForEach-Object { & curl.exe -s --max-time 5 -o NUL $cf }
  Start-Sleep 20
  $st = AlarmState
  if ($st -eq 'ALARM') { $reached = $true; break }
}
L "Trafic 5xx genere pendant $([int]((Get-Date)-$t0).TotalMinutes) min -> etat de l'alarme : $(AlarmState)"
$msg = Aws sqs receive-message --queue-url $s.queue --max-number-of-messages 5 --wait-time-seconds 10 --query 'Messages[].Body'
L "Notification SNS recue dans sqs-exploitation-leman-TP-AC : $(([string]$msg) -replace '\\n|\s+',' ' | ForEach-Object { if ($_.Length -gt 400) { $_.Substring(0,400) + '...' } else { $_ } })"
# retour a la normale : on cesse de generer des erreurs
$t1 = Get-Date
while (((Get-Date) - $t1).TotalMinutes -lt 20) { if ((AlarmState) -eq 'OK') { break }; Start-Sleep 30 }
L "Apres arret des erreurs ($([int]((Get-Date)-$t1).TotalMinutes) min) -> etat de l'alarme : $(AlarmState)"
$msg2 = Aws sqs receive-message --queue-url $s.queue --max-number-of-messages 5 --wait-time-seconds 10 --query 'Messages[].Body'
L "Notification de retour a la normale presente : $(if ($msg2 -match 'OK') {'oui'} else {'non vue'})"

L "`n=== TP3 : Logs Insights (REJECT) ==="
$q = 'fields @timestamp, srcAddr, dstAddr, dstPort, action | filter action = "REJECT" and dstPort = 22 | stats count(*) as n by srcAddr, dstPort | sort n desc | limit 10'
$qid = Aws logs start-query --log-group-name /leman/vpc-prod/flow-TP-AC --start-time ([DateTimeOffset]::UtcNow.AddHours(-2).ToUnixTimeSeconds()) --end-time ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --query-string $q --query queryId
do { Start-Sleep 5; $st = Aws logs get-query-results --query-id $qid --query status } while ($st -in 'Running','Scheduled')
$res = Aws logs get-query-results --query-id $qid --output json | ConvertFrom-Json
L "Requete : $q"
L "Resultats : $(($res.results | ForEach-Object { ($_ | ForEach-Object { "$($_.field)=$($_.value)" }) -join ' ' }) -join ' | ')"
$log | Set-Content $outFile -Encoding utf8
