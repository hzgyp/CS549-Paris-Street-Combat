param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [Parameter(Mandatory=$true)][ValidateSet('source_probe','city')][string]$Mode,
 [ValidateSet('locomotion','holding')][string]$Probe='locomotion')
$ErrorActionPreference='Stop'
if($Mode -eq 'city'){throw 'AN007: full V19 action proof fails reload sleeve and complete return fade. Do not rerun this mechanism; new bounded repair or separate human-viewing entry required.'}
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Another engine owns the serialized slot'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'Lane A native slot claimed.*V19')){throw 'V19 slot not claimed'}
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FPUpperBodyV19/$Identity"
$taskLog=Join-Path $taskRoot "tmp/fp-upper-body-v19/$Identity.log"
if((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_FP_V19_ID=$Identity
$env:CS549_FP_V19_PROBE=$Probe
$taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'city'){'ue_city.py'}else{'ue_source_probe.py'})
$taskMap=if($Mode -eq 'city'){'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}else{'/Engine/Maps/Entry'}
$taskPlugins=if($Mode -eq 'city'){' -EnablePlugins=ParisGripBindingV18'}else{''}
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" '+$taskMap+' -DisablePlugins=ParisEditorBridge'+$taskPlugins+' -RenderOffscreen -unattended -NoP4 -NoSplash -NoSound -ExecCmds="py '+$taskScript.Replace('\','/')+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "V19 $Mode task PID $($taskProcess.Id), identity $Identity"
$taskDeadline=(Get-Date).AddMinutes(6)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id; $taskProcess.WaitForExit()}
$taskProcess.Refresh()
$taskExit=[ordered]@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut;mode=$Mode;identity=$Identity;log=$taskLog}
$taskExit|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskExit|ConvertTo-Json
if($taskTimedOut -or $taskProcess.ExitCode -ne 0){throw 'Task failed; retain evidence and check guards'}
