# Prepare une VRAIE fenetre PowerShell (conhost) pour l'enregistrement video : police lisible, taille fixe, position fixe,
# pas de selection a la souris (QuickEdit coupe). A dot-sourcer au debut de chaque demo : . .\term-init.ps1
Add-Type @'
using System; using System.Runtime.InteropServices;
public class TpacCon {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct CFI { public int cbSize; public int nFont; public short X; public short Y; public int FontFamily; public int FontWeight;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string FaceName; }
  [DllImport("kernel32.dll", SetLastError = true)] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref CFI i);
  [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int n);
  [DllImport("kernel32.dll")] public static extern bool GetConsoleMode(IntPtr h, out int m);
  [DllImport("kernel32.dll")] public static extern bool SetConsoleMode(IntPtr h, int m);
  [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int w, int cx, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
'@
$script:TermCols = 120; $script:TermRows = 31
function Initialize-Term($title = 'Satom Cloud Network - TP-AC', $fontPx = 19) {
  $h = [TpacCon]::GetStdHandle(-11)
  $fi = New-Object TpacCon+CFI; $fi.cbSize = [Runtime.InteropServices.Marshal]::SizeOf($fi); $fi.FaceName = 'Consolas'; $fi.FontFamily = 54; $fi.FontWeight = 400; $fi.Y = $fontPx
  [void][TpacCon]::SetCurrentConsoleFontEx($h, $false, [ref]$fi)
  $raw = $Host.UI.RawUI
  $raw.BufferSize = New-Object Management.Automation.Host.Size($script:TermCols, 3000)
  $raw.WindowSize = New-Object Management.Automation.Host.Size($script:TermCols, $script:TermRows)
  $raw.BackgroundColor = 'Black'; $raw.ForegroundColor = 'Gray'; $raw.WindowTitle = $title
  $hin = [TpacCon]::GetStdHandle(-10); $m = 0; [void][TpacCon]::GetConsoleMode($hin, [ref]$m)
  [void][TpacCon]::SetConsoleMode($hin, (($m -bor 0x80) -band (-bnot 0x40)))   # QuickEdit coupe
  $hw = [TpacCon]::GetConsoleWindow(); [void][TpacCon]::SetWindowPos($hw, [IntPtr]::Zero, 20, 10, 0, 0, 0x0001 -bor 0x0004)   # position, sans changer la taille
  Clear-Host
}
function Show-Prompt { Write-Host -NoNewline 'PS' -ForegroundColor Cyan; Write-Host -NoNewline '> ' -ForegroundColor DarkGray }
# Affiche une commande "tapee" puis l'execute pour de vrai.
function Show-Cmd([string]$cmd, [int]$typeMs = 18, [int]$pauseAfterMs = 900) {
  Show-Prompt
  foreach ($c in $cmd.ToCharArray()) { Write-Host -NoNewline $c -ForegroundColor White; Start-Sleep -Milliseconds $typeMs }
  Start-Sleep -Milliseconds 350; Write-Host ''
  Invoke-Expression $cmd
  Start-Sleep -Milliseconds $pauseAfterMs
}
# Commentaire de section (en vert), comme une legende dans le terminal.
function Show-Note([string]$t, [int]$ms = 700) { Write-Host ''; Write-Host "# $t" -ForegroundColor Green; Start-Sleep -Milliseconds $ms }

# --- raccourcis pour garder des commandes lisibles a l'ecran ---
$env:AWS_PROFILE = 'TP-AC'; $env:AWS_DEFAULT_REGION = 'eu-north-1'; $env:AWS_PAGER = ''
$F = 'Name=tag:Equipe,Values=TP-AC'                 # filtre : seulement nos ressources
$N = 'Tags[?Key==`Name`]|[0].Value'                 # lit le tag Name
$S = (Get-Content 'C:\Perso\AWS\scripts\state.json' -Raw | ConvertFrom-Json)
$RTP = $S.tgwRtProd
$script:Ids = @{ 'app-01'=$S.app; 'web-01'=$S.web; 'dev-01'=$S.dev; 'rtr-siege'=$S.rtrSiege; 'rtr-agence'=$S.rtrAgence; 'rtr-aws'=$S.rtrAws }
# ssm : execute une commande sur une instance (Session Manager, sans SSH) et affiche sa sortie
function ssm([string]$vm, [string]$cmd) {
  $json = @{ commands = @($cmd) } | ConvertTo-Json -Compress
  $f = Join-Path $env:TEMP "ssm-demo.json"; [IO.File]::WriteAllText($f, $json)
  $id = $script:Ids[$vm]
  $cid = aws ssm send-command --instance-ids $id --document-name AWS-RunShellScript --parameters "file://$f" --query Command.CommandId --output text
  for ($i = 0; $i -lt 40; $i++) { Start-Sleep 2; $st = aws ssm get-command-invocation --command-id $cid --instance-id $id --query Status --output text 2>$null; if ($st -in 'Success','Failed','TimedOut') { break } }
  (aws ssm get-command-invocation --command-id $cid --instance-id $id --query StandardOutputContent --output text) -split "`n" | Where-Object { $_ -notmatch "^plugin '" -and $_.Trim() }
}
