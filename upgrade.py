from pathlib import Path
import math, wave, struct
p=Path(__file__).parent/'app'
h=(p/'SonaStudy.html').read_text(encoding='utf-8-sig')
h=h.replace('14.1.3','14.2.0')
h=h.replace("  obj.tasks=obj.tasks.filter(t=>t&&['debt','homework'].includes(t.type));",'')
h=h.replace('  delete obj.grades;','')
h=h.replace("  try{localStorage.setItem(STORAGE_KEY,JSON.stringify(obj))}catch(e){}",'')
h=h.replace("const raw=localStorage.getItem(STORAGE_KEY);return normalizeData", "const raw=localStorage.getItem(STORAGE_KEY);try{if(raw&&!localStorage.getItem('sonaStudyBackupBeforeV142'))localStorage.setItem('sonaStudyBackupBeforeV142',raw)}catch(e){}return normalizeData")
h=h.replace('JSON.stringify(data,null,2)',"JSON.stringify({...data,__sonaStorage:Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('sona')&&!k.includes('BackupBefore')).map(k=>[k,localStorage.getItem(k)]))},null,2)")
h=h.replace('data=normalizeData(obj);save();',"const settings=obj.__sonaStorage;delete obj.__sonaStorage;if(settings&&typeof settings==='object')for(const [k,v] of Object.entries(settings))if(k.startsWith('sona')&&k!==STORAGE_KEY&&typeof v==='string')localStorage.setItem(k,v);data=normalizeData(obj);save();")
h=h.replace("const tasks=data.tasks.filter(t=>['homework','debt'].includes(t.type));","const tasks=data.tasks;")
h=h.replace("if(result.updateAvailable){pendingUpdate", "if(compareVersions(result.version,APP_VERSION)>0){pendingUpdate")
h=h.replace("if(isAuto&&bridgeOk&&$('#autoUpdateToggle')?.checked)setTimeout(installUpdate,700)","showStartupUpdate(result,bridgeOk)")
h=h.replace("setTimeout(()=>checkForUpdates(true),4200)","setTimeout(()=>checkForUpdates(true),300)")
h=h.replace("const c=new AbortController(),t=setTimeout(()=>c.abort(),5000);","const c=new AbortController(),t=setTimeout(()=>c.abort(),path.startsWith('/update/')?18000:10000);")
h=h.replace("loader.classList.add('done');setTimeout(()=>loader.remove(),700)","if(!document.getElementById('startupUpdate')){loader.classList.add('done');setTimeout(()=>loader.remove(),700)}")
h=h.replace("const applyCover=(img,on,off)=>", "const applyCoverLegacy=(img,on,off)=>")
h=h.replace("applyCover(cover,", "applyCover(cover,primaryArt,fallbackArt,").replace("applyCover(fc,", "applyCover(fc,primaryArt,fallbackArt,")
h=h.replace("if(!s||!s.connected){", "if(!s||!s.connected){const fc=$('#focusShieldCover');if(fc){fc.removeAttribute('src');delete fc.dataset.artKey;}$('#focusShieldPlayer')?.classList.remove('has-cover');$('#focusShieldTrack').textContent='Нет связи';$('#focusShieldArtist').textContent='Ожидаю медиамост';")
h=h.replace("function renderYBridge(s){", """function applyCover(img,primary,secondary,on,off){
  if(!img)return;
  const key=primary+'|'+secondary;
  if(img.dataset.artKey===key&&img.getAttribute('src'))return;
  img.dataset.artKey=key;img.onload=null;img.onerror=null;off?.();
  if(!primary){img.removeAttribute('src');return;}
  let alternate=false;
  img.onload=()=>{if(img.dataset.artKey===key)on?.()};
  img.onerror=()=>{if(img.dataset.artKey!==key)return;if(secondary&&!alternate){alternate=true;img.src=secondary}else{img.removeAttribute('src');off?.()}};
  img.src=primary;
}
function showStartupUpdate(result,canInstall){
  document.getElementById('startupUpdate')?.remove();
  const box=document.createElement('section');box.id='startupUpdate';box.setAttribute('role','dialog');box.setAttribute('aria-label','Обновление Соночка Study');
  box.innerHTML='<h2></h2><p style="white-space:pre-line"></p><button class="primary">Обновить сейчас</button> <button class="ghost">Позже</button><small></small>';
  box.querySelector('h2').textContent='Доступна версия '+result.version;
  box.querySelector('p').textContent=result.notes||'Улучшения приложения.';
  const buttons=box.querySelectorAll('button');buttons[0].disabled=!canInstall;
  buttons[0].onclick=async()=>{buttons[0].disabled=true;await installUpdate();box.querySelector('small').textContent=$('#updateStatus').textContent;buttons[0].disabled=$('#updateInstallBtn').disabled};
  buttons[1].onclick=()=>{box.remove();$('#appLoader')?.remove()};
  if(!canInstall)box.querySelector('small').textContent='Для установки открой SonochkaStudy.exe.';
  document.body.append(box);
}
function renderYBridge(s){""")
h=h.replace('</style>', '''
#startupUpdate{position:fixed;z-index:999999;left:50%;top:50%;transform:translate(-50%,-50%);width:min(520px,90vw);max-height:85vh;overflow:auto;padding:28px;border:1px solid var(--line);border-radius:24px;background:var(--panel);color:var(--ink);box-shadow:0 15px 100px #0006}#startupUpdate small{display:block;margin-top:12px}
#ymBridgeToggle,#focusShieldPlay{display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:0!important;line-height:1!important}#ymBridgeToggle svg,#focusShieldPlay svg{position:static!important;flex:none;vertical-align:middle}
.focus-shield.has-focus-backdrop h2,.focus-shield.has-focus-backdrop #focusShieldTimer{color:#fff!important}.focus-shield.has-focus-backdrop>p{color:#f7edf5!important}
.calendar-shell-v12{max-width:1120px}.calendar-cell-v12{min-height:88px}.calendar-board-v12{padding:11px}
</style>''')
(p/'SonaStudy.html').write_text(h,encoding='utf-8-sig')
b=(p/'SonaMusicBridge.ps1').read_text(encoding='utf-8-sig').replace("$AppVersion = '14.1.0'","$AppVersion = '14.2.0'")
b=b.replace('$task.Wait()',"if (-not $task.Wait(4000)) { throw 'Media operation timed out' }")
b=b.replace("$script:coverFailAt = [DateTime]::MinValue\nfunction", "$script:coverFailAt = [DateTime]::MinValue\n$script:coverSuccessAt = [DateTime]::MinValue\nfunction")
b=b.replace("-not [string]::IsNullOrWhiteSpace($script:coverData))", "-not [string]::IsNullOrWhiteSpace($script:coverData) -and ((Get-Date)-$script:coverSuccessAt).TotalSeconds -lt 10)")
b=b.replace("$size = [uint32][Math]::Min([double]$stream.Size, 4194304)","if ($stream.Size -gt 16777216) { throw 'Thumbnail too large' }; $size = [uint32]$stream.Size")
b=b.replace("if ($loaded -le 0)", "if ($loaded -ne $size)")
b=b.replace("$data = 'data:' + $mime + ';base64,' + [Convert]::ToBase64String($bytes)","""# Normalize Windows artwork (including BMP) to browser-readable PNG.
    $memory = [IO.MemoryStream]::new($bytes,$false)
    $decoded = $null; $output = [IO.MemoryStream]::new()
    try { $decoded=[Drawing.Image]::FromStream($memory); $decoded.Save($output,[Drawing.Imaging.ImageFormat]::Png); $data='data:image/png;base64,'+[Convert]::ToBase64String($output.ToArray()) }
    finally { if($decoded){$decoded.Dispose()}; $memory.Dispose(); $output.Dispose() }
    $script:coverSuccessAt=Get-Date""")
b=b.replace(".TotalMinutes -lt 20", ".TotalSeconds -lt $(if($script:yCoverUrl){1200}else{15})")
b=b.replace("if ($null -eq $best) { $best = $tracks[0] }", "if ($null -eq $best -or $bestScore -lt 14) { return '' }")
b=b.replace("$coverUrl = Get-YandexCoverUrl $title $artist $key", "$coverUrl = ''; if (-not $cover) { $coverUrl = Get-YandexCoverUrl $title $artist $key }")
b=b.replace("$key = $title + '|'", "$key = (''+$session.SourceAppUserModelId) + '|' + $title + '|'")
start=b.index('    if ($null -eq $stream -or $stream.Size')
end=b.index('    # Normalize Windows artwork',start)
b=b[:start]+'''    # PowerShell receives a COM interface without directly exposed Size/GetInputStreamAt.
    # The .NET WinRT adapter reads the underlying IRandomAccessStream safely.
    $adapter = [System.IO.WindowsRuntimeStreamExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsStream' -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
    $artStream = $adapter.Invoke($null,@($stream))
    if ($artStream.Length -le 0 -or $artStream.Length -gt 16777216) { throw 'Invalid thumbnail size' }
    $artBytes = [IO.MemoryStream]::new()
    try { $artStream.CopyTo($artBytes); [byte[]]$bytes=$artBytes.ToArray() }
    finally { $artBytes.Dispose(); $artStream.Dispose() }
'''+b[end:]
b=b.replace("    return $null\n  }\n}\n\nfunction Normalize-MediaText", "    return $null\n  } finally { foreach($resource in @($reader,$input,$stream)){if($resource){try{$resource.Dispose()}catch{}}} }\n}\n\nfunction Normalize-MediaText")
(p/'SonaMusicBridge.ps1').write_text(b,encoding='utf-8-sig')
(p/'version.txt').write_text('14.2.0\n')
u=(p/'SonaUpdater.ps1').read_text(encoding='utf-8-sig')
u=u.replace("$backup=Join-Path $tmp 'backup'", "$backup=Join-Path $AppRoot ('update-backups\\'+(Get-Date -Format 'yyyyMMdd-HHmmss'))")
(p/'SonaUpdater.ps1').write_text(u,encoding='utf-8-sig')
rate=44100
with wave.open(str(p/'startup-chime.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
 samples=[]
 for i in range(rate*3):
  t=i/rate;v=0
  for start,freq in [(0,523.25),(.32,659.25),(.65,783.99),(1,1046.5)]:
   x=t-start
   if x>=0:v+=.11*(1-math.exp(-x*20))*math.exp(-x*2.5)*math.sin(2*math.pi*freq*x)
  samples.append(struct.pack('<h',int(v*32767)))
 w.writeframes(b''.join(samples))
