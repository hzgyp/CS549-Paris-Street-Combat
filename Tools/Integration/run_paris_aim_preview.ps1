$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close the existing Unreal session before this review.'}
$taskLog=Join-Path $taskRoot ('tmp/paris-city-gameplay-20261002/human-aim-preview-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.log')
$env:CS549_PLAYER_AIM_HUMAN_IDENTITY='human_preview_'+(Get-Date -Format 'yyyyMMdd_HHmmss')
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash','-NoSound',
 ('-ExecutePythonScript="'+(Join-Path $PSScriptRoot 'ue_player_aim_human_preview.py')+'"'),('-abslog="'+$taskLog+'"'))
# Visible specifically for Yupu's human review; substitutions occur in PIE only.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
Write-Output "Runtime-only aiming preview PID $($taskProcess.Id); log $taskLog"
Write-Output 'Click PIE viewport: WASD / mouse / left click / R. Esc ends PIE; current city is not saved.'
