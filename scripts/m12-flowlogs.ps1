# Module 12 - TP3 : tentatives TCP sur le port 22 de web-01 (refusees par sg-web) puis requete Logs Insights sur les REJECT
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m12\tests.txt'
$ip = Aws ec2 describe-addresses --allocation-ids $s.eipWeb --query 'Addresses[0].PublicIp'
$res = foreach ($i in 1..8) {
  $c = New-Object Net.Sockets.TcpClient; $ar = $c.BeginConnect($ip, 22, $null, $null)
  $ok = $ar.AsyncWaitHandle.WaitOne(2000); $c.Close(); "tentative $i : $(if ($ok) {'connecte'} else {'timeout (paquet rejete par le groupe de securite)'})"
}
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("`n=== TP3 (reprise) : Flow Logs ==="); $lines.Add("8 tentatives TCP vers web-01:22 depuis une machine non autorisee :"); $res | ForEach-Object { $lines.Add("  $_") }
Write-Host 'Attente de la livraison des Flow Logs (~8 min)...'; Start-Sleep 480
$q = 'fields srcAddr, dstAddr, dstPort, action | filter action = "REJECT" and dstPort = 22 | stats count(*) as n by srcAddr, dstPort | sort n desc | limit 10'
for ($k = 0; $k -lt 6; $k++) {
  $qid = Aws logs start-query --log-group-name /leman/vpc-prod/flow-TP-AC --start-time ([DateTimeOffset]::UtcNow.AddHours(-2).ToUnixTimeSeconds()) --end-time ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --query-string $q --query queryId
  do { Start-Sleep 5; $st = Aws logs get-query-results --query-id $qid --query status } while ($st -in 'Running','Scheduled')
  $r = Aws logs get-query-results --query-id $qid --output json | ConvertFrom-Json
  if ($r.results.Count -gt 0) { break }; Start-Sleep 60
}
$lines.Add("Requete Logs Insights : $q")
$lines.Add("Resultats : " + $(if ($r.results.Count) { ($r.results | ForEach-Object { ($_ | Where-Object field -ne '@ptr' | ForEach-Object { "$($_.field)=$($_.value)" }) -join ' ' }) -join ' | ' } else { 'aucune ligne (livraison encore en cours)' }))
$t = Get-Content $outFile -Raw
$t = $t -replace '(?s)\r?\n=== TP3 : Logs Insights \(REJECT\) ===.*$', ''
($t.TrimEnd() + "`n" + ($lines -join "`n") + "`n") | Set-Content $outFile -Encoding utf8
