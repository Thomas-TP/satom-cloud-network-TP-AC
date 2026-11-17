Clear-Host
Show-Note 'Journal du test du module 13 (page 1 sur 2)'
Show-Cmd 'Get-Content docs\modules\m13\tests.txt | Select-Object -First 23' 4 600
Show-Shot 'l13-1'
Clear-Host
Show-Note 'Journal du test du module 13 (page 2 sur 2)'
Show-Cmd 'Get-Content docs\modules\m13\tests.txt | Select-Object -Skip 23 -First 15' 4 600
Show-Shot 'l13-2'
