param([switch]$LoadSave)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'A current Unreal session is already open; preserve it'}
$taskMap='/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1'
if($LoadSave){$taskMap+='?ParisLoad'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),$taskMap,'-game','-EnablePlugins=ParisBridgeMissionV1','-DisablePlugins=ParisEditorBridge','-DisablePython','-windowed','-ResX=1920','-ResY=1080')
# This is an explicit human play entry; the user owns its visible window.
Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -PassThru | Select-Object Id
