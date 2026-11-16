# Module 12 - CloudWatch (tableau de bord, alarme, SNS) et VPC Flow Logs (TP-AC)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\lib.ps1"
$s = Get-State
function J($name,$obj) { $f = Join-Path $env:TEMP "tpac-$name.json"; [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 12 -Compress)); "file://$f" }
$tagArgs = @('Key=Projet,Value=SatomCloudNetwork','Key=Equipe,Value=TP-AC')

# dimensions CloudWatch de l'ALB et du groupe cible
$albDim = ($s.alb -split 'loadbalancer/')[1]; $tgDim = ($s.tgWeb -split ':')[-1]
$s.albDim = $albDim; $s.tgWebDim = $tgDim

# TP1 : tableau de bord
$widgets = @(
 @{type='metric';x=0;y=0;width=12;height=6;properties=@{title='Cibles saines / non saines (tg-web)';region='eu-north-1';stat='Average';period=60;metrics=@(@('AWS/ApplicationELB','HealthyHostCount','TargetGroup',$tgDim,'LoadBalancer',$albDim),@('.','UnHealthyHostCount','.','.','.','.'))}},
 @{type='metric';x=12;y=0;width=12;height=6;properties=@{title='Temps de reponse ALB (s)';region='eu-north-1';stat='Average';period=60;metrics=@(,@('AWS/ApplicationELB','TargetResponseTime','LoadBalancer',$albDim))}},
 @{type='metric';x=0;y=6;width=12;height=6;properties=@{title='Erreurs 5xx des cibles';region='eu-north-1';stat='Sum';period=60;metrics=@(,@('AWS/ApplicationELB','HTTPCode_Target_5XX_Count','LoadBalancer',$albDim))}},
 @{type='metric';x=12;y=6;width=12;height=6;properties=@{title='CloudFront - taux d''erreurs 5xx (%)';region='us-east-1';stat='Average';period=300;metrics=@(,@('AWS/CloudFront','5xxErrorRate','DistributionId',$s.cfId,'Region','Global'))}}
)
Aws cloudwatch put-dashboard --dashboard-name db-portail-leman-TP-AC --dashboard-body (J 'dash' @{widgets=$widgets}) | Out-Null

# TP2 : SNS -> file SQS (abonne verifiable ; un abonnement e-mail se rajoute avec : aws sns subscribe --protocol email)
$s.topic = Aws sns create-topic --name sns-exploitation-leman-TP-AC --tags $tagArgs --query TopicArn
$s.queue = Aws sqs create-queue --queue-name sqs-exploitation-leman-TP-AC --query QueueUrl
$qArn = Aws sqs get-queue-attributes --queue-url $s.queue --attribute-names QueueArn --query Attributes.QueueArn
$policy = @{Version='2012-10-17';Statement=@(@{Effect='Allow';Principal=@{Service='sns.amazonaws.com'};Action='sqs:SendMessage';Resource=$qArn;Condition=@{ArnEquals=@{'aws:SourceArn'=$s.topic}}})} | ConvertTo-Json -Depth 8 -Compress
$attr = @{Policy=$policy} | ConvertTo-Json -Compress
$af = Join-Path $env:TEMP 'tpac-qattr.json'; [IO.File]::WriteAllText($af,$attr)
Aws sqs set-queue-attributes --queue-url $s.queue --attributes "file://$af"
Aws sns subscribe --topic-arn $s.topic --protocol sqs --notification-endpoint $qArn --attributes RawMessageDelivery=false | Out-Null
Aws cloudwatch put-metric-alarm --alarm-name alarm-5xx-portail-TP-AC --alarm-description 'TP-AC : plus de 5 erreurs 5xx cibles sur 5 min, 2 periodes consecutives' `
  --namespace AWS/ApplicationELB --metric-name HTTPCode_Target_5XX_Count --dimensions "Name=LoadBalancer,Value=$albDim" --statistic Sum --period 300 --evaluation-periods 2 `
  --threshold 5 --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching --alarm-actions $s.topic --ok-actions $s.topic --tags $tagArgs
Save-State $s

# l'application doit pouvoir produire une vraie erreur 500 (/api/error) pour provoquer l'alarme
Invoke-Ssm $s.app @'
sed -i "s#self.send_response(200 if self.path in ('/health','/api/health','/') else 404)#self.send_response(500 if self.path=='/api/error' else (200 if self.path in ('/health','/api/health','/') else 404))#" /opt/tpac/app.py
systemctl restart tpac-app; sleep 1; curl -s -o /dev/null -w '%{http_code}' localhost:8080/api/error
'@ 40

# TP3 : Flow Logs
Aws logs create-log-group --log-group-name /leman/vpc-prod/flow-TP-AC --tags 'Equipe=TP-AC,Projet=SatomCloudNetwork'
Aws logs put-retention-policy --log-group-name /leman/vpc-prod/flow-TP-AC --retention-in-days 3
$trust = @{Version='2012-10-17';Statement=@(@{Effect='Allow';Principal=@{Service='vpc-flow-logs.amazonaws.com'};Action='sts:AssumeRole'})}
Aws iam create-role --role-name TP-AC-flowlogs-role --assume-role-policy-document (J 'trustfl' $trust) --tags 'Key=Equipe,Value=TP-AC' | Out-Null
$acct = Aws sts get-caller-identity --query Account
$pol = @{Version='2012-10-17';Statement=@(@{Effect='Allow';Action=@('logs:CreateLogStream','logs:PutLogEvents','logs:DescribeLogGroups','logs:DescribeLogStreams');Resource="arn:aws:logs:eu-north-1:${acct}:log-group:/leman/vpc-prod/flow-TP-AC:*"})}
Aws iam put-role-policy --role-name TP-AC-flowlogs-role --policy-name write-flowlogs --policy-document (J 'polfl' $pol)
Start-Sleep 12
$s.flowLog = Aws ec2 create-flow-logs --resource-type VPC --resource-ids $s.vpc --traffic-type ALL --log-destination-type cloud-watch-logs --log-group-name /leman/vpc-prod/flow-TP-AC --deliver-logs-permission-arn "arn:aws:iam::${acct}:role/TP-AC-flowlogs-role" --tag-specifications (Tags 'vpc-flow-log' 'fl-vpc-prod-leman-TP-AC') --query FlowLogIds
Save-State $s
$s | ConvertTo-Json

