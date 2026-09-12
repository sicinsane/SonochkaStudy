$ErrorActionPreference='Stop'
$testRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$source=(Get-Content (Join-Path $testRoot 'app/Launch.ps1') -Raw)
$source=$source.Replace('$appRoot=Split-Path -Parent $MyInvocation.MyCommand.Path',"`$appRoot='$($testRoot.Replace("'","''"))\app'")
$source=$source.Replace("  `$browser=Get-YandexBrowserPath","  function Get-YandexBrowserPath { return 'C:\Mock Yandex\browser.exe' }; `$browser=Get-YandexBrowserPath")
$script:launchCalls=@()
function Start-Process {param($FilePath,$ArgumentList,$WindowStyle,$WorkingDirectory);$script:launchCalls+=@{FilePath=$FilePath;Arguments=$ArgumentList}}
function Invoke-RestMethod {return @{connected=$true;appVersion='14.2.1'}}
. ([scriptblock]::Create($source))
$appCall=$script:launchCalls | Where-Object FilePath -eq 'C:\Mock Yandex\browser.exe' | Select-Object -Last 1
if($appCall.Arguments -notmatch '^--app="file:///.*SonaStudy.html" --start-maximized$'){throw 'App mode arguments are incorrect'}
if($appCall.Arguments -match 'user-data-dir|profile-directory'){throw 'Browser profile changed'}
Open-YandexLink 'https://example.org/path?x=1&y=two' | Out-Null
$link=$script:launchCalls[-1]
if($link.FilePath -ne 'C:\Mock Yandex\browser.exe' -or $link.Arguments -ne '"https://example.org/path?x=1&y=two"'){throw 'Link routing failed'}
$rejected=$false;try{Open-YandexLink 'file:///C:/Windows/notepad.exe'|Out-Null}catch{$rejected=$true}
if(-not $rejected){throw 'Local command accepted as external link'}
Write-Output 'PASS: Yandex app window arguments, unchanged file URL/profile, Yandex external links, invalid scheme rejected'
