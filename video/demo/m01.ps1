Show-Note 'Module 1 : les reseaux (VPC)'
Show-Cmd 'aws ec2 describe-vpcs --filters $F --query "Vpcs[].[$N,CidrBlock]" --output table'
Start-Sleep -Milliseconds 1500
Show-Shot 'm01-1'
Clear-Host
Show-Note 'Et leurs sous-reseaux'
Show-Cmd 'aws ec2 describe-subnets --filters $F --query "Subnets[].[$N,CidrBlock,AvailabilityZone]" --output table'
Show-Shot 'm01-2'
