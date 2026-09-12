function Get-YandexBrowserPath {
  $paths=@(
    "$env:LOCALAPPDATA\Yandex\YandexBrowser\Application\browser.exe",
    "$env:ProgramFiles\Yandex\YandexBrowser\Application\browser.exe",
    "${env:ProgramFiles(x86)}\Yandex\YandexBrowser\Application\browser.exe"
  )
  foreach($key in @('HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\browser.exe','HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\browser.exe','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\browser.exe')){
    try {$path=(Get-Item -LiteralPath $key -ErrorAction Stop).GetValue('');if($path -match '(?i)Yandex'){$paths+=(''+$path).Trim('"')}}catch{}
  }
  foreach($path in $paths){if(Test-Path -LiteralPath $path -PathType Leaf){return $path}}
  return $null
}
function Open-YandexLink([string]$Url){
  $uri=$null
  if(-not [Uri]::TryCreate($Url,[UriKind]::Absolute,[ref]$uri) -or $uri.Scheme -notin @('https','http') -or $uri.UserInfo){throw 'Only HTTP/HTTPS links are supported.'}
  $browser=Get-YandexBrowserPath
  if(-not $browser){throw 'Yandex Browser is not installed.'}
  $safeUrl=$uri.AbsoluteUri.Replace('"','%22')
  Start-Process -FilePath $browser -ArgumentList ('"'+$safeUrl+'"') | Out-Null
  return @{ok=$true}
}
