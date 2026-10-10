#requires -Version 7
param([ValidateSet('Execute','Verify')][string]$Phase='Execute')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskRecord=Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PackageRetirement20261009/run_v1'
$taskPython='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskPlanPath=Join-Path $taskRecord 'plan.json'
$taskResultPath=Join-Path $taskRecord 'result.json'
$taskWhitelist=@(
    'tmp/Playtest-G1-20261008',
    'tmp/Playtest-G1-20261009',
    'tmp/mvp-closeout-20261008/instrument_v13/Archive',
    'tmp/paris-city-package-20261002/package_v3/Archive',
    'Unreal/ParisStreetCombat/Saved/StagedBuilds',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v1/Archive',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v2/Archive',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v6/Archive',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v7/Archive',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v14/Archive',
    'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/instrument_v15/Archive'
)
function Idle {
    $active=@(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealEditor-Cmd|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\.exe$' -or
        ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
    })
    if($active.Count){throw 'Preserve active user/editor/build processes; no automatic termination'}
}
function CheckedPath([string]$relative) {
    if($relative -notin $taskWhitelist){throw "Not an authorized target: $relative"}
    $resolved=[IO.Path]::GetFullPath((Join-Path $taskRoot $relative))
    if(-not $resolved.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Outside workspace'}
    $ancestor=$resolved
    while($ancestor -ne $taskRoot){
        if(Test-Path -LiteralPath $ancestor){
            if((Get-Item -LiteralPath $ancestor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'}
        }
        $ancestor=Split-Path -Parent $ancestor
    }
    if(Test-Path -LiteralPath $resolved){
        foreach($item in Get-ChildItem -LiteralPath $resolved -Force -Recurse){
            if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse descendant'}
            if(-not $item.FullName.StartsWith($resolved+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected descendant'}
        }
    }
    return $resolved
}
$taskPlan=Get-Content -LiteralPath $taskPlanPath -Raw|ConvertFrom-Json
$taskPrepared=Get-Content -LiteralPath (Join-Path $taskRecord 'prepared.json') -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath $taskPlanPath).Hash.ToLowerInvariant() -ne $taskPrepared.plan_sha256){throw 'Plan changed'}
if($taskPlan.status -ne 'prepared_no_deletion' -or $taskPlan.authorization -ne '2026-10-09 user selects HUD development baseline and permits obsolete package deletion'){throw 'Wrong authorization'}
if($taskPlan.targets.Count -ne 11 -or @($taskPlan.targets.path|Sort-Object -Unique).Count -ne 11){throw 'Wrong target count'}
foreach($target in $taskPlan.targets){CheckedPath $target.path|Out-Null}
if($Phase -eq 'Execute'){
    if(Test-Path -LiteralPath $taskResultPath){throw 'Preserve previous result'}
    Idle
    & $taskPython (Join-Path $taskRoot 'Tools/Archive/retire_packaged_versions_20261009.py') predelete
    if($LASTEXITCODE -ne 0){throw 'Protected/recovery predelete check failed'}
    foreach($target in $taskPlan.targets){
        $absolute=CheckedPath $target.path
        $actual=@(Get-ChildItem -LiteralPath $absolute -Recurse -Force -File)
        $expected=@($taskPlan.files|Where-Object target -eq $target.path)
        if($actual.Count -ne $expected.Count){throw 'Input inventory changed'}
        $byPath=@{};foreach($file in $actual){$byPath[[IO.Path]::GetRelativePath($taskRoot,$file.FullName).Replace('\','/')]=$file}
        foreach($row in $expected){
            if(-not $byPath.ContainsKey($row.path)){throw 'Input path changed'}
            $file=$byPath[$row.path]
            $mtime=([long]$file.LastWriteTimeUtc.Ticks-621355968000000000L)*100L
            if($file.Length -ne $row.size_bytes -or $mtime -ne $row.mtime_ns){throw "Input metadata changed: $($row.path)"}
            if(-not $row.path.StartsWith($target.path+'/',[StringComparison]::OrdinalIgnoreCase)){throw 'Row escapes target'}
        }
    }
    $freeBefore=(Get-PSDrive -Name D).Free
    $removed=[Collections.Generic.List[object]]::new()
    foreach($target in $taskPlan.targets){
        Idle
        $absolute=CheckedPath $target.path
        Remove-Item -LiteralPath $absolute -Recurse -Force
        if(Test-Path -LiteralPath $absolute){throw 'Removal incomplete'}
        $removed.Add($target)
        @($removed)|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskRecord 'deleted_targets.json') -Encoding utf8
        Write-Output ("Removed obsolete output {0}: {1:N2} GiB" -f $target.path,($target.size_bytes/1GB))
    }
    & $taskPython (Join-Path $taskRoot 'Tools/Archive/retire_packaged_versions_20261009.py') verify
    if($LASTEXITCODE -ne 0){throw 'Post-removal baseline check failed'}
    $freeAfter=(Get-PSDrive -Name D).Free
    $logical=0L;foreach($target in $removed){$logical+=[long]$target.size_bytes}
    $surveyRecord=Get-Content -LiteralPath (Join-Path (Split-Path $taskRecord) 'before_run_v1.json') -Raw|ConvertFrom-Json
    $survey=[long]$surveyRecord.free_before_prepare_bytes
    [ordered]@{status='pass_selected_hud_baseline_obsolete_packages_retired';finished=(Get-Date).ToString('o');
        plan_sha256=$taskPrepared.plan_sha256;targets_removed=$removed.Count;logical_removed_bytes=$logical;
        new_unique_archive_bytes=$taskPlan.new_zip.size_bytes;free_before_prepare_bytes=$survey;
        free_before_delete_bytes=$freeBefore;free_after_bytes=$freeAfter;actual_free_increase_from_prepare_bytes=($freeAfter-$survey);
        current_hud_trial_intact=$true;selected_source40_and_authoring40_exact=$true;canonical758_protected703_exact=$true;
        previous_cleanup_receipts_unchanged=$true;recovery_override_files=7;source_logs_images_user_saves_retained=$true;
        no_engine_launch_or_termination=$true;no_git_commit_push=$true}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $taskResultPath -Encoding utf8
} else {
    & $taskPython (Join-Path $taskRoot 'Tools/Archive/retire_packaged_versions_20261009.py') verify
    if($LASTEXITCODE -ne 0){throw 'Post-removal verification failed'}
    Get-Content -LiteralPath $taskResultPath
}
