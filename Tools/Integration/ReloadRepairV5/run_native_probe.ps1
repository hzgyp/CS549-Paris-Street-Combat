param(
    [Parameter(Mandatory=$true)][string]$Identity,
    [Parameter(Mandatory=$true)][string]$Script,
    [string]$Map='/Engine/Maps/Entry'
)
$ErrorActionPreference='Stop'
$projectRoot='D:\0.Rutgers\CS549\Project-New'
if($Identity -notmatch '^[a-zA-Z0-9_]+$'){throw 'Invalid identity'}
if(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Another engine owns native slot'}
$scriptPath=[IO.Path]::GetFullPath((Join-Path $projectRoot $Script))
$allowedScripts=Join-Path $projectRoot 'Tools\Integration\ReloadRepairV5\'
if(-not $scriptPath.StartsWith($allowedScripts,[StringComparison]::OrdinalIgnoreCase)){throw 'Script outside Lane A'}
if(-not (Test-Path -LiteralPath $scriptPath)){throw 'Missing script'}
if([IO.Path]::GetFileName($scriptPath) -eq 'ue_owner_blend_city.py'){throw 'AN004 stopped both owner integrations. New cause-first mechanism required; do not rerun.'}
if([IO.Path]::GetFileName($scriptPath) -eq 'ue_sleeve_view_compare.py'){throw 'AN005 completed one local weight experiment; actual view failed. Do not rerun this candidate.'}
$evidencePath=Join-Path $projectRoot "Assets\LocalShared\SFTP\workspaces\yg745\paris-gameplay-v1\Evidence\ReloadRepairV5\$Identity"
$logPath=Join-Path $projectRoot "tmp\reload-repair-v5\$Identity.log"
$exitPath=Join-Path $projectRoot "tmp\reload-repair-v5\$Identity.exit.json"
if((Test-Path -LiteralPath $evidencePath) -or (Test-Path -LiteralPath $logPath) -or (Test-Path -LiteralPath $exitPath)){throw 'Occupied identity'}
$env:CS549_RELOAD_V5_IDENTITY=$Identity
$arguments='"'+(Join-Path $projectRoot 'Unreal\ParisStreetCombat\WW2FranceLiberation.uproject')+'" '+$Map+' -DisablePlugins=ParisEditorBridge -RenderOffscreen -unattended -NoP4 -NoSplash -NoSound -ExecCmds="py '+$scriptPath.Replace('\','/')+'" -abslog="'+$logPath+'"'
$probeProcess=Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru
$retainedHandle=$probeProcess.Handle
Write-Output "Started task PID $($probeProcess.Id), identity $Identity"
$normalExit=$probeProcess.WaitForExit(240000)
if(-not $normalExit){Stop-Process -Id $probeProcess.Id -Force; $probeProcess.WaitForExit()}
$probeProcess.Refresh()
$exitCode=$probeProcess.ExitCode
$record=[ordered]@{identity=$Identity;pid=$probeProcess.Id;exit_code=$exitCode;timeout_terminated=(-not $normalExit);log=$logPath;evidence=$evidencePath}
$record | ConvertTo-Json | Set-Content -LiteralPath $exitPath -Encoding UTF8
$record | ConvertTo-Json
if(-not $normalExit -or $exitCode -ne 0){throw 'Native probe failed; preserve evidence and recheck guards'}
