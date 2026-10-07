param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('audit','probe','retarget','author','review','test','preview')][string]$Mode='audit')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if($Mode -in @('retarget','author','review','test','preview') -and (Test-Path -LiteralPath (Join-Path $taskRoot 'Failures/AN001-20261004-existing-weapon-animation/STATE.json'))){throw 'AN001 stopped: do not rerun the rejected implementation; read the failure analysis'}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close user-owned editors before a new writer'}
$taskLog=Join-Path $taskRoot "tmp/weapon-animation-reuse/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied evidence identity'}
if(-not (Test-Path -LiteralPath (Join-Path $taskRoot 'tmp/weapon-animation-reuse/preflight_v1.json'))){throw 'Run guard preflight first'}
$env:CS549_ANIMATION_IDENTITY=$Identity
$taskScript=Join-Path $PSScriptRoot "ue_weapon_animation_$Mode.py"
$taskMap=if($Mode -in @('test','review','preview')){'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}else{'/Engine/Maps/Entry'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),$taskMap,
 '-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
if($Mode -ne 'preview'){$taskArgs+=@('-RenderOffscreen','-unattended','-NoSound')}
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
if($Mode -eq 'preview'){@{pid=$taskProcess.Id;log=$taskLog;user_owned=$true;map_saved=$false} | ConvertTo-Json;return}
"Task animation $Mode PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(8)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000) | Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned timeout; retain evidence'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity} | ConvertTo-Json | Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
if($taskProcess.ExitCode -ne 0){throw 'Nonzero engine exit; retain evidence'}
$taskResult=Get-Content -LiteralPath (Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponAnimationReuseV1/$Identity/result.json") -Raw | ConvertFrom-Json
if($taskResult.errors.Count -gt 0 -or $taskResult.status -like 'failed*'){throw 'Read failed result'}
