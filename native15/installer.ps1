param([Parameter(Mandatory=$true)][string]$Payload,[switch]$SelfTest,[string]$TestRoot='')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase
[xml]$xaml=@'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" Width="640" Height="560" WindowStartupLocation="CenterScreen" WindowStyle="None" AllowsTransparency="True" Background="Transparent" ResizeMode="NoResize" ShowInTaskbar="True" Title="Соночка Study — установка">
  <Border CornerRadius="28" Background="#FFF8FB" BorderBrush="#EAC7D8" BorderThickness="1" Padding="0">
    <Border.Effect><DropShadowEffect BlurRadius="34" ShadowDepth="8" Opacity="0.24" Color="#6A3E57"/></Border.Effect>
    <Grid>
      <Grid.RowDefinitions><RowDefinition Height="54"/><RowDefinition Height="*"/></Grid.RowDefinitions>
      <Border Grid.Row="0" Background="#F9E8F1" CornerRadius="28,28,0,0">
        <Grid Margin="22,0"><Grid.ColumnDefinitions><ColumnDefinition/><ColumnDefinition Width="40"/></Grid.ColumnDefinitions><StackPanel Orientation="Horizontal" VerticalAlignment="Center"><TextBlock Text="♡" FontSize="22" FontWeight="Bold" Foreground="#D978A6" Margin="0,0,9,0"/><TextBlock Text="СОНОЧКА STUDY" FontSize="13" FontWeight="Bold" Foreground="#3A2933" VerticalAlignment="Center"/></StackPanel><Button x:Name="CloseBtn" Grid.Column="1" Content="×" Width="30" Height="30" Background="Transparent" BorderThickness="0" Foreground="#806B77" FontSize="18" Cursor="Hand"/></Grid>
      </Border>
      <Grid Grid.Row="1" Margin="42,34,42,34">
        <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/><RowDefinition Height="Auto"/></Grid.RowDefinitions>
        <Border Width="68" Height="68" CornerRadius="22" HorizontalAlignment="Left" Background="#E38AB4"><TextBlock Text="♡" Foreground="White" FontSize="30" FontWeight="Bold" HorizontalAlignment="Center" VerticalAlignment="Center"/></Border>
        <TextBlock Grid.Row="1" Text="Соночка Study" Margin="0,20,0,0" FontSize="34" FontWeight="ExtraBold" Foreground="#2F222A"/>
        <TextBlock Grid.Row="2" Text="Отдельное приложение Windows. Перед переходом сохрани резервную копию из старой версии." Margin="0,8,0,0" FontSize="13" Foreground="#7F6D77" TextWrapping="Wrap"/>
        <StackPanel Grid.Row="3" Margin="0,26,0,0"><ProgressBar x:Name="Progress" Height="8" Minimum="0" Maximum="100" Value="0" Foreground="#DE82AE" Background="#F0DCE6" BorderThickness="0"/><TextBlock x:Name="Status" Text="Готово к установке" Margin="0,10,0,0" FontSize="11" Foreground="#8B7581"/></StackPanel>
        <StackPanel Grid.Row="4" Margin="0,18,0,0"><TextBlock Text="Установится без прав администратора" FontWeight="SemiBold" FontSize="11" Foreground="#4C3944"/><TextBlock Text="Ярлык появится на рабочем столе и в меню Пуск. Данные учёбы останутся локальными на этом компьютере." Margin="0,5,0,0" FontSize="10" Foreground="#927E89" TextWrapping="Wrap"/></StackPanel>
        <Grid Grid.Row="5" Margin="0,22,0,0"><Grid.ColumnDefinitions><ColumnDefinition/><ColumnDefinition Width="Auto"/></Grid.ColumnDefinitions><TextBlock x:Name="VersionText" Text="15.0.0 — Основа" VerticalAlignment="Center" Foreground="#A08A95" FontSize="10"/><Button x:Name="InstallBtn" Grid.Column="1" Content="Установить" Width="150" Height="46" Background="#DD83AE" Foreground="White" BorderBrush="#DD83AE" FontSize="13" FontWeight="Bold" Cursor="Hand"/></Grid>
      </Grid>
    </Grid>
  </Border>
</Window>
'@
$reader=New-Object System.Xml.XmlNodeReader $xaml
$window=[Windows.Markup.XamlReader]::Load($reader)
$window.Icon = New-Object Windows.Media.Imaging.BitmapImage([Uri](Join-Path (Split-Path -Parent $Payload) 'SonaStudy.ico'))
$close=$window.FindName('CloseBtn'); $install=$window.FindName('InstallBtn'); $progress=$window.FindName('Progress'); $status=$window.FindName('Status')
$close.Add_Click({$window.Close()})
$window.Add_MouseLeftButtonDown({ if($_.OriginalSource -is [System.Windows.Controls.Border]){ try{$window.DragMove()}catch{} } })
function UiStep([int]$value,[string]$text){$progress.Value=$value;$status.Text=$text;$window.Dispatcher.Invoke([action]{},[Windows.Threading.DispatcherPriority]::Background);Start-Sleep -Milliseconds 180}
$install.Add_Click({
  try{
    $install.IsEnabled=$false
    UiStep 8 'Подготавливаю папку приложения…'
    $appRoot=Join-Path $env:LOCALAPPDATA 'Programs\SonochkaStudy'
    if($SelfTest -and $TestRoot){$appRoot=$TestRoot}
    $runtime=@("${env:ProgramFiles(x86)}\Microsoft\EdgeWebView\Application","$env:LOCALAPPDATA\Microsoft\EdgeWebView\Application") | Where-Object {Test-Path -LiteralPath $_}
    if(-not $runtime -and -not $SelfTest){
      UiStep 12 'Устанавливаю компонент окна приложения WebView2…'
      $runtimeSetup=Join-Path $env:TEMP ('SonochkaWebView-'+[guid]::NewGuid().ToString('N')+'.exe')
      Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile $runtimeSetup -UseBasicParsing -TimeoutSec 90
      $signature=Get-AuthenticodeSignature -LiteralPath $runtimeSetup
      if($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Microsoft Corporation'){throw 'Не удалось проверить установщик Microsoft WebView2.'}
      $runtimeProcess=Start-Process -FilePath $runtimeSetup -ArgumentList '/silent /install' -WindowStyle Hidden -PassThru
      $runtimeProcess.WaitForExit()
      if($runtimeProcess.ExitCode -ne 0){throw 'WebView2 не установился. Проверь подключение к интернету.'}
    }
    if(Get-Process SonochkaStudy -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq (Join-Path $appRoot 'SonochkaStudy.exe')}){throw 'Сначала закрой установленную Соночка Study и нажми Установить ещё раз.'}
    New-Item -ItemType Directory -Path $appRoot -Force | Out-Null
    $stage=Join-Path $env:TEMP ('SonochkaStudy-stage-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    UiStep 25 'Распаковываю Соночка Study…'
    Expand-Archive -LiteralPath $Payload -DestinationPath $stage -Force
    UiStep 54 'Копирую файлы…'
    Copy-Item -Path (Join-Path $stage '*') -Destination $appRoot -Recurse -Force
    UiStep 72 'Создаю красивые ярлыки…'
    $ws=New-Object -ComObject WScript.Shell
    $target=Join-Path $appRoot 'SonochkaStudy.exe'; $ico=Join-Path $appRoot 'SonaStudy.ico'
    $desktop=[Environment]::GetFolderPath('Desktop')
    if($SelfTest){$desktop=$appRoot}
    $lnk=$ws.CreateShortcut((Join-Path $desktop 'Соночка Study.lnk'));$lnk.TargetPath=$target;$lnk.WorkingDirectory=$appRoot;$lnk.IconLocation=$ico+',0';$lnk.Description='Соночка Study';$lnk.Save()
    $start=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'; if($SelfTest){$start=$appRoot}; New-Item -ItemType Directory -Path $start -Force | Out-Null
    $lnk2=$ws.CreateShortcut((Join-Path $start 'Соночка Study.lnk'));$lnk2.TargetPath=$target;$lnk2.WorkingDirectory=$appRoot;$lnk2.IconLocation=$ico+',0';$lnk2.Description='Соночка Study';$lnk2.Save()
    if(-not $SelfTest){
      $reg='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\SonochkaStudy'
      New-Item $reg -Force | Out-Null
      $values=@{DisplayName='Соночка Study';DisplayVersion='15.0.0';Publisher='Sonochka Study';InstallLocation=$appRoot;DisplayIcon=$target;UninstallString=('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "'+(Join-Path $appRoot 'Uninstall.ps1')+'"')}
      foreach($key in $values.Keys){Set-ItemProperty $reg $key $values[$key]}
    }
    UiStep 92 'Проверяю запуск…'
    if(-not (Test-Path $target)){throw 'Не найден файл запуска.'}
    UiStep 100 'Готово ♡ Запускаю приложение…'
    if(-not $SelfTest){Start-Process $target | Out-Null}
    Start-Sleep -Milliseconds 850
    # Temporary staging is retained for troubleshooting; user data is outside the installation.
    $window.Close()
  }catch{
    $status.Text='Не удалось установить: '+$_.Exception.Message
    $progress.Value=0;$install.IsEnabled=$true
    if($SelfTest){[IO.File]::WriteAllText((Join-Path (Split-Path -Parent $Payload) 'installer-test-error.txt'),$_.Exception.ToString());$window.Close()}
  }
})
if($SelfTest){$window.Add_ContentRendered({if($TestRoot){$install.RaiseEvent((New-Object Windows.RoutedEventArgs([Windows.Controls.Button]::ClickEvent)))}else{$window.Close()}})}; [void]$window.ShowDialog()

