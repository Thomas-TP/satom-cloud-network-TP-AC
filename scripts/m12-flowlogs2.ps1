# Module 12 - TP3 (version finale) : tentative SSH propre, puis recherche de MA connexion refusee dans les Flow Logs (IP source masquee)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m12\tests.txt'
$ip = Aws ec2 describe-addresses --allocation-ids $s.eipWeb --query 'Addresses[0].PublicIp'
$me = (& curl.exe -s --max-time 10 https://checkip.amazonaws.com).Trim()
$mask = ($me -split '\.')[0..1] -join '.'; $mask += '.x.x'
$t0 = [DateTimeOffset]::UtcNow
$res = foreach ($i in 1..10) { $c = New-Object Net.Sockets.TcpClient; $ar = $c.BeginConnect($ip, 22, $null, $null); $ok = $ar.AsyncWaitHandle.WaitOne(1500); $c.Close(); if ($ok) {'connecte'} else {'timeout'}; Start-Sleep -Milliseconds 300 }
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("`n=== TP3 (version finale) : Flow Logs ===")
$lines.Add("10 tentatives TCP depuis une machine non autorisee ($mask) vers web-01:22 -> $(($res | Group-Object | ForEach-Object { "$($_.Count) $($_.Name)" }) -join ', ') (refusees par sg-web)")
$pat = "[version, account, eni, source=`"$me`", destination, srcport, destport=`"22`", protocol, packets, bytes, windowstart, windowend, action=`"REJECT`", flowlogstatus]"
$found = $null
for ($k = 0; $k -lt 14; $k++) {
  Start-Sleep 45
  $ev = Aws logs filter-log-events --log-group-name /leman/vpc-prod/flow-TP-AC --filter-pattern $pat --start-time $t0.AddMinutes(-1).ToUnixTimeMilliseconds() --query 'events[].message'
  if ($ev -and $ev -ne 'None') { $found = $ev; break }
}
$lines.Add("Recherche dans /leman/vpc-prod/flow-TP-AC (filtre : source = cette machine, port 22, action REJECT) :")
if ($found) { ($found -split "`t") | ForEach-Object { $lines.Add('  ' + ($_ -replace [regex]::Escape($me), $mask -replace '000000000000','000000000000') -replace '\d{12}','000000000000') } } else { $lines.Add('  aucune ligne encore livree') }
# requete Logs Insights : rejets sur le port 22, par source (toutes sources, IP masquees partiellement)
$q = 'filter action = "REJECT" and dstPort = 22 | stats count(*) as n by srcAddr | sort n desc | limit 5'
$qid = Aws logs start-query --log-group-name /leman/vpc-prod/flow-TP-AC --start-time ([DateTimeOffset]::UtcNow.AddHours(-2).ToUnixTimeSeconds()) --end-time ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --query-string $q --query queryId
do { Start-Sleep 5; $st = Aws logs get-query-results --query-id $qid --query status } while ($st -in 'Running','Scheduled')
$r = Aws logs get-query-results --query-id $qid --output json | ConvertFrom-Json
$lines.Add("Logs Insights : $q")
$lines.Add("Resultat (srcAddr masquee) : " + $(if ($r.results.Count) { ($r.results | ForEach-Object { ($_ | Where-Object field -ne '@ptr' | ForEach-Object { $v = $_.value; if ($_.field -eq 'srcAddr') { $v = (($v -split '\.')[0..1] -join '.') + '.x.x' }; "$($_.field)=$v" }) -join ' ' }) -join ' | ' } else { 'aucune ligne' }))
$t = Get-Content $outFile -Raw
$t = $t -replace '(?s)\r?\n=== TP3 \(reprise\) : Flow Logs ===.*$', ''
($t.TrimEnd() + "`n" + ($lines -join "`n") + "`n") | Set-Content $outFile -Encoding utf8
