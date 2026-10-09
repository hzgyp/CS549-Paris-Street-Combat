#requires -Version 7
param([ValidateSet('Prepare','Execute','Verify')][string]$Phase='Prepare')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskRecord=Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/StorageCleanup20261009/run_v1'
$taskPlanPath=Join-Path $taskRecord 'plan.json'
$taskZipPath=Join-Path $taskRecord 'intermediate_unique_payloads.zip'
$taskPython='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskAllowed=@('tmp/g1-playtest-revision-20261008','tmp/mvp-closeout-20261008')
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Rel([string]$p){return [IO.Path]::GetRelativePath($taskRoot,$p).Replace('\','/')}
function SafePath([string]$p){
    $full=[IO.Path]::GetFullPath((Join-Path $taskRoot $p))
    if(-not $full.StartsWith($taskRoot.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Outside workspace: $full"}
    return $full
}
function AssertTarget([string]$p){
    $full=SafePath $p
    $allowed=$false
    foreach($base in $taskAllowed){if($full.StartsWith((SafePath $base)+'\',[StringComparison]::OrdinalIgnoreCase)){$allowed=$true}}
    if(-not $allowed){throw "Outside named cleanup roots: $full"}
    $cursor=$full
    while($cursor -ne $taskRoot){
        if(Test-Path -LiteralPath $cursor){if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse ancestor: $cursor"}}
        $cursor=Split-Path -Parent $cursor
    }
    if(Test-Path -LiteralPath $full){
        foreach($f in Get-ChildItem -LiteralPath $full -Recurse -Force){
            if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse descendant: $($f.FullName)"}
            if(-not $f.FullName.StartsWith($full+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected descendant path'}
        }
    }
    return $full
}
function AssertIdle{
    $active=@(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealEditor-Cmd|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\.exe$' -or
        ($_.Name -match '^dotnet\.exe$' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
    })
    if($active.Count){throw 'Active UE/game/build process; no automatic termination'}
}
function AssertContracts{
    & $taskPython (Join-Path $taskRoot 'Tools/Integration/verify_team_source.py')
    if($LASTEXITCODE -ne 0){throw 'Canonical source mismatch'}
    $code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(r'$taskRoot')/'Tools/Integration/NPCInteractionV1'));from common import guard_rows,guards_match;r=guard_rows();assert len(r)==703 and guards_match(r);print('protected703 exact')"
    & $taskPython -c $code
    if($LASTEXITCODE -ne 0){throw 'Protected asset/source mismatch'}
}
function Hash([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function AssertDeletionTarget($row){
    $p=$row.path
    $recoverable=(
        $p -match '^tmp/g1-playtest-revision-20261008/(candidate_v3|candidate_v5|candidate_v6|candidate_v8|candidate_v9|candidate_v10|hud_v1|hud_v2)/Archive$' -or
        $p -match '^tmp/mvp-closeout-20261008/(package_v2|instrument_v3|instrument_v4|instrument_v5|instrument_v8|instrument_v9|instrument_v11)/Archive$' -or
        $p -in @('tmp/g1-playtest-revision-20261008/candidate_v3/Project/Saved/StagedBuilds','tmp/mvp-closeout-20261008/package_v2/Project/Saved/StagedBuilds')
    )
    $cache=(
        $p -eq 'tmp/g1-playtest-revision-20261008/candidate_v3/Project/Intermediate/Build' -or
        $p -match '^tmp/mvp-closeout-20261008/(package_v2|instrument_v3|instrument_v4|instrument_v5|instrument_v8|instrument_v9|instrument_v11|instrument_v13)/Project/Intermediate/Build$'
    )
    if(-not (($recoverable -and $row.kind -eq 'recoverable') -or ($cache -and $row.kind -eq 'regenerable_cache'))){throw "Not an exact declared deletion target: $p"}
}
function CheckZip($plan){
    if((Hash $taskZipPath) -ne $plan.zip_sha256){throw 'ZIP identity mismatch'}
    $read=[IO.Compression.ZipFile]::OpenRead($taskZipPath)
    try{
        if($read.Entries.Count -ne $plan.zip_objects.Count){throw 'ZIP entry count mismatch'}
        foreach($r in $plan.zip_objects){
            $e=$read.GetEntry($r.entry);if(-not $e -or $e.Length -ne $r.size_bytes){throw 'ZIP entry missing/size mismatch'}
            $stream=$e.Open();$sha=[Security.Cryptography.SHA256]::Create()
            try{$actual=[Convert]::ToHexString($sha.ComputeHash($stream)).ToLowerInvariant()}finally{$stream.Dispose();$sha.Dispose()}
            if($actual -ne $r.sha256){throw "ZIP readback mismatch: $($r.entry)"}
        }
    }finally{$read.Dispose()}
}
function CheckRetained($plan,[switch]$HashAll){
    foreach($r in $plan.retained_files){
        $p=SafePath $r.path;$f=Get-Item -LiteralPath $p
        if($f.Length -ne $r.size_bytes -or $f.LastWriteTimeUtc.Ticks -ne $r.mtime_ticks){throw "Retained file changed: $p"}
        if($HashAll -and (Hash $p) -ne $r.sha256){throw "Retained hash mismatch: $p"}
    }
    foreach($r in $plan.user_trial_files){
        $p=SafePath $r.path;$f=Get-Item -LiteralPath $p
        if($f.Length -ne $r.size_bytes -or $f.LastWriteTimeUtc.Ticks -ne $r.mtime_ticks){throw "User trial changed: $p"}
        if($r.sha256 -and (Hash $p) -ne $r.sha256){throw "User entry identity changed: $p"}
    }
}
if($Phase -eq 'Prepare'){
    AssertIdle;AssertContracts
    if(Test-Path -LiteralPath $taskRecord){throw 'Preserve occupied cleanup record'}
    $before=(Get-PSDrive -Name D).Free
    $targets=[Collections.Generic.List[object]]::new()
    foreach($id in @('candidate_v3','candidate_v5','candidate_v6','candidate_v8','candidate_v9','candidate_v10','hud_v1','hud_v2')){
        $targets.Add([ordered]@{path="tmp/g1-playtest-revision-20261008/$id/Archive";kind='recoverable'})
    }
    foreach($id in @('package_v2','instrument_v3','instrument_v4','instrument_v5','instrument_v8','instrument_v9','instrument_v11')){
        $targets.Add([ordered]@{path="tmp/mvp-closeout-20261008/$id/Archive";kind='recoverable'})
    }
    foreach($rel in @('tmp/g1-playtest-revision-20261008/candidate_v3/Project','tmp/mvp-closeout-20261008/package_v2/Project')){
        $targets.Add([ordered]@{path="$rel/Saved/StagedBuilds";kind='recoverable'})
    }
    $projects=@('tmp/g1-playtest-revision-20261008/candidate_v3/Project')
    foreach($id in @('package_v2','instrument_v3','instrument_v4','instrument_v5','instrument_v8','instrument_v9','instrument_v11','instrument_v13')){$projects+="tmp/mvp-closeout-20261008/$id/Project"}
    foreach($p in $projects){$targets.Add([ordered]@{path="$p/Intermediate/Build";kind='regenerable_cache'})}
    foreach($t in $targets){$p=AssertTarget $t.path;if(-not (Test-Path -LiteralPath $p)){throw "Expected target missing: $p"}}
    $retainedBySize=@{};$retainedHash=@{};$usedRetained=@{};$zipObjects=@{};$all=[Collections.Generic.List[object]]::new()
    foreach($base in @('tmp/g1-playtest-revision-20261008/hud_v3/Archive','tmp/mvp-closeout-20261008/instrument_v13/Archive')){
        $p=AssertTarget $base
        foreach($f in Get-ChildItem -LiteralPath $p -File -Recurse -Force){$key=[string]$f.Length;if(-not $retainedBySize.ContainsKey($key)){$retainedBySize[$key]=[Collections.Generic.List[object]]::new()};$retainedBySize[$key].Add($f)}
    }
    $trialFiles=@()
    foreach($base in @('tmp/Playtest-G1-20261008','tmp/Playtest-G1-20261009','tmp/Playtest-G1-HUD-20261009')){
        foreach($f in Get-ChildItem -LiteralPath (SafePath $base) -File -Recurse -Force){
            $sha=$null;if($f.Extension -in @('.exe','.cmd') -and $f.Name -match 'WW2FranceLiberation|PLAY_G1'){$sha=Hash $f.FullName}
            $trialFiles+=[ordered]@{path=(Rel $f.FullName);size_bytes=$f.Length;mtime_ticks=$f.LastWriteTimeUtc.Ticks;sha256=$sha}
        }
    }
    New-Item -ItemType Directory -Path $taskRecord|Out-Null
    $zip=[IO.Compression.ZipFile]::Open($taskZipPath,[IO.Compression.ZipArchiveMode]::Create)
    try{
        foreach($t in $targets){
            $p=AssertTarget $t.path;$count=0;$total=0
            foreach($f in Get-ChildItem -LiteralPath $p -File -Recurse -Force){
                $r=[ordered]@{path=(Rel $f.FullName);target=$t.path;size_bytes=$f.Length;mtime_ticks=$f.LastWriteTimeUtc.Ticks;recovery='regenerate'}
                $keep=($t.kind -eq 'recoverable' -or $f.Extension -in @('.json','.cpp','.h','.cs','.txt','.rsp','.response','.manifest','.ini','.xml','.map','.pdb'))
                if($keep){
                    $sha=Hash $f.FullName;$r.sha256=$sha;$match=$null;$key=[string]$f.Length
                    if($t.kind -eq 'recoverable' -and $retainedBySize.ContainsKey($key)){
                        foreach($candidate in $retainedBySize[$key]){
                            if(-not $retainedHash.ContainsKey($candidate.FullName)){$retainedHash[$candidate.FullName]=Hash $candidate.FullName}
                            if($retainedHash[$candidate.FullName] -eq $sha){$match=$candidate;break}
                        }
                    }
                    if($match){
                        $r.recovery='retained_file';$r.retained_path=Rel $match.FullName
                        $usedRetained[$match.FullName]=[ordered]@{path=$r.retained_path;size_bytes=$match.Length;mtime_ticks=$match.LastWriteTimeUtc.Ticks;sha256=$sha}
                    }else{
                        if($f.Length -gt 1GB){throw "Unknown large unique payload; stop before deletion: $($f.FullName)"}
                        $entry="objects/$sha";$r.recovery='zip_entry';$r.entry=$entry
                        if(-not $zipObjects.ContainsKey($sha)){
                            [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$f.FullName,$entry,[IO.Compression.CompressionLevel]::Fastest)|Out-Null
                            $zipObjects[$sha]=[ordered]@{entry=$entry;size_bytes=$f.Length;sha256=$sha}
                        }
                    }
                }
                $all.Add($r);$count++;$total+=$f.Length
            }
            $t.files=$count;$t.size_bytes=$total
            Write-Output ("Archived/checklisted {0}: {1:N2} GiB / {2} files" -f $t.path,($total/1GB),$count)
        }
    }finally{$zip.Dispose()}
    $plan=[ordered]@{status='prepared_no_deletion';authorization='2026-10-09 user requests packing/removing unused intermediate files';created=(Get-Date).ToString('o');free_before_bytes=$before;targets=@($targets);files=@($all);retained_files=@($usedRetained.Values);user_trial_files=$trialFiles;zip_objects=@($zipObjects.Values);zip_sha256=(Hash $taskZipPath);zip_size_bytes=(Get-Item -LiteralPath $taskZipPath).Length;canonical_source_files=758;protected_files=703;scope='Only explicit private superseded Archives/staging and rebuildable Build caches; no source/asset/evidence/user save deletion'}
    CheckZip $plan;CheckRetained $plan
    $plan|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $taskPlanPath -Encoding utf8
    $eligible=0L;foreach($t in $targets){$eligible+=[long]$t.size_bytes}
    Write-Output ("PREPARED: {0:N2} GiB eligible; ZIP {1:N2} MiB; {2} targets" -f ($eligible/1GB),($plan.zip_size_bytes/1MB),$targets.Count)
    exit
}
$plan=Get-Content -LiteralPath $taskPlanPath -Raw|ConvertFrom-Json
if($plan.status -ne 'prepared_no_deletion' -or $plan.authorization -ne '2026-10-09 user requests packing/removing unused intermediate files'){throw 'Exact prepared authorization required'}
if($plan.targets.Count -ne 26 -or @($plan.targets.path|Sort-Object -Unique).Count -ne 26){throw 'Exact unique target count required'}
foreach($t in $plan.targets){AssertDeletionTarget $t}
foreach($r in $plan.files){if($r.target -notin $plan.targets.path -or -not $r.path.StartsWith($r.target+'/',[StringComparison]::OrdinalIgnoreCase)){throw 'File row outside explicit target'}}
AssertContracts;CheckZip $plan;CheckRetained $plan
$resultPath=Join-Path $taskRecord 'result.json'
if($Phase -eq 'Execute'){
    AssertIdle
    if(Test-Path -LiteralPath $resultPath){throw 'Preserve existing cleanup result'}
    foreach($t in $plan.targets){
        $p=AssertTarget $t.path;$files=@(Get-ChildItem -LiteralPath $p -File -Recurse -Force)
        $expected=@($plan.files|Where-Object target -eq $t.path)
        if($files.Count -ne $expected.Count){throw "Target inventory changed: $p"}
        foreach($r in $expected){$f=Get-Item -LiteralPath (SafePath $r.path);if($f.Length -ne $r.size_bytes -or $f.LastWriteTimeUtc.Ticks -ne $r.mtime_ticks){throw "Target file changed: $($r.path)"}}
    }
    $freeBeforeDelete=(Get-PSDrive -Name D).Free;$done=[Collections.Generic.List[object]]::new()
    foreach($t in $plan.targets){
        AssertIdle;$p=AssertTarget $t.path
        Remove-Item -LiteralPath $p -Recurse -Force
        if(Test-Path -LiteralPath $p){throw "Removal incomplete: $p"}
        $done.Add($t)
        $done|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskRecord 'deleted_targets.json') -Encoding utf8
        Write-Output ("Removed {0}: {1:N2} GiB" -f $t.path,($t.size_bytes/1GB))
    }
    CheckRetained $plan;AssertContracts
    $freeAfter=(Get-PSDrive -Name D).Free
    $logicalRemoved=0L;foreach($t in $done){$logicalRemoved+=[long]$t.size_bytes}
    [ordered]@{status='pass_storage_only_cleanup';finished=(Get-Date).ToString('o');plan_sha256=(Hash $taskPlanPath);targets_removed=$done.Count;logical_removed_bytes=$logicalRemoved;zip_bytes=$plan.zip_size_bytes;free_before_survey_bytes=$plan.free_before_bytes;free_before_delete_bytes=$freeBeforeDelete;free_after_bytes=$freeAfter;actual_free_increase_from_survey_bytes=($freeAfter-$plan.free_before_bytes);all_three_user_trials_unchanged=$true;final_archives_retained=$true;source758_guards703_exact=$true;raw_failure_and_source_snapshots_retained=$true;no_engine_launch_or_termination=$true}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $resultPath -Encoding utf8
}
$result=Get-Content -LiteralPath $resultPath -Raw|ConvertFrom-Json
if($result.status -ne 'pass_storage_only_cleanup' -or $result.plan_sha256 -ne (Hash $taskPlanPath)){throw 'Cleanup receipt mismatch'}
foreach($t in $plan.targets){if(Test-Path -LiteralPath (AssertTarget $t.path)){throw "Target unexpectedly present: $($t.path)"}}
CheckRetained $plan -HashAll
Write-Output ($result|ConvertTo-Json -Depth 5)
