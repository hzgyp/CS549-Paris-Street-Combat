$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$rifleDir=Join-Path $projectRoot 'tmp/rifle-motion-20261002-v1'
$draftDir=Join-Path $projectRoot 'tmp/paris-reload-draft-20261002-v1'
$native=[IO.File]::ReadAllText((Join-Path $projectRoot 'Assets/Sync/manifests/rifle-pro-mocap-ue582-selected.json')) | ConvertFrom-Json -Depth 12
$snapshot=[IO.File]::ReadAllText((Join-Path $projectRoot 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json')) | ConvertFrom-Json -Depth 12
$fresh=[IO.File]::ReadAllText((Join-Path $projectRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P4/SimplifiedReload20261002/fresh_v2.json')) | ConvertFrom-Json -Depth 12
$records=@();$n=0
foreach($e in $native.files){
    $records+=@{path=(Join-Path $rifleDir "client-native-$n.dat");entry=$e}
    $records+=@{path=(Join-Path $rifleDir ('server-verify-'+$e.sha256+'.dat'));entry=$e};$n++
}
foreach($e in $snapshot.files){$records+=@{path=(Join-Path $draftDir ($e.sha256+'.dat'));entry=$e}}
$n=0;foreach($e in $fresh.assets){$records+=@{path=(Join-Path $draftDir "workspace-$n.dat");entry=$e};$n++}
$original=[IO.File]::ReadAllText((Join-Path $projectRoot 'Assets/Sync/manifests/rifle-pro-mocap-original.json')) | ConvertFrom-Json -Depth 12
$sample=@($original.files | Where-Object {$_.path.EndsWith('/W2_Stand_Aim_Reload_IP.uasset')})
if($sample.Count -ne 1){throw 'Unexpected original probe'}
$records+=@{path=(Join-Path $rifleDir 'client-original-sample.dat');entry=$sample[0]}
$verified=@();$bytes=0
foreach($rec in $records){
    $p=[IO.Path]::GetFullPath($rec.path)
    if(-not ($p.StartsWith($rifleDir+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or $p.StartsWith($draftDir+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase))){throw 'Unsafe temporary download target'}
    if(-not (Test-Path -LiteralPath $p)){continue}
    $e=$rec.entry;$retained=Join-Path $projectRoot $e.path
    if((Get-Item -LiteralPath $p).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Refuse download alias'}
    if((Get-Item -LiteralPath $p).Length -ne $e.size_bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $e.sha256){throw 'Probe bytes differ'}
    if((Get-Item -LiteralPath $retained).Length -ne $e.size_bytes -or (Get-FileHash -LiteralPath $retained).Hash.ToLowerInvariant() -ne $e.sha256){throw 'Retained working/original bytes differ'}
    $verified+=@($p);$bytes+=$e.size_bytes
}
foreach($p in $verified){Remove-Item -LiteralPath $p -Force}
@{status='complete';removed_temporary_verified_downloads=$verified.Count;freed_bytes=$bytes;retained='Native writable/original bytes, immutable SFTP objects, manifests, logs and validation records unchanged'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $draftDir 'download-cleanup.json') -Encoding utf8
Write-Output "Removed $($verified.Count) verified temporary downloads ($bytes bytes); no originals or versions removed."
