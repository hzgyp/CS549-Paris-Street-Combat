param([switch]$Execute)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskCase = 'FP001-20261003-first-person-view'
$taskPublic = Join-Path $taskRoot "Failures/$taskCase"
$taskStore = Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
$taskPrivate = Join-Path $taskStore "FailureArchive/$taskCase"
$taskEvidence = Join-Path $taskStore 'Evidence/CityGameplay20261002'
$taskEntries = [Collections.Generic.List[object]]::new()
$taskSeen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
function Within([string]$path,[string]$base) {
    $resolved = [IO.Path]::GetFullPath($path)
    $prefix = [IO.Path]::GetFullPath($base).TrimEnd('\') + '\'
    if(-not $resolved.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw "Escaping path: $resolved"}
    return $resolved
}
function Rel([string]$path) { return [IO.Path]::GetRelativePath($taskRoot,$path).Replace('\','/') }
function Add-Entry([string]$source,[string]$destination,[string]$action='move') {
    $source = Within $source $taskRoot
    $destination = Within $destination $taskRoot
    if(-not ((Within $destination (Split-Path $destination)) -eq $destination)){throw 'Invalid destination'}
    if(-not ($destination.StartsWith($taskPublic+'\',[StringComparison]::OrdinalIgnoreCase) -or $destination.StartsWith($taskPrivate+'\',[StringComparison]::OrdinalIgnoreCase))){throw 'Destination outside case roots'}
    if(Test-Path -LiteralPath $destination){throw "Occupied: $destination"}
    $item = Get-Item -LiteralPath $source
    if($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw "Not an ordinary file: $source"}
    if(-not $taskSeen.Add($source)){throw "Duplicate source: $source"}
    $taskEntries.Add([ordered]@{original_path=(Rel $source);archive_path=(Rel $destination);action=$action;size_bytes=$item.Length;sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()})
}
function Add-Tree([string]$source,[string]$destination) {
    $source = Within $source $taskRoot
    $destination = Within $destination $taskPrivate
    if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse source root: $source"}
    $items = @(Get-ChildItem -LiteralPath $source -Force -Recurse)
    if(@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count){throw "Reparse descendant in $source"}
    foreach($item in $items | Where-Object {-not $_.PSIsContainer}){
        Add-Entry $item.FullName (Join-Path $destination ([IO.Path]::GetRelativePath($source,$item.FullName)))
    }
}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close Unreal before archival'}
$audit = Get-Content -LiteralPath (Join-Path $taskRoot 'tmp/failure-archive-20261003/dependencies.json') -Raw | ConvertFrom-Json
if(-not $audit.passed){throw 'Referencer audit must pass'}
$v3 = Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json') -Raw | ConvertFrom-Json
$deps = Get-Content -LiteralPath (Join-Path $taskRoot $v3.retained_dependency_inventory) -Raw | ConvertFrom-Json
$aim = Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json') -Raw | ConvertFrom-Json
$fp = Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json') -Raw | ConvertFrom-Json
$protected = @($v3.files)+@($deps.files)+@($v3.retained_unselected_rejected_trial)+@($aim.files)
foreach($entry in @($protected)+@($fp.files)){
    $path = Within (Join-Path $taskRoot $entry.path) $taskRoot
    if((Get-Item -LiteralPath $path).Length -ne $entry.size_bytes -or (Get-FileHash -LiteralPath $path).Hash.ToLowerInvariant() -ne $entry.sha256){throw "Preflight mismatch: $path"}
}
foreach($entry in $fp.files){
    if($entry.package -notlike '*/FirstPersonViewV1/*'){throw 'Wrong package scope'}
    $source = Join-Path $taskRoot $entry.path
    $relativeContent = [IO.Path]::GetRelativePath((Join-Path $taskStore 'Content'),$source)
    Add-Entry $source (Join-Path $taskPrivate "Native/Content/$relativeContent")
}
foreach($file in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Docs/Development') -File -Filter 'FIRST_PERSON_VIEW_REPAIR_*.md'){
    Add-Entry $file.FullName (Join-Path $taskPublic "Docs/$($file.Name)")
}
foreach($pattern in @('ue_first_person_view_*.py','run_first_person_view_*.ps1')){
    foreach($file in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Tools/Integration') -File -Filter $pattern){Add-Entry $file.FullName (Join-Path $taskPublic "Tools/$($file.Name)")}
}
Add-Entry (Join-Path $taskRoot 'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json') (Join-Path $taskPublic 'Metadata/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json')
Add-Tree (Join-Path $taskEvidence 'FirstPersonViewV1') (Join-Path $taskPrivate 'Evidence/FirstPersonViewV1')
foreach($version in 1..3){Add-Tree (Join-Path $taskEvidence "Runtime/combat_fp_v$version") (Join-Path $taskPrivate "Evidence/Runtime/combat_fp_v$version")}
Add-Tree (Join-Path $taskRoot 'tmp/paris-first-person-view-20261002') (Join-Path $taskPrivate 'LogsAndBuild')
$crashRoot = Join-Path $taskRoot 'Unreal/ParisStreetCombat/Saved/Crashes'
foreach($crash in Get-ChildItem -LiteralPath $crashRoot -Directory){
    $context = Join-Path $crash.FullName 'CrashContext.runtime-xml'
    if((Test-Path -LiteralPath $context) -and (Select-String -LiteralPath $context -Pattern 'first-person-view-20261002|ue_first_person_view_' -Quiet)){
        Add-Tree $crash.FullName (Join-Path $taskPrivate "Crashes/$($crash.Name)")
    }
}
$cacheRoot = Join-Path $taskRoot 'Tools/Integration/__pycache__'
if(Test-Path -LiteralPath $cacheRoot){foreach($file in Get-ChildItem -LiteralPath $cacheRoot -File -Filter 'ue_first_person_view_*.pyc'){Add-Entry $file.FullName (Join-Path $taskPrivate "PythonCache/$($file.Name)")}}
foreach($source in @('Tools/Integration/ue_paris_combat_pie.py','Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Source/ParisEditorBridge/Private/ParisBlueprintAuthoring.cpp','Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Source/ParisEditorBridge/Public/ParisBlueprintAuthoring.h')){
    Add-Entry (Join-Path $taskRoot $source) (Join-Path $taskPublic "Changes/Before/$source") 'snapshot'
}
foreach($name in @('UnrealEditor-ParisEditorBridge.dll','UnrealEditor-ParisEditorBridge.pdb','UnrealEditor.modules')){
    Add-Entry (Join-Path $taskRoot "Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Binaries/Win64/$name") (Join-Path $taskPrivate "DeployedV25/$name") 'snapshot'
}
[long]$taskTotal = 0
foreach($entry in $taskEntries){$taskTotal += $entry.size_bytes}
$manifest = [ordered]@{case_id=$taskCase;date='2026-10-03';status='planned';scope='FP001 seven exclusive native assets and associated documentation/scripts/evidence; previous 40 packages protected';private_storage=(Rel $taskPrivate);map_sha256='d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f';protected_files=$protected;entry_count=$taskEntries.Count;total_bytes=$taskTotal;entries=$taskEntries}
New-Item -ItemType Directory -Path $taskPublic -Force | Out-Null
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskPublic 'MANIFEST.json') -Encoding utf8
if(-not $Execute){[pscustomobject]@{planned_entries=$taskEntries.Count;bytes=$manifest.total_bytes;protected=$protected.Count}|ConvertTo-Json;exit}
$journal = Join-Path $taskPublic 'MOVE_JOURNAL.jsonl'
foreach($entry in $taskEntries){
    $source = Within (Join-Path $taskRoot $entry.original_path) $taskRoot
    $dest = Within (Join-Path $taskRoot $entry.archive_path) $taskRoot
    if(Test-Path -LiteralPath $dest){throw "Occupied during execution: $dest"}
    New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
    if($entry.action -eq 'snapshot'){Copy-Item -LiteralPath $source -Destination $dest}else{Move-Item -LiteralPath $source -Destination $dest}
    if((Get-Item -LiteralPath $dest).Length -ne $entry.size_bytes -or (Get-FileHash -LiteralPath $dest).Hash.ToLowerInvariant() -ne $entry.sha256){throw "Archived byte mismatch: $dest"}
    if($entry.action -eq 'move' -and (Test-Path -LiteralPath $source)){throw "Source still exists: $source"}
    [ordered]@{original_path=$entry.original_path;archive_path=$entry.archive_path;sha256=$entry.sha256;verified=$true} | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal -Encoding utf8
}
foreach($entry in $protected){if((Get-FileHash -LiteralPath (Join-Path $taskRoot $entry.path)).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Protected package changed'}}
$manifest.status='moved_and_byte_verified_shared_source_withdrawal_pending'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskPublic 'MANIFEST.json') -Encoding utf8
[pscustomobject]@{verified_entries=$taskEntries.Count;bytes=$manifest.total_bytes;protected=$protected.Count;status=$manifest.status}|ConvertTo-Json
