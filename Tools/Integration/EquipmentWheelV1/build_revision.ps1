param([string]$Revision='candidate_equipment_wheel_build_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot ('tmp/g1-tactical-equipment-20261010/'+$Revision)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve revision identity'}
$taskProject=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project'
New-Item -ItemType Directory -Path $taskOut | Out-Null
@{status='independent_source_receipt';project=$taskProject;revision=$Revision;parent_revision='candidate_grenade_models_v5'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'prepare.json')
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $taskRoot 'Tools/Integration/GrenadeModelsV1/snapshot.py') $taskProject (Join-Path $taskOut 'compiled-source-game')
if($LASTEXITCODE -ne 0){throw 'Snapshot failed'}
$taskReceipt=[ordered]@{status='building';target='Game';started=[DateTimeOffset]::Now.ToString('o');source_snapshot=(Join-Path $taskOut 'compiled-source-game')}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'build-game.json')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' WW2FranceLiberation Win64 Development ('-Project='+$taskProject+'/WW2FranceLiberation.uproject') -WaitMutex -NoHotReload 2>&1 | Tee-Object -FilePath (Join-Path $taskOut 'build-game.log') | Out-Null
$taskReceipt.exit_code=$LASTEXITCODE;$taskReceipt.status=if($LASTEXITCODE -eq 0){'built_runtime_unverified'}else{'compile_failed'};$taskReceipt.finished=[DateTimeOffset]::Now.ToString('o')
if($LASTEXITCODE -eq 0){$taskReceipt.game_sha256=(Get-FileHash -LiteralPath (Join-Path $taskProject 'Binaries/Win64/WW2FranceLiberation.exe')).Hash.ToLowerInvariant()}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'build-game.json')
Get-Content -LiteralPath (Join-Path $taskOut 'build-game.log') -Tail 9
if($taskReceipt.exit_code -ne 0){throw 'Keep failed build identity'}
