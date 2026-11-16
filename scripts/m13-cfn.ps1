# Module 13 - CloudFormation : etape 1 (reseau) -> change set (instances + ALB) -> drift -> suppression/redeploiement (TP-AC)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$outFile = Join-Path $PSScriptRoot '..\docs\modules\m13\tests.txt'; New-Item -ItemType Directory -Force (Split-Path $outFile) | Out-Null
$log = New-Object System.Collections.Generic.List[string]; function L($t) { $log.Add($t); Write-Host $t }
$stack = 'stack-portail-leman-TP-AC'
$full = Join-Path $PSScriptRoot '..\cfn\reseau-leman.yaml'
$etape1 = Join-Path $PSScriptRoot '..\cfn\reseau-leman-etape1.yaml'
# etape 1 = meme template, tronque avant les instances (VPC, sous-reseaux, IGW, routage, SG)
$t = Get-Content $full -Raw
$cut = $t.Substring(0, $t.IndexOf("  Web01:"))
$cut + "Outputs:`n  VpcId:`n    Description: ID du VPC`n    Value: !Ref Vpc`n    Export: {Name: !Sub '`${AWS::StackName}-VpcId'}`n  SgWebId:`n    Value: !Ref SgWeb`n    Export: {Name: !Sub '`${AWS::StackName}-SgWebId'}`n" | Set-Content $etape1 -Encoding utf8
$pf = Join-Path $env:TEMP 'tpac-cfn-params.json'
[IO.File]::WriteAllText($pf, (@(@{ParameterKey='Environnement';ParameterValue='prod'},@{ParameterKey='CertificateArn';ParameterValue=$s.cert}) | ConvertTo-Json -Compress))
$tags = @('Key=Projet,Value=SatomCloudNetwork','Key=Equipe,Value=TP-AC','Key=Environnement,Value=prod')

function Wait-Stack($want) {
  do { Start-Sleep 15; $st = & $script:aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].StackStatus' --output text --profile TP-AC --region eu-north-1 2>&1 | Out-String; $st = $st.Trim() } while ($st -match 'IN_PROGRESS')
  $st
}
function Deploy-Full($label, $paramFile = $pf) {
  $cs = "cs-$label-$(Get-Random)"
  Aws cloudformation create-change-set --stack-name $stack --change-set-name $cs --change-set-type UPDATE --template-body "file://$full" --parameters "file://$paramFile" --capabilities CAPABILITY_IAM | Out-Null
  do { Start-Sleep 5; $st = Aws cloudformation describe-change-set --stack-name $stack --change-set-name $cs --query Status } while ($st -in 'CREATE_PENDING','CREATE_IN_PROGRESS')
  $chg = Aws cloudformation describe-change-set --stack-name $stack --change-set-name $cs --query 'Changes[].ResourceChange.[Action,LogicalResourceId,ResourceType]'
  L "Change set $cs : $($chg.Count) changements ; actions = $(($chg | ForEach-Object { ($_ -split "`t")[0] } | Sort-Object -Unique) -join ',')"
  L (($chg | ForEach-Object { '   ' + ($_ -replace "`t",'  ') }) -join "`n")
  Aws cloudformation execute-change-set --stack-name $stack --change-set-name $cs
  Wait-Stack 'UPDATE_COMPLETE'
}

L "=== TP1 : validation et creation de la stack (reseau seul) ==="
L "validate-template : parametres = $((Aws cloudformation validate-template --template-body "file://$full" --query 'Parameters[].ParameterKey') -join ', ')"
Aws cloudformation create-stack --stack-name $stack --template-body "file://$etape1" --parameters "file://$pf" --tags $tags --capabilities CAPABILITY_IAM --on-failure DELETE | Out-Null
$st = Wait-Stack 'CREATE_COMPLETE'
L "Statut : $st ; sorties : $(Aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]')"

L "`n=== TP2 : change set (instances, groupes cibles, ALB) ==="
$st = Deploy-Full 'ajouts'
L "Statut apres execution : $st"
$alb = Aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].Outputs[?OutputKey==`AlbDns`].OutputValue'
$tgW = Aws elbv2 describe-target-groups --names tg-web-cfn-TP-AC --query 'TargetGroups[0].TargetGroupArn'; $tgA = Aws elbv2 describe-target-groups --names tg-app-cfn-TP-AC --query 'TargetGroups[0].TargetGroupArn'
for ($i = 0; $i -lt 40; $i++) { $h1 = Aws elbv2 describe-target-health --target-group-arn $tgW --query 'TargetHealthDescriptions[0].TargetHealth.State'; $h2 = Aws elbv2 describe-target-health --target-group-arn $tgA --query 'TargetHealthDescriptions[0].TargetHealth.State'; if ($h1 -eq 'healthy' -and $h2 -eq 'healthy') { break }; Start-Sleep 10 }
L "Cibles : tg-web=$h1  tg-app=$h2"
L "curl -k https://$alb/api/health -> $(& curl.exe -sk --max-time 10 "https://$alb/api/health")"
L "curl -k https://$alb/ -> $(& curl.exe -sk --max-time 10 "https://$alb/")"

L "`n=== TP3 : drift, suppression, redeploiement ==="
$sgWeb = Aws cloudformation describe-stack-resource --stack-name $stack --logical-resource-id SgWeb --query StackResourceDetail.PhysicalResourceId
Aws ec2 authorize-security-group-ingress --group-id $sgWeb --ip-permissions 'IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=203.0.113.0/24,Description=ajout manuel hors template}]' | Out-Null
function Drift { $id = Aws cloudformation detect-stack-drift --stack-name $stack --query StackDriftDetectionId; do { Start-Sleep 5; $d = Aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $id --query '[DetectionStatus,StackDriftStatus]' } while ($d -match 'IN_PROGRESS'); $d }
L "Regle SSH ajoutee a la main sur sg-web-cfn -> drift stack : $(Drift)"
L "Detail : $(Aws cloudformation describe-stack-resource-drifts --stack-name $stack --stack-resource-drift-status-filters MODIFIED --query 'StackResourceDrifts[].[LogicalResourceId,StackResourceDriftStatus,PropertyDifferences[0].PropertyPath,PropertyDifferences[0].DifferenceType]')"
# Correction : la regle SSH est legitime (salle d'exploitation). On retire la regle posee a la main, puis on la DECLARE dans le template
# (parametre AdminCidr) et on redeploie : CloudFormation la cree lui-meme, donc la stack redevient conforme.
Aws ec2 revoke-security-group-ingress --group-id $sgWeb --ip-permissions 'IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=203.0.113.0/24}]' | Out-Null
L "Regle manuelle retiree -> drift stack : $(Drift)"
$pfa = Join-Path $env:TEMP 'tpac-cfn-params-admin.json'
[IO.File]::WriteAllText($pfa, (@(@{ParameterKey='Environnement';ParameterValue='prod'},@{ParameterKey='CertificateArn';ParameterValue=$s.cert},@{ParameterKey='AdminCidr';ParameterValue='203.0.113.0/24'}) | ConvertTo-Json -Compress))
$st = Deploy-Full 'declaration-template' $pfa
L "Regle declaree dans le template (AdminCidr) puis redeploiement -> statut : $st"
L "Apres correction par le template -> drift stack : $(Drift)"
L "Regles de sg-web-cfn : $(Aws ec2 describe-security-groups --group-ids $sgWeb --query 'SecurityGroups[0].IpPermissions[].[IpProtocol,FromPort,IpRanges[0].CidrIp,UserIdGroupPairs[0].GroupId]')"
Aws cloudformation delete-stack --stack-name $stack
$t0 = Get-Date; do { Start-Sleep 20; $r = & $script:aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].StackStatus' --output text --profile TP-AC --region eu-north-1 2>&1 | Out-String } while ($r -match 'IN_PROGRESS')
L "Suppression de la stack (ordre inverse des dependances) : $([int]((Get-Date)-$t0).TotalMinutes) min -> $(if ($r -match 'does not exist') {'DELETE_COMPLETE (stack disparue)'} else {$r.Trim()})"
L "VPC restants avec le tag de la stack : $(Aws ec2 describe-vpcs --filters 'Name=tag:Name,Values=vpc-prod-leman-cfn-TP-AC' --query 'length(Vpcs)')"
Aws cloudformation create-stack --stack-name $stack --template-body "file://$etape1" --parameters "file://$pf" --tags $tags --capabilities CAPABILITY_IAM | Out-Null
Wait-Stack 'CREATE_COMPLETE' | Out-Null
$st = Deploy-Full 'redeploiement'
$alb = Aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].Outputs[?OutputKey==`AlbDns`].OutputValue'
$tgW = Aws elbv2 describe-target-groups --names tg-web-cfn-TP-AC --query 'TargetGroups[0].TargetGroupArn'; $tgA = Aws elbv2 describe-target-groups --names tg-app-cfn-TP-AC --query 'TargetGroups[0].TargetGroupArn'
for ($i = 0; $i -lt 40; $i++) { $h1 = Aws elbv2 describe-target-health --target-group-arn $tgW --query 'TargetHealthDescriptions[0].TargetHealth.State'; $h2 = Aws elbv2 describe-target-health --target-group-arn $tgA --query 'TargetHealthDescriptions[0].TargetHealth.State'; if ($h1 -eq 'healthy' -and $h2 -eq 'healthy') { break }; Start-Sleep 10 }
L "Redeploiement : $st ; cibles tg-web=$h1 tg-app=$h2 ; curl -k https://$alb/api/health -> $(& curl.exe -sk --max-time 10 "https://$alb/api/health")"
$log | Set-Content $outFile -Encoding utf8


