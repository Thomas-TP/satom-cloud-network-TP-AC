# Masque l'identifiant de compte AWS dans les preuves/documents avant publication (a lancer avant commit/partage)
$root = Join-Path $PSScriptRoot '..'
$files = Get-ChildItem $root -Recurse -Include *.txt,*.md,*.yaml -File | Where-Object { $_.FullName -notmatch '\\(state\.json|\.git)\\' -and $_.Name -ne 'state.json' }
$n = 0
foreach ($f in $files) {
  $t = [IO.File]::ReadAllText($f.FullName)
  $u = $t -replace '\b\d{12}\b(?=[:/\-]|\b)', { if ($_.Value -match '^0{12}$') { $_.Value } else { '000000000000' } }
  if ($u -ne $t) { [IO.File]::WriteAllText($f.FullName, $u); $n++ }
}
"fichiers modifies : $n"
