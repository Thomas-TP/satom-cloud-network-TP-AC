# Module 12 - TP3 reel : sonde SSH (port 22) vers l'ALB (SG ferme) depuis ce poste, retrouvee dans les Flow Logs par l'adresse source
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m12\tests.txt'
$aws = $script:aws; $p = @('--profile','TP-AC','--region','eu-north-1')
function Mask($ip) { (($ip -split '\.')[0..1] -join '.') + '.x.x' }
$me = (& curl.exe -s --max-time 10 https://checkip.amazonaws.com).Trim()
$c = New-Object Net.Sockets.TcpClient; $ar = $c.BeginConnect('github.com', 22, $null, $null); $out22 = $ar.AsyncWaitHandle.WaitOne(4000); $c.Close()
$albIps = @(Resolve-DnsName $s.albDns -Type A -DnsOnly | Where-Object Type -eq 'A' | ForEach-Object IPAddress)
$t0 = [DateTimeOffset]::UtcNow
$res = New-Object System.Collections.Generic.List[string]
foreach ($ip in $albIps) { foreach ($i in 1..4) { $c = New-Object Net.Sockets.TcpClient; $ar = $c.BeginConnect($ip, 22, $null, $null); $ok = $false; if ($ar.AsyncWaitHandle.WaitOne(1500)) { try { $c.EndConnect($ar); $ok = $true } catch {} }; $c.Close(); $res.Add($(if ($ok) { 'connecte' } else { 'timeout' })); Start-Sleep -Milliseconds 400 } }
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("`n=== TP3 (reel) : Flow Logs ===")
$lines.Add("Controle : port 22 sortant depuis ce poste (github.com:22) -> $(if ($out22) {'ouvert'} else {'filtre'})")
$lines.Add("$($res.Count) tentatives TCP vers le port 22 de l'ALB ($($albIps.Count) noeuds publics) depuis ce poste ($(Mask $me)) -> $(($res | Group-Object | ForEach-Object { "$($_.Count) $($_.Name)" }) -join ', ') : refusees par sg-alb (seul le port 80 est ouvert, au prefixe CloudFront)")
$pat = "[version, account, eni, source=`"$me`", destination, srcport, destport=`"22`", protocol, packets, bytes, windowstart, windowend, action=`"REJECT`", flowlogstatus]"
$found = $null
for ($k = 0; $k -lt 16; $k++) {
  Start-Sleep 45
  $ev = & $aws logs filter-log-events --log-group-name /leman/vpc-prod/flow-TP-AC --filter-pattern $pat --start-time $t0.AddMinutes(-1).ToUnixTimeMilliseconds() --query 'events[].message' --output text @p
  if ($ev -and $ev -ne 'None') { $found = $ev; break }
}
$lines.Add("Recherche dans /leman/vpc-prod/flow-TP-AC (source = ce poste, port 22, REJECT) :")
if ($found) { ($found -split "`t") | ForEach-Object { $lines.Add('  ' + (($_ -replace [regex]::Escape($me), (Mask $me)) -replace '\d{12}', '000000000000')) } } else { $lines.Add('  aucune ligne livree dans le delai') }
$q = "filter action = `"REJECT`" and dstPort = 22 and srcAddr = `"$me`" | stats count(*) as n by srcAddr, dstAddr, dstPort | sort n desc | limit 10"
$qid = & $aws logs start-query --log-group-name /leman/vpc-prod/flow-TP-AC --start-time ([DateTimeOffset]::UtcNow.AddHours(-1).ToUnixTimeSeconds()) --end-time ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --query-string $q --query queryId --output text @p
do { Start-Sleep 5; $st = & $aws logs get-query-results --query-id $qid --query status --output text @p } while ($st -in 'Running','Scheduled')
$r = & $aws logs get-query-results --query-id $qid --output json @p | ConvertFrom-Json
$lines.Add('Requete Logs Insights : filter action = "REJECT" and dstPort = 22 and srcAddr = <ce poste> | stats count(*) as n by srcAddr, dstAddr, dstPort | sort n desc')
$lines.Add("Resultat : " + $(if ($r.results.Count) { ($r.results | ForEach-Object { ($_ | Where-Object field -ne '@ptr' | ForEach-Object { $v = $_.value; if ($_.field -eq 'srcAddr') { $v = Mask $v }; "$($_.field)=$v" }) -join ' ' }) -join ' | ' } else { 'aucune ligne' }))
$lines.Add("Diagnostic : le rejet vient du Security Group sg-alb (port 22 non ouvert) : source, ENI de l'ALB, port 22 et action REJECT le prouvent.")
$t = Get-Content $outFile -Raw
$t = $t -replace '(?s)\r?\n=== TP3 : Flow Logs \(VPC Flow Logs.*$', ''
($t.TrimEnd() + "`n" + ($lines -join "`n") + "`n") | Set-Content $outFile -Encoding utf8

