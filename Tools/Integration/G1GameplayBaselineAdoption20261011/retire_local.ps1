#requires -Version 7
param([switch]$Resume)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut = Join-Path $taskRoot 'tmp/g1-gameplay-baseline-adoption-20261011'
$taskPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskPlanPath = Join-Path $taskOut 'retirement.json'
$taskAuthority = Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/Development/G1GameplayBaselineAdoption20261011/RETIREMENT_INVENTORY_20261011.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $taskPlanPath).Hash.ToLowerInvariant() -ne $taskAuthority.inventory_sha256) { throw 'Frozen plan changed' }
$taskPlan = Get-Content -LiteralPath $taskPlanPath -Raw | ConvertFrom-Json
$taskProtectedCandidates = @('candidate_grenade_equip_v1','candidate_grenade_equip_build_v4','candidate_full_v8','candidate_full_v16')
function CheckedPath([string]$taskRelative) {
    $taskAbsolute = [IO.Path]::GetFullPath((Join-Path $taskRoot $taskRelative))
    if (-not $taskAbsolute.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside workspace' }
    if ($taskRelative -eq 'tmp/Playtest-G1-GrenadeEquip-20261011' -or $taskRelative -like 'tmp/Playtest-G1-EnemyClear*') { throw 'Retained normal package' }
    foreach ($taskName in $taskProtectedCandidates) {
        if ($taskRelative.StartsWith('tmp/g1-tactical-equipment-20261010/' + $taskName + '/')) { throw 'Current/active project protected' }
    }
    $taskCursor = $taskAbsolute
    while ($taskCursor -ne $taskRoot) {
        if (Test-Path -LiteralPath $taskCursor) {
            if ((Get-Item -LiteralPath $taskCursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse ancestor' }
        }
        $taskCursor = Split-Path -Parent $taskCursor
    }
    return $taskAbsolute
}
$taskTargetAbsolutes = @(foreach ($taskTarget in $taskPlan.targets) { CheckedPath $taskTarget.path })
$taskTargetProjects = @(foreach ($taskTarget in $taskPlan.targets) {
    if ($taskTarget.path -match '^(.*?/Project)(?:/|$)') { [IO.Path]::GetFullPath((Join-Path $taskRoot $Matches[1])) }
}) | Select-Object -Unique
function CheckProcesses {
    $taskProcesses = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match 'UnrealEditor|WW2France|UnrealPak|ShaderCompile|UnrealBuildTool|AutomationTool' -or
        ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
    })
    $taskApproved = [Collections.Generic.HashSet[int]]::new()
    foreach ($taskProcess in $taskProcesses) {
        if ($taskProcess.Name -like 'WW2France*') { throw 'Preserve active user game; no termination' }
        $taskCommand = [string]$taskProcess.CommandLine
        if (-not $taskCommand) { throw 'Unidentified process' }
        foreach ($taskTargetAbsolute in $taskTargetAbsolutes) {
            if ($taskCommand.IndexOf($taskTargetAbsolute,[StringComparison]::OrdinalIgnoreCase) -ge 0) { throw 'Process using deletion target' }
        }
        foreach ($taskProjectAbsolute in $taskTargetProjects) {
            if ($taskCommand.IndexOf($taskProjectAbsolute,[StringComparison]::OrdinalIgnoreCase) -ge 0) { throw 'Process using retired author project' }
        }
        if ($taskCommand -match '"([^"]+\.uproject)"|(\S+\.uproject)') {
            $taskActualProject = if ($Matches[1]) { $Matches[1] } else { $Matches[2] }
            if (Test-Path -LiteralPath $taskActualProject) { $null = $taskApproved.Add([int]$taskProcess.ProcessId) }
        }
    }
    foreach ($taskProcess in $taskProcesses) {
        if ($taskApproved.Contains([int]$taskProcess.ProcessId)) { continue }
        if ($taskProcess.Name -ne 'ShaderCompileWorker.exe' -or -not $taskApproved.Contains([int]$taskProcess.ParentProcessId)) { throw 'Unknown build owner; preserve it' }
    }
}
CheckProcesses
$taskDeletedPath = Join-Path $taskOut 'deleted_targets.json'
$taskRemoved = [Collections.Generic.List[string]]::new()
if ($Resume) {
    foreach ($taskOld in @(Get-Content -LiteralPath $taskDeletedPath -Raw | ConvertFrom-Json)) { $taskRemoved.Add([string]$taskOld) }
    foreach ($taskOld in $taskRemoved) { if (Test-Path -LiteralPath (CheckedPath $taskOld)) { throw 'Deleted target reappeared' } }
} else {
    if (Test-Path -LiteralPath $taskDeletedPath) { throw 'Use explicit resume for occupied execution identity' }
    & $taskPython (Join-Path $PSScriptRoot 'manage.py') predelete
    if ($LASTEXITCODE -ne 0) { throw 'Predelete protection/recovery failed' }
}
$taskFreeBefore = (Get-PSDrive D).Free
foreach ($taskTarget in $taskPlan.targets) {
    if ($taskRemoved.Contains([string]$taskTarget.path)) { continue }
    CheckProcesses
    $taskAbsolute = CheckedPath $taskTarget.path
    if (-not (Test-Path -LiteralPath $taskAbsolute)) { throw 'Target unexpectedly absent' }
    $taskChildren = @(Get-ChildItem -LiteralPath $taskAbsolute -Recurse -Force)
    if (@($taskChildren | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Reparse descendant' }
    $taskFiles = @($taskChildren | Where-Object { -not $_.PSIsContainer })
    $taskExpected = @($taskPlan.files | Where-Object { $_.target -eq $taskTarget.path })
    if ($taskFiles.Count -ne $taskExpected.Count) { throw 'File inventory changed' }
    $taskByName = @{}
    foreach ($taskFile in $taskFiles) { $taskByName[[IO.Path]::GetRelativePath($taskRoot,$taskFile.FullName).Replace('\','/')] = $taskFile }
    foreach ($taskRow in $taskExpected) {
        if (-not $taskByName.ContainsKey($taskRow.path)) { throw 'Unexpected file' }
        $taskFile = $taskByName[$taskRow.path]
        $taskMtime = ([long]$taskFile.LastWriteTimeUtc.Ticks - 621355968000000000L) * 100L
        if ($taskFile.Length -ne $taskRow.size_bytes -or $taskMtime -ne $taskRow.mtime_ns) { throw 'Target metadata changed' }
    }
    Remove-Item -LiteralPath $taskAbsolute -Recurse -Force
    if (Test-Path -LiteralPath $taskAbsolute) { throw 'Removal incomplete' }
    $taskRemoved.Add([string]$taskTarget.path)
    @($taskRemoved) | ConvertTo-Json | Set-Content -LiteralPath $taskDeletedPath -Encoding utf8
    if ($taskRemoved.Count % 15 -eq 0) { Write-Output ('Retired ' + $taskRemoved.Count + '/' + $taskPlan.targets.Count) }
}
[ordered]@{finished=(Get-Date).ToString('o');targets=$taskRemoved.Count;free_before_delete_bytes=$taskFreeBefore;free_after_bytes=(Get-PSDrive D).Free;no_process_terminated=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'local-retirement.json') -Encoding utf8
& $taskPython (Join-Path $PSScriptRoot 'manage.py') postdelete
if ($LASTEXITCODE -ne 0) { throw 'Postdelete validation failed' }
