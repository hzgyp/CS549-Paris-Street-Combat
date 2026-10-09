param([string]$Identity='plain_v1',[string]$BuildIdentity='candidate_v3',
      [ValidateSet(1280,1920)][int]$Width=1920,[ValidateSet(720,1080)][int]$Height=1080)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve active user engine'}
$taskBuild=Join-Path $taskRoot ('tmp/g1-playtest-revision-20261008/'+$BuildIdentity)
$taskOut=Join-Path $taskRoot ('tmp/g1-playtest-revision-20261008/'+$Identity)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve identity'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$taskBinary=Join-Path $taskBuild 'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
$taskQuality='r.SetRes 1920x1080w,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0,csvprofile STARTFILE=ux_ready,csvprofile FRAMES=1500'
$taskQuality='DisableAllScreenMessages,'+$taskQuality
$taskQuality=$taskQuality.Replace('r.SetRes 1920x1080w',('r.SetRes '+$Width+'x'+$Height+'w'))
$taskArgs=@('-RenderOffscreen','-windowed','-ForceRes',('-ResX='+$Width),('-ResY='+$Height),'-NoSplash','-NoSound','-unattended','-DisablePython','-noraytracing','-seconds=60',
 '-ExitAfterCsvProfiling',('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),
 ('-ExecCmds="'+$taskQuality+'"'),('-csvExecCmds="1000:Shot SHOWUI -nosuffix filename='+($taskOut.Replace('\','/'))+'/ready.png"'))
$taskProcess=Start-Process $taskBinary -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskRecord=[ordered]@{identity=$Identity;build=$BuildIdentity;pid=$taskProcess.Id;arguments=$taskArgs;width=$Width;height=$Height;binary_sha256=(Get-FileHash $taskBinary).Hash.ToLower();scope='Ordinary packaged Ready/HUD image only; no test observer or action acceptance'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if(-not $taskProcess.WaitForExit(120000)){$taskRecord.deadline_terminated=$true;$taskProcess.Kill();$taskProcess.WaitForExit()}
$taskRecord.exit_code=$taskProcess.ExitCode
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if($taskRecord.exit_code -ne 0){throw 'Startup failed; retain evidence'}
