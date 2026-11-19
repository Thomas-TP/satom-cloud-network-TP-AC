# Lance un Chrome Beta DEDIE au tournage (profil separe, port de debogage 9333). La connexion AWS se fait a la main dans cette fenetre.
$chrome = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'
$profile = 'C:\Perso\AWS\video\rig\profile'
New-Item -ItemType Directory -Force $profile | Out-Null
$argsList = @("--remote-debugging-port=9333", "--user-data-dir=$profile", "--lang=fr", "--accept-lang=fr-FR,fr", "--window-size=1920,1080", "--window-position=0,0",
  "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding", "--disable-background-timer-throttling", "--no-first-run", "--no-default-browser-check",
  "--disable-features=Translate", "https://console.aws.amazon.com/")
Start-Process $chrome -ArgumentList $argsList
