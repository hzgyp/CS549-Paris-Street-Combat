# Grant only known, hash-verified integration drafts; never recurse or touch the chroot root.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close editors before draft handoff'}
$taskBase=[IO.Path]::GetFullPath((Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Weapons/GermanRifleUEV1'))
$taskProof=Join-Path $taskRoot 'tmp/german-rifle-ue-v1/native_acl_v1.json'
if(Test-Path -LiteralPath $taskProof){throw 'Preserve occupied ACL proof'}
$taskFiles=@()
foreach($taskIdentity in @('import_v3','author_v1','author_v2')){
    $taskReport=Get-Content -LiteralPath (Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanRifleUEV1/$taskIdentity/result.json") -Raw | ConvertFrom-Json
    if($taskReport.errors.Count){throw 'Do not grant unknown/failed outputs'}
    $taskFiles+=@($taskReport.native_files)
}
$taskAccount=$env:COMPUTERNAME+'\cs549sftp'
foreach($taskFile in $taskFiles){
    $taskFull=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskFile.path))
    if(-not $taskFull.StartsWith($taskBase+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Target escaped exact rifle namespace'}
    if((Get-Item -LiteralPath $taskFull).Length -ne $taskFile.size_bytes -or (Get-FileHash -LiteralPath $taskFull -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFile.sha256){throw 'Draft byte conflict before ACL grant'}
    & icacls.exe $taskFull '/grant' ($taskAccount+':M') | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Exact file ACL grant failed'}
    $taskAce=(Get-Acl -LiteralPath $taskFull).Access | Where-Object {$_.IdentityReference.Value -eq $taskAccount -and $_.AccessControlType -eq 'Allow' -and ($_.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Modify) -eq [Security.AccessControl.FileSystemRights]::Modify}
    if(-not $taskAce){throw 'Named Modify absent after exact grant'}
}
@{status='named_modify_verified_exact_native_drafts';file_count=$taskFiles.Count;root_acl_touched=$false;recursive_grant=$false;files=$taskFiles} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskProof -Encoding utf8
Get-Content -LiteralPath $taskProof -TotalCount 7
