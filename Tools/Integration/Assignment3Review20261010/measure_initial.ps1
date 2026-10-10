param([ValidateSet('baseline1','baseline2','baseline3')][Parameter(Mandatory=$true)][string]$Case)
$ErrorActionPreference='Stop'
$reviewRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build; no launch'}
$reviewSelector=Get-Content -LiteralPath (Join-Path $reviewRoot 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json') -Raw|ConvertFrom-Json
$reviewExe=Join-Path $reviewRoot 'tmp/Playtest-G1-Foley-V2-20261009/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $reviewExe).Hash.ToLower() -ne $reviewSelector.game_sha256){throw 'Selected Game drift'}
$reviewManifest=Get-Content -LiteralPath (Join-Path $reviewRoot $reviewSelector.source_manifest) -Raw|ConvertFrom-Json
foreach($reviewRow in $reviewManifest.files){
 $reviewPath=Join-Path (Join-Path $reviewRoot $reviewSelector.source_snapshot) $reviewRow.path
 if((Get-FileHash -LiteralPath $reviewPath).Hash.ToLower() -ne $reviewRow.sha256){throw ('Selected source drift '+$reviewRow.path)}
}
$reviewOut=Join-Path $reviewRoot ('tmp/assignment3-review-20261010/performance/'+$Case)
if(Test-Path -LiteralPath $reviewOut){throw 'Preserve occupied case'}
New-Item -ItemType Directory -Path $reviewOut|Out-Null
$reviewQuality='sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0,csvprofile STARTFILE='+$Case+',csvprofile FRAMES=12000'
$reviewArgs=@('-RenderOffscreen','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-DisablePython','-noraytracing','-ExitAfterCsvProfiling','-ParisSavePrefix=ParisG1PlaytestV5',('-UserDir="'+$reviewOut+'/UserDir"'),('-ABSLOG="'+$reviewOut+'/game.log"'),'-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0',('-ExecCmds="'+$reviewQuality+'"'))
$reviewRecord=[ordered]@{case=$Case;started=(Get-Date).ToString('o');game_sha256=$reviewSelector.game_sha256;source_files_verified=$reviewManifest.files.Count;args=$reviewArgs;scope='Exact normal selected Game; existing initial scene only; no gameplay input/helper, NPC addition, or full stress acceptance'}
$reviewProcess=Start-Process -FilePath $reviewExe -ArgumentList $reviewArgs -WorkingDirectory (Split-Path $reviewExe) -WindowStyle Hidden -PassThru
$reviewRecord.pid=$reviewProcess.Id;$reviewRecord.status='owned_game_launched'
$reviewRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $reviewOut 'launch.json')
$reviewRecord|ConvertTo-Json -Depth 5
$reviewProcess.WaitForExit()
$reviewRecord.exit_code=$reviewProcess.ExitCode;$reviewRecord.status='owned_game_exited';$reviewRecord.finished=(Get-Date).ToString('o')
$reviewRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $reviewOut 'launch.json')
$reviewRecord|ConvertTo-Json -Depth 5
if($reviewRecord.exit_code -ne 0){throw 'Entry failure retained; no retries under same identity'}
