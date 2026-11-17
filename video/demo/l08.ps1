Clear-Host
Show-Note 'Journal du test du module 8 (page 1 sur 4)'
Show-Cmd 'Get-Content docs\modules\m08\tests.txt | Select-Object -First 24' 4 600
Show-Shot 'l08-1'
Clear-Host
Show-Note 'Journal du test du module 8 (page 2 sur 4)'
Show-Cmd 'Get-Content docs\modules\m08\tests.txt | Select-Object -Skip 24 -First 25' 4 600
Show-Shot 'l08-2'
Clear-Host
Show-Note 'Journal du test du module 8 (page 3 sur 4)'
Show-Cmd 'Get-Content docs\modules\m08\tests.txt | Select-Object -Skip 49 -First 25' 4 600
Show-Shot 'l08-3'
Clear-Host
Show-Note 'Journal du test du module 8 (page 4 sur 4)'
Show-Cmd 'Get-Content docs\modules\m08\tests.txt | Select-Object -Skip 74 -First 22' 4 600
Show-Shot 'l08-4'
