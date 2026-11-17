Clear-Host
Show-Note 'Journal du test du module 11 (page 1 sur 2)'
Show-Cmd 'Get-Content docs\modules\m11\tests.txt | Select-Object -First 25' 4 600
Show-Shot 'l11-1'
Clear-Host
Show-Note 'Journal du test du module 11 (page 2 sur 2)'
Show-Cmd 'Get-Content docs\modules\m11\tests.txt | Select-Object -Skip 25 -First 6' 4 600
Show-Shot 'l11-2'
