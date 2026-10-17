$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-medical-guidance-music-playtest-20261017'
$taskProof=Join-Path $taskRoot 'Docs/Development/TutorialReleaseV1/RETIREMENT_INVENTORY.json'
$taskGate=Get-Content -LiteralPath (Join-Path $taskRoot 'tmp/tutorial-release-v1-20261017/PREDELETE.json') -Raw|ConvertFrom-Json
if($taskGate.status -ne 'pass' -or (Get-FileHash -LiteralPath $taskProof).Hash.ToLowerInvariant() -ne $taskGate.inventory_sha256){throw 'Missing exact gate'}
if(Get-CimInstance Win32_Process|Where-Object {$_.Name -match 'UnrealEditor|WW2France|UnrealBuildTool|AutomationTool|ShaderCompileWorker'}){throw 'Preserve other owner'}
$taskPlan=Get-Content -LiteralPath $taskProof -Raw|ConvertFrom-Json
if($taskPlan.targets.Count -ne 7){throw 'Wrong inventory'}
foreach($taskTarget in $taskPlan.targets){
 $taskAbsolute=[IO.Path]::GetFullPath($taskTarget.path)
 $taskRelative=[IO.Path]::GetRelativePath($taskBase,$taskAbsolute)
 if($taskRelative -notmatch '^game_v[123678][\\/]Runtime(_stage_v2)?$'){throw 'Target outside named allowlist'}
 if($taskAbsolute -ne $taskTarget.path -or -not $taskAbsolute.StartsWith($taskBase+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Target escapes workspace'}
 $taskItems=@(Get-Item -LiteralPath $taskAbsolute -Force)+@(Get-ChildItem -LiteralPath $taskAbsolute -Recurse -Force)
 if($taskItems|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}){throw 'Preserve reparse target'}
}
foreach($taskTarget in $taskPlan.targets){Remove-Item -LiteralPath $taskTarget.path -Recurse -Force}
Write-Output 'Removed only7 fully inventoried generated Runtime directories; sources/evidence/saves retained.'
