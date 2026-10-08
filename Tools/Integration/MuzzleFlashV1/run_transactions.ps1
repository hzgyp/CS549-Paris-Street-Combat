param(
 [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
 [ValidateSet('Api','Transient','SaveFresh','Fresh','Formal')][string]$Mode='Transient',
 [ValidatePattern('^[A-Za-z0-9_]+$')][string]$Previous
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
function Assert-FreeNativeSlot {
 if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve foreign native slot'}
 if(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run|launch)(?:_|\.)[^\s"]*' }){throw 'Preserve foreign launcher'}
}
Assert-FreeNativeSlot
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MuzzleFlashV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/muzzle-flash-v1/$Identity.log"
if((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied native identity'}
$taskCandidate=Join-Path $taskRoot 'tmp/muzzle-flash-v1/Candidate_intake_formal_v6_20261008'
if($Mode -eq 'Formal'){$taskCandidate=Join-Path $taskRoot 'Unreal/ParisStreetCombat'}
$taskPackage=Join-Path $taskRoot 'tmp/muzzle-flash-v1/Build_native_formal_v13_20261008/ParisMuzzleFlashV1'
if(-not (Test-Path -LiteralPath (Join-Path $taskPackage 'Binaries/Win64/UnrealEditor-ParisMuzzleFlashV1.dll'))){throw 'Private v13 build absent'}
if($Mode -ne 'Formal'){
 $taskPlugin=Join-Path $taskCandidate 'Plugins/ParisMuzzleFlashV1'
 if(Test-Path -LiteralPath $taskPlugin){
  $taskBinding=Get-Item -LiteralPath $taskPlugin
  if($taskBinding.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($taskBinding.Target[0]) -ne [IO.Path]::GetFullPath($taskPackage)){throw 'Preserve occupied candidate binding'}
 }else{New-Item -ItemType Junction -Path $taskPlugin -Target $taskPackage|Out-Null}
}
& python -B -c "import sys;sys.path.insert(0,r'$PSScriptRoot');from common import guards,intake_rows;from formal_contract import approved_profiles;assert len(guards())==703 and len(intake_rows())==68;approved_profiles();print('Approved size/current inputs exact')"
if($LASTEXITCODE -ne 0){throw 'Current protection/approval failed'}
New-Item -ItemType Directory -Path $taskEvidence|Out-Null
foreach($taskName in @('ue_transactions.py','common.py','formal_contract.py','geometry_mounts.py','scale_contract.py')){
 $taskDestination=if($taskName -eq 'ue_transactions.py'){'native_source.py'}else{$taskName}
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskName) -Destination (Join-Path $taskEvidence $taskDestination)
}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskEvidence 'launcher_source.ps1')
$env:CS549_MUZZLE_ID=$Identity
$env:CS549_MUZZLE_ROOT=$taskRoot
$env:CS549_MUZZLE_TRANSACTION_MODE=$Mode
$env:CS549_MUZZLE_PREVIOUS=$Previous
$taskArgs=@(('"'+(Join-Path $taskCandidate 'WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry','-unattended','-NoP4','-NoSplash','-NoSound','-RenderOffscreen','-DisablePlugins=ParisEditorBridge',('-ExecCmds="py '+(Join-Path $taskEvidence 'native_source.py').Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
if($Mode -ne 'Formal'){$taskArgs+='-EnablePlugins=ParisMuzzleFlashV1'}
Assert-FreeNativeSlot
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "Muzzle transactions owned PID $($taskProcess.Id); $Identity / $Mode"
$taskDeadline=(Get-Date).AddMinutes(5)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id;$taskProcess.WaitForExit()}
$taskProcess.Refresh()
@{identity=$Identity;pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal error:|Ensure condition failed|Assertion failed:')
@{strict_errors=$taskErrors.Count;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskEvidence 'log_validation.json') -Encoding utf8
if(-not (Test-Path -LiteralPath (Join-Path $taskEvidence 'result.json'))){throw 'No native result; retain source/log/exit'}
$taskReport=Get-Content -LiteralPath (Join-Path $taskEvidence 'result.json') -Raw|ConvertFrom-Json
$taskReport|Select-Object status,errors|ConvertTo-Json -Depth 8
if($taskTimedOut -or $taskProcess.ExitCode -ne 0 -or $taskErrors.Count -or $taskReport.errors.Count -or $taskReport.status -notlike 'pass_*'){throw 'Real transaction gate failed; preserve identity'}
