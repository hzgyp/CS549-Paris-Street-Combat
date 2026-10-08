param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$BuildIdentity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve occupied native slot'}
$taskPlugin=Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisBridgeMissionV1'
$taskPackage=Join-Path $taskRoot "tmp/g1-mission-v1/Build_$BuildIdentity"
foreach($taskSource in Get-ChildItem -LiteralPath (Join-Path $taskPlugin 'Source') -File -Recurse){
 $taskRelative=[IO.Path]::GetRelativePath($taskPlugin,$taskSource.FullName)
 $taskBuiltSource=Join-Path $taskPackage $taskRelative
 if((Get-FileHash -LiteralPath $taskSource.FullName).Hash -ne (Get-FileHash -LiteralPath $taskBuiltSource).Hash){throw 'Compiled source differs; rebuild before installation'}
}
foreach($taskFile in Get-ChildItem -LiteralPath (Join-Path $taskPackage 'Binaries') -File -Recurse){
 $taskRelative=[IO.Path]::GetRelativePath((Join-Path $taskPackage 'Binaries'),$taskFile.FullName)
 $taskDestination=Join-Path (Join-Path $taskPlugin 'Binaries') $taskRelative
 New-Item -ItemType Directory -Path (Split-Path $taskDestination) -Force | Out-Null
 Copy-Item -LiteralPath $taskFile.FullName -Destination $taskDestination -Force
}
