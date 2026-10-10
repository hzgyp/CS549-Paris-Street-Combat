param([ValidateSet('actions','legacy')][string]$Mode='actions')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-foot-contact-audio-v2-20261009'
$taskOut=Join-Path $taskBase ('checks/'+$Mode)
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve user engine'}
if(Test-Path -LiteralPath (Join-Path $taskOut 'launch.json')){throw 'Preserve occupied check'}
$taskBuild=Get-Content -LiteralPath (Join-Path $taskBase 'candidate_v1/build.json') -Raw | ConvertFrom-Json
if($taskBuild.status -ne 'built_runtime_unverified' -or $taskBuild.exit_code -ne 0){throw 'Require built Game'}
$taskBinary=Join-Path $taskBase 'candidate_v1/Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskBinary).Hash.ToLower() -ne $taskBuild.game_sha256){throw 'Executable drift'}
New-Item -ItemType Directory -Path $taskOut -Force|Out-Null
$taskPrefix='ParisFootV220261009_'+$Mode
if($Mode -eq 'legacy'){
 $taskSaveDir=Join-Path $taskOut 'User/Saved/SaveGames';New-Item -ItemType Directory -Path $taskSaveDir -Force|Out-Null
 $taskOld=Join-Path $taskRoot 'tmp/g1-demo-draft-20261009/checkpoint/User/Saved/SaveGames/ParisDemo20261009_checkpoint_A.sav'
 $taskCopy=Join-Path $taskSaveDir ($taskPrefix+'_A.sav');Copy-Item -LiteralPath $taskOld -Destination $taskCopy
 if((Get-FileHash -LiteralPath $taskOld).Hash -ne (Get-FileHash -LiteralPath $taskCopy).Hash){throw 'Old journal copy mismatch'}
}
$taskQuality='DisableAllScreenMessages,sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.PostProcessQuality 2,sg.TextureQuality 2,sg.EffectsQuality 2,sg.FoliageQuality 2,sg.ShadingQuality 2,r.ScreenPercentage 100,r.Streaming.PoolSize 1536,r.VSync 0,t.MaxFPS 0'
$taskArgs=@('-windowed','-ForceRes','-ResX=1920','-ResY=1080','-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',
 ('-ParisSavePrefix='+$taskPrefix),('-UserDir="'+$taskOut+'/User"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisAVAuditOut="'+$taskOut+'"'),
 ('-ExecCmds="'+$taskQuality+'"'),('-ParisUXTest='+$Mode),('-ParisUXTestOut="'+$taskOut+'"'),'-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0')
$taskProcess=Start-Process -FilePath $taskBinary -ArgumentList $taskArgs -PassThru
$taskReceipt=[ordered]@{mode=$Mode;pid=$taskProcess.Id;started=(Get-Date).ToString('o');game_sha256=$taskBuild.game_sha256;arguments=$taskArgs;
 scope='Existing finite native input/audio check, isolated UserDir/master mix WAV; no OBS or new screen recording; acoustic acceptance pending'}
$taskReceipt|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{pid=$taskProcess.Id;mode=$Mode;scope='AUDIO CHECK ONLY / NO SCREEN RECORDING'}|ConvertTo-Json
if($taskProcess.WaitForExit(180000)){$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.exited=(Get-Date).ToString('o')}
else{$taskReceipt.deadline=$true;$taskReceipt.note='Inspect owned game, no automatic force termination'}
$taskReceipt|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
$taskReceipt|ConvertTo-Json -Depth 5

