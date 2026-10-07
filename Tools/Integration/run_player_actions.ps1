param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('audit','author','owner_author','test','combat')][string]$Mode='audit')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close existing Unreal sessions before another writer'}
$taskLog=Join-Path $taskRoot "tmp/player-actions/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied evidence identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_ACTION_IDENTITY=$Identity
$taskScript=Join-Path $PSScriptRoot "ue_player_actions_$Mode.py"
$taskMap=if($Mode -in @('test','combat')){'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}else{'/Engine/Maps/Entry'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 $taskMap,'-DisablePlugins=ParisEditorBridge','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Task-owned actions $Mode PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(8)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned action job timed out; preserve evidence'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
