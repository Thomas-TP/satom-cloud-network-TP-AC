Show-Note 'Module 13 : CloudFormation'
Show-Cmd 'aws cloudformation describe-stacks --query "Stacks[?contains(StackName,''TP-AC'')].[StackName,StackStatus]" --output table'
Show-Note 'Detection de derive, puis retour a IN_SYNC'
Show-Cmd 'Get-Content docs\modules\m13\tests.txt | Select-String "DRIFTED|IN_SYNC"'
