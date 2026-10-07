# Explicit human inspection request only; no stopped animation authoring entry.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor is user-owned; do not launch a concurrent process'}
$taskIdentity='human_reload_assets_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$env:CS549_RELOAD_ASSET_REVIEW_ID=$taskIdentity
$taskLog=Join-Path $taskRoot ('tmp/weapon-animation-reuse/'+$taskIdentity+'.log')
$taskScript=Join-Path $PSScriptRoot 'ue_reload_asset_human_preview.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Engine/Maps/Entry','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
# User explicitly requested a visible interactive asset preview.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity;log=$taskLog;user_owned=$true;map_saved=$false;repair_resumed=$false}|ConvertTo-Json
