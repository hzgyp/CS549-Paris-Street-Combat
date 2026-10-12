param([string]$Revision='candidate_v1',[ValidateSet('Game','Editor')][string]$Target='Game')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot ('tmp/g1-tactical-equipment-20261010/'+$Revision)
$taskPlan=Get-Content -LiteralPath (Join-Path $taskOut 'prepare.json') -Raw | ConvertFrom-Json
$taskReceiptPath=Join-Path $taskOut ('build-'+$Target.ToLowerInvariant()+'.json')
if(Test-Path -LiteralPath $taskReceiptPath){throw 'Preserve occupied build identity'}
$taskSnapshot=Join-Path $taskOut ('compiled-source-'+$Target.ToLowerInvariant())
New-Item -ItemType Directory -Path $taskSnapshot | Out-Null
foreach($taskDir in @('Config','Source','Plugins')){Copy-Item -LiteralPath (Join-Path $taskPlan.project $taskDir) -Destination $taskSnapshot -Recurse}
Copy-Item -LiteralPath (Join-Path $taskPlan.project 'WW2FranceLiberation.uproject') -Destination $taskSnapshot
$taskReceipt=[ordered]@{status='building';target=$Target;started=[DateTimeOffset]::Now.ToString('o');source_snapshot=$taskSnapshot}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
$taskTargetName=if($Target -eq 'Editor'){'WW2FranceLiberationEditor'}else{'WW2FranceLiberation'}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' $taskTargetName Win64 Development ('-Project='+$taskPlan.project+'/WW2FranceLiberation.uproject') -WaitMutex -NoHotReload 2>&1 | Tee-Object -FilePath (Join-Path $taskOut ('build-'+$Target.ToLowerInvariant()+'.log')) | Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
$taskReceipt.status=if($LASTEXITCODE -eq 0){'built_runtime_unverified'}else{'compile_failed'}
$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
if($Target -eq 'Game' -and $LASTEXITCODE -eq 0){$taskReceipt.game_sha256=(Get-FileHash -LiteralPath (Join-Path $taskPlan.project 'Binaries/Win64/WW2FranceLiberation.exe')).Hash.ToLowerInvariant()}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
Get-Content -LiteralPath (Join-Path $taskOut ('build-'+$Target.ToLowerInvariant()+'.log')) -Tail 12
if($taskReceipt.exit_code -ne 0){throw 'Preserve failed source/build identity'}
