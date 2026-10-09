param([string]$Identity='plain_startup_v1',[string]$BuildIdentity='package_v2',[switch]$NoHardwareRayTracing)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve active game/editor'}
$taskOut=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$Identity)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve identity'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$taskBinary=Get-ChildItem (Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$BuildIdentity+'/Archive')) -Recurse -Filter WW2FranceLiberation.exe|Where-Object {$_.DirectoryName -match 'Binaries\\Win64$'}
if(@($taskBinary).Count -ne 1){throw 'Ambiguous executable'}
$taskQuality='r.SetRes 1920x1080w,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0,csvprofile STARTFILE=plain_startup,csvprofile FRAMES=1500'
$taskArgs=@('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-NoSound','-unattended','-DisablePython','-seconds=60',
 '-csvCompression=0','-csvGpuStats','-ExitAfterCsvProfiling',('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),
 ('-ExecCmds="'+$taskQuality+'"'),('-csvExecCmds="1000:Shot SHOWUI -nosuffix filename='+($taskOut.Replace('\','/'))+'/ready.png"'))
if($NoHardwareRayTracing){$taskArgs+='-noraytracing'}
$taskProcess=Start-Process $taskBinary.FullName -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskRecord=[ordered]@{identity=$Identity;build=$BuildIdentity;pid=$taskProcess.Id;arguments=$taskArgs;binary_sha256=(Get-FileHash $taskBinary.FullName).Hash.ToLower();scope='Observer-disabled packaged startup/Ready only; cold stationary CSV is NOT FPS acceptance'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if(-not $taskProcess.WaitForExit(150000)){$taskRecord.deadline_terminated=$true;$taskProcess.Kill();$taskProcess.WaitForExit()}
$taskRecord.exit_code=$taskProcess.ExitCode
$taskRecord|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'launch.json')
if($taskRecord.exit_code -ne 0){throw 'Packaged startup failed; retain log'}
