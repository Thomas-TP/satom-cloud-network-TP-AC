"""Genere video/demo/mNN.ps1 : une demo de terminal par module (commandes reelles, puis journaux de test reels pour ce qui n'existe plus).
Chaque element : ('note', texte) | ('cmd', commande) | ('clear',) | ('pause', ms)"""
import io, os
D = os.path.dirname(os.path.abspath(__file__))
CLOUDFRONT = 'd14byb6fexq6px.cloudfront.net'
DEMOS = {
 'm00': [('note', "Plan d'adressage et regles de nommage"),
         ('cmd', 'Get-Content docs\\00-plan-adressage.md -TotalCount 16'),
         ('pause', 1800), ('clear',),
         ('note', "Toutes nos ressources portent le tag Equipe=TP-AC"),
         ('cmd', 'aws resourcegroupstaggingapi get-resources --tag-filters Key=Equipe,Values=TP-AC --query "length(ResourceTagMappingList)"')],
 'm01': [('note', 'Module 1 : les reseaux (VPC)'),
         ('cmd', 'aws ec2 describe-vpcs --filters $F --query "Vpcs[].[$N,CidrBlock]" --output table'),
         ('pause', 1500), ('clear',),
         ('note', 'Et leurs sous-reseaux'),
         ('cmd', 'aws ec2 describe-subnets --filters $F --query "Subnets[].[$N,CidrBlock,AvailabilityZone]" --output table')],
 'm02': [('note', 'Module 2 : sortie vers Internet par la NAT'),
         ('cmd', 'aws ec2 describe-nat-gateways --filter $F --query "NatGateways[].[$N,State,NatGatewayAddresses[0].PublicIp]" --output table'),
         ('note', "app-01 n'a pas d'adresse publique : voici l'adresse qu'Internet voit"),
         ('cmd', 'ssm app-01 "curl -s https://checkip.amazonaws.com"')],
 'm03': [('note', 'Module 3 : Security Groups et NACL'),
         ('cmd', 'aws ec2 describe-security-groups --filters $F --query "SecurityGroups[].[GroupName,length(IpPermissions)]" --output table'),
         ('note', 'dev-01 -> app-01 : le port 8080 est ouvert, le 22 est ferme'),
         ('cmd', 'ssm dev-01 "curl -s -m 5 http://10.20.1.10:8080/api/health"'),
         ('cmd', 'ssm dev-01 "timeout 4 bash -c \'</dev/tcp/10.20.1.10/22\' && echo ouvert || echo ferme"')],
 'm04': [('note', 'Module 4 : Network Firewall (journal du test du 17/11, pare-feu supprime depuis)'),
         ('cmd', 'Get-Content docs\\modules\\m04\\tests.txt')],
 'm05': [('note', 'Module 5 : peering (journal du test, supprime au module 6 comme demande)'),
         ('cmd', 'Get-Content docs\\modules\\m05\\tests.txt -TotalCount 22')],
 'm06': [('note', 'Module 6 : le Transit Gateway'),
         ('cmd', 'aws ec2 describe-transit-gateway-vpc-attachments --filters $F Name=state,Values=available --query "TransitGatewayVpcAttachments[].[$N,State]" --output table'),
         ('cmd', 'aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $RTP --filters Name=state,Values=active --query "Routes[].[DestinationCidrBlock,Type]" --output table'),
         ('note', 'dev-01 joint app-01 par le Transit Gateway'),
         ('cmd', 'ssm dev-01 "curl -s -m 5 http://10.20.1.10:8080/api/health"')],
 'm07': [('note', 'Module 7 : le VPN AWS, 2 tunnels par site'),
         ('cmd', 'aws ec2 describe-vpn-connections --query "VpnConnections[].VgwTelemetry[].[OutsideIpAddress,Status]" --output table'),
         ('note', 'Cote routeur du siege (strongSwan)'),
         ('cmd', 'ssm rtr-siege "swanctl --list-sas 2>/dev/null | grep ESTABLISHED"'),
         ('cmd', 'ssm rtr-siege "ping -c 3 -I 192.168.10.10 10.20.1.10 | tail -2"'),
         ('note', 'Coupure du tunnel 1 : journal mesure'),
         ('cmd', 'Get-Content docs\\modules\\m07\\tests.txt | Select-String "interruption|T\\+10"')],
 'm08': [('note', 'Module 8 : Direct Connect Gateway (reel)'),
         ('cmd', 'aws directconnect describe-direct-connect-gateways --query "directConnectGateways[].[directConnectGatewayName,amazonSideAsn,directConnectGatewayState]" --output table'),
         ('cmd', 'aws directconnect describe-direct-connect-gateway-associations --direct-connect-gateway-id $S.dxgw --query "directConnectGatewayAssociations[].[associationState,allowedPrefixesToDirectConnectGateway[].cidr]" --output text'),
         ('note', 'Liaison simulee : sessions BGP du routeur siege'),
         ('cmd', 'ssm rtr-siege "vtysh -c \'show bgp summary\' | grep -E \'Neighbor|^169\'"'),
         ('cmd', 'ssm rtr-siege "ip route get 10.20.1.10 from 192.168.10.50 | head -1"'),
         ('note', 'Panne du DX : mesure'),
         ('cmd', 'Get-Content docs\\modules\\m08\\tests.txt | Select-String "interruption|T\\+10|T\\+40|T\\+70"')],
 'm09': [('note', 'Module 9 : load balancer'),
         ('cmd', 'aws elbv2 describe-load-balancers --names alb-prod-leman-TP-AC --query "LoadBalancers[].[LoadBalancerName,Scheme,State.Code]" --output table'),
         ('cmd', 'aws elbv2 describe-target-health --target-group-arn $S.tgWeb --query "TargetHealthDescriptions[].TargetHealth.State" --output text'),
         ('note', 'Journal des tests de panne (nginx arrete, 443 ferme)'),
         ('cmd', 'Get-Content docs\\modules\\m09\\tests.txt | Select-Object -First 12')],
 'm10': [('note', 'Module 10 : Route 53'),
         ('cmd', 'aws route53 list-hosted-zones --query "HostedZones[].[Name,Config.PrivateZone]" --output table'),
         ('cmd', 'ssm web-01 "getent hosts app.prod.leman.internal"'),
         ('cmd', 'aws route53 get-health-check-status --health-check-id $S.hc --query "[length(HealthCheckObservations[?starts_with(StatusReport.Status,\'Success\')]),length(HealthCheckObservations)]" --output text'),
         ('note', 'Bascule du DNS quand nginx est arrete (journal du test)'),
         ('cmd', 'Get-Content docs\\modules\\m10\\tests.txt | Select-String "apres 34"')],
 'm11': [('note', 'Module 11 : CloudFront, premiere requete puis deuxieme'),
         ('cmd', f'curl.exe -sI https://{CLOUDFRONT}/static/logo.png | Select-String "HTTP|X-Cache"'),
         ('cmd', f'curl.exe -sI https://{CLOUDFRONT}/static/logo.png | Select-String "HTTP|X-Cache"')],
 'm12': [('note', 'Module 12 : surveillance'),
         ('cmd', 'aws cloudwatch describe-alarms --query "MetricAlarms[?contains(AlarmName,\'TP-AC\')].[AlarmName,StateValue]" --output table'),
         ('cmd', 'aws cloudwatch list-dashboards --query "DashboardEntries[?contains(DashboardName,\'TP-AC\')].DashboardName" --output text'),
         ('note', 'Flow Logs : tentatives SSH refusees, retrouvees dans Logs Insights'),
         ('cmd', 'Get-Content docs\\modules\\m12\\tests.txt | Select-String "Flow|SSH|Insights|REJECT"')],
 'm13': [('note', 'Module 13 : CloudFormation'),
         ('cmd', 'aws cloudformation describe-stacks --query "Stacks[?contains(StackName,\'TP-AC\')].[StackName,StackStatus]" --output table'),
         ('note', 'Detection de derive, puis retour a IN_SYNC'),
         ('cmd', 'Get-Content docs\\modules\\m13\\tests.txt | Select-String "DRIFTED|IN_SYNC"')],
}
HEAD = ". '$PSScriptRoot\\term-init.ps1' | Out-Null\n"
for name, items in DEMOS.items():
    lines = []; k = 0
    for it in items:
        if it[0] == 'note': lines.append("Show-Note '" + it[1].replace("'", "''") + "'")
        elif it[0] == 'cmd': lines.append("Show-Cmd '" + it[1].replace("'", "''") + "'")
        elif it[0] == 'clear':
            k += 1; lines.append("Show-Shot '%s-%d'" % (name, k)); lines.append('Clear-Host')
        elif it[0] == 'pause': lines.append('Start-Sleep -Milliseconds %d' % it[1])
    k += 1; lines.append("Show-Shot '%s-%d'" % (name, k))
    NL = chr(10)
    io.open(os.path.join(D, name + '.ps1'), 'w', encoding='utf-8', newline=NL).write(NL.join(lines) + NL)
print('demos :', ', '.join(DEMOS))
