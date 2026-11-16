# Collecte l'etat reel des ressources TP-AC (tableaux AWS CLI) -> captures/mNN/*.txt, puis rendu PNG par render_captures.py
. "$PSScriptRoot\lib.ps1"
$s = Get-State
$root = Join-Path $PSScriptRoot '..\captures'
function Cap($mod, $name, $cmdline, [string[]]$cliArgs) {
  $dir = Join-Path $root $mod; New-Item -ItemType Directory -Force $dir | Out-Null
  $out = & $script:aws @cliArgs --profile TP-AC --region eu-north-1 --output table 2>&1 | Out-String
  ("$ " + $cmdline + "`n" + $out.TrimEnd()) | Set-Content (Join-Path $dir "$name.txt") -Encoding utf8
}
$tag = 'Name=tag:Equipe,Values=TP-AC'
Cap 'm01' '01-vpc'      'aws ec2 describe-vpcs --filters Name=tag:Equipe,Values=TP-AC' @('ec2','describe-vpcs','--filters',$tag,'--query','Vpcs[].{Nom:Tags[?Key==`Name`]|[0].Value,VpcId:VpcId,CIDR:CidrBlock,Env:Tags[?Key==`Environnement`]|[0].Value}')
Cap 'm01' '02-subnets'  'aws ec2 describe-subnets --filters Name=tag:Equipe,Values=TP-AC' @('ec2','describe-subnets','--filters',$tag,'--query','Subnets[].{Nom:Tags[?Key==`Name`]|[0].Value,CIDR:CidrBlock,Zone:AvailabilityZone,Libres:AvailableIpAddressCount}')
Cap 'm01' '03-instances' 'aws ec2 describe-instances --filters Name=tag:Equipe,Values=TP-AC' @('ec2','describe-instances','--filters',$tag,'--query','Reservations[].Instances[].{Nom:Tags[?Key==`Name`]|[0].Value,Etat:State.Name,IP:PrivateIpAddress,Type:InstanceType}')
Cap 'm02' '01-routes'   'aws ec2 describe-route-tables (rt-public / rt-prive)' @('ec2','describe-route-tables','--route-table-ids',$s.rtPublic,$s.rtPrive,'--query','RouteTables[].Routes[].{Destination:DestinationCidrBlock,IGW:GatewayId,NAT:NatGatewayId,Etat:State}')
Cap 'm02' '02-nat'      'aws ec2 describe-nat-gateways' @('ec2','describe-nat-gateways','--filter',$tag,'--query','NatGateways[].{Nom:Tags[?Key==`Name`]|[0].Value,Etat:State,Subnet:SubnetId}')
Cap 'm03' '01-sg'       'aws ec2 describe-security-groups (sg-web / sg-app)' @('ec2','describe-security-groups','--group-ids',$s.sgWeb,$s.sgApp,'--query','SecurityGroups[].IpPermissions[].{Proto:IpProtocol,De:FromPort,A:ToPort,CIDR:IpRanges[0].CidrIp,SG:UserIdGroupPairs[0].GroupId}')
Cap 'm03' '02-nacl'     'aws ec2 describe-network-acls (nacl-public-TP-AC)' @('ec2','describe-network-acls','--network-acl-ids',$s.naclPublic,'--query','NetworkAcls[0].Entries[?RuleNumber<`32767`].{N:RuleNumber,Sortie:Egress,Proto:Protocol,CIDR:CidrBlock,Action:RuleAction,De:PortRange.From,A:PortRange.To}')
Cap 'm05' '01-peering'  'aws ec2 describe-vpc-peering-connections' @('ec2','describe-vpc-peering-connections','--filters','Name=status-code,Values=active',$tag,'--query','VpcPeeringConnections[].{Nom:Tags[?Key==`Name`]|[0].Value,Etat:Status.Code,Prod:RequesterVpcInfo.CidrBlock,Dev:AccepterVpcInfo.CidrBlock}')
Cap 'm05' '02-routes-dev' 'aws ec2 describe-route-tables (rt-dev)' @('ec2','describe-route-tables','--route-table-ids',$s.rtDev,'--query','RouteTables[0].Routes[].{Destination:DestinationCidrBlock,IGW:GatewayId,Peering:VpcPeeringConnectionId}')
Cap 'm09' '01-alb'      'aws elbv2 describe-load-balancers' @('elbv2','describe-load-balancers','--load-balancer-arns',$s.alb,'--query','LoadBalancers[].{Nom:LoadBalancerName,Etat:State.Code,Schema:Scheme,DNS:DNSName}')
Cap 'm09' '02-targets-web' 'aws elbv2 describe-target-health (tg-web)' @('elbv2','describe-target-health','--target-group-arn',$s.tgWeb,'--query','TargetHealthDescriptions[].{Cible:Target.Id,Port:Target.Port,Etat:TargetHealth.State}')
Cap 'm09' '03-targets-app' 'aws elbv2 describe-target-health (tg-app)' @('elbv2','describe-target-health','--target-group-arn',$s.tgApp,'--query','TargetHealthDescriptions[].{Cible:Target.Id,Port:Target.Port,Etat:TargetHealth.State}')
Cap 'm09' '04-rules'    'aws elbv2 describe-rules (listener HTTPS)' @('elbv2','describe-rules','--listener-arn',$s.listener,'--query','Rules[].{Priorite:Priority,Condition:Conditions[0].Values[0],Action:Actions[0].Type}')
Cap 'm10' '01-zones'    'aws route53 list-hosted-zones' @('route53','list-hosted-zones','--query','HostedZones[?contains(Name,`leman`)].{Zone:Name,Privee:Config.PrivateZone,Enregistrements:ResourceRecordSetCount}')
Cap 'm10' '02-records'  'aws route53 list-resource-record-sets (zone publique)' @('route53','list-resource-record-sets','--hosted-zone-id',$s.zonePub,'--query','ResourceRecordSets[?Type==`A`].{Nom:Name,Politique:Failover,Id:SetIdentifier,Alias:AliasTarget.DNSName,IP:ResourceRecords[0].Value}')
Cap 'm10' '03-records-privee' 'aws route53 list-resource-record-sets (zone privee)' @('route53','list-resource-record-sets','--hosted-zone-id',$s.zonePriv,'--query','ResourceRecordSets[?Type==`A`].{Nom:Name,Valeur:ResourceRecords[0].Value}')
Cap 'm11' '01-distribution' 'aws cloudfront get-distribution' @('cloudfront','get-distribution','--id',$s.cfId,'--query','Distribution.{Id:Id,Etat:Status,Domaine:DomainName,Comportements:DistributionConfig.CacheBehaviors.Items[].PathPattern|join(`, `,@)}')
Cap 'm12' '01-alarm'    'aws cloudwatch describe-alarms' @('cloudwatch','describe-alarms','--alarm-names','alarm-5xx-portail-TP-AC','--query','MetricAlarms[].{Alarme:AlarmName,Etat:StateValue,Metrique:MetricName,Seuil:Threshold,Periode:Period,Evaluations:EvaluationPeriods}')
Cap 'm12' '02-flowlog'  'aws ec2 describe-flow-logs' @('ec2','describe-flow-logs','--filter',$tag,'--query','FlowLogs[].{Nom:Tags[?Key==`Name`]|[0].Value,Trafic:TrafficType,Destination:LogGroupName,Etat:FlowLogStatus}')
Cap 'm12' '03-sns'      'aws sns list-subscriptions-by-topic' @('sns','list-subscriptions-by-topic','--topic-arn',$s.topic,'--query','Subscriptions[].{Protocole:Protocol,Statut:SubscriptionArn}')
Cap 'm13' '01-stack'    'aws cloudformation describe-stacks' @('cloudformation','describe-stacks','--query','Stacks[?starts_with(StackName,`stack-portail`)].{Stack:StackName,Statut:StackStatus,Cree:CreationTime}')
"captures collectees"
