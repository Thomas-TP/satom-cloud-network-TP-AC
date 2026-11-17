# Rejoue tous les tests des modules 4, 6, 7 et 8 sur le deploiement fait par le modele CloudFormation (environ 35 minutes).
$ErrorActionPreference = 'Continue'
$here = $PSScriptRoot
foreach ($step in @(
    @('m04-tests.ps1'), @('m06-tests.ps1'),
    @('m07-vpn-aws.ps1', '-Stage', '2'), @('m07-vpn-aws.ps1', '-Stage', '3'), @('m07-vpn-aws.ps1', '-Stage', '4'),
    @('m08-dx-sim.ps1'))) {
  "=== $($step -join ' ')  $(Get-Date -Format HH:mm:ss)"
  & pwsh -NoProfile -File (Join-Path $here $step[0]) @($step | Select-Object -Skip 1) 2>&1 | Out-Null
}
"TERMINE $(Get-Date -Format HH:mm:ss)"
