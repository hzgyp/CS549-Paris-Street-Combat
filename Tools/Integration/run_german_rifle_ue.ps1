param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('import','author','review','combat','preview')][string]$Mode='import')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(-not (Test-Path -LiteralPath (Join-Path $taskRoot 'tmp/german-rifle-ue-v1/preflight_v1.json'))){throw 'Verified protection checkpoint must exist before launching Unreal'}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close existing user-owned Unreal sessions before another engine job'}
$taskLog=Join-Path $taskRoot "tmp/german-rifle-ue-v1/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied evidence identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_GERMAN_UE_IDENTITY=$Identity
$taskScript=Join-Path $PSScriptRoot "ue_german_rifle_$Mode.py"
$taskMap=if($Mode -in @('review','combat','preview')){'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}else{'/Engine/Maps/Entry'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 $taskMap,'-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
if($Mode -ne 'preview'){$taskArgs+=@('-RenderOffscreen','-unattended','-NoSound')}
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
if($Mode -eq 'preview'){@{pid=$taskProcess.Id;log=$taskLog;user_owned=$true;map_saved=$false;runtime='native Blueprint'} | ConvertTo-Json; return}
"Task-owned German rifle $Mode PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(8)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000) | Out-Null; $taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned job timed out; preserve evidence'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity} | ConvertTo-Json | Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
if($taskProcess.ExitCode -ne 0){throw 'Unreal job exited nonzero; preserve its evidence'}
$taskResultPath=if($Mode -eq 'combat'){
 Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Runtime/$Identity/combat.json"
}else{
 Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanRifleUEV1/$Identity/result.json"
}
if(-not (Test-Path -LiteralPath $taskResultPath)){throw 'No task result; engine exit alone is not acceptance'}
$taskResult=Get-Content -LiteralPath $taskResultPath -Raw | ConvertFrom-Json
if($taskResult.errors.Count -gt 0 -or $taskResult.status -like 'failed*' -or ($Mode -eq 'combat' -and -not $taskResult.all_assertions_passed)){
 throw 'Task result failed; preserve report and inspect it before continuing'
}
