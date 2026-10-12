#requires -Version 7
param([ValidateSet('Execute','Verify')][string]$Phase='Execute',[switch]$Resume)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskAudit=Join-Path $taskRoot 'tmp/storage-cleanup-20261011'
$taskPlan=Get-Content -LiteralPath (Join-Path $taskAudit 'PLAN.json') -Raw | ConvertFrom-Json
function Hash([string]$path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function SafeTarget($row) {
    $rel=$row.path
    $approved=($rel -match '^tmp/g1-tactical-equipment-20261010/candidate_[a-z0-9_]+/Project/(Plugins/[A-Za-z0-9_]+/)?Intermediate/Build$' -or $rel -match '^tmp/g1-demo-draft03-20261009/recording_v[12]/Project/(Plugins/[A-Za-z0-9_]+/)?Intermediate/Build$')
    if(-not $approved -or $rel -match '/(candidate_death_v6|candidate_full_v8|candidate_full_v16)/'){throw "Unapproved target: $rel"}
    $full=[IO.Path]::GetFullPath((Join-Path $taskRoot $rel))
    if(-not $full.StartsWith($taskRoot.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Outside workspace: $full"}
    $cursor=$full
    while($cursor -ne $taskRoot) {
        if(Test-Path -LiteralPath $cursor) {
            if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Linked ancestor: $cursor"}
        }
        $cursor=Split-Path -Parent $cursor
    }
    if(Test-Path -LiteralPath $full) {
        foreach($f in Get-ChildItem -LiteralPath $full -Recurse -Force) {
            if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Linked descendant: $($f.FullName)"}
            if(-not $f.FullName.StartsWith($full+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected descendant'}
        }
    }
    return $full
}
function AssertProcesses {
    $active=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'Unreal|WW2France|ShaderCompile|dotnet' })
    foreach($p in $active) {
        $cmd=($p.CommandLine ?? '').Replace('/','\')
        foreach($row in $taskPlan.targets) {
            $project=[IO.Path]::GetFullPath((Join-Path $taskRoot $row.project))
            if($cmd.Contains($project,[StringComparison]::OrdinalIgnoreCase)){throw "Active process $($p.ProcessId) uses cleanup project $project"}
        }
        if($p.Name -eq 'dotnet.exe' -and $cmd -match 'UnrealBuildTool|AutomationTool') {
            $independent=[IO.Path]::GetFullPath((Join-Path $taskRoot 'Assets/LocalWorking/AssetWorkbench'))+'\'
            $match=[regex]::Match($cmd,[regex]::Escape($independent)+'[^"\r\n]*?\.uproject',[Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if($match.Success -and (Test-Path -LiteralPath $match.Value -PathType Leaf)) {
                [ordered]@{status='known_independent_asset_workbench_build';process_id=$p.ProcessId;project=$match.Value;command_line=$p.CommandLine;observed_at=(Get-Date).ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $taskAudit 'INDEPENDENT_BUILDS.jsonl')
            }
            else {
                [ordered]@{status='unknown_build_stop';process_id=$p.ProcessId;command_line=$p.CommandLine;observed_at=(Get-Date).ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $taskAudit 'BUILD_STOPS.jsonl')
                throw 'Unknown Unreal build is active; stop before next deletion'
            }
        }
    }
    return $active | Select-Object ProcessId,Name,CommandLine
}
foreach($property in $taskPlan.receipts.PSObject.Properties) {
    if((Hash (Join-Path $taskAudit $property.Name)) -ne $property.Value){throw "Audit changed: $($property.Name)"}
}
$protected=@(Get-Content -LiteralPath (Join-Path $taskAudit 'PROTECTED.json') -Raw | ConvertFrom-Json)
$metadata=@(Get-Content -LiteralPath (Join-Path $taskAudit 'METADATA.json') -Raw | ConvertFrom-Json)
function AssertProtected([switch]$FullHash) {
    foreach($r in $protected) {
        $p=Get-Item -LiteralPath $r.path
        $expectedTicks=([decimal]$r.mtime_ns/100)+[decimal]621355968000000000
        if($p.Length -ne $r.size_bytes -or [Math]::Abs([decimal]$p.LastWriteTimeUtc.Ticks-$expectedTicks) -gt 2){throw "Protected file changed: $($r.path)"}
        if($FullHash -and (Hash $r.path) -ne $r.sha256){throw "Protected bytes changed: $($r.path)"}
    }
}
foreach($r in $metadata) {
    if((Hash (Join-Path $taskRoot $r.backup)) -ne $r.sha256){throw "Metadata backup mismatch: $($r.backup)"}
}
if($Phase -eq 'Execute') {
    if(Test-Path -LiteralPath (Join-Path $taskAudit 'EXECUTION.json')){throw 'Keep occupied execution audit'}
    $taskBeforeFree=[long](Get-PSDrive D).Free
    $initialSource='execution_start'
    $done=@{}
    if(Test-Path -LiteralPath (Join-Path $taskAudit 'DELETED.jsonl')) {
        if(-not $Resume){throw 'Partial execution exists; explicit Resume required'}
        foreach($line in Get-Content -LiteralPath (Join-Path $taskAudit 'DELETED.jsonl')) {
            $r=$line | ConvertFrom-Json
            $original=@($taskPlan.targets | Where-Object path -eq $r.path)
            if($original.Count -ne 1 -or $r.bytes -ne $original[0].bytes -or $r.files -ne $original[0].files){throw 'Partial journal differs from frozen plan'}
            if(Test-Path -LiteralPath (SafeTarget $original[0])){throw "Recorded deleted target exists: $($r.path)"}
            if($done.ContainsKey($r.path)){throw 'Repeated deleted journal entry'}
            $done[$r.path]=$true
        }
        $taskBeforeFree=[long]$taskPlan.disk_free_before
        $initialSource='frozen_preparation_disk_snapshot_before_first_deletion'
    }
    $active=AssertProcesses
    AssertProtected
    $inventory=@(Get-Content -LiteralPath (Join-Path $taskAudit 'INVENTORY.json') -Raw | ConvertFrom-Json)
    foreach($row in $taskPlan.targets) {
        if($done.ContainsKey($row.path)){continue}
        $full=SafeTarget $row
        $actual=@(Get-ChildItem -LiteralPath $full -File -Recurse -Force)
        if($actual.Count -ne $row.files){throw "Inventory count changed: $full"}
        foreach($r in $inventory | Where-Object { $_.path.StartsWith($row.path+'/',[StringComparison]::Ordinal) }) {
            $f=Get-Item -LiteralPath (Join-Path $taskRoot $r.path)
            $expectedTicks=([decimal]$r.mtime_ns/100)+[decimal]621355968000000000
            if($f.Length -ne $r.size_bytes -or [Math]::Abs([decimal]$f.LastWriteTimeUtc.Ticks-$expectedTicks) -gt 2){throw "Inventory file changed: $($r.path)"}
        }
    }
    foreach($row in $taskPlan.targets) {
        if($done.ContainsKey($row.path)){continue}
        $null=AssertProcesses
        $full=SafeTarget $row
        Remove-Item -LiteralPath $full -Recurse -Force
        if(Test-Path -LiteralPath $full){throw "Deletion incomplete: $full"}
        [ordered]@{path=$row.path;bytes=$row.bytes;files=$row.files;deleted_at=(Get-Date).ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $taskAudit 'DELETED.jsonl')
    }
    $taskAfterFree=[long](Get-PSDrive D).Free
    [ordered]@{status='deleted_pending_final_verification';before_free=$taskBeforeFree;initial_measurement_source=$initialSource;after_free=$taskAfterFree;actual_freed=[long]($taskAfterFree-$taskBeforeFree);logical_bytes=$taskPlan.logical_bytes;targets=$taskPlan.targets.Count;resumed_after=$done.Count;initial_processes=$active;completed_at=(Get-Date).ToString('o')} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskAudit 'EXECUTION.json')
    Write-Output "Deleted $($taskPlan.targets.Count) cache directories; measured net release $([Math]::Round(($taskAfterFree-$taskBeforeFree)/1GB,2)) GiB"
}
else {
    AssertProtected -FullHash
    foreach($row in $taskPlan.targets) { $full=SafeTarget $row; if(Test-Path -LiteralPath $full){throw "Retired cache still exists: $full"} }
    $active=AssertProcesses
    foreach($pidToKeep in @(50836,51148)) { if(-not (Get-Process -Id $pidToKeep -ErrorAction SilentlyContinue)){throw "Retained Editor no longer present: $pidToKeep"} }
    $execution=Get-Content -LiteralPath (Join-Path $taskAudit 'EXECUTION.json') -Raw | ConvertFrom-Json
    [ordered]@{status='pass';protected_files=$protected.Count;metadata_files=$metadata.Count;deleted_targets=$taskPlan.targets.Count;logical_bytes=$taskPlan.logical_bytes;actual_freed=$execution.actual_freed;disk_free_now=[long](Get-PSDrive D).Free;retained_editors=@(50836,51148);verified_at=(Get-Date).ToString('o')} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskAudit 'RESULT.json')
    Write-Output "PASS protected bytes, diagnostic backups, deleted targets, retained Editors; actual freed $([Math]::Round($execution.actual_freed/1GB,2)) GiB"
}
