$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-demo-draft04-20261010/recording_stats_v1'
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
$taskPlan=Get-Content -LiteralPath (Join-Path $taskOut 'prepare.json') -Raw|ConvertFrom-Json
foreach($taskRow in $taskPlan.files){if((Get-FileHash -LiteralPath (Join-Path $taskPlan.project $taskRow.path)).Hash.ToLower() -ne $taskRow.sha256){throw 'Prepared source drift'}}
if(Test-Path -LiteralPath (Join-Path $taskOut 'build.json')){throw 'Preserve build receipt'}
$taskReceipt=[ordered]@{status='building';started=(Get-Date).ToString('o');scope='Separate Game diagnostics only; no Editor/save/recook'}
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'build.json')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' WW2FranceLiberation Win64 Development ('-Project='+$taskPlan.project+'/WW2FranceLiberation.uproject') -WaitMutex -NoHotReload 2>&1|Tee-Object -FilePath (Join-Path $taskOut 'build.log')|Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){$taskReceipt.status='failed_compile';$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'build.json');Get-Content -LiteralPath (Join-Path $taskOut 'build.log') -Tail 24;throw 'Preserve failed compile'}
$taskNew=Join-Path $taskPlan.project 'Binaries/Win64/WW2FranceLiberation.exe'
$taskFrozenGame=Join-Path $taskOut 'Game.exe'
Copy-Item -LiteralPath $taskNew -Destination $taskFrozenGame
$taskReceipt.game_sha256=(Get-FileHash -LiteralPath $taskFrozenGame).Hash.ToLower()
if((Get-FileHash -LiteralPath $taskPlan.stable_runtime).Hash.ToLower() -ne $taskPlan.retained_v6_sha256){throw 'Stable V6 runtime drift'}
Copy-Item -LiteralPath $taskFrozenGame -Destination $taskPlan.stable_runtime
if((Get-FileHash -LiteralPath $taskPlan.stable_runtime).Hash.ToLower() -ne $taskReceipt.game_sha256){throw 'Runtime parity'}
$taskReceipt.status='diagnostic_game_built_runtime_unverified';$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'build.json')
$taskReceipt|ConvertTo-Json
