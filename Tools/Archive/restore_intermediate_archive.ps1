#requires -Version 7
param([Parameter(Mandatory=$true)][string]$Target)
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
$zipPath=Join-Path $taskRecord 'intermediate_unique_payloads.zip'
if((Get-FileHash -LiteralPath $zipPath).Hash.ToLowerInvariant() -ne $plan.zip_sha256){throw 'ZIP identity mismatch'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead($zipPath)
try{
    foreach($r in @($plan.files|Where-Object target -eq $Target)){
        $p=Safe $r.path
        if(-not $p.StartsWith($destination+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Restore row escapes selected target'}
        if(Test-Path -LiteralPath $p){throw 'Preserve occupied output'}
        New-Item -ItemType Directory -Path (Split-Path $p) -Force|Out-Null
        if($r.recovery -eq 'retained_file'){
            $source=Safe $r.retained_path
            if((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $r.sha256){throw 'Retained source mismatch'}
            Copy-Item -LiteralPath $source -Destination $p
        }elseif($r.recovery -eq 'zip_entry'){
            $e=$zip.GetEntry($r.entry);if(-not $e){throw 'ZIP entry missing'}
            [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$p,$false)
        }else{throw 'Cache regeneration is not archive restoration'}
        if((Get-Item -LiteralPath $p).Length -ne $r.size_bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $r.sha256){throw 'Restore readback mismatch'}
    }
}finally{$zip.Dispose()}
Write-Output "Restored exact recorded bytes: $Target"
