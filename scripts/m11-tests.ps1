# Module 11 - Tests CloudFront (GET avec en-tetes ; preuves dans docs/modules/m11/tests.txt)
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m11\tests.txt'
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$d = $s.cfDomain
function Get-Hdr($path) {
  for ($i = 0; $i -lt 5; $i++) {
    $r = & curl.exe -s -D - -o NUL --max-time 20 --ssl-no-revoke --http1.1 "https://$d$path" 2>&1 | Select-String '^HTTP|x-cache|x-amz-cf-pop' | ForEach-Object { '   ' + $_.Line.Trim() }
    if ($r) { return $r }
    Start-Sleep 2
  }
  '   (pas de reponse apres 5 essais)'
}
function Body($path) {
  for ($i = 0; $i -lt 5; $i++) { $r = & curl.exe -s --max-time 20 --ssl-no-revoke --http1.1 "https://$d$path" 2>&1; if ($r) { return ($r -join ' ') }; Start-Sleep 2 }
  '(pas de reponse)'
}

L "=== TP1 : distribution $($s.cfId) (domaine $d) ==="
L "GET / (comportement par defaut, TTL 0) :"; Get-Hdr '/' | ForEach-Object { L $_ }
L "`n=== TP2 : comportements ==="
Invoke-Ssm $s.web 'echo "logo v1" > /usr/share/nginx/static/logo.png' 20 | Out-Null
$inv0 = Aws cloudfront create-invalidation --distribution-id $s.cfId --paths '/static/*' --query 'Invalidation.Id'; Aws cloudfront wait invalidation-completed --distribution-id $s.cfId --id $inv0
L "/static/logo.png 1re requete (apres invalidation initiale) :"; Get-Hdr '/static/logo.png' | ForEach-Object { L $_ }
L "/static/logo.png 2e requete :"; Get-Hdr '/static/logo.png' | ForEach-Object { L $_ }
L "/api/health 1re :"; Get-Hdr '/api/health' | ForEach-Object { L $_ }
L "/api/health 2e (jamais servi depuis le cache) :"; Get-Hdr '/api/health' | ForEach-Object { L $_ }
L "`n=== TP3 : verrouillage de l'origine et invalidation ==="
L "acces direct a l'ALB depuis Internet : http -> $(& curl.exe -s --max-time 8 -o NUL -w 'HTTP %{http_code}' "http://$($s.albDns)/" 2>&1) $(if ($LASTEXITCODE -ne 0) {'(bloque : timeout)'}) ; https -> $(& curl.exe -sk --max-time 8 -o NUL -w 'HTTP %{http_code}' "https://$($s.albDns)/" 2>&1) $(if ($LASTEXITCODE -ne 0) {'(bloque : timeout)'})"
L "via CloudFront : $(Body '/')"
Invoke-Ssm $s.web 'echo "logo v2" > /usr/share/nginx/static/logo.png' 20 | Out-Null
L "origine modifiee en 'v2', sans invalidation, CloudFront sert encore : $(Body '/static/logo.png')"
$inv = Aws cloudfront create-invalidation --distribution-id $s.cfId --paths '/static/logo.png' --query 'Invalidation.Id'
Aws cloudfront wait invalidation-completed --distribution-id $s.cfId --id $inv
L "apres invalidation $inv : $(Body '/static/logo.png')"
L "`nRoute 53 : alias primaire -> CloudFront ; reponse DNS : $(Aws route53 test-dns-answer --hosted-zone-id $s.zonePub --record-name portefeuilles.leman-finance.example --record-type A --query 'RecordData')"
$log | Set-Content $outFile -Encoding utf8
