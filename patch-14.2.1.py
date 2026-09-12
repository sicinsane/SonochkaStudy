from pathlib import Path
import shutil
root=Path(__file__).parent
p=root/'app'
for src,dest in [('BrowserSupport.ps1','BrowserSupport.ps1'),('Launch-14.2.1.ps1','Launch.ps1')]:
 text=(root/'release-tools'/src).read_text(encoding='utf-8-sig')
 (p/dest).write_text(text,encoding='utf-8-sig')
b=(p/'SonaMusicBridge.ps1').read_text(encoding='utf-8-sig').replace('14.2.0','14.2.1')
b=b.replace("$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path", "$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path\n. (Join-Path $AppRoot 'BrowserSupport.ps1')\n$script:artReadError=''; $script:artDownloadError=''")
# Preserve browser-supported artwork, including WebP, instead of requiring GDI to decode it.
start=b.index('    # Normalize Windows artwork')
end=b.index('    $script:coverSuccessAt=Get-Date',start)
b=b[:start]+'''    $mime=''
    if($bytes.Length -ge 12){
      if($bytes[0]-eq 137 -and $bytes[1]-eq 80 -and $bytes[2]-eq 78){$mime='image/png'}
      elseif($bytes[0]-eq 255 -and $bytes[1]-eq 216){$mime='image/jpeg'}
      elseif([Text.Encoding]::ASCII.GetString($bytes,0,3)-eq 'GIF'){$mime='image/gif'}
      elseif([Text.Encoding]::ASCII.GetString($bytes,8,4)-eq 'WEBP'){$mime='image/webp'}
    }
    if($mime){$data='data:'+$mime+';base64,'+[Convert]::ToBase64String($bytes)}
    else {
      $memory=[IO.MemoryStream]::new($bytes,$false);$decoded=$null;$output=[IO.MemoryStream]::new()
      try{$decoded=[Drawing.Image]::FromStream($memory);$decoded.Save($output,[Drawing.Imaging.ImageFormat]::Png);$data='data:image/png;base64,'+[Convert]::ToBase64String($output.ToArray())}
      finally{if($decoded){$decoded.Dispose()};$memory.Dispose();$output.Dispose()}
    }
    $script:artReadError=''
'''+b[end:]
b=b.replace('$script:coverFailAt = Get-Date',"$script:artReadError=$_.Exception.Message; $script:coverFailAt = Get-Date")
b=b.replace('Select-Object -First 8','Select-Object -First 20')
insert='''
$script:downloadArtKey=''; $script:downloadArtData=''; $script:downloadArtAt=[DateTime]::MinValue
function Get-DownloadedCover([string]$Url){
  if(-not $Url){return ''}
  if($script:downloadArtKey -eq $Url -and ((Get-Date)-$script:downloadArtAt).TotalSeconds -lt $(if($script:downloadArtData){600}else{10})){return $script:downloadArtData}
  $script:downloadArtKey=$Url;$script:downloadArtData='';$script:downloadArtAt=Get-Date
  try{
    $uri=[Uri]$Url
    if($uri.Scheme -ne 'https' -or $uri.Host -notmatch '(^|\\.)yandex\\.(net|ru)$'){throw 'Unsupported artwork host'}
    $response=Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 5 -Headers @{'User-Agent'='SonochkaStudy/14.2.1'}
    $mime=(''+$response.Headers['Content-Type']).Split(';')[0]
    if($mime -notin @('image/jpeg','image/png','image/webp','image/gif')){throw 'Invalid artwork response'}
    $memory=[IO.MemoryStream]::new()
    try{$response.RawContentStream.Position=0;$response.RawContentStream.CopyTo($memory);$bytes=$memory.ToArray()}finally{$memory.Dispose()}
    if($bytes.Length -le 0 -or $bytes.Length -gt 16777216){throw 'Invalid artwork length'}
    $script:downloadArtData='data:'+$mime+';base64,'+[Convert]::ToBase64String($bytes)
    $script:artDownloadError=''
    return $script:downloadArtData
  }catch{$script:artDownloadError=$_.Exception.Message;return ''}
}
'''
b=b.replace('function Get-StatusObject {',insert+'\nfunction Get-StatusObject {')
b=b.replace("$coverUrl = ''; if (-not $cover) { $coverUrl = Get-YandexCoverUrl $title $artist $key }", "$coverUrl = ''; if (-not $cover) { $coverUrl = Get-YandexCoverUrl $title $artist $key; $cover=Get-DownloadedCover $coverUrl }")
b=b.replace("if (-not [string]::IsNullOrWhiteSpace($cover)) { $coverSource = 'windows' }", "if (-not [string]::IsNullOrWhiteSpace($cover)) { $coverSource = $(if($coverUrl){'yandex'}else{'windows'}) }")
b=b.replace("cover=$cover; coverUrl=$coverUrl; coverSource=$coverSource;", "cover=$cover; coverUrl=$coverUrl; coverSource=$coverSource; coverError=$script:artReadError; coverDownloadError=$script:artDownloadError;")
b=b.replace("      while (($line = $reader.ReadLine()) -ne $null -and $line -ne '') { }", "      $requestOrigin=''; while (($line = $reader.ReadLine()) -ne $null -and $line -ne '') { if($line -match '^Origin:\\s*(.*)$'){$requestOrigin=$Matches[1]} }")
b=b.replace("        '/status'", "        '/open-link' { try { if($method -ne 'POST' -or $requestOrigin -notin @('','null')){throw 'Local app POST required'}; Write-HttpJson $stream (Open-YandexLink (Get-QueryValue $target 'url')) } catch { Write-HttpJson $stream @{ok=$false;error=$_.Exception.Message} 400 } }\n        '/status'")
b=b.replace('Access-Control-Allow-Methods: GET, OPTIONS','Access-Control-Allow-Methods: GET, POST, OPTIONS')
(p/'SonaMusicBridge.ps1').write_text(b,encoding='utf-8-sig')
h=(p/'SonaStudy.html').read_text(encoding='utf-8-sig').replace('14.2.0','14.2.1')
h=h.replace('function renderYBridge(s){',"let lastArtworkStatus=null;\nfunction renderYBridge(s){\n  lastArtworkStatus=s;")
h=h.replace('function copyDiagnostics(){const lines=[',"function copyDiagnostics(){const lines=[`Медиамост: ${lastArtworkStatus?.appVersion||'нет связи'}`,`Обложка: ${lastArtworkStatus?.coverSource||'нет'}; байт строки: ${lastArtworkStatus?.cover?.length||0}`,`Ошибка обложки: ${lastArtworkStatus?.coverError||lastArtworkStatus?.coverDownloadError||'нет'}`,`Изображение: ${$('#ymDesktopCover')?.naturalWidth||0} px`,")
h=h.replace("if(img.dataset.artKey===key&&img.getAttribute('src'))return;", "if(img.dataset.artKey===key&&img.getAttribute('src')){if(img.complete&&img.naturalWidth>0)on?.();return;}")
h=h.replace("async function refreshYBridge(){try{renderYBridge(await yBridge('/status'))}catch(e){renderYBridge(null)}}", "let mediaPollBusy=false;async function refreshYBridge(){if(mediaPollBusy)return;mediaPollBusy=true;try{renderYBridge(await yBridge('/status'))}catch(e){renderYBridge(null)}finally{mediaPollBusy=false}}")
external='''
async function openExternalInYandex(url){
  try{
    const parsed=new URL(url);if(!['https:','http:'].includes(parsed.protocol))return;
    const response=await fetch(YANDEX_BRIDGE+'/open-link?url='+encodeURIComponent(parsed.href),{method:'POST',signal:AbortSignal.timeout(8000)});
    const result=await response.json();if(!result.ok)throw new Error();
  }catch(e){toast('Не удалось открыть Яндекс Браузер. Запусти Соночка Study через EXE.');}
}
function handleExternalLink(event){
  if(event.defaultPrevented||event.target.closest('button,input'))return;
  const link=event.target.closest('a[href]');if(!link||!/^https?:/i.test(link.href))return;
  if(event.type==='auxclick'&&event.button!==1)return;
  event.preventDefault();openExternalInYandex(link.href);
}
document.addEventListener('click',handleExternalLink);
document.addEventListener('auxclick',handleExternalLink);
'''
h=h.replace("runBeautifulLoader();$('#pageTitle')",external+"\nrunBeautifulLoader();$('#pageTitle')")
(p/'SonaStudy.html').write_text(h,encoding='utf-8-sig')
(p/'version.txt').write_text('14.2.1\n')
u=(p/'SonaUpdater.ps1').read_text(encoding='utf-8-sig').replace("'SonaStudy.html','SonaMusicBridge.ps1'","'BrowserSupport.ps1','SonaStudy.html','SonaMusicBridge.ps1'")
(p/'SonaUpdater.ps1').write_text(u,encoding='utf-8-sig')

