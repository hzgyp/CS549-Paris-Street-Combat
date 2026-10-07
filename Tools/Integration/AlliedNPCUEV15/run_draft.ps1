param([ValidateSet('save','fresh')][string]$Mode)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve current editor'}
$taskIdentity="draft_asset_$Mode"
$taskLog=Join-Path $taskRoot "tmp/allied-npc-ue-v15/$taskIdentity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied draft proof'}
$env:CS549_ALLIED_DRAFT_ID=$taskIdentity;$env:CS549_ALLIED_DRAFT_MODE=$Mode
$taskScript=(Join-Path $PSScriptRoot 'ue_save_draft.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Engine/Maps/Entry -EnablePlugins=ParisNPCGripV15 -DisablePlugins=ParisEditorBridge -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity=$taskIdentity}|ConvertTo-Json | Set-Content -LiteralPath "$taskLog.exit.json"
Get-Content -LiteralPath "$taskLog.exit.json"
