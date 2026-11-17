Show-Note 'Module 2 : sortie vers Internet par la NAT'
Show-Cmd 'aws ec2 describe-nat-gateways --filter $F --query "NatGateways[].[$N,State,NatGatewayAddresses[0].PublicIp]" --output table'
Show-Note 'app-01 n''a pas d''adresse publique : voici l''adresse qu''Internet voit'
Show-Cmd 'ssm app-01 "curl -s https://checkip.amazonaws.com"'
