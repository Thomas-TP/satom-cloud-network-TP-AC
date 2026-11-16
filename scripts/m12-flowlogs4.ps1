# Module 12 - TP3 tel que demande : sonde SSH (port 22) vers web-01 depuis une machine non autorisee, retrouvee dans les Flow Logs
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m12\tests.txt'
$aws = $script:aws; $p = @('--profile','TP-AC','--region','eu-north-1')
function Mask($ip) { (($ip -split '\.')[0..1] -join '.') + '.x.x' }
Aws ec2 start-instances --instance-ids $s.web | Out-Null
Aws ec2 wait instance-running --instance-ids $s.web; Start-Sleep 30
$ip = Aws ec2 describe-addresses --allocation-ids $s.eipWeb --query 'Addresses[0].PublicIp'
$me = (& curl.exe -s --max-time 10 https://checkip.amazonaws.com).Trim()
$ctl = '000'; for ($k = 0; $k -lt 12 -and $ctl -ne '200'; $k++) { $ctl = & curl.exe -sk --max-time 8 -o NUL -w '%{http_code}' "https://$ip/"; if ($ctl -ne '200') { Start-Sleep 10 } }
$t0 = [DateTimeOffset]::UtcNow
$res = foreach ($i in 1..10) { $c = New-Object Net.Sockets.TcpClient; $ar = $c.BeginConnect($ip, 22, $null, $null); $ok = $false; if ($ar.AsyncWaitHandle.WaitOne(1500)) { try { $c.EndConnect($ar); $ok = $true } catch {} }; $c.Close(); $(if ($ok) { 'connecte' } else { 'timeout' }); Start-Sleep -Milliseconds 300 }
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("`n=== TP3 (web-01) : Flow Logs, sonde SSH vers web-01 ===")
$lines.Add("Controle : https vers web-01 (443 ouvert) -> HTTP $ctl")
$lines.Add("10 tentatives TCP vers web-01:22 depuis une machine non autorisee ($(Mask $me)) -> $(($res | Group-Object | ForEach-Object { "$($_.Count) $($_.Name)" }) -join ', ') (sg-web n'ouvre le 22 qu'a la salle d'exploitation)")
$pat = "[version, account, eni, source=`"$me`", destination=`"10.20.0.10`", srcport, destport=`"22`", protocol, packets, bytes, windowstart, windowend, action=`"REJECT`", flowlogstatus]"
$found = $null
for ($k = 0; $k -lt 16; $k++) {
  Start-Sleep 45
  $ev = & $aws logs filter-log-events --log-group-name /leman/vpc-prod/flow-TP-AC --filter-pattern $pat --start-time $t0.AddMinutes(-1).ToUnixTimeMilliseconds() --query 'events[].message' --output text @p
  if ($ev -and $ev -ne 'None') { $found = $ev; break }
}
$lines.Add("Recherche dans /leman/vpc-prod/flow-TP-AC (source = ce poste, destination 10.20.0.10, port 22, REJECT) :")
if ($found) { ($found -split "`t") | ForEach-Object { $lines.Add('  ' + (($_ -replace [regex]::Escape($me), (Mask $me)) -replace '\d{12}', '000000000000')) } } else { $lines.Add('  aucune ligne livree dans le delai') }
$q = "filter action = `"REJECT`" and dstPort = 22 and srcAddr = `"$me`" and dstAddr = `"10.20.0.10`" | stats count(*) as n by srcAddr, dstAddr, dstPort"
$qid = & $aws logs start-query --log-group-name /leman/vpc-prod/flow-TP-AC --start-time ([DateTimeOffset]::UtcNow.AddHours(-1).ToUnixTimeSeconds()) --end-time ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --query-string $q --query queryId --output text @p
do { Start-Sleep 5; $st = & $aws logs get-query-results --query-id $qid --query status --output text @p } while ($st -in 'Running','Scheduled')
$r = & $aws logs get-query-results --query-id $qid --output json @p | ConvertFrom-Json
$lines.Add('Requete Logs Insights : filter action = "REJECT" and dstPort = 22 and srcAddr = <ce poste> and dstAddr = "10.20.0.10" | stats count(*) as n by srcAddr, dstAddr, dstPort')
$lines.Add("Resultat : " + $(if ($r.results.Count) { ($r.results | ForEach-Object { ($_ | Where-Object field -ne '@ptr' | ForEach-Object { $v = $_.value; if ($_.field -eq 'srcAddr') { $v = Mask $v }; "$($_.field)=$v" }) -join ' ' }) -join ' | ' } else { 'aucune ligne' }))
$lines.Add("Diagnostic : rejet par sg-web (port 22 non ouvert a cette source) ; ENI de web-01, port 22, action REJECT.")
$t = Get-Content $outFile -Raw
($t.TrimEnd() + "`n" + ($lines -join "`n") + "`n") | Set-Content $outFile -Encoding utf8
Aws ec2 stop-instances --instance-ids $s.web | Out-Null


