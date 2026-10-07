param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){Write-Output 'Foreign native slot preserved; compile only into vacant private package outputs, with no engine entry or installed DLL write'}
$taskBuild=[IO.Path]::GetFullPath((Join-Path $taskRoot "tmp/recoil-v1/Build_$Identity"))
if(-not $taskBuild.StartsWith((Join-Path $taskRoot 'tmp/recoil-v1/') , [StringComparison]::OrdinalIgnoreCase)){throw 'Build output outside intended temporary directory'}
if(Test-Path -LiteralPath $taskBuild){throw 'Preserve occupied build output'}
foreach($taskPlugin in @('ParisGripBindingV18','ParisNPCGripV15')){
    $taskPackage=Join-Path $taskBuild $taskPlugin
    if(Test-Path -LiteralPath $taskPackage){throw 'BuildPlugin must receive a vacant package path'}
    & 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' BuildPlugin "-Plugin=$taskRoot/Unreal/ParisStreetCombat/Plugins/$taskPlugin/$taskPlugin.uplugin" "-Package=$taskPackage" -HostPlatforms=Win64 -NoTargetPlatforms -StrictIncludes
    if($LASTEXITCODE -ne 0){throw "Candidate $taskPlugin compile failed; retain output"}
}
Write-Output "Two candidate modules built in $taskBuild; no installed binaries replaced"
