param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidatePattern('^[A-Za-z0-9_]+$')][string]$NativeReferenceIdentity
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskProject=Join-Path $taskRoot "tmp/muzzle-flash-v1/Candidate_$Identity"
if(Test-Path -LiteralPath $taskProject){throw 'Preserve occupied candidate'}
$taskIntakeArgs=@('--identity',$Identity)
if($NativeReferenceIdentity){$taskIntakeArgs+=@('--native-reference-identity',$NativeReferenceIdentity)}
& python (Join-Path $PSScriptRoot 'intake_candidate.py') @taskIntakeArgs
if($LASTEXITCODE -ne 0){throw 'Purchased source/current epoch preflight failed'}
$taskReceipt=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MuzzleFlashV1/$Identity/intake.json"
$taskData=Get-Content -LiteralPath $taskReceipt -Raw|ConvertFrom-Json
New-Item -ItemType Directory -Path (Join-Path $taskProject 'Content/MsvFx_MuzzleFlash_Pack') -Force|Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskProject 'Plugins') -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject') -Destination (Join-Path $taskProject 'WW2FranceLiberation.uproject')
New-Item -ItemType Directory -Path (Join-Path $taskProject 'Config')|Out-Null
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Config') -Filter '*.ini' -File|ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $taskProject 'Config')}
foreach($taskRow in $taskData.closure){
    $taskRelative=$taskRow.package.Substring('/Game/'.Length)+'.uasset'
    $taskDestination=Join-Path (Join-Path $taskProject 'Content') $taskRelative
    if(Test-Path -LiteralPath $taskDestination){throw 'Refuse candidate asset overwrite'}
    New-Item -ItemType Directory -Path (Split-Path $taskDestination) -Force|Out-Null
    Copy-Item -LiteralPath (Join-Path $taskRoot $taskRow.path) -Destination $taskDestination
    if((Get-FileHash -LiteralPath $taskDestination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskRow.sha256){throw 'Candidate copy differs'}
}
# Entry proof does not need city content; add read-only per-root junctions for
# subsequent supported-rifle inspection, not a second city asset copy.
foreach($taskDirectory in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Content') -Directory){
    if($taskDirectory.Name -eq 'MsvFx_MuzzleFlash_Pack'){throw 'Purchased effect root unexpectedly already integrated'}
    if($taskDirectory.Name -eq 'ParisCombat'){
        New-Item -ItemType Directory -Path (Join-Path $taskProject 'Content/ParisCombat') -Force|Out-Null
        foreach($taskChild in Get-ChildItem -LiteralPath $taskDirectory.FullName -Directory){
            if($taskChild.Name -eq 'VFX'){throw 'Inspect existing VFX home before making a private candidate'}
            New-Item -ItemType Junction -Path (Join-Path $taskProject ('Content/ParisCombat/'+$taskChild.Name)) -Target $taskChild.FullName|Out-Null
        }
    }else{New-Item -ItemType Junction -Path (Join-Path $taskProject ('Content/'+$taskDirectory.Name)) -Target $taskDirectory.FullName|Out-Null}
}
foreach($taskPlugin in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins') -Directory){
    if($taskPlugin.Name -ne 'ParisMuzzleFlashV1'){New-Item -ItemType Junction -Path (Join-Path $taskProject ('Plugins/'+$taskPlugin.Name)) -Target $taskPlugin.FullName|Out-Null}
}
Write-Output "Purchased candidate prepared: $taskProject; original delivery and selected assets unchanged"
