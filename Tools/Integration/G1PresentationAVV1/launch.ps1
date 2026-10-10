param(
 [ValidateSet('checkpoint','actions','legacy')][string]$Mode='checkpoint',
 [Parameter(Mandatory=$true)][string]$CaseDirectory,
 [switch]$RecordAudio
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=[IO.Path]::GetFullPath((Join-Path $taskRoot $CaseDirectory))
if(-not $taskOut.StartsWith(($taskRoot+'\tmp\'),[StringComparison]::OrdinalIgnoreCase)){throw 'Case must remain under workspace tmp'}
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve active user engine'}
if(Test-Path -LiteralPath (Join-Path $taskOut 'launch.json')){throw 'Preserve occupied identity'}
$taskBuilt=Get-Content -LiteralPath (Join-Path $taskRoot 'tmp/g1-av-revision-20261009/candidate_v3/build.json') -Raw | ConvertFrom-Json
if($taskBuilt.status -ne 'built_private_runtime_unverified' -or $taskBuilt.exit_code -ne 0){throw 'Game must be built'}
$taskBinary=Join-Path $taskRoot 'tmp/g1-av-revision-20261009/candidate_v3/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
$taskHash=(Get-FileHash -LiteralPath $taskBinary).Hash.ToLower()
if($taskHash -ne $taskBuilt.game_sha256){throw 'Game hash drift'}
New-Item -ItemType Directory -Path $taskOut -Force|Out-Null
$taskPrefix='ParisAV20261009_'+$Mode
if($Mode -eq 'legacy'){
 $taskSaveDir=Join-Path $taskOut 'User/Saved/SaveGames';New-Item -ItemType Directory -Path $taskSaveDir -Force|Out-Null
 $taskLegacy=Join-Path $taskRoot 'tmp/g1-demo-draft-20261009/checkpoint/User/Saved/SaveGames/ParisDemo20261009_checkpoint_A.sav'
 $taskCopied=Join-Path $taskSaveDir ($taskPrefix+'_A.sav')
 Copy-Item -LiteralPath $taskLegacy -Destination $taskCopied
 if((Get-FileHash -LiteralPath $taskLegacy).Hash -ne (Get-FileHash -LiteralPath $taskCopied).Hash){throw 'Legacy journal copy mismatch'}
}
$taskQuality='DisableAllScreenMessages,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',
 ('-ParisSavePrefix='+$taskPrefix),('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisAVAuditOut="'+$taskOut+'"'),('-ExecCmds="'+$taskQuality+'"'),
 ('-ParisUXTest='+$Mode),('-ParisUXTestOut="'+$taskOut+'"'))
if($RecordAudio){$taskArgs+= '-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0'}
$taskProcess=Start-Process -FilePath $taskBinary -ArgumentList $taskArgs -PassThru
$taskRecord=[ordered]@{mode=$Mode;pid=$taskProcess.Id;started=(Get-Date).ToString('o');arguments=$taskArgs;binary_sha256=$taskHash;scope='Visible real fixed game/audio, isolated V5 journal, disclosed finite native input observer, no UDP messaging'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{mode=$Mode;pid=$taskProcess.Id;directory=$taskOut;sha256=$taskHash}|ConvertTo-Json
if($taskProcess.WaitForExit(300000)){$taskRecord.exit_code=$taskProcess.ExitCode;$taskRecord.exited=(Get-Date).ToString('o')}
else{$taskRecord.deadline=$true;$taskRecord.note='Inspect owned window, do not force terminate'}
$taskRecord|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{mode=$Mode;exit_code=$taskRecord.exit_code;deadline=$taskRecord.deadline;directory=$taskOut}|ConvertTo-Json
