param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('Early','Solo','Squad','Encounter')][string]$Stage='Early',
 [ValidateSet('flat','turning','height')][string]$Category='flat',[switch]$BootstrapLatch)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Test-Path -LiteralPath (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FormalMapVerificationV1/final_summary_v1_20261007/summary.json')){throw 'Completed bankV3 is locked; retain negatives and prepare a new bounded bank/plan before another physical entry'}
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Competing engine: preserve ownership'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FormalMapVerificationV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/formal-map-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve unique evidence'}
if($Stage -ne 'Early'){
 $taskGate=Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FormalMapVerificationV1/early_v1_20261007/audit_v1.json'
 if(-not(Test-Path -LiteralPath $taskGate)){throw 'Require independently audited early gate'}
 $taskAdmission=Get-Content -LiteralPath $taskGate -Raw|ConvertFrom-Json
 if($taskAdmission.status -ne 'pass_independent_formal_receipt_audit' -or $taskAdmission.passed -ne 6){throw 'Early gate not admitted'}
}
New-Item -ItemType Directory -Path $taskOut -Force|Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_verify.py') -Destination (Join-Path $taskOut 'ue_verify.py')
$env:CS549_FORMAL_ROOT=$taskRoot;$env:CS549_FORMAL_OUT=$taskOut;$env:CS549_FORMAL_STAGE=$Stage;$env:CS549_FORMAL_CATEGORY=$Category
$env:CS549_FORMAL_LATCH=if($BootstrapLatch){'1'}else{'0'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge','-EnablePlugins=ParisFormalSurveyV1',('-ExecCmds="py '+((Join-Path $taskOut 'ue_verify.py').Replace('\','/'))+'"'),('-abslog="'+$taskLog+'"'))
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{identity=$Identity;stage=$Stage;category=$Category;owned_pid=$taskEngine.Id;started_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'entry.json') -Encoding utf8
Write-Output "Formal map $Stage owned PID $($taskEngine.Id)"
$taskDeadline=(Get-Date).AddMinutes(15)
$taskPattern='Error:|Fatal:|Fatal error:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED'
while(-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline){
 $taskEngine.WaitForExit(1000)|Out-Null;$taskEngine.Refresh()
 if((Test-Path -LiteralPath $taskLog) -and -not(Test-Path -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json'))){
  $taskLive=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
  if($taskLive.Count){@{reason='strict live log gate';count=$taskLive.Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json') -Encoding utf8}
 }
}
if(-not $taskEngine.HasExited){Stop-Process -Id $taskEngine.Id;throw 'Owned timeout; retain failure'}
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
@{owned_pid=$taskEngine.Id;exit_code=$taskEngine.ExitCode;strict_log_errors=$taskErrors.Count;ended_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'exit.json') -Encoding utf8
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json
$taskResult|Select-Object status,stage,summary,errors,protected_bytes_unchanged|ConvertTo-Json -Depth 5
if($taskEngine.ExitCode -ne 0 -or $taskErrors.Count -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged){throw 'Formal verification API/log/guard gate failed; preserve original evidence'}
