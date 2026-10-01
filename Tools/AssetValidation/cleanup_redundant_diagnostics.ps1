[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$taskRoot='D:\0.Rutgers\CS549\Project-New'
$taskLab=Join-Path $taskRoot 'Assets\LocalShared\SFTP\workspaces\yg745\character-ue582-v1'
$taskExports=Join-Path $taskLab 'Evidence\Exports'
$taskRetained=Join-Path $taskLab 'Evidence\Repair20261001\Exchange'
$taskVerify=Get-Content -LiteralPath (Join-Path $taskLab 'Evidence\Repair20261001\exchange_fresh_verification.json') -Raw|ConvertFrom-Json
if(Get-Process UnrealEditor*,blender -ErrorAction SilentlyContinue){throw 'Close affected jobs/editors before cleanup.'}
if($taskVerify.errors.Count -or $taskVerify.meshes.Count -ne 12 -or $taskVerify.animations.Count -ne 7 -or $taskVerify.sources.Count -ne 12){throw 'Retained repair verification is incomplete.'}
if($taskVerify.sources | Where-Object {$_.missing_images.Count}){throw 'Retained sources have missing textures.'}
foreach($taskEntry in @($taskVerify.meshes)+@($taskVerify.animations)+@($taskVerify.sources)){
    if(-not $taskEntry.sha256 -or (Get-FileHash -LiteralPath (Join-Path $taskRetained $taskEntry.file) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskEntry.sha256){throw 'Retained artifact changed since fresh verification.'}
}
$taskTargets=@(Get-ChildItem -LiteralPath $taskExports -File | Where-Object {$_.Extension -eq '.fbx' -or $_.Name -like '*_diagnostic.blend'})
$taskTargets+=@(Get-ChildItem -LiteralPath (Join-Path $taskExports 'UE582Resaved') -File | Where-Object {$_.Name -like '*_diagnostic.blend'})
foreach($taskCache in @('Intermediate','DerivedDataCache')){
    $taskCachePath=Join-Path $taskLab $taskCache
    if(Test-Path -LiteralPath $taskCachePath){$taskTargets+=Get-Item -LiteralPath $taskCachePath}
}
$taskReport=[ordered]@{completed_at=$null;removed=@();bytes_removed=0;recovery='Old diagnostic FBX/Blender files can be regenerated from retained native UE packages with the original test scripts. Intermediate/DDC are disposable caches. Original intake, native Content, repaired source/exports, native baseline FBX and diagnostic logs/images are preserved.'}
foreach($taskTarget in $taskTargets){
    $taskAbsolute=[IO.Path]::GetFullPath($taskTarget.FullName)
    $taskPrefix=[IO.Path]::GetFullPath($taskLab).TrimEnd('\')+'\'
    if(-not $taskAbsolute.StartsWith($taskPrefix,[StringComparison]::OrdinalIgnoreCase) -or ($taskTarget.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Unsafe cleanup path.'}
    if(-not $taskTarget.PSIsContainer){
        $taskName=if($taskTarget.Extension -eq '.fbx'){$taskTarget.Name}else{$taskTarget.Name.Replace('_diagnostic.blend','.blend')}
        # No equivalent editable source for equipment is needed; native package is retained.
        if($taskTarget.Extension -eq '.fbx' -and -not(Test-Path -LiteralPath (Join-Path $taskRetained $taskName))){throw 'No retained repaired exchange file.'}
        if($taskTarget.Extension -eq '.blend' -and -not(Test-Path -LiteralPath (Join-Path $taskRetained $taskName))){throw 'No retained repaired editable source.'}
    }
    $taskFiles=if($taskTarget.PSIsContainer){@(Get-ChildItem -LiteralPath $taskAbsolute -Recurse -File -Force)}else{@($taskTarget)}
    $taskBytes=[long](($taskFiles|Measure-Object Length -Sum).Sum)
    $taskReport.removed+=@{path=$taskAbsolute.Substring($taskRoot.Length+1);bytes=$taskBytes;files=$taskFiles.Count}
    Remove-Item -LiteralPath $taskAbsolute -Recurse -Force
    $taskReport.bytes_removed+=$taskBytes
}
$taskReport.completed_at=Get-Date -Format o
$taskReport|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskLab 'Evidence\Repair20261001\cleanup.json') -Encoding utf8
$taskReport|Select-Object bytes_removed,completed_at
