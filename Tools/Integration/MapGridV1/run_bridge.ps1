param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [Parameter(Mandatory=$true)][string]$BankDirectory)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve competing engine'}
$taskBank=[IO.Path]::GetFullPath($BankDirectory)
$taskPrivate=[IO.Path]::GetFullPath((Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/BridgeConnectivityV1'))
if(-not $taskBank.StartsWith($taskPrivate+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Bridge bank must stay private'}
$taskAdaptation=Get-Content -LiteralPath (Join-Path $taskBank 'adaptation.json') -Raw | ConvertFrom-Json
if((Get-FileHash -LiteralPath (Join-Path $taskBank 'cases.json')).Hash.ToLower() -ne $taskAdaptation.bank_sha256 -or (Get-FileHash -LiteralPath (Join-Path $taskBank 'ue_bridge_verify.py')).Hash.ToLower() -ne $taskAdaptation.adapted_source_sha256){throw 'Frozen grid bank/observer changed'}
$taskOut=Join-Path $taskPrivate $Identity;$taskLog=Join-Path $taskRoot "tmp/bridge-connectivity-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve unique runtime bank'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $taskBank 'ue_bridge_verify.py') -Destination (Join-Path $taskOut 'ue_bridge_verify.py')
$env:CS549_FORMAL_ROOT=$taskRoot;$env:CS549_FORMAL_OUT=$taskOut;$env:CS549_FORMAL_STAGE='Early';$env:CS549_FORMAL_CATEGORY='flat';$env:CS549_FORMAL_LATCH='0'
$env:CS549_BRIDGE_BANK=Join-Path $taskBank 'cases.json'
$taskScript=Join-Path $taskOut 'ue_bridge_verify.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge','-EnablePlugins=ParisFormalSurveyV1',('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{identity=$Identity;owned_pid=$taskEngine.Id;bank=$taskBank;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'entry.json') -Encoding utf8
Write-Output "Bridge original-role verification owned PID $($taskEngine.Id)"
$taskDeadline=(Get-Date).AddMinutes(18)
$taskPattern='Error:|Fatal:|Fatal error:|Ensure condition failed|Assertion failed:|Accessed None|BOOTSTRAP_FAILED'
while(-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline){
 $taskEngine.WaitForExit(1000) | Out-Null;$taskEngine.Refresh()
 if((Test-Path -LiteralPath $taskLog) -and -not(Test-Path -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json'))){
  $taskLive=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
  if($taskLive.Count){@{reason='strict live log gate';count=$taskLive.Count} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json') -Encoding utf8}
 }
}
if(-not $taskEngine.HasExited){Stop-Process -Id $taskEngine.Id;throw 'Owned runtime timeout; preserve failure'}
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern $taskPattern)
@{owned_pid=$taskEngine.Id;exit_code=$taskEngine.ExitCode;strict_log_errors=$taskErrors.Count;ended_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'exit.json') -Encoding utf8
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw | ConvertFrom-Json
$taskResult | Select-Object status,summary,errors,protected_bytes_unchanged | ConvertTo-Json -Depth 4
if($taskEngine.ExitCode -ne 0 -or $taskErrors.Count -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged){throw 'Bridge original-role verification failed; preserve negative'}
