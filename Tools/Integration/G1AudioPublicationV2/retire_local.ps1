#requires -Version 7
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'tmp/g1-audio-publication-20261009'
$taskPython=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskPlanPath=Join-Path $taskOut 'retirement.json'
$taskPlan=Get-Content -LiteralPath $taskPlanPath -Raw|ConvertFrom-Json
$taskAuthority=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/Development/G1AudioPublicationV2/RETIREMENT_INVENTORY_20261009.json') -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath $taskPlanPath).Hash.ToLowerInvariant() -ne $taskAuthority.plan_sha256){throw 'Retirement plan changed'}
$taskWhitelist=@(
 'tmp/Playtest-G1-HUD-20261009',
 'tmp/Playtest-G1-AV-20261009',
 'tmp/Playtest-G1-Foley-20261009',
 'tmp/g1-playtest-revision-20261008/hud_v3/Archive',
 'tmp/g1-av-revision-20261009/candidate_v2/Archive',
 'tmp/g1-av-revision-20261009/candidate_v3/Archive',
 'tmp/g1-recorded-foley-20261009/candidate_v1/Archive',
 'tmp/g1-foot-contact-audio-v2-20261009/candidate_v1/Archive',
 'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Archive',
 'tmp/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip'
)
if($taskPlan.targets.Count -ne $taskWhitelist.Count){throw 'Unexpected target count'}
foreach($taskTarget in $taskPlan.targets){if($taskTarget.path -notin $taskWhitelist){throw 'Unknown deletion target'}}
function CheckIdle {
 $taskActive=@(Get-CimInstance Win32_Process|Where-Object {
  $_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\.exe$' -or
  ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
 })
 if($taskActive.Count){throw 'Preserve active user/build processes'}
}
function CheckedPath([string]$taskRelative){
 $taskAbsolute=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskRelative))
 if(-not $taskAbsolute.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Target outside workspace'}
 $taskCursor=$taskAbsolute
 while($taskCursor -ne $taskRoot){
  if(Test-Path -LiteralPath $taskCursor){if((Get-Item -LiteralPath $taskCursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'}}
  $taskCursor=Split-Path -Parent $taskCursor
 }
 return $taskAbsolute
}
CheckIdle
& $taskPython (Join-Path $PSScriptRoot 'publish.py') predelete
if($LASTEXITCODE -ne 0){throw 'Predelete protection/recovery check failed'}
$taskFreeBefore=(Get-PSDrive D).Free
$taskRemoved=[Collections.Generic.List[object]]::new()
foreach($taskTarget in $taskPlan.targets){
 CheckIdle
 $taskAbsolute=CheckedPath $taskTarget.path
 if(-not (Test-Path -LiteralPath $taskAbsolute)){throw 'Input unexpectedly absent'}
 if($taskTarget.kind -eq 'directory'){
  $taskItems=@(Get-ChildItem -LiteralPath $taskAbsolute -Recurse -Force)
  if(@($taskItems|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Reparse descendant'}
  $taskFiles=@($taskItems|Where-Object {-not $_.PSIsContainer})
  $taskExpected=@($taskPlan.files|Where-Object {$_.target -eq $taskTarget.path})
  if($taskFiles.Count -ne $taskExpected.Count){throw 'File inventory changed'}
  $taskByName=@{};foreach($taskFile in $taskFiles){$taskByName[[IO.Path]::GetRelativePath($taskRoot,$taskFile.FullName).Replace('\','/')]=$taskFile}
  foreach($taskRow in $taskExpected){
   if(-not $taskByName.ContainsKey($taskRow.path)){throw 'Input path changed'}
   $taskFile=$taskByName[$taskRow.path]
   $taskMtime=([long]$taskFile.LastWriteTimeUtc.Ticks-621355968000000000L)*100L
   if($taskFile.Length -ne $taskRow.size_bytes -or $taskMtime -ne $taskRow.mtime_ns){throw 'Input metadata changed'}
  }
  Remove-Item -LiteralPath $taskAbsolute -Recurse -Force
 }elseif($taskTarget.kind -eq 'file'){
  if((Get-FileHash -LiteralPath $taskAbsolute).Hash.ToLowerInvariant() -ne $taskTarget.sha256){throw 'ZIP changed'}
  Remove-Item -LiteralPath $taskAbsolute -Force
 }else{throw 'Unknown target type'}
 if(Test-Path -LiteralPath $taskAbsolute){throw 'Removal incomplete'}
 $taskRemoved.Add($taskTarget)
 @($taskRemoved)|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskOut 'local_deleted_targets.json') -Encoding utf8
 Write-Output ('Retired '+$taskTarget.path)
}
[ordered]@{finished=(Get-Date).ToString('o');targets=$taskRemoved.Count;free_before_bytes=$taskFreeBefore;free_after_bytes=(Get-PSDrive D).Free;no_user_process_terminated=$true}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'local-retirement.json') -Encoding utf8
