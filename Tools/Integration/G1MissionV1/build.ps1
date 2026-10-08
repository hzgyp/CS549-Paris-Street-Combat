param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,[switch]$CompileOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(-not $CompileOnly -and (Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue)){throw 'Native slot occupied'}
$taskPlugin=Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisBridgeMissionV1'
$taskPackage=Join-Path $taskRoot "tmp/g1-mission-v1/Build_$Identity"
if(Test-Path -LiteralPath $taskPackage){throw 'Preserve previous build'}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' BuildPlugin "-Plugin=$taskPlugin/ParisBridgeMissionV1.uplugin" "-Package=$taskPackage" -HostPlatforms=Win64 -NoTargetPlatforms -StrictIncludes
if($LASTEXITCODE -ne 0){throw "Build failed ($LASTEXITCODE), preserve diagnostics"}
if($CompileOnly){"Isolated build ready: $taskPackage (not installed)";return}
foreach($taskFile in Get-ChildItem -LiteralPath (Join-Path $taskPackage 'Binaries') -File -Recurse){
 $taskRelative=[IO.Path]::GetRelativePath((Join-Path $taskPackage 'Binaries'),$taskFile.FullName)
 $taskDestination=Join-Path (Join-Path $taskPlugin 'Binaries') $taskRelative
 New-Item -ItemType Directory -Path (Split-Path $taskDestination) -Force | Out-Null
 Copy-Item -LiteralPath $taskFile.FullName -Destination $taskDestination -Force
}
