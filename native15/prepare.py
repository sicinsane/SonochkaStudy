from pathlib import Path
import shutil
root=Path(__file__).resolve().parent.parent
p=root/'app'
for name in ['WallpaperEngine.ps1']:
 (p/name).write_text((root/'native15'/name).read_text(encoding='utf-8-sig'),encoding='utf-8-sig')
(p/'StartServices.ps1').write_text('''$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
try{$s=Invoke-RestMethod http://127.0.0.1:8765/status -TimeoutSec 6;if($s.appVersion -eq '15.0.0'){exit};if($s.connected){Invoke-RestMethod http://127.0.0.1:8765/shutdown -TimeoutSec 5|Out-Null;Start-Sleep -Milliseconds 700}}catch{}
& (Join-Path $root 'SonaMusicBridge.ps1')
''',encoding='utf-8-sig')
(p/'OpenLink.ps1').write_text("param([string]$Url)\n. (Join-Path $PSScriptRoot 'BrowserSupport.ps1')\nOpen-YandexLink $Url | Out-Null\n",encoding='utf-8-sig')
(p/'Launch.ps1').write_text("Start-Process -FilePath (Join-Path $PSScriptRoot 'SonochkaStudy.exe') -WorkingDirectory $PSScriptRoot\n",encoding='utf-8-sig')
b=(p/'SonaMusicBridge.ps1').read_text(encoding='utf-8-sig').replace('14.2.1','15.0.0')
b=b.replace(". (Join-Path $AppRoot 'BrowserSupport.ps1')",". (Join-Path $AppRoot 'BrowserSupport.ps1')\n. (Join-Path $AppRoot 'WallpaperEngine.ps1')")
b=b.replace("        '/wallpaper'", "        '/wallpaper-engine' { Write-HttpJson $stream (Get-WallpaperEngineState) }\n        '/wallpaper'")
(p/'SonaMusicBridge.ps1').write_text(b,encoding='utf-8-sig')
h=(p/'SonaStudy.html').read_text(encoding='utf-8-sig').replace('14.2.1','15.0.0')
h=h.replace('a.due.localeCompare(b.due)',"String(a.due||'9999').localeCompare(String(b.due||'9999'))")
h=h.replace('<option value="wallpaper">','<option value="engine">Wallpaper Engine</option><option value="wallpaper">')
h=h.replace('async function resolveFocusBackdrop(force=false){',"async function resolveFocusBackdrop(force=false){if(focusBackdropMode()==='engine')return await fetchEngineWallpaper();engineCurrentKey='';$('#engineVideo')?.remove();")
js='''
let engineCurrentKey='';
function setWallpaperVideo(url){
 if(focusBackdropMode()!=='engine')return;
 let v=$('#engineVideo');if(!v){v=document.createElement('video');v.id='engineVideo';v.autoplay=true;v.loop=true;v.muted=true;v.playsInline=true;$('#focusShield').prepend(v)}
 if(v.src!==url)v.src=url;v.play().catch(()=>{});
 $('#focusShield').classList.add('has-focus-backdrop');
}
async function fetchEngineWallpaper(){
 try{const result=await yBridge('/wallpaper-engine');if(!result.ok)throw new Error(result.error);
  if(result.kind==='video'){
   setFocusBackdropStatus('Wallpaper Engine: '+result.title+' · видео');
   if(window.chrome?.webview&&engineCurrentKey!==result.key){engineCurrentKey=result.key;chrome.webview.postMessage({type:'wallpaper-video',path:result.videoPath})}
   return '';
  }
  $('#engineVideo')?.remove();engineCurrentKey='';setFocusBackdropStatus('Wallpaper Engine: '+result.title+' · превью сцены');return result.data||'';
 }catch(e){setFocusBackdropStatus(e.message||'Wallpaper Engine недоступен');return '';}
}
setInterval(()=>{if(focusBackdropMode()==='engine'&&$('#focusShield')?.classList.contains('open'))applyFocusBackdrop(true)},6000);
function sendNativeSnapshot(){try{if(window.chrome?.webview)chrome.webview.postMessage({type:'snapshot',data:JSON.stringify({...data,__sonaStorage:Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('sona')).map(k=>[k,localStorage.getItem(k)]))})})}catch(e){}}
const browserSave=save;save=function(){browserSave();sendNativeSnapshot()};
setInterval(sendNativeSnapshot,10000);
const browserInstallUpdate=installUpdate;
installUpdate=async function(){if(window.chrome?.webview){sendNativeSnapshot();chrome.webview.postMessage({type:'update'});}else await browserInstallUpdate()};
function showNativeMigration(){
 if(!window.chrome?.webview||localStorage.getItem('sonaV15Welcome')||localStorage.getItem('sonaNativeImportedV15'))return;
 const box=document.createElement('div');box.className='native-welcome';box.innerHTML='<h2>Соночка Study — Основа</h2><p>Теперь это отдельное приложение. Если раньше ты пользовалась браузерной версией, загрузи её резервную копию: Настройки → Скачать копию в старой версии.</p><button class="primary" id="nativeImport">Перенести сохранения</button><button class="ghost" id="nativeLater">Позже</button>';
 document.body.append(box);$('#nativeImport').onclick=()=>chrome.webview.postMessage({type:'import'});$('#nativeLater').onclick=()=>{localStorage.setItem('sonaV15Welcome','1');box.remove()};
}
setTimeout(showNativeMigration,7600);
'''
h=h.replace("runBeautifulLoader();$('#pageTitle')",js+"\nrunBeautifulLoader();$('#pageTitle')")
h=h.replace('</style>', '''#engineVideo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-1;pointer-events:none}.native-welcome{position:fixed;z-index:999999;top:50%;left:50%;transform:translate(-50%,-50%);max-width:520px;width:88vw;background:var(--panel);color:var(--ink);padding:28px;border-radius:22px;box-shadow:0 20px 80px #0005}.native-welcome p{line-height:1.6}.native-welcome button{margin:4px}</style>''')
h=h.replace("sh.classList.toggle('has-focus-backdrop',!!src)","sh.classList.toggle('has-focus-backdrop',!!src||!!$('#engineVideo'))")
h=h.replace('Можно синхронизировать полноэкранный фокус с обоями Windows или выбрать своё спокойное фото.','Выбери Wallpaper Engine, обои Windows или своё фото. Видео Wallpaper Engine воспроизводится; сцены и веб-обои показываются как синхронизированное превью.')
(p/'SonaStudy.html').write_text(h,encoding='utf-8-sig')
u=(p/'SonaUpdater.ps1').read_text(encoding='utf-8-sig')
u=u.replace('[Parameter(Mandatory=$true)][string]$AppRoot','[Parameter(Mandatory=$true)][string]$AppRoot,\n  [int]$WaitForProcessId=0')
u=u.replace("  Start-Sleep -Milliseconds 650", "  if($WaitForProcessId){Wait-Process -Id $WaitForProcessId -Timeout 30 -ErrorAction SilentlyContinue}\n  Start-Sleep -Milliseconds 650",1)
u=u.replace("'BrowserSupport.ps1','SonaStudy.html'","'Microsoft.Web.WebView2.Core.dll','Microsoft.Web.WebView2.WinForms.dll','WebView2Loader.dll','WallpaperEngine.ps1','StartServices.ps1','OpenLink.ps1','BrowserSupport.ps1','SonaStudy.html'")
(p/'SonaUpdater.ps1').write_text(u,encoding='utf-8-sig')
(p/'version.txt').write_text('15.0.0\n')
shutil.copyfile(root/'native15'/'meow.wav',p/'startup-chime.wav')
shutil.copyfile(root/'native15'/'SOUND-LICENSE.txt',p/'SOUND-LICENSE.txt')
(p/'Uninstall.ps1').write_text((root/'native15'/'Uninstall.ps1').read_text(encoding='utf-8-sig'),encoding='utf-8-sig')
