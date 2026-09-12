using System;
using System.IO;
using System.Reflection;
using System.Diagnostics;
using System.Windows.Forms;
class Setup {
 [STAThread] static int Main(string[] args) {
  bool test = args.Length == 1 && args[0] == "--self-test";
  string dir = Path.Combine(Path.GetTempPath(), "SonochkaSetup-" + Guid.NewGuid().ToString("N"));
  try {
   Directory.CreateDirectory(dir);
   foreach(string name in new[]{"payload.zip","installer.ps1","SonaStudy.ico"}) {
    using(Stream src = Assembly.GetExecutingAssembly().GetManifestResourceStream(name))
    using(Stream dst = File.Create(Path.Combine(dir,name))) { src.CopyTo(dst); }
   }
   var info = new ProcessStartInfo(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),@"WindowsPowerShell\v1.0\powershell.exe"));
   info.Arguments = "-NoProfile -STA -ExecutionPolicy Bypass -File \"" + Path.Combine(dir,"installer.ps1") + "\" -Payload \"" + Path.Combine(dir,"payload.zip") + "\"" + (test ? " -SelfTest" : "");
   info.UseShellExecute = false; info.CreateNoWindow = true;
   info.RedirectStandardError = true;
   using(Process p = Process.Start(info)) {
    string error = p.StandardError.ReadToEnd(); p.WaitForExit();
    if(p.ExitCode != 0) {
     if(test) File.WriteAllText(Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location),"self-test-error.txt"), error);
     else MessageBox.Show(error,"Sonochka Study — ошибка установки",MessageBoxButtons.OK,MessageBoxIcon.Error);
    }
    return p.ExitCode;
   }
  } catch(Exception e) { if(!test) MessageBox.Show(e.Message,"Sonochka Study"); return 1; }
  finally { try { if(Directory.Exists(dir)) Directory.Delete(dir,true); } catch {} }
 }
}
