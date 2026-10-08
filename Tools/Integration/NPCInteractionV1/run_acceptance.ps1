param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidateSet('roles','blocked','travel','radius','combat_off','combat_on')][string]$Scenario='roles',
    [switch]$LongFrame
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Another UE process owns native slot'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NPCInteractionV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/npc-interaction-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied evidence'}
& python (Join-Path $PSScriptRoot 'preflight.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Current protection preflight failed'}
$env:CS549_NPC_IDENTITY=$Identity
$env:CS549_NPC_ACCEPT_SCENARIO=$Scenario
$env:CS549_NPC_ACCEPT_LONG_FRAME=$(if($LongFrame){'1'}else{'0'})
$env:CS549_NPC_SOURCE_DIR=$PSScriptRoot
$taskScript=Join-Path $PSScriptRoot 'ue_acceptance_test.py'
foreach($taskFile in @($PSCommandPath,$taskScript,(Join-Path $PSScriptRoot 'common.py'),(Join-Path $PSScriptRoot 'ue_formal_roster.py'))){
    Copy-Item -LiteralPath $taskFile -Destination (Join-Path $taskOut ([IO.Path]::GetFileName($taskFile)))
}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry',
    '-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge',
    ('-ExecCmds="py '+((Join-Path $taskOut 'ue_acceptance_test.py') -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "$Scenario owned PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(4)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Owned job timeout; evidence retained'}
@{identity=$Identity;scenario=$Scenario;pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'acceptance.json') -Raw|ConvertFrom-Json
$taskLogErrors=@(Get-Content -LiteralPath $taskLog | Where-Object {$_ -match 'Error:|Fatal error:|Assertion failed:|Ensure condition failed:|BOOTSTRAP_FAILED|Accessed None'} | ForEach-Object {[string]$_})
@{identity=$Identity;matched_errors=$taskLogErrors;matched_error_count=$taskLogErrors.Count;exit_code=$taskProcess.ExitCode}|ConvertTo-Json -Depth 3|Set-Content -LiteralPath (Join-Path $taskOut 'log_validation.json')
$taskResult|Select-Object identity,scenario,status,protected_count,protected_guards_unchanged,checks,summary,errors|ConvertTo-Json -Depth 6
if($taskProcess.ExitCode -ne 0 -or $taskLogErrors.Count -ne 0 -or $taskResult.status -notlike 'pass_*' -or -not $taskResult.protected_guards_unchanged -or $taskResult.protected_count -ne 703){throw 'Acceptance gate failed; preserve evidence'}
