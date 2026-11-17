Clear-Host
Show-Note 'Journal du test du module 1 (page 1 sur 2)'
Show-Cmd 'Get-Content docs\modules\m01\tests.txt | Select-Object -First 19' 4 600
Show-Shot 'l01-1'
Clear-Host
Show-Note 'Journal du test du module 1 (page 2 sur 2)'
Show-Cmd 'Get-Content docs\modules\m01\tests.txt | Select-Object -Skip 19 -First 1' 4 600
Show-Shot 'l01-2'
