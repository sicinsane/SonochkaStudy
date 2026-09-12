using System;
using System.IO;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using System.Threading.Tasks;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

class StudyWindow : Form {
 readonly WebView2 view=new WebView2();
 readonly JavaScriptSerializer json=new JavaScriptSerializer {MaxJsonLength=32*1024*1024};
 readonly string root=AppDomain.CurrentDomain.BaseDirectory;
 readonly string dataRoot;
 readonly bool test;
 bool closingUpdate=false;
 int testStage=0;
 public StudyWindow(bool selfTest) {
  test=selfTest;
  dataRoot=test?Path.Combine(root,"self-test-data"):Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"SonochkaStudy","UserData");
  Directory.CreateDirectory(dataRoot);
  Text="Соночка Study — Основа"; Width=1280;Height=850;MinimumSize=new Size(980,680);StartPosition=FormStartPosition.CenterScreen;
  try{Icon=new Icon(Path.Combine(root,"SonaStudy.ico"));}catch{}
  view.Dock=DockStyle.Fill; Controls.Add(view);Shown+=async(s,e)=>await Initialize();
 }
 async Task Initialize(){
  try{
   if(!test) StartScript("StartServices.ps1","");
   var env=await CoreWebView2Environment.CreateAsync(null,Path.Combine(dataRoot,"WebView2"));
   await view.EnsureCoreWebView2Async(env);
   var core=view.CoreWebView2;
   if(test)await core.AddScriptToExecuteOnDocumentCreatedAsync("window.__nativeErrors=[];window.addEventListener('error',e=>{if(e.message)__nativeErrors.push(e.message)})");
   core.Settings.AreDevToolsEnabled=test;core.Settings.IsStatusBarEnabled=false;
   core.SetVirtualHostNameToFolderMapping("app.sonochka.local",root,CoreWebView2HostResourceAccessKind.DenyCors);
   core.NewWindowRequested+=(s,e)=>{e.Handled=true;OpenLink(e.Uri);};
   core.NavigationStarting+=(s,e)=>{if(!e.Uri.StartsWith("https://app.sonochka.local/",StringComparison.OrdinalIgnoreCase)&&e.Uri!="about:blank"){e.Cancel=true;OpenLink(e.Uri);}};
   core.DownloadStarting+=(s,e)=>{
    if(test)return;
    using(var d=new SaveFileDialog()){d.FileName=Path.GetFileName(e.ResultFilePath);d.Filter="Все файлы|*.*";if(d.ShowDialog(this)==DialogResult.OK)e.ResultFilePath=d.FileName;else e.Cancel=true;}
   };
   core.WebMessageReceived+=async(s,e)=>{
    if(!e.Source.StartsWith("https://app.sonochka.local/",StringComparison.OrdinalIgnoreCase))return;
    try{
     var m=json.Deserialize<System.Collections.Generic.Dictionary<string,object>>(e.WebMessageAsJson);
     string type=Convert.ToString(m["type"]);
     if(type=="snapshot")SaveSnapshot(Convert.ToString(m["data"]));
     if(type=="import")ImportBackup();
     if(type=="update"&&!closingUpdate){
      await Snapshot();closingUpdate=true;StartScript("SonaUpdater.ps1"," -ManifestUrl 'https://raw.githubusercontent.com/sicinsane/SonochkaStudy/main/stable.json' -AppRoot '"+root.Replace("'","''")+"' -WaitForProcessId "+Process.GetCurrentProcess().Id);Close();
     }
     if(type=="wallpaper-video"){
      string file=Path.GetFullPath(Convert.ToString(m["path"]));string ext=Path.GetExtension(file).ToLowerInvariant();
      if(File.Exists(file)&&(ext==".mp4"||ext==".webm"||ext==".m4v")){
       core.SetVirtualHostNameToFolderMapping("wallpaper.sonochka.local",Path.GetDirectoryName(file),CoreWebView2HostResourceAccessKind.DenyCors);
       await core.ExecuteScriptAsync("setWallpaperVideo("+json.Serialize("https://wallpaper.sonochka.local/"+Uri.EscapeDataString(Path.GetFileName(file)))+")");
      }
     }
    }catch(Exception ex){Log(ex.Message);}
   };
   string pending=Path.Combine(dataRoot,"pending-import.json");
   if(File.Exists(pending)){
    string backup=json.Serialize(json.DeserializeObject(File.ReadAllText(pending)));
    await core.AddScriptToExecuteOnDocumentCreatedAsync("if(location.hostname==='app.sonochka.local'&&!localStorage.getItem('sonaNativeImportedV15')){const b="+backup+";const s=b.__sonaStorage||{};for(const k of Object.keys(s))if(k.startsWith('sona')&&typeof s[k]==='string')localStorage.setItem(k,s[k]);delete b.__sonaStorage;localStorage.setItem('sonaStudyDataV1',JSON.stringify(b));localStorage.setItem('sonaNativeImportedV15','1');}");
   }
   core.NavigationCompleted+=async(s,e)=>{
    if(!e.IsSuccess){Log("Navigation failed: "+e.WebErrorStatus);return;}
    if(test){await Task.Delay(1000);await SelfTest();return;}
    try{new System.Media.SoundPlayer(Path.Combine(root,"startup-chime.wav")).Play();}catch{}
   };
   core.Navigate("https://app.sonochka.local/SonaStudy.html");
  }catch(Exception ex){Log(ex.ToString());if(!test)MessageBox.Show(this,"Не удалось открыть приложение. Проверь наличие Microsoft Edge WebView2 Runtime или повторно запусти установщик.\n\n"+ex.Message,Text);else File.WriteAllText(Path.Combine(root,"self-test-error.txt"),ex.ToString());Close();}
 }
 void StartScript(string name,string extra){
  string command="& '"+Path.Combine(root,name).Replace("'","''")+"'"+extra;
  var p=new ProcessStartInfo(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),@"WindowsPowerShell\v1.0\powershell.exe"),"-NoProfile -ExecutionPolicy Bypass -EncodedCommand "+Convert.ToBase64String(System.Text.Encoding.Unicode.GetBytes(command)));
  p.UseShellExecute=false;p.CreateNoWindow=true;Process.Start(p);
 }
 void OpenLink(string url){Uri u;if(Uri.TryCreate(url,UriKind.Absolute,out u)&&(u.Scheme=="https"||u.Scheme=="http"))StartScript("OpenLink.ps1"," -Url '"+u.AbsoluteUri.Replace("'","''")+"'");}
 void SaveSnapshot(string value){
  var parsed=json.DeserializeObject(value);if(parsed==null)return;
  string file=Path.Combine(dataRoot,"last-backup.json"),tmp=file+".tmp";File.WriteAllText(tmp,value);
  if(File.Exists(file))File.Replace(tmp,file,Path.Combine(dataRoot,"previous-backup.json"));else File.Move(tmp,file);
 }
 async Task Snapshot(){string encoded=await view.CoreWebView2.ExecuteScriptAsync("JSON.stringify({...data,__sonaStorage:Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('sona')).map(k=>[k,localStorage.getItem(k)]))})");SaveSnapshot(json.Deserialize<string>(encoded));}
 void ImportBackup(){
  using(var d=new OpenFileDialog()){d.Filter="Копия Соночка Study (*.json)|*.json";if(d.ShowDialog(this)!=DialogResult.OK)return;
   try{string raw=File.ReadAllText(d.FileName);var b=json.Deserialize<System.Collections.Generic.Dictionary<string,object>>(raw);if(!b.ContainsKey("tasks"))throw new Exception("В файле нет учебных задач.");
    File.WriteAllText(Path.Combine(dataRoot,"pending-import.json"),raw);
    view.CoreWebView2.ExecuteScriptAsync("localStorage.removeItem('sonaNativeImportedV15')").ContinueWith(t=>BeginInvoke(new Action(()=>{Application.Restart();Close();})));
   }catch(Exception ex){MessageBox.Show(this,ex.Message,Text);}
  }
 }
 async Task SelfTest(){
  try{
   if(testStage==0){testStage=1;await view.CoreWebView2.ExecuteScriptAsync("if(!data.tasks.some(t=>t.id==='native-test'))data.tasks.push({id:'native-test',type:'homework',title:'Проверка сохранения',done:false});save();localStorage.setItem('sonaNativeTest','retained')");await Task.Delay(200);view.CoreWebView2.Reload();return;}
   string result=await view.CoreWebView2.ExecuteScriptAsync("JSON.stringify({version:APP_VERSION,native:!!window.chrome.webview,homework:!!document.querySelector('#view-homework'),origin:location.origin,wallpaper:!!document.querySelector('#focusBackdropMode option[value=engine]'),persisted:data.tasks.some(t=>t.id==='native-test')&&localStorage.getItem('sonaNativeTest')==='retained',errors:window.__nativeErrors})");
   File.WriteAllText(Path.Combine(root,"self-test-result.json"),json.Deserialize<string>(result));
   using(var stream=File.Create(Path.Combine(root,"native-window.png")))await view.CoreWebView2.CapturePreviewAsync(CoreWebView2CapturePreviewImageFormat.Png,stream);
  }catch(Exception ex){File.WriteAllText(Path.Combine(root,"self-test-error.txt"),ex.ToString());}Close();
 }
 void Log(string s){try{File.AppendAllText(Path.Combine(dataRoot,"app.log"),DateTime.Now+" "+s+Environment.NewLine);}catch{}}
 [STAThread]static void Main(string[] args){Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(new StudyWindow(Array.IndexOf(args,"--self-test")>=0));}
}
