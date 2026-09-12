$ErrorActionPreference='Stop'
$appRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
try {
  . (Join-Path $appRoot 'BrowserSupport.ps1')
  $browser=Get-YandexBrowserPath
  if(-not $browser){throw 'Не найден Яндекс Браузер. Установи его и повторно открой SonochkaStudy.exe.'}
  $html=Join-Path $appRoot 'SonaStudy.html'
  if(-not(Test-Path -LiteralPath $html)){throw 'Распакуй весь архив приложения перед запуском EXE.'}
  # Reuse the Yandex profile and exact file URL that hold the existing study data.
  $appUrl=([Uri]$html).AbsoluteUri
  $expected=(Get-Content (Join-Path $appRoot 'version.txt') -Raw).Trim()
  try {
    $running=Invoke-RestMethod 'http://127.0.0.1:8765/status' -TimeoutSec 2
    if($running.connected -and $running.appVersion -ne $expected){
      Invoke-RestMethod 'http://127.0.0.1:8765/shutdown' -TimeoutSec 2 | Out-Null
      Start-Sleep -Milliseconds 700
    }
  }catch{}
  function Start-StudyHelper([string]$command){
    $encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    Start-Process -FilePath "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-EncodedCommand',$encoded) -WorkingDirectory $appRoot | Out-Null
  }
  $bridge=(Join-Path $appRoot 'SonaMusicBridge.ps1').Replace("'","''")
  Start-StudyHelper ("& '"+$bridge+"'")
  $chime=Join-Path $appRoot 'startup-chime.wav'
  if(Test-Path -LiteralPath $chime){Start-StudyHelper ("[System.Media.SoundPlayer]::new('"+$chime.Replace("'","''")+"').PlaySync()")}
  Start-Process -FilePath $browser -ArgumentList ('--app="'+$appUrl+'" --start-maximized') -WorkingDirectory $appRoot | Out-Null
}catch{
  try{Add-Type -AssemblyName System.Windows.Forms;[Windows.Forms.MessageBox]::Show($_.Exception.Message,'Соночка Study')|Out-Null}catch{}
  exit 1
}
