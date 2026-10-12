$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'tmp/g1-gameplay-publication-20261011'))
$publication = Get-Content -LiteralPath (Join-Path $taskRoot 'publication.json') -Raw | ConvertFrom-Json
$package = Get-Content -LiteralPath (Join-Path $taskRoot 'package.json') -Raw | ConvertFrom-Json
if ($publication.status -ne 'authenticated_verified_pending_selection' -or -not $publication.named_readback) {
    throw 'Missing complete authenticated readback proof'
}
$readbackRoot = [IO.Path]::GetFullPath((Join-Path $taskRoot 'readbacks'))
$taskPrefix = $taskRoot.TrimEnd('\') + '\'
$targets = @()
foreach ($record in @($package.zip) + @($package.resources)) {
    $targets += [pscustomobject]@{Path=(Join-Path $readbackRoot $record.sha256); Bytes=[long]$record.size_bytes; Hash=$record.sha256}
}
$targets += [pscustomobject]@{Path=(Join-Path $taskRoot 'named-readback.zip'); Bytes=[long]$package.zip.size_bytes; Hash=$package.zip.sha256}
$actual = @(Get-ChildItem -LiteralPath $readbackRoot -Force)
if ($actual.Count -ne ($targets.Count - 1)) { throw 'Unexpected readback inventory' }
$verified = @()
foreach ($target in $targets) {
    $absolute = [IO.Path]::GetFullPath($target.Path)
    if (-not $absolute.StartsWith($taskPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Target escapes task directory' }
    $ancestor = $absolute
    while ($ancestor -and $ancestor.Length -ge $projectRoot.Length) {
        $info = Get-Item -LiteralPath $ancestor -Force
        if ($info.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse target or ancestor' }
        $ancestor = [IO.Path]::GetDirectoryName($ancestor)
    }
    $item = Get-Item -LiteralPath $absolute -Force
    if ($item.PSIsContainer -or $item.Length -ne $target.Bytes) { throw 'Readback identity changed' }
    if ((Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash.ToLowerInvariant() -ne $target.Hash) { throw 'Readback bytes changed' }
    $verified += [pscustomobject]@{path=$absolute; size_bytes=$item.Length; sha256=$target.Hash; last_write_ticks=$item.LastWriteTimeUtc.Ticks}
}
# Validate the entire frozen set before removing any single file. Retain the
# authoritative latest ZIP, teacher backup and all resources/manifests.
foreach ($record in $verified) {
    $item = Get-Item -LiteralPath $record.path -Force
    if ($item.Length -ne $record.size_bytes -or $item.LastWriteTimeUtc.Ticks -ne $record.last_write_ticks) { throw 'Readback changed after verification' }
    Remove-Item -LiteralPath $record.path -Force
}
if (@(Get-ChildItem -LiteralPath $readbackRoot -Force).Count -ne 0) { throw 'Readback directory is not empty' }
Remove-Item -LiteralPath $readbackRoot
$sum = ($verified | Measure-Object -Property size_bytes -Sum).Sum
$receipt = [ordered]@{status='verified_task_readback_copies_removed'; removed_files=$verified.Count; removed_logical_bytes=[long]$sum; files=$verified; current_package_retained=$package.zip.path; teacher_backup_retained=$package.teacher_backup.path; no_old_package_deleted=$true; completed_at=[DateTimeOffset]::Now.ToString('o')}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskRoot 'READBACK_CLEANUP.json') -Encoding utf8
Write-Output "Removed $($verified.Count) verified task readback files; $([math]::Round($sum / 1GB, 2)) GiB. Latest and teacher packages retained."
