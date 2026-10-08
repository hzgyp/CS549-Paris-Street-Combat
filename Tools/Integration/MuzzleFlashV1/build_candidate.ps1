param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve foreign native slot; defer private build'}
if(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run|launch)(?:_|\.)[^\s"]*' }){throw 'Preserve foreign launcher; defer private build'}
if(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'AutomationTool\.dll|UnrealBuildTool\.dll' }){throw 'Preserve foreign UAT/build slot; no competing build'}
$taskBuild=Join-Path $taskRoot "tmp/muzzle-flash-v1/Build_$Identity"
if(Test-Path -LiteralPath $taskBuild){throw 'Preserve occupied private build'}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' BuildPlugin "-Plugin=$taskRoot/Unreal/ParisStreetCombat/Plugins/ParisMuzzleFlashV1/ParisMuzzleFlashV1.uplugin" "-Package=$taskBuild/ParisMuzzleFlashV1" -HostPlatforms=Win64 -NoTargetPlatforms -StrictIncludes
if($LASTEXITCODE -ne 0){throw 'Independent muzzle build failed; preserve private output'}
Write-Output "Private muzzle build $Identity complete; no selected DLL replaced"
