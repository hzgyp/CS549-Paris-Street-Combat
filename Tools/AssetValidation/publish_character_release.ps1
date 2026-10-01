[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\0.Rutgers\CS549\Project-New'
$taskShare = Join-Path $taskRoot 'Assets\LocalShared\SFTP'
$taskRun = 'character-20261001-v1'
$taskOut = Join-Path $taskRoot ('tmp\' + $taskRun)
$taskPlan = Get-Content -LiteralPath (Join-Path $taskOut 'plan.json') -Raw | ConvertFrom-Json
$taskAccount = "$env:COMPUTERNAME\cs549sftp"
$taskOwner = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$taskUtf8 = [Text.UTF8Encoding]::new($false)
$taskReleases = [Collections.Generic.List[object]]::new()
$taskReport = [ordered]@{status='running';run_id=$taskRun;releases=@();root_acl_unchanged=$false}
$taskExistingResult = Join-Path $taskOut 'publication-result.json'
if (Test-Path -LiteralPath $taskExistingResult) {
    $taskPrevious = Get-Content -LiteralPath $taskExistingResult -Raw | ConvertFrom-Json
    if ($taskPrevious.status -eq 'complete') {
        throw 'This immutable release is already published. Verify its catalog; do not rerun the dated publisher.'
    }
}
function Save-Json($Path,$Value) { [IO.File]::WriteAllText($Path,($Value|ConvertTo-Json -Depth 20),$taskUtf8) }
function Within($Base,$Path) {
    $prefix=[IO.Path]::GetFullPath($Base).TrimEnd('\')+'\'
    $absolute=[IO.Path]::GetFullPath($Path)
    if(-not $absolute.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw "Unsafe target: $Path"}
    return $absolute
}
function Hash($Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Verify($Path,$Entry) {
    if(-not(Test-Path -LiteralPath $Path -PathType Leaf) -or (Get-Item -LiteralPath $Path).Length -ne $Entry.size_bytes -or (Hash $Path) -ne $Entry.sha256){throw "SHA/size mismatch: $Path"}
}
function Remote($Path) {
    if(-not $Path.StartsWith('/') -or $Path -match '(^|/)\.\.(/|$)' -or $Path.Contains(':')){throw 'Unsafe remote path'}
    Within $taskShare (Join-Path $taskShare $Path.TrimStart('/').Replace('/','\'))
}
function Ordinary-Tree($Path) {
    $entries=@(Get-Item -LiteralPath $Path -Force)+@(Get-ChildItem -LiteralPath $Path -Recurse -Force)
    foreach($e in $entries){if($e.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Refusing reparse tree: $($e.FullName)"}}
}
function Acl($Path,$Grant,$Recursive=$false) {
    if($Recursive){& icacls.exe $Path /grant $Grant /T /C | Out-Null}
    else {& icacls.exe $Path /grant $Grant /C | Out-Null}
    if($LASTEXITCODE -ne 0){throw "ACL grant failed: $Path"}
}
try {
    if(-not([Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Administrator required'}
    if($taskPlan.run_id -ne $taskRun -or $taskPlan.intake_source -ne 'Assets/LocalShared/SFTP/workspaces/yg745/character-intake-20260930' -or $taskPlan.intake_remote -ne ('/baselines/character-original-intake/'+$taskRun)){throw 'Unexpected publication plan'}
    if((Hash (Join-Path $taskRoot 'Assets\Sync\RIGHTS.md')) -ne $taskPlan.rights_sha256){throw 'Rights record changed; regenerate plan'}
    if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Close affected editors before publication'}
    $taskRootAcl=(Get-Acl -LiteralPath $taskShare).Sddl
    $taskSource=Within $taskShare (Join-Path $taskRoot $taskPlan.intake_source)
    $taskBaseline=Remote $taskPlan.intake_remote
    $taskOriginals=@($taskPlan.groups | Where-Object {$_.asset_id -ne 'character-ue582-integration-baseline'} | ForEach-Object {$_.files})
    if($taskOriginals.Count -ne 590){throw 'Incomplete original intake inventory'}
    if(-not(Test-Path -LiteralPath $taskBaseline)){
        Ordinary-Tree $taskSource
        foreach($entry in $taskOriginals){Verify (Within $taskSource (Join-Path $taskRoot $entry.source_path)) $entry}
        New-Item -ItemType Directory -Path (Split-Path $taskBaseline -Parent) -Force | Out-Null
        # Same-volume move preserves originals without a second complete copy.
        Move-Item -LiteralPath $taskSource -Destination $taskBaseline
    } elseif(Test-Path -LiteralPath $taskSource){
        $taskAlias=Get-Item -LiteralPath $taskSource -Force
        if(-not($taskAlias.Attributes -band [IO.FileAttributes]::ReparsePoint) -or [IO.Path]::GetFullPath([string]$taskAlias.Target) -ne [IO.Path]::GetFullPath($taskBaseline)){throw 'Existing baseline/source conflict; never merge or overwrite'}
    }
    Ordinary-Tree $taskBaseline
    $taskBaselineFiles=@(Get-ChildItem -LiteralPath $taskBaseline -File -Recurse -Force)
    if($taskBaselineFiles.Count -ne 590){throw 'Relocated baseline contains unexpected files'}
    foreach($entry in $taskOriginals){Verify (Remote $entry.remote_path) $entry}
    & icacls.exe $taskBaseline /reset /T /C | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Baseline ACL inheritance failed'}
    Acl $taskBaseline "${taskAccount}:(OI)(CI)M" $true
    Acl $taskBaseline "${taskOwner}:(OI)(CI)RX" $true
    if(-not(Test-Path -LiteralPath $taskSource)){New-Item -ItemType Junction -Path $taskSource -Target $taskBaseline | Out-Null}
    $taskWorkspace=Within $taskShare (Join-Path $taskShare 'workspaces')
    $taskOwnerWorkspace=Within $taskWorkspace (Join-Path $taskWorkspace 'yg745')
    Acl $taskWorkspace "${taskAccount}:RX"
    Acl $taskOwnerWorkspace "${taskAccount}:RX"
    $taskLab=Within $taskOwnerWorkspace (Join-Path $taskOwnerWorkspace 'character-ue582-v1')
    Ordinary-Tree $taskLab
    Acl $taskLab "${taskAccount}:(OI)(CI)M" $true
    $taskDone=0
    $taskManifestDir=Join-Path $taskOut 'verified-manifests'
    New-Item -ItemType Directory -Path $taskManifestDir -Force | Out-Null
    foreach($group in $taskPlan.groups){
        $records=[Collections.Generic.List[object]]::new()
        foreach($entry in $group.files){
            $source=Within $taskShare (Join-Path $taskRoot $entry.source_path)
            Verify $source $entry
            $final=Remote $entry.remote_path
            if(-not(Test-Path -LiteralPath $final)){
                if($entry.remote_path -ne ('/objects/sha256/'+$entry.sha256.Substring(0,2)+'/'+$entry.sha256)){throw 'Unexpected object location'}
                $stageDir=Remote ('/incoming/yg745/'+$taskRun)
                New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
                $stage=Within $stageDir (Join-Path $stageDir ($entry.sha256+'.part'))
                if(-not(Test-Path -LiteralPath $stage)){[IO.File]::Copy($source,$stage,$false)}
                Verify $stage $entry
                New-Item -ItemType Directory -Path (Split-Path $final -Parent) -Force | Out-Null
                [IO.File]::Move($stage,$final)
            }
            Verify $final $entry
            Verify $source $entry
            $records.Add([ordered]@{path=$entry.path;storage='sftp';size_bytes=$entry.size_bytes;sha256=$entry.sha256;remote_path=$entry.remote_path})
            $taskDone++
            if($taskDone % 100 -eq 0){Save-Json (Join-Path $taskOut 'progress.json') @{done=$taskDone;total=$taskPlan.file_count;phase='final-server-verification'}}
        }
        $manifest=[ordered]@{schema_version=1;asset_id=$group.asset_id;asset_version=$taskRun;owner='Yupu Guo';published_at=(Get-Date -Format o);source=$group.source;license_record='Assets/Sync/RIGHTS.md#soldier-and-rifle-animation-intake';sharing_status='owner_attested_private_three_member_original_and_derivative_sharing';recipients=@('Yupu Guo','Yuqi Pu','Jingdi Wu');dependencies=@($group.dependencies);engine=if($group.asset_id -eq 'character-ue582-integration-baseline'){'UE 5.8.2; Blender 5.2.2 LTS'}else{'Original delivered version; not normalized'};files=@($records.ToArray());file_count=$records.Count;size_bytes=[long](($records|ForEach-Object{[long]$_['size_bytes']}|Measure-Object -Sum).Sum);retired_paths=@();excluded_files=@();verification=@{method='Live source and final server SHA-256/size for every file';verifier='Authorized local administrator';verified_at=(Get-Date -Format o);teammate_restoration='not performed';runtime='Local lab regressions in Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md; not final gameplay acceptance'}}
        $localManifest=Join-Path $taskManifestDir ($group.asset_id+'.json')
        Save-Json $localManifest $manifest
        $manifestHash=Hash $localManifest
        $releaseDir=Remote ('/releases/'+$taskRun)
        New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
        $release=Within $releaseDir (Join-Path $releaseDir ($group.asset_id+'.json'))
        $manifestEntry=@{size_bytes=(Get-Item -LiteralPath $localManifest).Length;sha256=$manifestHash}
        if(-not(Test-Path -LiteralPath $release)){[IO.File]::Copy($localManifest,$release,$false)}
        Verify $release $manifestEntry
        $taskReleases.Add(@{asset_id=$group.asset_id;file_count=$records.Count;size_bytes=$manifest.size_bytes;manifest_sha256=$manifestHash;release_manifest=('/releases/'+$taskRun+'/'+$group.asset_id+'.json')})
    }
    if((Get-Acl -LiteralPath $taskShare).Sddl -ne $taskRootAcl){throw 'Root ACL changed unexpectedly'}
    $taskReport.status='complete'
    $taskReport.completed_at=Get-Date -Format o
    $taskReport.releases=@($taskReleases.ToArray())
    $taskReport.root_acl_unchanged=$true
    $taskReport.verified_files=$taskDone
} catch {
    $taskReport.status='failed'
    $taskReport.error=$_.Exception.Message
    $taskReport.releases=@($taskReleases.ToArray())
} finally {
    Save-Json (Join-Path $taskOut 'publication-result.json') $taskReport
}
if($taskReport.status -ne 'complete'){exit 1}
