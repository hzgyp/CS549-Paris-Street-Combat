param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
 [ValidateSet('Crowd')][string]$Stage='Crowd')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Test-Path -LiteralPath (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NativeConvergenceV1/closure_v1_20261007.json')){throw 'Completed convergence banks locked; prepare a new plan and bank before physical testing'}
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve competing/user-owned engine'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NativeConvergenceV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/native-convergence-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Frozen native identity occupied'}
if($Stage -eq 'Crowd'){
 $taskEarly=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NativeConvergenceV1/full_v1_20261007/audit.json') -Raw|ConvertFrom-Json
 if($taskEarly.status -ne 'pass_independent_convergence_audit' -or $taskEarly.cases -ne 134){throw 'Require independently admitted early mechanism'}
}
New-Item -ItemType Directory -Path $taskOut -Force|Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_crowd.py') -Destination (Join-Path $taskOut 'ue_crowd.py')
$env:CS549_CONVERGE_ROOT=$taskRoot;$env:CS549_CONVERGE_OUT=$taskOut;$env:CS549_CONVERGE_STAGE=$Stage
$taskScript=Join-Path $taskOut 'ue_crowd.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge','-EnablePlugins=ParisFormalSurveyV1',('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{identity=$Identity;stage=$Stage;owned_pid=$taskEngine.Id;started_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'entry.json') -Encoding utf8
Write-Output "Convergence $Stage owned PID $($taskEngine.Id)"
$taskPattern='Error:|Fatal:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED'
$taskDeadline=(Get-Date).AddMinutes(12)
while(-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline){
 $taskEngine.WaitForExit(1000)|Out-Null;$taskEngine.Refresh()
 if((Test-Path -LiteralPath $taskLog) -and -not(Test-Path -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json'))){
  $taskLive=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
  if($taskLive.Count){@{reason='strict live log gate';count=$taskLive.Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json') -Encoding utf8}
 }
}
if(-not $taskEngine.HasExited){Stop-Process -Id $taskEngine.Id;throw 'Owned native deadline, preserve partial receipt'}
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
@{owned_pid=$taskEngine.Id;exit_code=$taskEngine.ExitCode;strict_log_errors=$taskErrors.Count;ended_utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'exit.json') -Encoding utf8
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json
$taskResult|Select-Object status,summary,errors,protected_bytes_unchanged,helpers_unchanged|ConvertTo-Json -Depth 6
if($taskEngine.ExitCode -ne 0 -or $taskErrors.Count -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged -or -not $taskResult.helpers_unchanged){throw 'Native entry rejected; preserve originals'}
