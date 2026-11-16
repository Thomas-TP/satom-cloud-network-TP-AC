# Fonctions communes (equipe TP-AC, region eu-north-1)
$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$script:aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
$script:p = @('--profile','TP-AC','--region','eu-north-1','--output','text')
$script:stateFile = Join-Path $PSScriptRoot 'state.json'
function Get-State { if (Test-Path $script:stateFile) { Get-Content $script:stateFile | ConvertFrom-Json -AsHashtable } else { @{} } }
function Save-State($s) { $s | ConvertTo-Json | Set-Content $script:stateFile }
function Tags($type,$name,$env='prod') { "ResourceType=$type,Tags=[{Key=Name,Value=$name},{Key=Projet,Value=SatomCloudNetwork},{Key=Equipe,Value=TP-AC},{Key=Environnement,Value=$env}]" }
function Aws { & $script:aws @args @script:p }

# Execute une commande shell sur une instance via SSM (pas de SSH, pas de cle)
function Invoke-Ssm($instanceId, $command, $timeoutSec = 60) {
  $json = @{ commands = @($command) } | ConvertTo-Json -Compress
  $f = Join-Path $env:TEMP "ssm-$([guid]::NewGuid()).json"; [IO.File]::WriteAllText($f, $json)
  $cid = Aws ssm send-command --instance-ids $instanceId --document-name AWS-RunShellScript --parameters "file://$f" --query Command.CommandId
  for ($i=0; $i -lt ($timeoutSec/3); $i++) {
    Start-Sleep 3
    $st = Aws ssm get-command-invocation --command-id $cid --instance-id $instanceId --query Status 2>$null
    if ($st -in 'Success','Failed','TimedOut','Cancelled') { break }
  }
  $out = Aws ssm get-command-invocation --command-id $cid --instance-id $instanceId --query '[Status,StandardOutputContent,StandardErrorContent]'
  Remove-Item $f -ErrorAction SilentlyContinue
  $out
}
function Wait-Ssm($instanceId, $maxSec = 300) {
  for ($i=0; $i -lt ($maxSec/5); $i++) {
    $r = Aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$instanceId" --query 'InstanceInformationList[0].PingStatus'
    if ($r -eq 'Online') { return $true }
    Start-Sleep 5
  }
  return $false
}
