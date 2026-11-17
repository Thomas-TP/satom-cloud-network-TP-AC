# Module 4 - tests du pare-feu deploye par le modele CloudFormation : un flux autorise et un flux bloque, les deux retrouves dans les journaux
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m04\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
function Run($cmd) { ((Invoke-Ssm $s.app $cmd 60) -join ' ').Replace('Success', '').Trim() }
Aws ec2 start-instances --instance-ids $s.app | Out-Null; Wait-Ssm $s.app 240 | Out-Null
$fw = & $script:aws network-firewall describe-firewall --firewall-name nfw-prod-leman-TP-AC --profile TP-AC --region eu-north-1 --output json | ConvertFrom-Json
$ep = ($fw.FirewallStatus.SyncStates.PSObject.Properties | Select-Object -First 1).Value.Attachment
L "=== Module 4 : pare-feu deploye par la stack stack-interconnexion-leman-TP-AC ==="
L "Pare-feu nfw-prod-leman-TP-AC : statut $($fw.FirewallStatus.Status), endpoint $($ep.EndpointId) dans le sous-reseau sub-fw-1a-TP-AC (10.20.2.0/28)"
L "Routes : rt-prive 0.0.0.0/0 -> $((Aws ec2 describe-route-tables --route-table-ids $s.rtPrive --query 'RouteTables[0].Routes[?DestinationCidrBlock==`0.0.0.0/0`]|[0].GatewayId')) (endpoint du pare-feu)"
L "[autorise] curl https://cdn.amazonlinux.com/ -> $(Run 'curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://cdn.amazonlinux.com/ 2>&1')"
L "[bloque]   curl https://example.com/        -> $(Run 'curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://example.com/ 2>&1')"
L "[bloque]   curl https://www.wikipedia.org/  -> $(Run 'curl -sS -m 10 -o /dev/null -w "HTTP %{http_code}" https://www.wikipedia.org/ 2>&1')"
L "[interne]   web-01 -> app-01:8080 (trafic interne, autorise par la regle 1 du pare-feu) -> $((Invoke-Ssm $s.web 'curl -s -m 5 http://10.20.1.10:8080/api/health || echo ECHEC' 40) -join ' ')"
Start-Sleep 150
$t0 = [DateTimeOffset]::UtcNow.AddMinutes(-10).ToUnixTimeMilliseconds()
function Events($grp, $pattern) {
  $a = @('logs', 'filter-log-events', '--log-group-name', $grp, '--start-time', $t0, '--output', 'json', '--profile', 'TP-AC', '--region', 'eu-north-1'); if ($pattern) { $a += @('--filter-pattern', $pattern) }
  @((& $script:aws @a | ConvertFrom-Json).events | ForEach-Object { $_.message | ConvertFrom-Json })
}
L "`nJournal des alertes /leman/nfw-alert-TP-AC (flux bloques) :"
$ev = Events '/leman/nfw-alert-TP-AC' $null
L "  $($ev.Count) alertes ; exemples :"
foreach ($j in ($ev | Select-Object -First 3)) { L ("  src {0} -> dst {1}:{2} | proto {3} | action {4} | {5}" -f $j.event.src_ip, $j.event.dest_ip, $j.event.dest_port, $j.event.app_proto, $j.event.alert.action, $j.event.alert.signature) }
L "`nJournal des flux /leman/nfw-flow-TP-AC (tous les flux vus par le pare-feu, dont le flux autorise) :"
$fl = @(Events '/leman/nfw-flow-TP-AC' '10.20.1.10')
L "  $($fl.Count) flux vus (app-01 et web-01 vers app-01) ; exemples :"
foreach ($j in ($fl | Select-Object -First 4)) { L ("  src {0}:{1} -> dst {2}:{3} | proto {4} | octets {5}" -f $j.event.src_ip, $j.event.src_port, $j.event.dest_ip, $j.event.dest_port, $j.event.proto, $j.event.netflow.bytes) }
$log | Set-Content $outFile -Encoding utf8
