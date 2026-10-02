param(
    [string]$EditorPath = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
)
$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$taskProject = Join-Path $taskRoot 'Unreal\ParisStreetCombat\WW2FranceLiberation.uproject'
if (-not (Test-Path -LiteralPath $EditorPath -PathType Leaf)) { throw 'Pinned Unreal editor executable not found.' }
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'Close existing Unreal sessions before this shared-asset review.' }
$taskLogs = Join-Path $taskRoot 'tmp\paris-city-gameplay-20261002'
New-Item -ItemType Directory -Path $taskLogs -Force | Out-Null
$taskLog = Join-Path $taskLogs ('human-review-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
if (Test-Path -LiteralPath $taskLog) { throw 'Preserve occupied review log.' }
$taskArguments = @(
    ('"' + $taskProject + '"'),
    '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1',
    '-game', '-DisablePlugins=ParisEditorBridge', '-NoP4', '-NoSplash', '-NoSound',
    '-windowed', '-ResX=1280', '-ResY=720',
    ('-abslog="' + $taskLog + '"')
)
# Visible specifically for the human keyboard/mouse/usability review.
$taskProcess = Start-Process -FilePath $EditorPath -ArgumentList $taskArguments -WindowStyle Normal -PassThru
Write-Output ('Paris review PID: ' + $taskProcess.Id)
Write-Output ('Launch log: ' + $taskLog)
Write-Output 'Click the game window: WASD / mouse / left click / R. Alt+F4 closes it.'
Write-Output 'This is an un-packaged review, not mission, physical-input or FPS acceptance.'
