$ErrorActionPreference='Stop'
$reviewRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active user engine/build'}
$reviewExe=Join-Path $reviewRoot 'tmp/g1-demo-draft03-20261009/recording_v4/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $reviewExe).Hash.ToLower() -ne 'a6015c94fd91fb73732d4ea18316ba80754d6de0e5d369a16e7e5725c9799472'){throw 'V6 Game drift'}
$reviewOut=Join-Path $reviewRoot 'tmp/assignment3-review-20261010/performance/dynamic_v6'
if(Test-Path -LiteralPath $reviewOut){throw 'Preserve occupied entry'}
New-Item -ItemType Directory -Path $reviewOut|Out-Null
$reviewQuality='sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0,csvprofile STARTFILE=dynamic_v6,csvprofile FRAMES=15000'
$reviewArgs=@('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-DisablePython','-noraytracing','-ExitAfterCsvProfiling','-ParisSavePrefix=ParisG1PlaytestV5','-ParisDemoMode=victory',('-ParisDemoOut="'+$reviewOut+'"'),('-UserDir="'+$reviewOut+'/UserDir"'),('-ABSLOG="'+$reviewOut+'/game.log"'),'-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0',('-ExecCmds="'+$reviewQuality+'"'))
$reviewRecord=[ordered]@{started=(Get-Date).ToString('o');args=$reviewArgs;game_sha256=(Get-FileHash -LiteralPath $reviewExe).Hash.ToLower();scope='Separate existingV6 normal-input helper; accepted gameplay/cooked data plus telemetry overhead; not exact normalGame performance'}
$reviewProcess=Start-Process -FilePath $reviewExe -ArgumentList $reviewArgs -WorkingDirectory (Split-Path $reviewExe) -WindowStyle Hidden -PassThru
$reviewRecord.pid=$reviewProcess.Id;$reviewRecord.status='owned_game_launched'
$reviewRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $reviewOut 'launch.json')
$reviewRecord|ConvertTo-Json -Depth 5
$reviewProcess.WaitForExit()
$reviewRecord.exit_code=$reviewProcess.ExitCode;$reviewRecord.status='owned_game_exited';$reviewRecord.finished=(Get-Date).ToString('o')
$reviewRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $reviewOut 'launch.json')
$reviewRecord|ConvertTo-Json -Depth 5
if($reviewRecord.exit_code -ne 0){throw 'Entry failure retained; no automatic retry'}
