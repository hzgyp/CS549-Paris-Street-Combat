param([ValidateSet('recording_v1','recording_v2','recording_v3','recording_v4','recording_v5','recording_v6')][string]$Revision='recording_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-demo-draft03-20261009'
$taskPlanPath=Join-Path $taskOut ($Revision+'_prepare.json')
if($Revision -eq 'recording_v1' -and !(Test-Path -LiteralPath $taskPlanPath)){$taskPlanPath=Join-Path $taskOut 'prepare.json'}
$taskPlan=Get-Content -LiteralPath $taskPlanPath -Raw|ConvertFrom-Json
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active engine/build'}
$taskProject=$taskPlan.project
foreach($taskRow in $taskPlan.recording_source_files){if((Get-FileHash -LiteralPath (Join-Path $taskProject $taskRow.path)).Hash.ToLower() -ne $taskRow.sha256){throw 'Recording source drift'}}
$taskReceipt=[ordered]@{status='building';started=(Get-Date).ToString('o');scope='Separate recording input fixture; Game only; no Editor/native save/recook'}
$taskReceiptPath=Join-Path $taskOut ($Revision+'/build.json')
if(Test-Path -LiteralPath $taskReceiptPath){throw 'Preserve occupied build receipt'}
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' WW2FranceLiberation Win64 Development ('-Project='+$taskProject+'/WW2FranceLiberation.uproject') -WaitMutex -NoHotReload 2>&1|Tee-Object -FilePath (Join-Path $taskOut ($Revision+'/build.log'))|Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){$taskReceipt.status='failed_compile';$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath;Get-Content (Join-Path $taskOut ($Revision+'/build.log')) -Tail 25;throw 'Preserve failed compile'}
$taskArchive=Join-Path $taskOut ($Revision+'/Archive')
$taskInner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
foreach($taskRow in $taskPlan.normal_files){
 if($taskRow.path -eq $taskInner -or $taskRow.path -eq 'PLAY_G1_REVISION.cmd'){continue}
 $taskFrom=Join-Path $taskPlan.normal_playable $taskRow.path
 if((Get-FileHash -LiteralPath $taskFrom).Hash.ToLower() -ne $taskRow.sha256){throw 'Normal closure drift'}
 $taskTo=Join-Path $taskArchive $taskRow.path
 New-Item -ItemType Directory -Path (Split-Path $taskTo) -Force|Out-Null
 New-Item -ItemType HardLink -Path $taskTo -Target $taskFrom|Out-Null
}
Copy-Item -LiteralPath (Join-Path $taskProject 'Binaries/Win64/WW2FranceLiberation.exe') -Destination (Join-Path $taskArchive $taskInner)
$taskReceipt.game_sha256=(Get-FileHash -LiteralPath (Join-Path $taskArchive $taskInner)).Hash.ToLower()
$taskReceipt.status='built_runtime_unverified';$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath
$taskReceipt|ConvertTo-Json
