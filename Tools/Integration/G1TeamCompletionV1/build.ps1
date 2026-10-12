param([ValidateSet('candidate_v1','candidate_v2','candidate_v3','candidate_v4','candidate_v5','candidate_v6','candidate_v7','candidate_v8','candidate_v9')][string]$Revision='candidate_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot ('tmp/g1-team-completion-20261010/'+$Revision)
$taskPlan=Get-Content -LiteralPath (Join-Path $taskOut 'prepare.json') -Raw | ConvertFrom-Json
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active user engine/build'}
foreach($taskRow in $taskPlan.source_files){if((Get-FileHash -LiteralPath (Join-Path $taskPlan.project $taskRow.path)).Hash.ToLowerInvariant() -ne $taskRow.sha256){throw 'Candidate source drift'}}
$taskReceiptPath=Join-Path $taskOut 'build.json'
if(Test-Path -LiteralPath $taskReceiptPath){throw 'Preserve occupied build identity'}
$taskReceipt=[ordered]@{status='building';started=[DateTimeOffset]::Now.ToString('o');scope='Game-only bounded interaction; no Editor/native save/recook'}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' WW2FranceLiberation Win64 Development ('-Project='+$taskPlan.project+'/WW2FranceLiberation.uproject') -WaitMutex -NoHotReload 2>&1 | Tee-Object -FilePath (Join-Path $taskOut 'build.log') | Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){$taskReceipt.status='compile_failed';$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath;Get-Content -LiteralPath (Join-Path $taskOut 'build.log') -Tail 36;throw 'Retain failed build/source identity'}
$taskBinary=Join-Path $taskPlan.project 'Binaries/Win64/WW2FranceLiberation.exe'
$taskReceipt.game_sha256=(Get-FileHash -LiteralPath $taskBinary).Hash.ToLowerInvariant()
$taskReceipt.status='built_runtime_unverified';$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
$taskReceipt | ConvertTo-Json
