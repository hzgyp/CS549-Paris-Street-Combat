$ErrorActionPreference = 'Stop'
$workspacePath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$deliveryPath = Join-Path $workspacePath 'Assets\LocalShared\Deliverables\Assignment3'
$archivePath = Join-Path $workspacePath 'Assets\LocalShared\Archives\Assignment3_20261010'
$manifestPath = Join-Path $archivePath 'MANIFEST.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$journalPath = Join-Path $archivePath 'DELETED.jsonl'
if (Test-Path -LiteralPath $journalPath) { throw 'An execution journal already exists; inspect before retry.' }
if ($manifest.workspace -ne $workspacePath -or $manifest.delivery_root -ne $deliveryPath) {
    throw 'Unexpected workspace/delivery root.'
}

function Assert-BoundPath([string]$pathValue, [string]$allowedRoot) {
    $resolved = [IO.Path]::GetFullPath($pathValue)
    $prefix = $allowedRoot.TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside its declared root: $resolved"
    }
    $cursor = Get-Item -LiteralPath $resolved -Force
    while ($null -ne $cursor) {
        if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point: $($cursor.FullName)" }
        if ($cursor.FullName -eq $workspacePath) { break }
        $cursor = Get-Item -LiteralPath ([IO.Path]::GetDirectoryName($cursor.FullName)) -Force
    }
    return $resolved
}

function Assert-FileRow($fileRow, [bool]$checkTime) {
    $pathValue = Assert-BoundPath $fileRow.path $workspacePath
    $info = Get-Item -LiteralPath $pathValue -Force
    if ($info.PSIsContainer -or $info.Length -ne $fileRow.bytes) { throw "File size/type changed: $pathValue" }
    if ((Get-FileHash -LiteralPath $pathValue -Algorithm SHA256).Hash.ToLowerInvariant() -ne $fileRow.sha256) {
        throw "File hash changed: $pathValue"
    }
    if ($checkTime) {
        $timestampSeconds = ([DateTimeOffset]$info.LastWriteTimeUtc).ToUnixTimeSeconds()
        if ([Math]::Abs($timestampSeconds - ([double]$fileRow.mtime_ns / 1000000000)) -gt 1.001) {
            throw "File timestamp changed: $pathValue"
        }
    }
}

$archiveFile = Assert-BoundPath $manifest.archive_file $archivePath
if (-not $manifest.archive_all_members_verified) { throw 'Archive member verification missing.' }
if ((Get-FileHash -LiteralPath $archiveFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.archive_sha256) {
    throw 'Archive hash changed.'
}
foreach ($guard in $manifest.guards) { Assert-FileRow $guard $false }
foreach ($entry in $manifest.entries) {
    $checked = Assert-BoundPath $entry.path $deliveryPath
    if ($checked.StartsWith((Join-Path $deliveryPath 'SFTPAccess_20261010') + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Attempt to delete a protected access file.'
    }
    if ([IO.Path]::GetExtension($checked) -eq '.mp4') { throw 'Attempt to delete current video.' }
    Assert-FileRow $entry $true
    $probe = [IO.File]::Open($checked, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None)
    $probe.Dispose()
}
$driveBefore = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($workspacePath)).AvailableFreeSpace
foreach ($entry in $manifest.entries) {
    $checked = Assert-BoundPath $entry.path $deliveryPath
    Assert-FileRow $entry $true
    Remove-Item -LiteralPath $checked -Force
    @{ path = $checked; bytes = $entry.bytes; sha256 = $entry.sha256; deleted_at = [DateTime]::UtcNow.ToString('o') } |
        ConvertTo-Json -Compress | Add-Content -LiteralPath $journalPath -Encoding UTF8
}
$subdirs = Get-ChildItem -LiteralPath $deliveryPath -Directory -Recurse -Force | Sort-Object { $_.FullName.Length } -Descending
foreach ($dir in $subdirs) {
    $checked = Assert-BoundPath $dir.FullName $deliveryPath
    if (@(Get-ChildItem -LiteralPath $checked -Force).Count -eq 0) { Remove-Item -LiteralPath $checked -Force }
}
$pdfSource = Assert-BoundPath $manifest.pdf_source $workspacePath
$pdfTarget = [IO.Path]::GetFullPath($manifest.pdf_delivery)
if ([IO.Path]::GetDirectoryName($pdfTarget) -ne $deliveryPath) { throw 'Wrong report delivery target.' }
if (Test-Path -LiteralPath $pdfTarget) { throw 'Report delivery target already exists.' }
Copy-Item -LiteralPath $pdfSource -Destination $pdfTarget
if ((Get-FileHash -LiteralPath $pdfTarget).Hash -ne (Get-FileHash -LiteralPath $pdfSource).Hash) {
    throw 'Report copy hash mismatch.'
}
foreach ($guard in $manifest.guards) { Assert-FileRow $guard $false }
$driveAfter = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($workspacePath)).AvailableFreeSpace
$result = @{
    status = 'completed'; archived_files = @($manifest.entries).Count;
    deleted_original_bytes = $manifest.retired_original_bytes; archive_bytes = $manifest.archive_bytes;
    logical_net_saving_bytes = $manifest.projected_net_saving_bytes;
    free_space_before_delete = $driveBefore; free_space_after = $driveAfter;
    protected_files = @($manifest.guards).Count; protected_hashes_match = $true;
    delivery_files = @(Get-ChildItem -LiteralPath $deliveryPath -File -Recurse).Count;
    completed_at = [DateTime]::UtcNow.ToString('o')
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $archivePath 'RESULT.json') -Encoding UTF8
$result | ConvertTo-Json -Compress
