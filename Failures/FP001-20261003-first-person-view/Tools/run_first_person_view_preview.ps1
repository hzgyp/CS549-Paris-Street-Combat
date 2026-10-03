$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close the existing Unreal session before review'}
$taskIdentity='human_fp_'+(Get-Date -Format 'yyyyMMdd_HHmmss')
$env:CS549_FP_HUMAN_IDENTITY=$taskIdentity
$taskLog=Join-Path $taskRoot "tmp/paris-first-person-view-20261002/$taskIdentity.log"
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash','-NoSound',
 ('-ExecutePythonScript="'+(Join-Path $PSScriptRoot 'ue_first_person_view_human_preview.py')+'"'),('-abslog="'+$taskLog+'"'))
# Interactive review is explicitly visible; this process becomes user-owned.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
Write-Output "First-person review PID $($taskProcess.Id); identity $taskIdentity; log $taskLog"
Write-Output 'Click PIE: WASD / mouse / left click / R. Esc ends PIE. Saved city is unchanged.'
