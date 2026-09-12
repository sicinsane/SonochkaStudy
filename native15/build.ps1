$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$app=Join-Path $repo 'app'
$sdk=Join-Path $PSScriptRoot 'sdk'
if(-not(Test-Path (Join-Path $sdk 'lib/net462/Microsoft.Web.WebView2.Core.dll'))){
 $package=Join-Path $PSScriptRoot 'webview.zip'
 Invoke-WebRequest 'https://api.nuget.org/v3-flatcontainer/microsoft.web.webview2/1.0.4191.47/microsoft.web.webview2.1.0.4191.47.nupkg' -OutFile $package
 if((Get-FileHash $package -Algorithm SHA256).Hash -ne 'F492BBF547D0DA329553B6727435B677579B1E9F91CC9E4A1AD029366D5F23D0'){throw 'WebView2 SDK checksum mismatch'}
 Expand-Archive $package $sdk -Force
}
Copy-Item (Join-Path $sdk 'lib/net462/Microsoft.Web.WebView2.Core.dll'),(Join-Path $sdk 'lib/net462/Microsoft.Web.WebView2.WinForms.dll'),(Join-Path $sdk 'runtimes/win-x64/native/WebView2Loader.dll') $app
Copy-Item (Join-Path $PSScriptRoot 'SonaStudy.ico') $app
Get-ChildItem $app -Filter *.ps1 | ForEach-Object {
 $content=[IO.File]::ReadAllText($_.FullName);[IO.File]::WriteAllText($_.FullName,$content,[Text.UTF8Encoding]::new($true))
 $tokens=$null;$errors=$null;[Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors)|Out-Null;if($errors){throw $errors}
}
$compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
& $compiler /nologo /codepage:65001 /target:winexe /platform:x64 ("/out:"+(Join-Path $app 'SonochkaStudy.exe')) ("/win32icon:"+(Join-Path $app 'SonaStudy.ico')) /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll ("/reference:"+(Join-Path $app 'Microsoft.Web.WebView2.Core.dll')) ("/reference:"+(Join-Path $app 'Microsoft.Web.WebView2.WinForms.dll')) (Join-Path $PSScriptRoot 'Program.cs')
if($LASTEXITCODE){throw 'Native build failed'}
$release=Join-Path $repo 'release15';New-Item -ItemType Directory $release -Force|Out-Null
$stage=Join-Path $PSScriptRoot ('stage-'+[guid]::NewGuid().ToString('N'));New-Item -ItemType Directory $stage|Out-Null
Get-ChildItem $app -File | Where-Object {$_.Extension -in @('.ps1','.cmd','.html','.wav','.ico','.exe','.dll','.md','.txt') -and $_.Name -notlike 'self-test*'} | Copy-Item -Destination $stage
Copy-Item (Join-Path $repo 'release-notes/v15.0.0.md') (Join-Path $stage 'CHANGELOG-15.0.0.md')
$payload=Join-Path $release 'SonochkaStudy-update.zip'
Compress-Archive (Join-Path $stage '*') $payload -Force
Copy-Item $payload (Join-Path $release 'SonochkaStudy-v15.0.0-portable.zip')
$installer=Join-Path $PSScriptRoot 'installer.ps1';[IO.File]::WriteAllText($installer,[IO.File]::ReadAllText($installer),[Text.UTF8Encoding]::new($true))
& $compiler /nologo /codepage:65001 /target:winexe /platform:x64 ("/out:"+(Join-Path $release 'SonochkaStudySetup.exe')) ("/win32icon:"+(Join-Path $app 'SonaStudy.ico')) /reference:System.Windows.Forms.dll ("/resource:"+$payload+',payload.zip') ("/resource:"+$installer+',installer.ps1') ("/resource:"+(Join-Path $app 'SonaStudy.ico')+',SonaStudy.ico') (Join-Path $PSScriptRoot 'Setup.cs')
if($LASTEXITCODE){throw 'Installer build failed'}
Get-ChildItem $release -File | Select-Object Name,Length
