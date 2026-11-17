Clear-Host
Show-Note 'Journal du test du module 7 (page 1 sur 4)'
Show-Cmd 'Get-Content docs\modules\m07\tests.txt | Select-Object -First 23' 4 600
Show-Shot 'l07-1'
Clear-Host
Show-Note 'Journal du test du module 7 (page 2 sur 4)'
Show-Cmd 'Get-Content docs\modules\m07\tests.txt | Select-Object -Skip 23 -First 25' 4 600
Show-Shot 'l07-2'
Clear-Host
Show-Note 'Journal du test du module 7 (page 3 sur 4)'
Show-Cmd 'Get-Content docs\modules\m07\tests.txt | Select-Object -Skip 48 -First 25' 4 600
Show-Shot 'l07-3'
Clear-Host
Show-Note 'Journal du test du module 7 (page 4 sur 4)'
Show-Cmd 'Get-Content docs\modules\m07\tests.txt | Select-Object -Skip 73 -First 22' 4 600
Show-Shot 'l07-4'
