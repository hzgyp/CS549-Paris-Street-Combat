param([ValidateSet('early','author','fresh','audit')][string]$Mode,[string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if($Identity -notmatch '^[A-Za-z0-9_]+$'){throw 'Explicit unique identity required'}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor owns slot; preserve it'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'Lane A native slot claimed.*formal adoption')){throw 'Formal slot not claimed'}
$taskLog=Join-Path $taskRoot "tmp/first-person-formal-v21/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied log identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_FORMAL_FP_MODE=$Mode
$env:CS549_FORMAL_FP_ID=$Identity
$taskScript=(Join-Path $PSScriptRoot 'ue_entry.py').Replace('\','/')
$taskPluginFlag=if($Mode -eq 'early'){' -EnablePlugins=ParisGripBindingV18'}else{''}
$taskRenderFlag=if($Mode -in @('author','audit')){' -NullRHI -Unattended -NoSound'}else{''}
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -DisablePlugins=ParisEditorBridge'+$taskPluginFlag+$taskRenderFlag+' -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;mode=$Mode;identity=$Identity;log=$taskLog}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity}|ConvertTo-Json
