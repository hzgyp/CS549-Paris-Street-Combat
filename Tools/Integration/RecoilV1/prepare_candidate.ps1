param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$BuildIdentity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskProject=Join-Path $taskRoot "tmp/recoil-v1/Candidate_$BuildIdentity"
if(Test-Path -LiteralPath $taskProject){throw 'Preserve occupied candidate project'}
$taskBuild=Join-Path $taskRoot "tmp/recoil-v1/Build_$BuildIdentity"
foreach($taskPlugin in @('ParisGripBindingV18','ParisNPCGripV15')){
    if(-not (Test-Path -LiteralPath (Join-Path $taskBuild "$taskPlugin/Binaries/Win64/UnrealEditor-$taskPlugin.dll"))){throw 'Required candidate binary absent'}
}
New-Item -ItemType Directory -Path (Join-Path $taskProject 'Plugins') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject') -Destination (Join-Path $taskProject 'WW2FranceLiberation.uproject')
Copy-Item -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Config') -Destination (Join-Path $taskProject 'Config') -Recurse
New-Item -ItemType Junction -Path (Join-Path $taskProject 'Content') -Target (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content') | Out-Null
foreach($taskPlugin in @('ParisGripBindingV18','ParisNPCGripV15')){
    New-Item -ItemType Junction -Path (Join-Path $taskProject "Plugins/$taskPlugin") -Target (Join-Path $taskBuild $taskPlugin) | Out-Null
}
Write-Output "Unselected candidate project: $taskProject; original installed binaries unchanged"
