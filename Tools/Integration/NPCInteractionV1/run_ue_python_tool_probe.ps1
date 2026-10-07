param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidateSet('cast','cross_call','public_call')][string]$Mode='cast'
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Another Unreal process owns the native slot'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NPCInteractionV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/npc-interaction-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied probe identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskPython=(Get-Command python -ErrorAction Stop).Source
& $taskPython (Join-Path $PSScriptRoot 'preflight.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Offline guard preflight failed'}
$env:CS549_NPC_IDENTITY=$Identity
$taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'cast'){'ue_python_tool_probe.py'}elseif($Mode -eq 'cross_call'){'ue_cross_blueprint_call_probe.py'}else{'ue_cross_blueprint_public_call_probe.py'})
$taskArgs=@(
    ('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
    '/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
    ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"')
)
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "UE embedded-Python probe PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(4)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned tooling probe timed out'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity=$Identity}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
$taskResult=Join-Path $taskOut $(if($Mode -eq 'cast'){'ue_python_tool_probe.json'}elseif($Mode -eq 'cross_call'){'cross_blueprint_call_probe.json'}else{'cross_blueprint_public_call_probe.json'})
if(-not (Test-Path -LiteralPath $taskResult)){throw 'No UE Python probe result'}
$result=Get-Content -LiteralPath $taskResult -Raw|ConvertFrom-Json
$result|ConvertTo-Json -Depth 8
if($taskProcess.ExitCode -ne 0 -or $result.status -notlike 'pass_*' -or -not $result.protected_guards_unchanged -or $result.protected_count -ne 558){throw 'UE Python tooling probe failed; do not resume asset authoring'}
