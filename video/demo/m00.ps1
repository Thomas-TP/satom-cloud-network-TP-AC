Show-Note 'Plan d''adressage et regles de nommage'
Show-Cmd 'Get-Content docs\00-plan-adressage.md -TotalCount 16'
Start-Sleep -Milliseconds 1800
Show-Shot 'm00-1'
Clear-Host
Show-Note 'Toutes nos ressources portent le tag Equipe=TP-AC'
Show-Cmd 'aws resourcegroupstaggingapi get-resources --tag-filters Key=Equipe,Values=TP-AC --query "length(ResourceTagMappingList)"'
Show-Shot 'm00-2'
