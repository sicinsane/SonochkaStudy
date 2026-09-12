function Get-WallpaperEngineState {
 try {
  $process=Get-Process wallpaper32,wallpaper64 -ErrorAction SilentlyContinue | Select-Object -First 1
  if(-not $process){return @{ok=$false;error='Запусти Wallpaper Engine.'}}
  $exe=$process.Path;$engineRoot=Split-Path -Parent $exe
  $info=New-Object Diagnostics.ProcessStartInfo;$info.FileName=$exe;$info.Arguments='-control getWallpaper';$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true
  $query=[Diagnostics.Process]::Start($info)
  $read=$query.StandardOutput.ReadToEndAsync()
  if($query.WaitForExit(1800)){$path=$read.Result.Trim()}else{$query.Kill();$path=''}
  if(-not $path){
   $cfg=Get-Content (Join-Path $engineRoot 'config.json') -Raw | ConvertFrom-Json
   $user=$cfg.PSObject.Properties | Where-Object Name -eq $env:USERNAME | Select-Object -First 1
   if(-not $user){$user=$cfg.PSObject.Properties | Where-Object {$_.Value.general.wallpaperconfig.selectedwallpapers} | Select-Object -First 1}
   $screens=$user.Value.general.wallpaperconfig.selectedwallpapers
   $selected=$screens.PSObject.Properties | Sort-Object Name | Select-Object -First 1
   $path=''+$selected.Value.file
  }
  if(-not $path -or -not(Test-Path -LiteralPath $path)){return @{ok=$false;error='Не удалось прочитать текущие обои Wallpaper Engine.'}}
  $folder=Split-Path -Parent $path;$projectPath=Join-Path $folder 'project.json';$project=$null
  if(Test-Path -LiteralPath $projectPath){$project=Get-Content $projectPath -Raw|ConvertFrom-Json}
  $title=if($project.title){''+$project.title}else{Split-Path $folder -Leaf}
  $file=if($project.file){Join-Path $folder $project.file}else{$path}
  if([IO.Path]::GetExtension($file).ToLowerInvariant() -in @('.mp4','.webm','.m4v')){return @{ok=$true;kind='video';videoPath=$file;title=$title;key=$path}}
  $preview=if($project.preview){Join-Path $folder $project.preview}else{Join-Path $folder 'preview.jpg'}
  if(-not(Test-Path -LiteralPath $preview)){return @{ok=$false;error='У этих обоев нет доступного превью. Видеообои поддерживаются с движением.'}}
  $ext=[IO.Path]::GetExtension($preview).ToLowerInvariant();$mime=switch($ext){'.png'{'image/png'}'.gif'{'image/gif'}'.webp'{'image/webp'}default{'image/jpeg'}}
  $bytes=[IO.File]::ReadAllBytes($preview);if($bytes.Length -gt 16777216){throw 'Preview too large'}
  return @{ok=$true;kind='preview';data=('data:'+$mime+';base64,'+[Convert]::ToBase64String($bytes));title=$title;key=$path}
 }catch{return @{ok=$false;error=$_.Exception.Message}}
}
