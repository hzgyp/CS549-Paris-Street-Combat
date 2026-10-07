param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor owns serialized slot; preserve it'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'Lane A native slot claimed.*V20')){throw 'V20 serialized slot not claimed'}
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/LeftSupportV20/$Identity"
$taskLog=Join-Path $taskRoot "tmp/left-support-v20/$Identity.log"
if((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_LEFT_SUPPORT_V20_ID=$Identity
$taskScript=(Join-Path $PSScriptRoot 'ue_native_review.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -DisablePlugins=ParisEditorBridge -EnablePlugins=ParisGripBindingV18 -RenderOffscreen -unattended -NoP4 -NoSplash -NoSound -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "V20 local native review PID $($taskProcess.Id), identity $Identity"
$taskDeadline=(Get-Date).AddMinutes(7)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id;$taskProcess.WaitForExit()}
$taskProcess.Refresh()
$taskExit=[ordered]@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut;identity=$Identity;log=$taskLog}
$taskExit|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskExit|ConvertTo-Json
if($taskTimedOut -or $taskProcess.ExitCode -ne 0){throw 'V20 local task failed; preserve evidence'}
