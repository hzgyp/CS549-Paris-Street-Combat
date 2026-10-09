param([string]$Identity='external_demo_v1',[string]$BuildIdentity='instrument_v13')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve occupied native slot'}
$taskOut=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$Identity)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied identity'}
$taskBin=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$BuildIdentity+'/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')
if((Get-FileHash $taskBin).Hash.ToLower() -ne '965bf17c967d313e67e717fbd24080ab5b6093237dcf927355d387a3c111c4e3'){throw 'Original V13 binary differs'}
$taskFF='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
$taskPy='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
New-Item -ItemType Directory -Path $taskOut|Out-Null
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
$taskQuality='r.SetRes 1920x1080w,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-NoSound','-unattended','-DisablePython','-noraytracing',
 '-csvCompression=0','-ParisCloseout=candidate',('-ParisCloseoutOut="'+$taskOut+'"'),('-ParisSavePrefix=Closeout_'+$Identity),
 ('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ExecCmds="'+$taskQuality+'"'),'-ParisRounds=3','-ParisVerifyOldCheckpoint')
$taskStart=Get-Date;$taskRec=$null;$taskRecStart=$null;$taskAdmitted=$false;$taskFailure=$null
$taskGame=Start-Process $taskBin -ArgumentList $taskArgs -WindowStyle Normal -PassThru
$taskRecord=[ordered]@{identity=$Identity;mode='candidate';build=$BuildIdentity;pid=$taskGame.Id;binary_sha256=(Get-FileHash $taskBin).Hash.ToLower();arguments=$taskArgs;started=$taskStart.ToString('o');scope='Visible exact V13 product window, external HWND-only recorder; no native capture flag; NOT performance evidence'}
$taskRecord|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'launch.json')
try{
 while(-not $taskGame.WaitForExit(1000)){
  $taskLog=Join-Path $taskOut 'game.log';$taskText=if(Test-Path $taskLog){Get-Content $taskLog -Raw}else{''}
  if($taskText -match 'Error:|Fatal error:|Ensure condition failed:'){throw 'Native strict error; stop external entry'}
  if(((Get-Date)-$taskStart).TotalSeconds -gt 780){throw 'Original external game bound'}
  if(-not $taskRec -and $taskText.Contains('CLOSEOUT native_ready_six_member_roster')){
   $taskGame.Refresh();$taskHwnd=$taskGame.MainWindowHandle.ToInt64()
   if($taskHwnd -eq 0){throw 'No task-owned game window'}
   $taskRecArgs=@('-hide_banner','-nostdin','-f','gdigrab','-framerate','15','-draw_mouse','0','-i',('hwnd='+$taskHwnd),'-t','165','-c:v','libx264','-preset','veryfast','-crf','20','-threads','4','-g','30','-pix_fmt','yuv420p','-movflags','frag_keyframe+empty_moov',('-y'),('"'+$taskOut+'/raw.mp4"'))
   $taskRecStart=Get-Date
   $taskRec=Start-Process $taskFF -ArgumentList $taskRecArgs -WindowStyle Hidden -PassThru -RedirectStandardError (Join-Path $taskOut 'recorder.log') -RedirectStandardOutput (Join-Path $taskOut 'recorder_stdout.log')
   @{hwnd=$taskHwnd;game_pid=$taskGame.Id;recorder_pid=$taskRec.Id;started_utc=$taskRecStart.ToUniversalTime().ToString('o');arguments=$taskRecArgs;scope='Only exact owned application window, never desktop'}|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'recording.json')
  }
  if($taskRec){
   if($taskRec.HasExited -and $taskRec.ExitCode -ne 0){throw 'External recorder failed'}
   if(((Get-Date)-$taskRecStart).TotalSeconds -gt 185 -and -not $taskRec.HasExited){throw 'Recorder bound'}
   if(-not $taskAdmitted -and ((Get-Date)-$taskRecStart).TotalSeconds -ge 12){
    & $taskFF -hide_banner -nostdin -ss 2 -i (Join-Path $taskOut 'raw.mp4') -frames:v 1 (Join-Path $taskOut 'early_recorded.png') 2> (Join-Path $taskOut 'early_extract.log')
    if($LASTEXITCODE -ne 0){throw 'Actual external frame cannot be read'}
    & $taskPy (Join-Path $PSScriptRoot 'admit_window_capture.py') (Join-Path $taskOut 'early_recorded.png')
    if($LASTEXITCODE -ne 0){throw 'External frame size/blank admission failed'}
    $taskAdmitted=$true
   }
  }
 }
 if(-not $taskRec -or -not $taskAdmitted){throw 'Missing admitted external recording'}
 if(-not $taskRec.WaitForExit(1000)){throw 'Game exited before external recording completed'}
 if($taskRec.ExitCode -ne 0){throw 'Recorder exit failure'}
}catch{$taskFailure=$_.Exception.Message}
finally{
 if($taskFailure){
  if($taskRec -and -not $taskRec.HasExited){$taskRec.Kill();$taskRec.WaitForExit()}
  if(-not $taskGame.HasExited){$taskGame.Refresh();if($taskGame.Path -ne $taskBin){throw 'Preserve unknown process'};$taskGame.Kill();$taskGame.WaitForExit()}
 }
 $taskRecord.exit_code=$taskGame.ExitCode;$taskRecord.finished=(Get-Date).ToString('o');$taskRecord.failure=$taskFailure;$taskRecord.external_frame_admitted=$taskAdmitted
 $taskRecord|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'launch.json')
}
if($taskFailure){throw $taskFailure}
if($taskGame.ExitCode -ne 0){throw 'Native game failed'}
Get-Content (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json|Select-Object status,elapsed_wall_seconds|ConvertTo-Json
