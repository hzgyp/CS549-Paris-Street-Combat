param([ValidateSet('Prepare','Execute')][string]$Phase='Prepare')
$ErrorActionPreference='Stop'
$TaskRoot='D:\0.Rutgers\CS549\Project-New'
$TaskWork=Join-Path $TaskRoot 'tmp/g1-video-retirement-20261010'
$KeepRelative='Assets/LocalShared/Deliverables/Assignment3/DemoDraft04_20261010/Paris_G1_MVP_Draft_04_Live_Performance.mp4'
$KeepHash='8048195262f6dd45cc583985b1297227065bb9b4b2454d16763037564d073be0'
$Scope=@(
 'tmp/g1-demo-draft-20261009','tmp/g1-demo-draft02-20261009',
 'tmp/g1-demo-draft03-20261009','tmp/g1-demo-draft04-20261010',
 'Assets/LocalShared/Deliverables/Assignment3/DemoDraft20261009',
 'Assets/LocalShared/Deliverables/Assignment3/DemoDraft02_20261009',
 'Assets/LocalShared/Deliverables/Assignment3/DemoDraft03_20261009',
 'Assets/LocalShared/Deliverables/Assignment3/DemoDraft04_20261010',
 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/external_demo_v1/raw.mp4'
)
function Write-Json($Path,$Value) { $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding utf8 }
function Hash-File($Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert-Safe($Path) {
 $absolute=[IO.Path]::GetFullPath($Path)
 if(-not $absolute.StartsWith($TaskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Outside workspace: $absolute"}
 $relative=[IO.Path]::GetRelativePath($TaskRoot,$absolute).Replace('\','/')
 $allowed=$false
 foreach($entry in $Scope){if($relative -eq $entry -or $relative.StartsWith($entry+'/',[StringComparison]::OrdinalIgnoreCase)){$allowed=$true}}
 if(-not $allowed){throw "Outside allowlist: $relative"}
 $resolved=(Resolve-Path -LiteralPath $absolute).ProviderPath
 if(-not $resolved.Equals($absolute,[StringComparison]::OrdinalIgnoreCase)){throw "Resolution mismatch: $relative"}
 $cursor=$absolute
 while(-not $cursor.Equals($TaskRoot,[StringComparison]::OrdinalIgnoreCase)){
  if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse path: $cursor"}
  $cursor=[IO.Path]::GetDirectoryName($cursor)
 }
 return $absolute
}
function Assert-Keep {
 $path=Assert-Safe (Join-Path $TaskRoot $KeepRelative)
 if((Get-Item -LiteralPath $path).Length -ne 152158232 -or (Hash-File $path) -ne $KeepHash){throw 'Approved video identity changed'}
}
function Assert-Idle {
 $writers=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -like '*ffmpeg*' -or $_.Name -eq 'obs-ffmpeg-mux.exe'})
 if($writers.Count){throw 'Active video encoder/muxer; do not delete recording files'}
}
function Assert-Unlocked($Path) {
 $stream=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None)
 $stream.Dispose()
}
function Free-Bytes { [int64](Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'").FreeSpace }
function Scope-Files {
 Push-Location -LiteralPath $TaskRoot
 try{
  $existingScope=@($Scope | Where-Object { Test-Path -LiteralPath (Join-Path $TaskRoot $_) })
  $paths=@(& rg --files --hidden --no-ignore -- @existingScope)
  if($LASTEXITCODE -ne 0){throw 'Scope inventory failed'}
  return @($paths | ForEach-Object { Join-Path $TaskRoot $_ } | Sort-Object -Unique)
 }finally{Pop-Location}
}
Assert-Keep
Assert-Idle
$manifest=Join-Path $TaskWork 'MANIFEST.json'
if($Phase -eq 'Prepare'){
 if(Test-Path -LiteralPath $TaskWork){throw 'Keep previous cleanup identity'}
 $delete=@();$retain=@()
 foreach($candidate in (Scope-Files)){
  $extension=[IO.Path]::GetExtension($candidate).ToLowerInvariant()
  if($extension -in @('.mp4','.mkv','.avi','.mov','.webm')){
   $absolute=Assert-Safe $candidate
   $relative=[IO.Path]::GetRelativePath($TaskRoot,$absolute).Replace('\','/')
   if($relative -eq $KeepRelative){continue}
   Assert-Unlocked $absolute
   $item=Get-Item -LiteralPath $absolute
   $delete+= [pscustomobject]@{path=$relative;absolute_path=$absolute;bytes=$item.Length;modified_utc=$item.LastWriteTimeUtc.ToString('o');sha256=(Hash-File $absolute)}
  }else{
   $item=Get-Item -LiteralPath $candidate -Force
   $retain+= [pscustomobject]@{path=[IO.Path]::GetRelativePath($TaskRoot,$candidate).Replace('\','/');bytes=$item.Length;modified_utc=$item.LastWriteTimeUtc.ToString('o')}
  }
 }
 if(-not $delete.Count){throw 'No superseded videos identified'}
 New-Item -ItemType Directory -Path $TaskWork | Out-Null
 $plan=[ordered]@{status='prepared_not_deleted';authorization='User approves video04 and permits deletion of all other project recordings';prepared_utc=[DateTime]::UtcNow.ToString('o');keep=@{path=$KeepRelative;sha256=$KeepHash;bytes=152158232};delete=$delete;delete_count=$delete.Count;delete_bytes=($delete|Measure-Object bytes -Sum).Sum;nonvideo_retained=$retain;free_bytes_before=(Free-Bytes);scope=$Scope;restore='Deleted recording bytes are not archived or recoverable by this cleanup. Historical hashes/logs/screenshots retained.'}
 Write-Json $manifest $plan
 Write-Json (Join-Path $TaskWork 'PLAN_SHA256.json') @{sha256=(Hash-File $manifest)}
 [pscustomobject]@{status=$plan.status;count=$plan.delete_count;bytes=$plan.delete_bytes;nonvideo_files=$retain.Count} | ConvertTo-Json
 exit 0
}
$expected=Get-Content -LiteralPath (Join-Path $TaskWork 'PLAN_SHA256.json') -Raw | ConvertFrom-Json
if((Hash-File $manifest) -ne $expected.sha256){throw 'Frozen plan changed'}
$plan=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if(Test-Path -LiteralPath (Join-Path $TaskWork 'RESULT.json')){throw 'Already executed; retain result'}
foreach($row in $plan.delete){
 $path=Assert-Safe $row.absolute_path
 if([IO.Path]::GetRelativePath($TaskRoot,$path).Replace('\','/') -ne $row.path){throw 'Relative/absolute mismatch'}
 $item=Get-Item -LiteralPath $path
 if($item.Length -ne $row.bytes -or $item.LastWriteTimeUtc -ne ([datetime]$row.modified_utc).ToUniversalTime() -or (Hash-File $path) -ne $row.sha256){throw "Changed video: $path"}
 Assert-Unlocked $path
}
Assert-Keep
Assert-Idle
foreach($row in $plan.delete){
 Assert-Idle
 Assert-Keep
 $path=Assert-Safe $row.absolute_path
 if((Hash-File $path) -ne $row.sha256){throw "Video changed before removal: $path"}
 Assert-Unlocked $path
 Remove-Item -LiteralPath $path -Force
 if(Test-Path -LiteralPath $path){throw "Removal failed: $path"}
 @{path=$row.path;bytes=$row.bytes;sha256=$row.sha256;deleted_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $TaskWork 'DELETED.jsonl') -Encoding utf8
}
foreach($row in $plan.nonvideo_retained){
 $path=Join-Path $TaskRoot $row.path
 $item=Get-Item -LiteralPath $path -Force
 if($item.Length -ne $row.bytes -or $item.LastWriteTimeUtc -ne ([datetime]$row.modified_utc).ToUniversalTime()){throw "Retained nonvideo changed: $path"}
}
Assert-Keep
$remaining=@(Scope-Files | Where-Object {[IO.Path]::GetExtension($_).ToLowerInvariant() -in @('.mp4','.mkv','.avi','.mov','.webm')})
if($remaining.Count -ne 1 -or [IO.Path]::GetRelativePath($TaskRoot,$remaining[0]).Replace('\','/') -ne $KeepRelative){throw 'Video scope is not exactly the approved final MP4'}
$freeAfter=Free-Bytes
$result=[ordered]@{status='completed_only_approved_game_video_retained';completed_utc=[DateTime]::UtcNow.ToString('o');deleted_files=$plan.delete_count;deleted_bytes=$plan.delete_bytes;free_bytes_before=$plan.free_bytes_before;free_bytes_after=$freeAfter;observed_free_increase=$freeAfter-$plan.free_bytes_before;keep_path=$KeepRelative;keep_sha256=(Hash-File (Join-Path $TaskRoot $KeepRelative));nonvideo_files_unchanged=$plan.nonvideo_retained.Count;remote_operation='None';manifest_sha256=$expected.sha256}
Write-Json (Join-Path $TaskWork 'RESULT.json') $result
$result|ConvertTo-Json
