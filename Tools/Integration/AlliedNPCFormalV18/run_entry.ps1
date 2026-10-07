param([ValidateSet('early','author','fresh','audit')][string]$Mode,[string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if($Identity -notmatch '^[A-Za-z0-9_]+$'){throw 'Unique identity required'}
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve existing editor'}
$taskLog=Join-Path $taskRoot "tmp/allied-npc-formal-v18/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied evidence'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_ALLIED_FORMAL_MODE=$Mode
$env:CS549_ALLIED_FORMAL_ID=$Identity
$taskScript=(Join-Path $PSScriptRoot 'ue_entry.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -EnablePlugins=ParisNPCGripV15 -DisablePlugins=ParisEditorBridge -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity=$Identity;mode=$Mode}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity=$Identity}|ConvertTo-Json | Set-Content -LiteralPath "$taskLog.exit.json"
if($taskProcess.ExitCode -ne 0){throw 'Native entry failed; preserve evidence'}
Get-Content -LiteralPath "$taskLog.exit.json"
