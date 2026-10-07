param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [Parameter(Mandatory=$true)][ValidateSet('anim','owner','view','cpp_view','cpp_motion')][string]$Mode)
$ErrorActionPreference='Stop'
if($Mode -in @('anim','owner')){throw 'Stopped after second graph capability failure; do not rerun'}
if($Mode -in @('cpp_view','cpp_motion')){throw 'AN006: current full-body display source fails FP lateral-motion view; proof reruns stopped. Human viewing requires a separate scoped entry, not this repair/test launcher.'}
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Another engine owns the serialized slot'}
$taskSlot=Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 6
if(-not ($taskSlot -match 'Lane A native slot claimed.*V18 UE binding')){throw 'V18 binding slot is not claimed'}
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GripBindingV18/$Identity"
$taskLog=Join-Path $taskRoot "tmp/grip-binding-v18/$Identity.log"
if((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied evidence identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_GRIP_BINDING_ID=$Identity
$taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'cpp_motion'){'ue_cpp_view.py'}else{"ue_$Mode.py"})
$env:CS549_GRIP_BINDING_SCOPE=if($Mode -eq 'cpp_motion'){'motion'}else{'view'}
if(-not (Test-Path -LiteralPath $taskScript)){throw 'Missing scoped script'}
$taskMap='/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
$taskPlugin=if($Mode -in @('cpp_view','cpp_motion')){' -EnablePlugins=ParisGripBindingV18'}else{''}
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" '+$taskMap+' -DisablePlugins=ParisEditorBridge'+$taskPlugin+' -RenderOffscreen -unattended -NoP4 -NoSplash -NoSound -ExecCmds="py '+$taskScript.Replace('\','/')+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "V18 $Mode task PID $($taskProcess.Id), identity $Identity"
$taskDeadline=(Get-Date).AddMinutes(5)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id; $taskProcess.WaitForExit()}
$taskProcess.Refresh()
$taskExit=[ordered]@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut;mode=$Mode;identity=$Identity;log=$taskLog}
$taskExit|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskExit|ConvertTo-Json
if($taskTimedOut -or $taskProcess.ExitCode -ne 0){throw 'Task failed; retain evidence and recheck guards'}
