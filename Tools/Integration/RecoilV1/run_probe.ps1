param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidateSet('source','baseline','candidate','native_source','contract','visual','visual_isolated','installed')][string]$Mode='source',
    [ValidatePattern('^[A-Za-z0-9_]*$')][string]$CandidateBuild=''
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Another UE process owns the native slot'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/RecoilV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/recoil-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied evidence'}
& python (Join-Path $PSScriptRoot 'common.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Current guard preflight failed'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_RECOIL_ID=$Identity
$env:CS549_RECOIL_MODE=$Mode
$env:CS549_RECOIL_TOOL_DIR=$taskOut
$env:CS549_RECOIL_ROOT=$taskRoot
$taskScript=Join-Path $PSScriptRoot 'ue_probe.py'
Copy-Item -LiteralPath $taskScript -Destination (Join-Path $taskOut 'native_source.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'common.py') -Destination (Join-Path $taskOut 'guard_source.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'common.py') -Destination (Join-Path $taskOut 'common.py')
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
$taskScript=Join-Path $taskOut 'native_source.py'
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
if($Mode -in @('candidate','native_source','contract','visual','visual_isolated')){
    if(-not $CandidateBuild){throw 'Candidate build identity required'}
    $taskProject=Join-Path $taskRoot "tmp/recoil-v1/Candidate_$CandidateBuild/WW2FranceLiberation.uproject"
    if(-not (Test-Path -LiteralPath $taskProject)){throw 'Prepared candidate project absent'}
}
$taskArgs=@(('"'+$taskProject+'"'),'/Engine/Maps/Entry',
    '-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge',
    ('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
if($Mode -in @('source','native_source')){$taskArgs+='-NullRHI'}else{$taskArgs+='-RenderOffscreen'}
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "Recoil $Mode owned PID $($taskProcess.Id), identity $Identity"
$taskDeadline=(Get-Date).AddMinutes(5)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id;$taskProcess.WaitForExit()}
$taskProcess.Refresh()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut;mode=$Mode;identity=$Identity}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskReport=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw|ConvertFrom-Json
$taskLogErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal error:|Ensure condition failed|Assertion failed:')
@{strict_errors=$taskLogErrors.Count;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'log_validation.json') -Encoding utf8
$taskReport|Select-Object status,protected_count,errors,summary|ConvertTo-Json -Depth 6
if($taskTimedOut -or $taskProcess.ExitCode -ne 0 -or $taskLogErrors.Count -ne 0 -or $taskReport.errors.Count -ne 0 -or $taskReport.status -notlike 'pass_*'){throw 'New probe failed; retain evidence'}
