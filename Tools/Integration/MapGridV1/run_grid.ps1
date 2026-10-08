param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [ValidateSet('Early','Full')][string]$Stage='Early')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue){throw 'Preserve competing native process'}
if($Stage -eq 'Full'){
 $taskEarly=Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MapGridV1/early_v3_20261007'
 $taskProof=Get-Content -LiteralPath (Join-Path $taskEarly 'result.json') -Raw | ConvertFrom-Json
 $taskExit=Get-Content -LiteralPath (Join-Path $taskEarly 'exit.json') -Raw | ConvertFrom-Json
 $taskHelperHash=(Get-FileHash -LiteralPath (Join-Path $taskRoot 'Unreal/ParisStreetCombat/Plugins/ParisGridSurveyV1/Binaries/Win64/UnrealEditor-ParisGridSurveyV1.dll')).Hash.ToLower()
 if($taskProof.status -ne 'pass_early_grid_admission' -or $taskProof.errors.Count -or -not $taskProof.protected_bytes_unchanged -or -not $taskProof.old_helpers_unchanged -or $taskExit.exit_code -ne 0 -or $taskExit.strict_log_errors -ne 0 -or $taskHelperHash -ne $taskProof.grid_helper_sha256){throw 'Full grid requires exact admitted early helper'}
}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MapGridV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/map-grid-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve unique grid entry'}
New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskScript=Join-Path $taskOut 'ue_grid_sample.py'
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_grid_sample.py') -Destination $taskScript
foreach($taskSource in @('grid_core.py','prepare_candidates.py','prepare_links.py','prepare_sight.py')){
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskSource) -Destination (Join-Path $taskOut $taskSource)
}
$env:CS549_GRID_ROOT=$taskRoot;$env:CS549_GRID_OUT=$taskOut;$env:CS549_GRID_STAGE=$Stage
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Engine/Maps/Entry','-unattended','-NoP4','-NoSplash','-NoSound','-NullRHI',
 '-DisablePlugins=ParisEditorBridge','-EnablePlugins=ParisGridSurveyV1,ParisMapSurveyV1',
 ('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{identity=$Identity;stage=$Stage;owned_pid=$taskEngine.Id;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'entry.json') -Encoding utf8
Write-Output "Grid $Stage owned PID $($taskEngine.Id); $taskOut"
$taskDeadline=(Get-Date).AddMinutes($(if($Stage -eq 'Early'){12}else{60}))
while(-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline){
 $taskEngine.WaitForExit(1000) | Out-Null;$taskEngine.Refresh()
 if((Test-Path -LiteralPath $taskLog) -and -not (Test-Path -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json'))){
  $taskLiveErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked')
  if($taskLiveErrors.Count){@{reason='strict live log gate';errors=$taskLiveErrors.Count} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json') -Encoding utf8}
 }
}
if(-not $taskEngine.HasExited){Stop-Process -Id $taskEngine.Id;throw 'Owned grid timeout; preserve partial evidence'}
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked')
@{owned_pid=$taskEngine.Id;exit_code=$taskEngine.ExitCode;strict_log_errors=$taskErrors.Count;ended_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'exit.json') -Encoding utf8
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw | ConvertFrom-Json
$taskResult | Select-Object status,phase,passes,early_controls,errors,protected_bytes_unchanged,old_helpers_unchanged | ConvertTo-Json -Depth 9
if($taskEngine.ExitCode -ne 0 -or $taskErrors.Count -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged -or -not $taskResult.old_helpers_unchanged){throw 'Native grid entry failed; preserve exact evidence'}
