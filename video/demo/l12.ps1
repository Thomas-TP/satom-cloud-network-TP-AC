Clear-Host
Show-Note 'Journal du test du module 12 (page 1 sur 2)'
Show-Cmd 'Get-Content docs\modules\m12\tests.txt | Select-Object -First 21' 4 600
Show-Shot 'l12-1'
Clear-Host
Show-Note 'Journal du test du module 12 (page 2 sur 2)'
Show-Cmd 'Get-Content docs\modules\m12\tests.txt | Select-Object -Skip 21 -First 17' 4 600
Show-Shot 'l12-2'
