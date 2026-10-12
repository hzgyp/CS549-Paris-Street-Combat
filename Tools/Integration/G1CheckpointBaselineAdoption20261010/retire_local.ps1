#requires -Version 7
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut = Join-Path $taskRoot 'tmp/g1-checkpoint-baseline-adoption-20261010'
$taskPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskPlanPath = Join-Path $taskOut 'retirement.json'
$taskProof = Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/Development/G1CheckpointBaselineAdoption20261010/RETIREMENT_INVENTORY_20261010.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $taskPlanPath).Hash.ToLowerInvariant() -ne $taskProof.inventory_sha256) { throw 'Frozen plan changed' }
$taskPlan = Get-Content -LiteralPath $taskPlanPath -Raw | ConvertFrom-Json
function CheckIdle {
    $taskProcesses = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\.exe$' -or
        ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
    })
    if ($taskProcesses.Count) { throw 'Preserve active user/build process; no termination' }
}
function CheckedPath([string]$taskRelative) {
    $taskAbsolute = [IO.Path]::GetFullPath((Join-Path $taskRoot $taskRelative))
    if (-not $taskAbsolute.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside workspace' }
    if ($taskRelative -like 'tmp/Playtest-G1-EnemyClear-candidate_v3-20261010*' -or $taskRelative -like 'tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3*') { throw 'Current baseline protected' }
    $taskCursor = $taskAbsolute
    while ($taskCursor -ne $taskRoot) {
        if (Test-Path -LiteralPath $taskCursor) {
            if ((Get-Item -LiteralPath $taskCursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse ancestor' }
        }
        $taskCursor = Split-Path -Parent $taskCursor
    }
    return $taskAbsolute
}
CheckIdle
& $taskPython (Join-Path $PSScriptRoot 'manage.py') predelete
if ($LASTEXITCODE -ne 0) { throw 'Predelete guards/recovery failed' }
$taskFreeBefore = (Get-PSDrive D).Free
$taskRemoved = [Collections.Generic.List[string]]::new()
foreach ($taskTarget in $taskPlan.targets) {
    CheckIdle
    $taskAbsolute = CheckedPath $taskTarget.path
    if (-not (Test-Path -LiteralPath $taskAbsolute)) { throw 'Target unexpectedly absent' }
    if ($taskTarget.kind -eq 'directory') {
        $taskChildren = @(Get-ChildItem -LiteralPath $taskAbsolute -Recurse -Force)
        if (@($taskChildren | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Reparse descendant' }
        $taskFiles = @($taskChildren | Where-Object { -not $_.PSIsContainer })
    } elseif ($taskTarget.kind -eq 'file') {
        $taskFiles = @(Get-Item -LiteralPath $taskAbsolute)
    } else { throw 'Unknown target kind' }
    $taskExpected = @($taskPlan.files | Where-Object { $_.target -eq $taskTarget.path })
    if ($taskFiles.Count -ne $taskExpected.Count) { throw 'Target inventory changed' }
    $taskByName = @{}
    foreach ($taskFile in $taskFiles) { $taskByName[[IO.Path]::GetRelativePath($taskRoot, $taskFile.FullName).Replace('\', '/')] = $taskFile }
    foreach ($taskRow in $taskExpected) {
        if (-not $taskByName.ContainsKey($taskRow.path)) { throw 'Unexpected target file' }
        $taskFile = $taskByName[$taskRow.path]
        $taskMtime = ([long]$taskFile.LastWriteTimeUtc.Ticks - 621355968000000000L) * 100L
        if ($taskFile.Length -ne $taskRow.size_bytes -or $taskMtime -ne $taskRow.mtime_ns) { throw 'Target metadata changed' }
    }
    if ($taskTarget.kind -eq 'directory') { Remove-Item -LiteralPath $taskAbsolute -Recurse -Force }
    else { Remove-Item -LiteralPath $taskAbsolute -Force }
    if (Test-Path -LiteralPath $taskAbsolute) { throw 'Removal incomplete' }
    $taskRemoved.Add($taskTarget.path)
    @($taskRemoved) | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'deleted_targets.json') -Encoding utf8
    Write-Output ('Retired ' + $taskTarget.path)
}
[ordered]@{finished=(Get-Date).ToString('o');targets=$taskRemoved.Count;free_before_delete_bytes=$taskFreeBefore;free_after_bytes=(Get-PSDrive D).Free;no_process_terminated=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'local-retirement.json') -Encoding utf8
& $taskPython (Join-Path $PSScriptRoot 'manage.py') postdelete
if ($LASTEXITCODE -ne 0) { throw 'Postdelete validation failed' }
