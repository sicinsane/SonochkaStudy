$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
if([Windows.Forms.MessageBox]::Show('Удалить Соночка Study? Сохранения останутся на компьютере.','Соночка Study','YesNo') -ne 'Yes'){exit}
$target=[IO.Path]::GetFullPath($PSScriptRoot)
$expected=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs\SonochkaStudy'))
if($target -ne $expected){throw 'Unexpected installation directory'}
Get-Process SonochkaStudy -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq (Join-Path $target 'SonochkaStudy.exe')} | ForEach-Object {$_.CloseMainWindow()|Out-Null;$_.WaitForExit(5000)|Out-Null}
foreach($file in Get-ChildItem -LiteralPath $target -File){if($file.Extension -in @('.exe','.dll','.ps1','.cmd','.html','.wav','.ico','.txt','.md')){Remove-Item -LiteralPath $file.FullName -Force}}
foreach($link in @((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Соночка Study.lnk'),(Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Соночка Study.lnk'))){if(Test-Path -LiteralPath $link){Remove-Item -LiteralPath $link}}
Remove-Item -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\SonochkaStudy' -ErrorAction SilentlyContinue
[Windows.Forms.MessageBox]::Show('Программа удалена. Данные сохранены в LocalAppData\SonochkaStudy\UserData.','Соночка Study')|Out-Null
