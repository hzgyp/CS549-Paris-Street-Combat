param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity,
      [ValidateSet('Inventory','Survey','VehicleDiagnostic')][string]$Stage='Inventory',
      [ValidateSet('Early','FixedSurvey')][string]$Profile='Early',
      [ValidatePattern('^[a-zA-Z0-9_]*$')][string]$Previous='')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if (Get-Process UnrealEditor*,WW2FranceLiberation* -ErrorAction SilentlyContinue) { throw 'Competing engine: preserve ownership' }
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/pure-map-survey-v1/$Identity.log"
if ((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)) { throw 'Preserve unique evidence identity' }
$taskSource=if ($Stage -eq 'Inventory') {'ue_pure_map_inventory.py'} elseif ($Stage -eq 'VehicleDiagnostic') {'ue_vehicle_fixture_diagnostic.py'} else {'ue_pure_map_survey.py'}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $taskSource))) { throw 'Implement workflow stage before entry' }
New-Item -ItemType Directory -Path $taskOut -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskScript=Join-Path $taskOut $taskSource
Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskSource) -Destination $taskScript
if ($Stage -eq 'Survey') { Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'pure_map_graph.py') -Destination (Join-Path $taskOut 'pure_map_graph.py') }
if ($Stage -eq 'Survey') { Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'vehicle_prefix.py') -Destination (Join-Path $taskOut 'vehicle_prefix.py') }
if ($Stage -eq 'VehicleDiagnostic') { Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_pure_map_survey.py') -Destination (Join-Path $taskOut 'snapshot_source.py') }
$env:CS549_PURE_ROOT=$taskRoot
$env:CS549_PURE_OUT=$taskOut
$env:CS549_PURE_PROFILE=$Profile
$env:CS549_PURE_PREVIOUS=$Previous
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 '-DisablePlugins=ParisEditorBridge',('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
if ($Stage -eq 'Survey') { $taskArgs += '-EnablePlugins=ParisMapSurveyV1' }
if ($Stage -ne 'Inventory' -and $Profile -eq 'FixedSurvey') { $taskArgs += @('-NullRHI','-UseFixedTimeStep','-FPS=50') }
$taskEngine=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Pure-map $Stage PID $($taskEngine.Id); $taskOut"
@{identity=$Identity;stage=$Stage;profile=$Profile;owned_pid=$taskEngine.Id;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'entry.json') -Encoding utf8
$taskDeadline=(Get-Date).AddMinutes($(if ($Stage -eq 'Inventory') {5} else {55}))
while (-not $taskEngine.HasExited -and (Get-Date) -lt $taskDeadline) {
 $taskEngine.WaitForExit(1000) | Out-Null
 $taskEngine.Refresh()
 if ($Stage -ne 'Inventory' -and (Test-Path -LiteralPath $taskLog) -and -not (Test-Path -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json'))) {
  $taskLiveErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked')
  if ($taskLiveErrors.Count) { @{reason='strict live log gate';errors=$taskLiveErrors.Count} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'STOP_REQUEST.json') -Encoding utf8 }
 }
}
if (-not $taskEngine.HasExited) { Stop-Process -Id $taskEngine.Id; throw 'Owned pure-map entry timeout; preserve partial evidence' }
$taskReport=if ($Stage -eq 'Inventory') {'inventory.json'} else {'survey.json'}
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked')
@{owned_pid=$taskEngine.Id;exit_code=$taskEngine.ExitCode;strict_log_errors=$taskErrors.Count;ended_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'exit.json') -Encoding utf8
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut $taskReport) -Raw | ConvertFrom-Json
$taskResult | Select-Object status,summary,errors,protected_bytes_unchanged | ConvertTo-Json -Depth 5
if ($taskEngine.ExitCode -ne 0 -or $taskResult.errors.Count -or -not $taskResult.protected_bytes_unchanged -or $taskErrors.Count) { throw 'Pure-map API/log/guard gate failed; preserve original evidence' }
Write-Output "Owned pure-map $Stage exit0; strict log0; scope follows receipt"
