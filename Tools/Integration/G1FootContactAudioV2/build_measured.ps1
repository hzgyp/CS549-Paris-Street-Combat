$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2'
$taskPlan=Get-Content -LiteralPath (Join-Path $taskOut 'prepare.json') -Raw | ConvertFrom-Json
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active user engine/build'}
foreach($taskRow in $taskPlan.source_files){
 if((Get-FileHash -LiteralPath (Join-Path $taskPlan.project $taskRow.path)).Hash.ToLower() -ne $taskRow.sha256){throw 'Source drift'}
}
$taskReceiptPath=Join-Path $taskOut 'build.json'
if(Test-Path -LiteralPath $taskReceiptPath){throw 'Preserve occupied build identity'}
$taskReceipt=[ordered]@{started=(Get-Date).ToString('o');status='building';scope='Game-only one audio helper; no Editor/native save/recook/OBS'}
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath
$taskProject=Join-Path $taskPlan.project 'WW2FranceLiberation.uproject'
$taskArgs=@('WW2FranceLiberation','Win64','Development',('-Project='+$taskProject),'-WaitMutex','-NoHotReload')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' @taskArgs 2>&1 | Tee-Object -FilePath (Join-Path $taskOut 'game_build.log') | Out-Null
$taskReceipt.exit_code=$LASTEXITCODE
if($LASTEXITCODE -ne 0){
 $taskReceipt.status='compile_failed';$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath
 Get-Content -LiteralPath (Join-Path $taskOut 'game_build.log') -Tail 28
 throw 'Preserve failed build/source identity'
}
$taskInner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
foreach($taskRow in $taskPlan.archive_files){
 $taskFrom=Join-Path $taskPlan.reuse_archive $taskRow.path
 if((Get-FileHash -LiteralPath $taskFrom).Hash.ToLower() -ne $taskRow.sha256){throw 'Cooked closure drift'}
 if($taskRow.path -eq $taskInner){continue}
 $taskTo=Join-Path $taskOut ('Archive/'+$taskRow.path)
 New-Item -ItemType Directory -Path (Split-Path $taskTo) -Force|Out-Null
 if($taskRow.path -eq 'PLAY_G1_REVISION.cmd'){Copy-Item -LiteralPath $taskFrom -Destination $taskTo}
 else{New-Item -ItemType HardLink -Path $taskTo -Target $taskFrom|Out-Null}
}
$taskBinary=Join-Path $taskPlan.project 'Binaries/Win64/WW2FranceLiberation.exe'
$taskGameHash=(Get-FileHash -LiteralPath $taskBinary).Hash.ToLower()
if($taskGameHash -eq $taskPlan.parent.game_sha256){throw 'Expected new audio helper build'}
Copy-Item -LiteralPath $taskBinary -Destination (Join-Path $taskOut ('Archive/'+$taskInner))
Copy-Item -LiteralPath (Join-Path $taskOut 'Audio') -Destination (Join-Path $taskOut 'Archive/Windows/WW2FranceLiberation/Audio') -Recurse
$taskReceipt.status='built_runtime_unverified';$taskReceipt.game_sha256=$taskGameHash;$taskReceipt.finished=(Get-Date).ToString('o')
$taskReceipt|ConvertTo-Json|Set-Content -LiteralPath $taskReceiptPath
$taskReceipt|ConvertTo-Json

