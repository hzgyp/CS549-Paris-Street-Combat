param([ValidateSet('menu','checkpoint','restore')][string]$Mode='menu',[ValidatePattern('^[a-z0-9_]+$')][string]$Identity='menu_v1',[ValidateRange(640,3840)][int]$Width=1920,[ValidateRange(480,2160)][int]$Height=1080,[ValidatePattern('^[a-z0-9_]+$')][string]$SeedIdentity='checkpoint_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-team-completion-20261010'
$taskOut=Join-Path $taskBase ('checks/'+$Identity)
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied test identity'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskRuntime=Get-Content -LiteralPath (Join-Path $taskBase 'RUNTIME.json') -Raw | ConvertFrom-Json
$taskExe=Join-Path $taskRuntime.path 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
if((Get-FileHash -LiteralPath $taskExe).Hash.ToLowerInvariant() -ne $taskRuntime.game_sha256){throw 'Runtime changed'}
$taskUser=Join-Path $taskOut 'User'
$taskPrefix='ParisTeamP1_'+$Identity
if($Mode -eq 'restore'){$taskUser=Join-Path $taskBase ('checks/'+$SeedIdentity+'/User');$taskPrefix='ParisTeamP1_'+$SeedIdentity}
if($Mode -eq 'checkpoint'){
 $taskSaveDir=Join-Path $taskUser 'Saved/SaveGames';New-Item -ItemType Directory -Path $taskSaveDir -Force | Out-Null
 $taskOld=Join-Path $taskRoot 'tmp/g1-demo-draft-20261009/checkpoint/User/Saved/SaveGames/ParisDemo20261009_checkpoint_A.sav'
 $taskCopy=Join-Path $taskSaveDir ($taskPrefix+'_A.sav');Copy-Item -LiteralPath $taskOld -Destination $taskCopy
 if((Get-FileHash -LiteralPath $taskCopy).Hash -ne (Get-FileHash -LiteralPath $taskOld).Hash){throw 'Seeded old journal differs'}
}
$taskArgs=@('-windowed','-ForceRes',('-ResX='+$Width),('-ResY='+$Height),'-NoSplash','-DisablePython','-noraytracing','-UDPMESSAGING_TRANSPORT_ENABLE=false',('-UserDir="'+$taskUser+'"'),('-abslog="'+$taskOut+'/game.log"'),('-ParisSavePrefix='+$taskPrefix),('-ParisInteractionProbe='+$Mode),('-ParisInteractionOut="'+$taskOut+'"'),'-ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,r.VSync 0,t.MaxFPS 60"')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskReceipt=[ordered]@{status='running';mode=$Mode;identity=$Identity;pid=$taskProcess.Id;started=[DateTimeOffset]::Now.ToString('o');game_sha256=$taskRuntime.game_sha256;arguments=$taskArgs}
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
[ordered]@{pid=$taskProcess.Id;mode=$Mode;identity=$Identity}|ConvertTo-Json -Compress
$taskDeadline=[DateTime]::UtcNow.AddSeconds(130)
while(-not $taskProcess.WaitForExit(1000)){
 if([DateTime]::UtcNow -gt $taskDeadline){$taskReceipt.status='deadline_preserve_owned_process';$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json');throw 'Inspect owned game; no automatic force termination'}
}
$taskReceipt.exit_code=$taskProcess.ExitCode;$taskReceipt.status='exited';$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
$taskReceipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'launch.json')
if($taskProcess.ExitCode -ne 0){throw 'Game exited abnormally; preserve test'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'RESULT.json') -Raw | ConvertFrom-Json
[ordered]@{status=$taskResult.status;checks=$taskResult.checks.Count;exit_code=$taskProcess.ExitCode}|ConvertTo-Json -Compress
if(-not $taskResult.status.StartsWith('pass_')){throw 'Native interaction check failed'}
