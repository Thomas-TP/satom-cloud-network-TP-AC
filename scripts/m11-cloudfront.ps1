# Module 11 - CloudFront d-leman-portail-TP-AC (TP-AC)
# Ecarts assumes vs HackMD : pas de domaine reel -> pas de certificat ACM valide -> certificat *.cloudfront.net par defaut
# cote visiteur, et origine ALB jointe en HTTP (80) car le certificat auto-signe de l'ALB serait refuse par CloudFront.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m11\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function J($name,$obj) { $f = Join-Path $env:TEMP "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 12 -Compress)); "file://$f" }

# contenu statique de test sur web-01 + listener HTTP 80 de l'ALB (origine CloudFront)
Invoke-Ssm $s.web @'
mkdir -p /usr/share/nginx/static
echo "logo v1" > /usr/share/nginx/static/logo.png
cat > /etc/nginx/conf.d/static.conf <<'EOC'
server { listen 8081; location /static/ { alias /usr/share/nginx/static/; default_type text/plain; add_header Cache-Control "public, max-age=86400"; } }
EOC
python3 - <<'EOP'
p='/etc/nginx/conf.d/tpac.conf'
t=open(p).read()
t=t.replace('server { listen 80; location /health','server { listen 80; location /static/ { alias /usr/share/nginx/static/; default_type text/plain; } location /health',1)
open(p,'w').write(t)
EOP
nginx -t && systemctl reload nginx; curl -s localhost/static/logo.png
'@ 40 | Out-Null
if (-not $s.listenerHttp) {
  $s.listenerHttp = Aws elbv2 create-listener --load-balancer-arn $s.alb --protocol HTTP --port 80 --default-actions "Type=forward,TargetGroupArn=$($s.tgWeb)" --query 'Listeners[0].ListenerArn'
  Aws elbv2 create-rule --listener-arn $s.listenerHttp --priority 10 --conditions 'Field=path-pattern,Values=/api/*' --actions "Type=forward,TargetGroupArn=$($s.tgApp)" | Out-Null
  Aws ec2 authorize-security-group-ingress --group-id $s.sgAlb --ip-permissions 'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTP temporaire (avant prefixe CloudFront)}]' | Out-Null
  Save-State $s
}

# cache policy /static/* : TTL 86400, sans cookies/en-tetes/chaine de requete, compression
$cp = @{Name='cp-static-86400-TP-AC';Comment='TP-AC static 24h';DefaultTTL=86400;MaxTTL=86400;MinTTL=86400;ParametersInCacheKeyAndForwardedToOrigin=@{EnableAcceptEncodingGzip=$true;EnableAcceptEncodingBrotli=$true;HeadersConfig=@{HeaderBehavior='none'};CookiesConfig=@{CookieBehavior='none'};QueryStringsConfig=@{QueryStringBehavior='none'}}}
$s.cachePolicy = Aws cloudfront create-cache-policy --cache-policy-config (J 'cp' $cp) --query 'CachePolicy.Id'
$CachingDisabled = '4135ea2d-6df8-44a3-9df3-4b5a84be39ad'; $AllViewer = '216adef6-5c7f-47e4-b989-5492eafa07d3'
$all7 = @{Quantity=7;Items=@('GET','HEAD','OPTIONS','PUT','POST','PATCH','DELETE')}
$dist = @{
  CallerReference = "tpac-$(Get-Random)"; Comment = 'd-leman-portail-TP-AC'; Enabled = $true; PriceClass = 'PriceClass_100'
  Origins = @{Quantity=1;Items=@(@{Id='alb-prod-leman';DomainName=$s.albDns;CustomOriginConfig=@{HTTPPort=80;HTTPSPort=443;OriginProtocolPolicy='http-only';OriginSslProtocols=@{Quantity=1;Items=@('TLSv1.2')}}})}
  DefaultCacheBehavior = @{TargetOriginId='alb-prod-leman';ViewerProtocolPolicy='redirect-to-https';AllowedMethods=@{Quantity=7;Items=$all7.Items;CachedMethods=@{Quantity=2;Items=@('GET','HEAD')}};CachePolicyId=$CachingDisabled;OriginRequestPolicyId=$AllViewer;Compress=$true}
  CacheBehaviors = @{Quantity=2;Items=@(
    @{PathPattern='/static/*';TargetOriginId='alb-prod-leman';ViewerProtocolPolicy='redirect-to-https';AllowedMethods=@{Quantity=2;Items=@('GET','HEAD');CachedMethods=@{Quantity=2;Items=@('GET','HEAD')}};CachePolicyId=$s.cachePolicy;Compress=$true},
    @{PathPattern='/api/*';TargetOriginId='alb-prod-leman';ViewerProtocolPolicy='redirect-to-https';AllowedMethods=@{Quantity=7;Items=$all7.Items;CachedMethods=@{Quantity=2;Items=@('GET','HEAD')}};CachePolicyId=$CachingDisabled;OriginRequestPolicyId=$AllViewer})}
}
$distCfg = @{DistributionConfig=$dist;Tags=@{Items=@(@{Key='Projet';Value='SatomCloudNetwork'},@{Key='Equipe';Value='TP-AC'},@{Key='Name';Value='d-leman-portail-TP-AC'})}}
$r = Aws cloudfront create-distribution-with-tags --distribution-config-with-tags (J 'dist' $distCfg) --query 'Distribution.[Id,DomainName]'
$s.cfId, $s.cfDomain = $r -split '\s+'
Save-State $s
Write-Host "Attente du deploiement CloudFront ($($s.cfDomain))..."
Aws cloudfront wait distribution-deployed --id $s.cfId

function Hdr($path) { & curl.exe -sIk --max-time 15 "https://$($s.cfDomain)$path" 2>&1 | Select-String -Pattern '^HTTP|x-cache|x-amz-cf-pop|^age' | ForEach-Object { $_.Line.Trim() } }
L "=== TP1 : distribution $($s.cfId) ==="
L "curl -I https://$($s.cfDomain)/ :"; Hdr '/' | ForEach-Object { L "   $_" }
L "`n=== TP2 : comportements ==="
L "/static/logo.png (1re requete) :"; Hdr '/static/logo.png' | ForEach-Object { L "   $_" }
L "/static/logo.png (2e requete) :"; Hdr '/static/logo.png' | ForEach-Object { L "   $_" }
L "/api/health (1re) :"; Hdr '/api/health' | ForEach-Object { L "   $_" }
L "/api/health (2e)  :"; Hdr '/api/health' | ForEach-Object { L "   $_" }

# TP3 : verrouillage de l'ALB sur le prefixe gere CloudFront
$pl = Aws ec2 describe-managed-prefix-lists --filters 'Name=prefix-list-name,Values=com.amazonaws.global.cloudfront.origin-facing' --query 'PrefixLists[0].PrefixListId'
Aws ec2 authorize-security-group-ingress --group-id $s.sgAlb --ip-permissions "IpProtocol=tcp,FromPort=80,ToPort=80,PrefixListIds=[{PrefixListId=$pl,Description=CloudFront origin-facing}]" | Out-Null
Aws ec2 revoke-security-group-ingress --group-id $s.sgAlb --ip-permissions 'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0}]' | Out-Null
Aws ec2 revoke-security-group-ingress --group-id $s.sgAlb --ip-permissions 'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0}]' | Out-Null
Start-Sleep 10
L "`n=== TP3 : sg-alb limite au prefixe $pl (com.amazonaws.global.cloudfront.origin-facing) ==="
L "acces direct a l'ALB (http) -> $(& curl.exe -s --max-time 8 -o NUL -w 'HTTP %{http_code}' "http://$($s.albDns)/" 2>&1) $(if ($LASTEXITCODE -ne 0) {'ECHEC (bloque)'})"
L "acces direct a l'ALB (https) -> $(& curl.exe -sk --max-time 8 -o NUL -w 'HTTP %{http_code}' "https://$($s.albDns)/" 2>&1) $(if ($LASTEXITCODE -ne 0) {'ECHEC (bloque)'})"
L "via CloudFront -> $(& curl.exe -s --max-time 15 -w ' [HTTP %{http_code}]' "https://$($s.cfDomain)/")"
# invalidation
Invoke-Ssm $s.web 'echo "logo v2" > /usr/share/nginx/static/logo.png' 20 | Out-Null
L "apres changement d'origine, sans invalidation : $(& curl.exe -s --max-time 15 "https://$($s.cfDomain)/static/logo.png")"
$inv = Aws cloudfront create-invalidation --distribution-id $s.cfId --paths '/static/logo.png' --query 'Invalidation.Id'
Aws cloudfront wait invalidation-completed --distribution-id $s.cfId --id $inv
L "apres invalidation $inv : $(& curl.exe -s --max-time 15 "https://$($s.cfDomain)/static/logo.png")"
# Route 53 : l'alias primaire pointe desormais vers CloudFront (et le health check aussi)
$prim = @{Action='UPSERT';ResourceRecordSet=@{Name='portefeuilles.leman-finance.example';Type='A';SetIdentifier='primaire-alb';Failover='PRIMARY';HealthCheckId=$s.hc;AliasTarget=@{HostedZoneId='Z2FDTNDATAQYW2';DNSName=$s.cfDomain;EvaluateTargetHealth=$false}}}
Aws route53 change-resource-record-sets --hosted-zone-id $s.zonePub --change-batch (J 'fo2' @{Changes=@($prim)}) | Out-Null
Aws route53 update-health-check --health-check-id $s.hc --fully-qualified-domain-name $s.cfDomain | Out-Null
Start-Sleep 20
L "Route 53 : alias primaire deplace vers CloudFront -> $(Aws route53 test-dns-answer --hosted-zone-id $s.zonePub --record-name portefeuilles.leman-finance.example --record-type A --query 'RecordData')"
$s.cfPrefixList = $pl; Save-State $s
$log | Set-Content $outFile -Encoding utf8
$s | ConvertTo-Json
