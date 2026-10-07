param([ValidateSet('Move','RecoverAcl','Cleanup')][string]$Action = 'Move')
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$shareRoot = Join-Path $projectRoot 'Assets/LocalShared/SFTP'
$runRoot = Join-Path $projectRoot 'tmp/german-rifle-model-20261004-v1'
$plan = Get-Content -LiteralPath (Join-Path $runRoot 'relocation-plan.json') -Raw | ConvertFrom-Json
$workspace = [IO.Path]::GetFullPath((Join-Path $projectRoot $plan.workspace))

function Resolve-Scoped([string]$relative, [string]$base) {
    $absolute = [IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
    $boundary = [IO.Path]::GetFullPath($base).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
    if (-not $absolute.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) { throw "Path escapes scope: $relative" }
    if (Test-Path -LiteralPath $absolute) {
        $item = Get-Item -LiteralPath $absolute -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Alias not allowed: $relative" }
    }
    return $absolute
}
function Assert-Bytes([string]$path, $entry) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing file: $path" }
    if ((Get-Item -LiteralPath $path).Length -ne $entry.size_bytes -or
        (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -ne $entry.sha256) { throw "Changed bytes: $path" }
}
if (@(Get-Process blender,UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count) { throw 'Close affected editors before migration' }
$rootSddl = (Get-Acl -LiteralPath $shareRoot).Sddl
if ($Action -in @('Move','RecoverAcl')) {
    $journal = Join-Path $runRoot 'relocation.json'
    $records = @()
    if ($Action -eq 'Move') {
    if (Test-Path -LiteralPath $workspace) { throw 'Occupied workspace; no automatic merging/retry' }
    if (Test-Path -LiteralPath $journal) { throw 'Occupied journal; inspect partial moves before recovery' }
    foreach ($entry in $plan.files) {
        $source = Resolve-Scoped $entry.source $projectRoot
        if ($entry.operation -eq 'move') { $source = Resolve-Scoped $entry.source (Join-Path $projectRoot $plan.source_private_root) }
        $destination = Resolve-Scoped $entry.path $workspace
        Assert-Bytes $source $entry
        if (Test-Path -LiteralPath $destination) { throw 'Destination occupied' }
        $records += [pscustomobject]@{ entry=$entry; source=$source; destination=$destination }
    }
    $state = [ordered]@{status='relocating'; root_acl_before=$rootSddl; completed_paths=@(); files=$plan.files}
    $state | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $journal -Encoding utf8
    New-Item -ItemType Directory -Path $workspace | Out-Null
    foreach ($record in $records) {
        New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($record.destination)) -Force | Out-Null
        if ($record.entry.operation -eq 'move') { Move-Item -LiteralPath $record.source -Destination $record.destination }
        else { Copy-Item -LiteralPath $record.source -Destination $record.destination }
        Assert-Bytes $record.destination $record.entry
        $state.completed_paths += $record.entry.path
        $state | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $journal -Encoding utf8
    }
    } else {
        $prior = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
        if ($prior.status -ne 'relocating' -or $prior.completed_paths.Count -ne $plan.files.Count -or $prior.root_acl_before -ne $rootSddl) { throw 'Unrecognized partial migration' }
        if (@(Get-ChildItem -LiteralPath $workspace -File -Recurse).Count -ne $plan.files.Count) { throw 'Unexpected workspace file set' }
        foreach ($entry in $plan.files) {
            $destination = Resolve-Scoped $entry.path $workspace
            Assert-Bytes $destination $entry
            if ($entry.operation -eq 'move' -and (Test-Path -LiteralPath (Join-Path $projectRoot $entry.source))) { throw 'Move source still exists; preserve conflict' }
            $records += [pscustomobject]@{ entry=$entry; destination=$destination }
        }
        $state = [ordered]@{status='relocating'; root_acl_before=$prior.root_acl_before; completed_paths=@($prior.completed_paths); files=$plan.files; recovery='All exact moved files rehashed; explicit file Modify added after directory-inheritance-only check stopped'}
    }
    # Grant only this new owned workspace; never alter root/parents/old assets.
    $account = $env:COMPUTERNAME + '\cs549sftp'
    $aclOutput = & icacls $workspace /grant ($account + ':(OI)(CI)M') /T /C 2>&1
    $aclExit = $LASTEXITCODE
    $aclOutput | Set-Content -LiteralPath (Join-Path $runRoot 'workspace-acl.log') -Encoding utf8
    if ($aclExit -ne 0 -or ($aclOutput -join '\n') -match 'denied|拒绝|Failed processing [1-9]') { throw 'Shared ACL grant incomplete; preserve journal' }
    # The moved files retain original explicit ACLs; directory OI/CI alone did
    # not produce a named effective file ACE. Grant only each exact known file.
    foreach ($record in $records) {
        $fileAclOutput = & icacls $record.destination /grant ($account + ':M') 2>&1
        $fileAclExit = $LASTEXITCODE
        $fileAclOutput | Add-Content -LiteralPath (Join-Path $runRoot 'workspace-file-acl.log') -Encoding utf8
        if ($fileAclExit -ne 0 -or ($fileAclOutput -join '\n') -match 'denied|拒绝|Failed processing [1-9]') { throw 'Exact file Modify failed' }
    }
    $sid = ([Security.Principal.NTAccount]::new($account)).Translate([Security.Principal.SecurityIdentifier])
    foreach ($path in @($workspace) + @($records.destination)) {
        $matching = @((Get-Acl -LiteralPath $path).Access | Where-Object {
            $_.IdentityReference.Translate([Security.Principal.SecurityIdentifier]) -eq $sid -and
            $_.AccessControlType -eq 'Allow' -and ($_.FileSystemRights -band [Security.AccessControl.FileSystemRights]::Modify) -eq [Security.AccessControl.FileSystemRights]::Modify })
        if (-not $matching.Count) { throw "Shared Modify not verified: $path" }
    }
    if ((Get-Acl -LiteralPath $shareRoot).Sddl -ne $rootSddl) { throw 'Protected root ACL changed' }
    $state.status='workspace_verified_shared_modify'; $state.root_acl_unchanged=$true
    $state | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $journal -Encoding utf8
    Write-Output ('Moved accepted bundle: ' + $records.Count + ' files; shared Modify verified')
} else {
    $receipt = Get-Content -LiteralPath (Join-Path $runRoot 'publication.json') -Raw | ConvertFrom-Json
    if ($receipt.status -ne 'verified_pending_catalog_adoption') { throw 'Publication not verified' }
    $deletedBytes = 0; $deletedCount = 0
    foreach ($entry in $plan.files | Sort-Object sha256 -Unique) {
        Assert-Bytes (Resolve-Scoped $entry.path $workspace) $entry
        $download = Resolve-Scoped ('tmp/german-rifle-model-20261004-v1/verified-downloads/' + $entry.sha256) (Join-Path $runRoot 'verified-downloads')
        Assert-Bytes $download $entry
        $deletedBytes += $entry.size_bytes; $deletedCount++
        Remove-Item -LiteralPath $download
    }
    $cleanup = [ordered]@{status='verified_disposable_samples_removed'; files=$deletedCount; bytes=$deletedBytes; retained_workspace=$plan.workspace; root_acl_unchanged=((Get-Acl -LiteralPath $shareRoot).Sddl -eq $rootSddl)}
    $cleanup | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runRoot 'cleanup.json') -Encoding utf8
    Write-Output ('Removed only verified temporary downloads: ' + $deletedCount + ' files / ' + $deletedBytes + ' bytes')
}
