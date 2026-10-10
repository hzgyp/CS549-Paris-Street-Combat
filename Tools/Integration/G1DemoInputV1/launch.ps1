param([Parameter(Mandatory=$true)][ValidateSet('probe','actions','victory','defeat')][string]$Mode,[Parameter(Mandatory=$true)][string]$Case,[ValidateSet('recording_v1','recording_v2','recording_v3','recording_v4','recording_v5','recording_v6')][string]$Revision='recording_v6',[ValidateSet('recording_v4')][string]$RuntimeRevision,[switch]$RecordAudio)
$ErrorActionPreference='Stop'
if($Case -notmatch '^[a-z0-9_]+$'){throw 'Explicit safe case name required'}
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-demo-draft03-20261009'
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
$taskBuild=Get-Content -LiteralPath (Join-Path $taskOut ($Revision+'/build.json')) -Raw|ConvertFrom-Json
if($taskBuild.status -ne 'built_runtime_unverified'){throw 'No admitted Game build'}
$taskRuntime=if($RuntimeRevision){$RuntimeRevision}else{$Revision}
$taskExe=Join-Path $taskOut ($taskRuntime+'/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLower() -ne $taskBuild.game_sha256){throw 'Recording Game drift'}
$taskCase=Join-Path $taskOut $Case
if(Test-Path -LiteralPath $taskCase){throw 'Preserve occupied entry identity'}
New-Item -ItemType Directory -Path $taskCase|Out-Null
$taskDir=Join-Path $taskCase 'UserDir'
$taskQuality='sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-windowed','-ResX=1920','-ResY=1080','-DisablePython','-noraytracing','-ParisSavePrefix=ParisG1PlaytestV5',('-UserDir="'+$taskDir+'"'),('-ABSLOG="'+$taskCase+'/game.log"'),('-ParisDemoMode='+$Mode),('-ParisDemoOut="'+$taskCase+'"'),('-ExecCmds="'+$taskQuality+'"'))
if($RecordAudio){$taskArgs+='-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0'}
$taskRecord=[ordered]@{status='launching';started=(Get-Date).ToString('o');mode=$Mode;case=$Case;game=$taskExe;game_sha256=$taskBuild.game_sha256;args=$taskArgs;scope='Separate disclosed recording input helper; genuine original game rules; isolated user saves; GO gate initially absent'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WorkingDirectory (Split-Path $taskExe) -PassThru
$taskRecord.pid=$taskProcess.Id;$taskRecord.status='owned_game_launched'
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskRecord|ConvertTo-Json -Depth 5
$taskProcess.WaitForExit()
$taskRecord.exit_code=$taskProcess.ExitCode;$taskRecord.status='owned_game_exited';$taskRecord.finished=(Get-Date).ToString('o')
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskRecord|ConvertTo-Json -Depth 5
