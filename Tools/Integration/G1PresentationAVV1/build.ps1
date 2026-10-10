param([ValidatePattern('^candidate_v[0-9]+$')][string]$Identity='candidate_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot ('tmp/g1-av-revision-20261009/'+$Identity)
$taskPrepared=Get-Content -LiteralPath (Join-Path $taskOut 'prepare.json') -Raw | ConvertFrom-Json
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
$taskProject=Join-Path $taskPrepared.project 'WW2FranceLiberation.uproject'
if((Get-FileHash -LiteralPath $taskProject).Hash.ToLower() -ne $taskPrepared.descriptor_sha256){throw 'Descriptor drift'}
foreach($taskRow in $taskPrepared.private_source_files){
 if((Get-FileHash -LiteralPath (Join-Path $taskPrepared.project $taskRow.path)).Hash.ToLower() -ne $taskRow.sha256){throw ('Prepared source drift '+$taskRow.path)}
}
$taskReceiptPath=Join-Path $taskOut 'build.json'
if(Test-Path -LiteralPath $taskReceiptPath){throw 'Preserve occupied build receipt'}
$taskReceipt=[ordered]@{started=(Get-Date).ToString('o');status='building_game';scope='New owned selected-source working copy, no Editor/reflected schema/native/cook change'}
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
$taskArgs=@('WW2FranceLiberation','Win64','Development',('-Project='+$taskProject),'-WaitMutex','-NoHotReload')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' @taskArgs 2>&1 | Tee-Object -FilePath (Join-Path $taskOut 'game_build.log') | Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){
 $taskReceipt.status='compile_failed';$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
 Get-Content -LiteralPath (Join-Path $taskOut 'game_build.log') -Tail 32
 throw 'Preserve compile negative'
}
$taskReceipt.status='copying_exact_hud_cook'
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
foreach($taskRow in $taskPrepared.archive_files){
 $taskFrom=Join-Path $taskPrepared.reuse_archive $taskRow.path
 if((Get-Item -LiteralPath $taskFrom).Length -ne $taskRow.size_bytes -or (Get-FileHash -LiteralPath $taskFrom).Hash.ToLower() -ne $taskRow.sha256){throw 'Archived payload drift'}
 $taskTo=Join-Path $taskOut ('Archive/'+$taskRow.path)
 New-Item -ItemType Directory -Path (Split-Path $taskTo) -Force | Out-Null
 Copy-Item -LiteralPath $taskFrom -Destination $taskTo
 if((Get-FileHash -LiteralPath $taskTo).Hash.ToLower() -ne $taskRow.sha256){throw 'Archive copy mismatch'}
}
$taskGame=Join-Path $taskPrepared.project 'Binaries/Win64/WW2FranceLiberation.exe'
$taskGameHash=(Get-FileHash -LiteralPath $taskGame).Hash.ToLower()
if($taskGameHash -eq $taskPrepared.baseline.game_sha256){throw 'Expected rebuilt Game implementation'}
Copy-Item -LiteralPath $taskGame -Destination (Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')
Copy-Item -LiteralPath (Join-Path $taskOut 'Audio') -Destination (Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/Audio') -Recurse
$taskReceipt.status='built_private_runtime_unverified'
$taskReceipt.game_sha256=$taskGameHash
$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt | ConvertTo-Json | Set-Content -LiteralPath $taskReceiptPath
$taskReceipt | ConvertTo-Json
