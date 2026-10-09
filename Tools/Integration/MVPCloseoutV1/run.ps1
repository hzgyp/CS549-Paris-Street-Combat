param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Identity,
 [ValidateSet('startup','integrated','diagnose','geometry','navrepair','cohort','squad_diagnose','candidate','queries')][string]$Mode='startup',[string]$BuildIdentity='instrument_v8',[switch]$Capture,[switch]$NoHardwareRayTracing,[ValidateSet(1,3)][int]$Rounds=3,[switch]$VerifyOldCheckpoint)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve occupied native slot'}
$taskBuild=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$BuildIdentity)
$taskOut=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$Identity)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied identity'}
$taskBinary=Get-ChildItem (Join-Path $taskBuild 'Archive') -Recurse -Filter WW2FranceLiberation.exe|Where-Object {$_.DirectoryName -match 'Binaries\\Win64$'}
if(@($taskBinary).Count -ne 1){throw 'Ambiguous executable'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
$taskQuality='r.SetRes 1920x1080w,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-NoSound','-unattended','-DisablePython',
 '-csvCompression=0','-csvGpuStats',('-ParisCloseout='+$Mode),('-ParisCloseoutOut="'+$taskOut+'"'),
 ('-ParisSavePrefix=Closeout_'+$Identity),('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ExecCmds="'+$taskQuality+'"'))
if($Capture){$taskArgs+='-ParisCapture'}
if($NoHardwareRayTracing){$taskArgs+='-noraytracing'}
$taskArgs+=('-ParisRounds='+$Rounds)
if($VerifyOldCheckpoint){$taskArgs+='-ParisVerifyOldCheckpoint'}
$taskStart=Get-Date
$taskProcess=Start-Process $taskBinary.FullName -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskRecord=[ordered]@{identity=$Identity;mode=$Mode;build=$BuildIdentity;pid=$taskProcess.Id;binary_sha256=(Get-FileHash $taskBinary.FullName).Hash.ToLower();arguments=$taskArgs;started=$taskStart.ToString('o')}
$taskRecord|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'launch.json')
$taskLimit=if($Mode -eq 'startup'){180}else{780}
while(-not $taskProcess.WaitForExit(1000)){
 if(((Get-Date)-$taskStart).TotalSeconds -gt 60 -and -not(Test-Path -LiteralPath (Join-Path $taskOut 'samples.jsonl'))){$taskRecord.observer_missing_terminated=$true;$taskProcess.Kill();$taskProcess.WaitForExit();break}
 if(((Get-Date)-$taskStart).TotalSeconds -gt $taskLimit){$taskRecord.deadline_terminated=$true;$taskProcess.Kill();$taskProcess.WaitForExit();break}
}
$taskRecord.exit_code=$taskProcess.ExitCode;$taskRecord.finished=(Get-Date).ToString('o')
$taskRecord|ConvertTo-Json -Depth 6|Set-Content (Join-Path $taskOut 'launch.json')
if(Test-Path -LiteralPath (Join-Path $taskOut 'result.json')){Get-Content (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json|Select-Object status,mode,step,elapsed_wall_seconds|ConvertTo-Json}
if($taskRecord.exit_code -ne 0){throw 'Owned packaged game failed; preserve evidence'}
