param([Parameter(Mandatory=$true)][ValidateSet('probe','actions','victory','defeat')][string]$Mode,[Parameter(Mandatory=$true)][string]$Case)
$ErrorActionPreference='Stop'
if($Case -notmatch '^[a-z0-9_]+$'){throw 'Explicit safe case name required'}
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
$taskExe=Join-Path $taskRoot 'tmp/g1-demo-draft03-20261009/recording_v4/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
$taskBuild=Get-Content -LiteralPath (Join-Path $taskRoot 'tmp/g1-demo-draft04-20261010/recording_stats_v1/build.json') -Raw|ConvertFrom-Json
if($taskBuild.status -ne 'diagnostic_game_built_runtime_unverified' -or $taskBuild.exit_code -ne 0){throw 'No built diagnostic Game'}
$taskExpected=$taskBuild.game_sha256
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLower() -ne $taskExpected){throw 'Frozen V6 Game drift'}
$taskCase=Join-Path $taskRoot ('tmp/g1-demo-draft04-20261010/'+$Case)
if(Test-Path -LiteralPath $taskCase){throw 'Preserve occupied entry'}
New-Item -ItemType Directory -Path $taskCase|Out-Null
$taskDir=Join-Path $taskCase 'UserDir'
$taskQuality='sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-windowed','-ResX=1920','-ResY=1080','-DisablePython','-noraytracing','-ParisSavePrefix=ParisG1PlaytestV5','-ParisLiveStats',('-UserDir="'+$taskDir+'"'),('-ABSLOG="'+$taskCase+'/game.log"'),('-ParisDemoMode='+$Mode),('-ParisDemoOut="'+$taskCase+'"'),('-ExecCmds="'+$taskQuality+'"'),'-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0')
$taskRecord=[ordered]@{status='launching';started=(Get-Date).ToString('o');mode=$Mode;case=$Case;game=$taskExe;game_sha256=$taskExpected;args=$taskArgs;scope='V6 ordinary-input helper unchanged; opt-in read-only live UE diagnostic panel. Fresh UserDir; GO initially absent; no added NPC or selected gameplay/source edits'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WorkingDirectory (Split-Path $taskExe) -PassThru
$taskRecord.pid=$taskProcess.Id;$taskRecord.status='owned_game_launched'
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskRecord|ConvertTo-Json -Depth 5
$taskProcess.WaitForExit()
$taskRecord.exit_code=$taskProcess.ExitCode;$taskRecord.status='owned_game_exited';$taskRecord.finished=(Get-Date).ToString('o')
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskCase 'launch.json')
$taskRecord|ConvertTo-Json -Depth 5
