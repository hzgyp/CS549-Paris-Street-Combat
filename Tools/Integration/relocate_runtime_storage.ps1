[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\0.Rutgers\CS549\Project-New'
$taskShare = Join-Path $taskRoot 'Assets\LocalShared\SFTP'
$taskRuntime = Join-Path $taskShare 'workspaces\yg745\paris-gameplay-v1'
$taskCitySource = Join-Path $taskRoot 'Unreal\ParisStreetCombat\Content'
$taskTarget = Join-Path $taskRuntime 'Content'
$taskLab = Join-Path $taskShare 'workspaces\yg745\character-ue582-v1'
$taskOut = Join-Path $taskRoot 'tmp\paris-integration-20261001'
$taskReport = [ordered]@{status='running';phase='preflight';started_at=(Get-Date -Format o);moved=@();root_acl_changed=$false}
$taskUtf8 = [Text.UTF8Encoding]::new($false)
function Save-Report { [IO.File]::WriteAllText((Join-Path $taskOut 'storage.json'),($taskReport|ConvertTo-Json -Depth 12),$taskUtf8) }
function Within($Base,$Path) {
    $prefix=[IO.Path]::GetFullPath($Base).TrimEnd('\')+'\'
    $absolute=[IO.Path]::GetFullPath($Path)
    if(-not $absolute.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw "Unsafe target: $Path"}
    return $absolute
}
function Ordinary-Tree($Path) {
    $entries=@(Get-Item -LiteralPath $Path -Force)+@(Get-ChildItem -LiteralPath $Path -Recurse -Force)
    foreach($e in $entries){if($e.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Refusing existing reparse tree: $($e.FullName)"}}
}
function Verify($Base,$Entries,$Phase) {
    $taskReport.phase=$Phase
    $taskReport.done=0
    $taskReport.total=$Entries.Count
    Save-Report
    foreach($entry in $Entries){
        $path=Within $Base (Join-Path $Base $entry.relative)
        if(-not(Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -ne $entry.size_bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw "Unsynchronized or mismatched file: $path"}
        $taskReport.done++
        if($taskReport.done % 250 -eq 0){Save-Report}
    }
    $actual=@(Get-ChildItem -LiteralPath $Base -Recurse -File -Force)
    if($actual.Count -ne $Entries.Count){throw "Uncataloged files in $Base; preserve before relocation"}
    Save-Report
}
try {
    if(-not([Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Administrator required for protected SFTP child ACLs'}
    if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Close affected editors before relocation'}
    [void](Within $taskRoot $taskCitySource)
    [void](Within (Join-Path $taskShare 'workspaces\yg745') $taskRuntime)
    if(Test-Path -LiteralPath $taskRuntime){throw 'Runtime destination already exists; inspect prior result rather than merging'}
    Ordinary-Tree $taskCitySource
    $taskRootAcl=(Get-Acl -LiteralPath $taskShare).Sddl
    New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
    $catalog=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets\Sync\CATALOG.json') -Raw | ConvertFrom-Json
    $manifests=@{}
    foreach($id in @('france-liberation-content','character-ue582-integration-baseline')){
        $selected=@($catalog.active_manifests|Where-Object{$_.asset_id -eq $id})
        if($selected.Count -ne 1){throw 'Expected one selected manifest'}
        $manifestPath=Within $taskRoot (Join-Path $taskRoot $selected[0].path)
        if((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $selected[0].sha256){throw 'Catalog manifest hash mismatch'}
        $manifests[$id]=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    }
    $cityEntries=@($manifests['france-liberation-content'].files|ForEach-Object{
        if(-not $_.path.StartsWith('Unreal/ParisStreetCombat/Content/')){throw 'Unexpected city restore prefix'}
        @{relative=$_.path.Substring('Unreal/ParisStreetCombat/Content/'.Length);size_bytes=$_.size_bytes;sha256=$_.sha256}
    })
    if($cityEntries.Count -ne 15850){throw 'Unexpected city inventory; review scope'}
    $promotions=@()
    foreach($mount in @('GermanSoldier','USParatrooper','RifleAnimsetPro','ParisCombat/Characters/Adaptation')){
        $source=Within $taskLab (Join-Path $taskLab ('Content\'+$mount.Replace('/','\')))
        $target=Within $taskTarget (Join-Path $taskTarget $mount.Replace('/','\'))
        Ordinary-Tree $source
        $prefix='Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Content/'+$mount+'/'
        $entries=@($manifests['character-ue582-integration-baseline'].files|Where-Object{$_.path.StartsWith($prefix)}|ForEach-Object{@{relative=$_.path.Substring($prefix.Length);size_bytes=$_.size_bytes;sha256=$_.sha256}})
        if(-not $entries.Count){throw 'Missing native mount inventory'}
        $promotions+=@{source=$source;target=$target;entries=$entries;mount=$mount}
    }
    if([int](($promotions|ForEach-Object{$_.entries.Count}|Measure-Object -Sum).Sum) -ne 540){throw 'Incomplete native dependency closure'}
    Verify $taskCitySource $cityEntries 'verify-city-before-move'
    foreach($p in $promotions){Verify $p.source $p.entries ('verify-native-before-'+$p.mount)}
    # Only after every source check succeeds do we create/move the runtime tree.
    New-Item -ItemType Directory -Path $taskRuntime | Out-Null
    $owner=[Security.Principal.WindowsIdentity]::GetCurrent().Name
    $shared="$env:COMPUTERNAME\cs549sftp"
    & icacls.exe $taskRuntime /grant "${owner}:(OI)(CI)M" "${shared}:(OI)(CI)M" /C | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Could not grant runtime workspace Modify'}
    Move-Item -LiteralPath $taskCitySource -Destination $taskTarget
    $taskReport.moved+=@{source=$taskCitySource;target=$taskTarget;file_count=$cityEntries.Count}
    Save-Report
    Verify $taskTarget $cityEntries 'verify-city-after-move'
    New-Item -ItemType Junction -Path $taskCitySource -Target $taskTarget | Out-Null
    foreach($p in $promotions){
        if(Test-Path -LiteralPath $p.target){throw 'Native destination conflict; never merge'}
        New-Item -ItemType Directory -Path (Split-Path $p.target -Parent) -Force | Out-Null
        Move-Item -LiteralPath $p.source -Destination $p.target
        $taskReport.moved+=@{source=$p.source;target=$p.target;file_count=$p.entries.Count}
        Save-Report
        Verify $p.target $p.entries ('verify-native-after-'+$p.mount)
        New-Item -ItemType Junction -Path $p.source -Target $p.target | Out-Null
    }
    & icacls.exe $taskTarget /reset /T /C | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Could not inherit shared runtime ACLs'}
    if((Get-Acl -LiteralPath $taskShare).Sddl -ne $taskRootAcl){throw 'Protected root ACL changed'}
    $taskReport.status='complete'
    $taskReport.phase='P0-storage-complete'
    $taskReport.completed_at=Get-Date -Format o
    $taskReport.verified_city_files=15850
    $taskReport.verified_native_character_files=540
    $taskReport.note='Same-volume moves with before/after SHA-256 and size; aliases are not copies. Baselines and immutable objects unchanged. No editor runtime pass is implied.'
} catch {
    $taskReport.status='failed'
    $taskReport.error=$_.Exception.Message
} finally {
    if(Test-Path -LiteralPath $taskOut){Save-Report}
}
if($taskReport.status -ne 'complete'){exit 1}
