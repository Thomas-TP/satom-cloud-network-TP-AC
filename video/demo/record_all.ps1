# Enregistre toutes les demos de terminal (une vraie fenetre PowerShell par module). Dure environ 12 minutes.
Set-Location C:\Perso\AWS
$rec = 'C:\Perso\AWS\video\demo\record.ps1'
function Rec($m) { "=== $m  $(Get-Date -Format HH:mm:ss)"; pwsh -NoProfile -File $rec -Demo "$m.ps1" -Out "C:\Perso\AWS\video\clips\$m.mp4" 2>&1 | Select-Object -Last 3 }
foreach ($m in 'm00','m01','m02','m03','m04','m05','m06') { Rec $m }
Rec 'm08'                                                  # le siege est deja en configuration BGP
pwsh -NoProfile -File C:\Perso\AWS\video\demo\prep.ps1 -Module m07 | Out-Null
Rec 'm07'
pwsh -NoProfile -File C:\Perso\AWS\video\demo\prep.ps1 -Module m08 | Out-Null   # on remet le siege comme apres le module 8
foreach ($m in 'm09','m10') { Rec $m }
pwsh -NoProfile -File C:\Perso\AWSideo\demo\prep.ps1 -Module m11 | Out-Null
foreach ($m in 'm11','m12','m13') { Rec $m }
'TERMINE'
