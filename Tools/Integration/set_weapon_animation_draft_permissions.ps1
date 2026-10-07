# Exact failed-draft access only, not immutable publication or restore authority.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close editors before draft handoff'}
$taskStore=[IO.Path]::GetFullPath((Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'))
$taskSharedRoot=Join-Path $taskRoot 'Assets/LocalShared/SFTP'
$taskRootSddl=(Get-Acl -LiteralPath $taskSharedRoot).Sddl
$taskProof=Join-Path $taskRoot 'tmp/weapon-animation-reuse/native_acl_v1.json'
if(Test-Path -LiteralPath $taskProof){throw 'Preserve occupied proof'}
$taskReport=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json') -Raw | ConvertFrom-Json
if($taskReport.files.Count -ne 5 -or $taskReport.catalog_selected){throw 'Unexpected draft inventory'}
$taskNamespaces=@((Join-Path $taskStore 'Content/ParisCombat/Animation/WeaponAnimationReuseV1'),(Join-Path $taskStore 'Content/ParisCombat/Blueprints/WeaponAnimationReuseV1'))
$taskAccount=$env:COMPUTERNAME+'\cs549sftp'
foreach($taskFile in $taskReport.files){
    $taskFull=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskFile.path))
    $taskAllowed=$false
    foreach($taskNamespace in $taskNamespaces){if($taskFull.StartsWith($taskNamespace+'\',[StringComparison]::OrdinalIgnoreCase)){$taskAllowed=$true}}
    if(-not $taskAllowed){throw 'Target escaped exact namespaces'}
    if((Get-Item -LiteralPath $taskFull).Length -ne $taskFile.size_bytes -or (Get-FileHash -LiteralPath $taskFull -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFile.sha256){throw 'Native byte conflict'}
    & icacls.exe $taskFull '/grant' ($taskAccount+':M') | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Exact file ACL grant failed'}
    $taskAce=(Get-Acl -LiteralPath $taskFull).Access | Where-Object {$_.IdentityReference.Value -eq $taskAccount -and $_.AccessControlType -eq 'Allow' -and ($_.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Modify) -eq [Security.AccessControl.FileSystemRights]::Modify}
    if(-not $taskAce){throw 'Named Modify absent'}
}
if((Get-Acl -LiteralPath $taskSharedRoot).Sddl -ne $taskRootSddl){throw 'Shared root ACL changed'}
@{status='exact_five_draft_named_modify_verified';root_acl_unchanged=$true;recursive_grant=$false;immutable_publication=$false;files=$taskReport.files} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskProof -Encoding utf8
'Named Modify verified on 5 drafts; root ACL unchanged. Failed drafts remain unselected.'
