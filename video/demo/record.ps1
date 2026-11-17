# Enregistre une demo dans une VRAIE fenetre PowerShell (conhost) avec ffmpeg (capture de la fenetre).
# Usage : pwsh video\demo\record.ps1 -Demo m01.ps1 -Out ..\clips\m01.mp4
param([Parameter(Mandatory)][string]$Demo, [string]$Out = '', [string]$ShotDir = 'C:\Perso\AWS\captures\_shots')
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$env:Path += ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"
$title = 'Satom Cloud Network - TP-AC'
$done = Join-Path $env:TEMP 'tpac-demo-done.flag'; Remove-Item $done -ErrorAction SilentlyContinue
$demoPath = if ([IO.Path]::IsPathRooted($Demo)) { $Demo } else { Join-Path $here $Demo }
$noVideo = -not $Out
if ($noVideo) { $Out = Join-Path $env:TEMP 'tpac-novideo.mp4' }
$outPath = if ([IO.Path]::IsPathRooted($Out)) { $Out } else { [IO.Path]::GetFullPath((Join-Path (Get-Location) $Out)) }; New-Item -ItemType Directory -Force (Split-Path $outPath) | Out-Null

# fenetre console reelle (conhost), pas Windows Terminal
$cmdline = "pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -Command `". '$here\term-init.ps1'; Initialize-Term '$title'; . '$demoPath'; New-Item -ItemType File -Force '$done' | Out-Null; Start-Sleep 4`""
$proc = Start-Process conhost.exe -ArgumentList $cmdline -WorkingDirectory 'C:\Perso\AWS' -PassThru
$win = $null
for ($i = 0; $i -lt 60 -and -not $win; $i++) { Start-Sleep -Milliseconds 500; $win = Get-Process | Where-Object { $_.MainWindowTitle -eq $title } | Select-Object -First 1 }
if (-not $win) { throw 'fenetre du terminal introuvable' }
Start-Sleep -Milliseconds 800   # le temps que Initialize-Term ait pose la police et la taille

$psi = New-Object Diagnostics.ProcessStartInfo; $psi.FileName = 'ffmpeg'
$psi.Arguments = "-y -loglevel error -f gdigrab -framerate 30 -draw_mouse 0 -i title=`"$title`" -vf `"scale=trunc(iw/2)*2:trunc(ih/2)*2`" -c:v libx264 -preset veryfast -crf 14 -pix_fmt yuv420p -movflags frag_keyframe+empty_moov `"$outPath`""
$psi.RedirectStandardInput = $true; $psi.UseShellExecute = $false
$ff = [Diagnostics.Process]::Start($psi)
# la demo recommence a l'ecran propre : on attend son signal de fin
$t0 = Get-Date
$req = Join-Path $env:TEMP 'tpac-shot.req'; Remove-Item $req -ErrorAction SilentlyContinue
while (-not (Test-Path $done) -and ((Get-Date) - $t0).TotalSeconds -lt 900) {
  if (Test-Path $req) {
    $name = (Get-Content $req -Raw).Trim(); $png = Join-Path $ShotDir ($name + '.png'); New-Item -ItemType Directory -Force (Split-Path $png) | Out-Null
    & ffmpeg -y -loglevel error -f gdigrab -framerate 5 -draw_mouse 0 -i "title=$title" -frames:v 1 -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" $png
    Remove-Item $req -ErrorAction SilentlyContinue
  }
  Start-Sleep -Milliseconds 200
}
Start-Sleep -Milliseconds 1200
$ff.StandardInput.WriteLine('q'); $ff.WaitForExit(20000) | Out-Null
if (-not $ff.HasExited) { $ff.Kill() }
Start-Sleep -Milliseconds 500
Get-Process | Where-Object { $_.MainWindowTitle -eq $title } | Stop-Process -Force -ErrorAction SilentlyContinue
$d = & ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 $outPath
"enregistre : $outPath"; $d

