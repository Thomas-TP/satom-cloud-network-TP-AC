# Genere les pistes audio de la video avec VOTRE voix clonee (xAI / Grok, endpoint /v1/tts).
# Usage (dans votre propre terminal) :
#   $env:XAI_API_KEY = Read-Host "Cle xAI" -MaskInput       # la cle reste dans la memoire de CE terminal, jamais dans un fichier
#   pwsh scripts/tts_xai.ps1 -VoiceId <votre_voice_id>      # un .mp3 par fichier .txt de video/voix/
param([Parameter(Mandatory)][string]$VoiceId, [string]$Dir = "$PSScriptRoot\..\video\voix")
if (-not $env:XAI_API_KEY) { throw "Definissez d'abord `$env:XAI_API_KEY (voir l'en-tete du script)." }
Get-ChildItem $Dir -Filter *.txt | Sort-Object Name | ForEach-Object {
  $texte = (Get-Content $_.FullName -Raw -Encoding utf8).Trim()
  $body = @{ text = $texte; voice_id = $VoiceId; language = 'fr'; output_format = @{ codec = 'mp3'; sample_rate = 44100; bit_rate = 192000 } } | ConvertTo-Json -Compress -Depth 4
  $out = $_.FullName -replace '\.txt$', '.mp3'
  Invoke-WebRequest -Uri 'https://api.x.ai/v1/tts' -Method Post -Headers @{ Authorization = "Bearer $env:XAI_API_KEY" } `
    -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body)) -OutFile $out
  "OK  $($_.Name) -> $([IO.Path]::GetFileName($out))"
}
