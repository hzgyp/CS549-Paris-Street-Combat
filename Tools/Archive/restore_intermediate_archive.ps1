#requires -Version 7
param([Parameter(Mandatory=$true)][string]$Target,[switch]$VerifyRecoveryOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskRecord=Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/StorageCleanup20261009/run_v1'
$plan=Get-Content -LiteralPath (Join-Path $taskRecord 'plan.json') -Raw|ConvertFrom-Json
$result=Get-Content -LiteralPath (Join-Path $taskRecord 'result.json') -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath (Join-Path $taskRecord 'plan.json')).Hash.ToLowerInvariant() -ne $result.plan_sha256){throw 'Plan identity mismatch'}
$selected=@($plan.targets|Where-Object {$_.path -eq $Target -and $_.kind -eq 'recoverable'})
if($selected.Count -ne 1){throw 'Specify exactly one recoverable target from plan.json'}
$active=@(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealEditor-Cmd|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\.exe$' -or
    ($_.Name -match '^dotnet\.exe$' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')
})
if($active.Count){throw 'Preserve active user/build processes'}
function Safe([string]$rel){
    $p=[IO.Path]::GetFullPath((Join-Path $taskRoot $rel))
    if(-not $p.StartsWith($taskRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Path escapes workspace'}
    $cursor=$p
    while($cursor -ne $taskRoot){if(Test-Path -LiteralPath $cursor){if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'}};$cursor=Split-Path -Parent $cursor}
    return $p
}
$destination=Safe $Target
if(Test-Path -LiteralPath $destination){throw 'Preserve occupied restore target'}
$overridePath=Join-Path $taskRoot 'Docs/Development/PackageRetirementV1/RECOVERY_OVERRIDE_20261009.json'
$overrides=@{}
if(Test-Path -LiteralPath $overridePath){
    $override=Get-Content -LiteralPath $overridePath -Raw|ConvertFrom-Json
    if($override.original_plan_sha256 -ne $result.plan_sha256 -or $override.files.Count -ne 7){throw 'Wrong recovery override'}
    foreach($item in $override.files){
        if(-not $item.path.StartsWith('tmp/mvp-closeout-20261008/instrument_v13/Archive/')){throw 'Unexpected overridden reference'}
        if($overrides.ContainsKey($item.path)){throw 'Duplicate overridden reference'}
        $overrides[$item.path]=$item
    }
}
$zipPath=Join-Path $taskRecord 'intermediate_unique_payloads.zip'
if((Get-FileHash -LiteralPath $zipPath).Hash.ToLowerInvariant() -ne $plan.zip_sha256){throw 'ZIP identity mismatch'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead($zipPath)
$extraArchives=@{}
$audioRecovery=@{}
$audioMapPath=Join-Path $taskRoot 'Docs/Development/G1AudioPublicationV2/RECOVERY_MAP_20261009.json'
if(Test-Path -LiteralPath $audioMapPath){
    $audioAuthority=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/Development/G1AudioPublicationV2/RETIREMENT_INVENTORY_20261009.json') -Raw|ConvertFrom-Json
    if((Get-FileHash -LiteralPath $audioMapPath).Hash.ToLowerInvariant() -ne $audioAuthority.recovery_map_sha256){throw 'Audio retirement recovery map changed'}
    $audioMap=Get-Content -LiteralPath $audioMapPath -Raw|ConvertFrom-Json
    foreach($item in $audioMap.files){$audioRecovery[$item.path]=$item}
}
function EntryHash($entry){
    $stream=$entry.Open();$hasher=[Security.Cryptography.SHA256]::Create()
    try{return [Convert]::ToHexString($hasher.ComputeHash($stream)).ToLowerInvariant()}
    finally{$stream.Dispose();$hasher.Dispose()}
}
try{
    foreach($r in @($plan.files|Where-Object target -eq $Target)){
        $p=Safe $r.path
        if(-not $p.StartsWith($destination+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Restore row escapes selected target'}
        if(Test-Path -LiteralPath $p){throw 'Preserve occupied output'}
        if(-not $VerifyRecoveryOnly){New-Item -ItemType Directory -Path (Split-Path $p) -Force|Out-Null}
        if($r.recovery -eq 'retained_file'){
            if($overrides.ContainsKey($r.retained_path)){
                $item=$overrides[$r.retained_path]
                if($item.sha256 -ne $r.sha256 -or $item.size_bytes -ne $r.size_bytes){throw 'Override changes original bytes'}
                if(-not $extraArchives.ContainsKey($item.archive_path)){
                    $archivePath=Safe $item.archive_path
                    if((Get-FileHash -LiteralPath $archivePath).Hash.ToLowerInvariant() -ne $item.archive_sha256){throw 'Override ZIP mismatch'}
                    $extraArchives[$item.archive_path]=[IO.Compression.ZipFile]::OpenRead($archivePath)
                }
                $entry=$extraArchives[$item.archive_path].GetEntry($item.entry)
                if(-not $entry -or $entry.Length -ne $r.size_bytes){throw 'Override entry missing/wrong size'}
                if($VerifyRecoveryOnly){if((EntryHash $entry) -ne $r.sha256){throw 'Override entry bytes mismatch'}}
                else{[IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$p,$false)}
            }elseif($audioRecovery.ContainsKey($r.retained_path)){
                $item=$audioRecovery[$r.retained_path]
                if($item.sha256 -ne $r.sha256 -or $item.size_bytes -ne $r.size_bytes){throw 'Audio recovery changes original bytes'}
                if($item.recovery.kind -eq 'retained_file'){
                    $source=Safe $item.recovery.path
                    if((Get-Item -LiteralPath $source).Length -ne $r.size_bytes -or (Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $r.sha256){throw 'Retained audio baseline bytes mismatch'}
                    if(-not $VerifyRecoveryOnly){Copy-Item -LiteralPath $source -Destination $p}
                }elseif($item.recovery.kind -eq 'zip_entry'){
                    if(-not $extraArchives.ContainsKey($item.recovery.archive_path)){
                        $archivePath=Safe $item.recovery.archive_path
                        if((Get-FileHash -LiteralPath $archivePath).Hash.ToLowerInvariant() -ne $item.recovery.archive_sha256){throw 'Audio recovery ZIP mismatch'}
                        $extraArchives[$item.recovery.archive_path]=[IO.Compression.ZipFile]::OpenRead($archivePath)
                    }
                    $entry=$extraArchives[$item.recovery.archive_path].GetEntry($item.recovery.entry)
                    if(-not $entry -or $entry.Length -ne $r.size_bytes){throw 'Audio recovery entry mismatch'}
                    if($VerifyRecoveryOnly){if((EntryHash $entry) -ne $r.sha256){throw 'Audio recovery entry bytes mismatch'}}
                    else{[IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$p,$false)}
                }else{throw 'Unknown audio recovery kind'}
            }else{
                $source=Safe $r.retained_path
                if((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $r.sha256){throw 'Retained source mismatch'}
                if(-not $VerifyRecoveryOnly){Copy-Item -LiteralPath $source -Destination $p}
            }
        }elseif($r.recovery -eq 'zip_entry'){
            $e=$zip.GetEntry($r.entry);if(-not $e){throw 'ZIP entry missing'}
            if($VerifyRecoveryOnly){if($e.Length -ne $r.size_bytes -or (EntryHash $e) -ne $r.sha256){throw 'ZIP entry bytes mismatch'}}
            else{[IO.Compression.ZipFileExtensions]::ExtractToFile($e,$p,$false)}
        }else{throw 'Cache regeneration is not archive restoration'}
        if(-not $VerifyRecoveryOnly){
            if((Get-Item -LiteralPath $p).Length -ne $r.size_bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $r.sha256){throw 'Restore readback mismatch'}
        }
    }
}finally{$zip.Dispose();foreach($archive in $extraArchives.Values){$archive.Dispose()}}
if($VerifyRecoveryOnly){Write-Output "Verified every recorded recovery byte without creating target: $Target"}
else{Write-Output "Restored exact recorded bytes: $Target"}
