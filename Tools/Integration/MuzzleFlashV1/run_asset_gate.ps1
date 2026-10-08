param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$IntakeIdentity,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$BuildIdentity,
    [switch]$UseRendering,
    [ValidateSet('Assets','Effect','Pulse','RemainingPulse','RatePulse','Geometry','Mount')][string]$Probe='Assets'
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Foreign native slot preserved; no second engine entry'}
if(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run_|launch_)[^\s"]+' }){throw 'Foreign integration launcher preserved between batches'}
if($Probe -ne 'Assets' -and -not $UseRendering){throw 'Effect execution requires actual rendering'}
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MuzzleFlashV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/muzzle-flash-v1/$Identity.log"
$taskCandidate=Join-Path $taskRoot "tmp/muzzle-flash-v1/Candidate_$IntakeIdentity"
$taskPackage=Join-Path $taskRoot "tmp/muzzle-flash-v1/Build_$BuildIdentity/ParisMuzzleFlashV1"
$taskPlugin=Join-Path $taskCandidate 'Plugins/ParisMuzzleFlashV1'
if((Test-Path -LiteralPath $taskEvidence) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied native evidence'}
if(-not (Test-Path -LiteralPath (Join-Path $taskPackage 'Binaries/Win64/UnrealEditor-ParisMuzzleFlashV1.dll'))){throw 'Compiled private candidate absent'}
if(Test-Path -LiteralPath $taskPlugin){
    $taskBinding=Get-Item -LiteralPath $taskPlugin
    if($taskBinding.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($taskBinding.Target[0]) -ne [IO.Path]::GetFullPath($taskPackage)){throw 'Foreign candidate plugin binding preserved'}
}else{New-Item -ItemType Junction -Path $taskPlugin -Target $taskPackage|Out-Null}
New-Item -ItemType Directory -Path $taskEvidence|Out-Null
$taskProbe=if($Probe -eq 'Mount'){'ue_mount_gate.py'}elseif($Probe -eq 'Geometry'){'ue_rifle_geometry.py'}elseif($Probe -eq 'RatePulse'){'ue_rate_pulse_gate.py'}elseif($Probe -ne 'Assets'){'ue_effect_gate.py'}else{'ue_asset_gate.py'}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskProbe) -Destination (Join-Path $taskEvidence 'native_source.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'common.py') -Destination (Join-Path $taskEvidence 'common.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'asset_gate_contract.py') -Destination (Join-Path $taskEvidence 'asset_gate_contract.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'effect_gate_contract.py') -Destination (Join-Path $taskEvidence 'effect_gate_contract.py')
if($Probe -eq 'RatePulse'){Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'rate_pulse_contract.py') -Destination (Join-Path $taskEvidence 'rate_pulse_contract.py')}
if($Probe -eq 'Mount'){
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'geometry_mounts.py') -Destination (Join-Path $taskEvidence 'geometry_mounts.py')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'scale_contract.py') -Destination (Join-Path $taskEvidence 'scale_contract.py')
}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskEvidence 'launcher_source.ps1')
$env:CS549_MUZZLE_ID=$Identity
$env:CS549_MUZZLE_INTAKE=$IntakeIdentity
$env:CS549_MUZZLE_ROOT=$taskRoot
$env:CS549_MUZZLE_RENDERING=if($UseRendering){'true'}else{'false'}
$env:CS549_MUZZLE_EFFECT_MODE=$Probe
$taskScript=Join-Path $taskEvidence 'native_source.py'
$taskArguments=@(('"'+(Join-Path $taskCandidate 'WW2FranceLiberation.uproject')+'"'),'/Engine/Maps/Entry',
    '-unattended','-NoP4','-NoSplash','-NoSound','-DisablePlugins=ParisEditorBridge',
    '-EnablePlugins=ParisMuzzleFlashV1',('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
if(-not $UseRendering){$taskArguments+='-NullRHI'}
if($Probe -ne 'Assets'){$taskArguments+='-RenderOffscreen'}
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Foreign slot changed during preparation; preserve prepared entry without launch'}
if(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.Name -match '^(powershell|pwsh|python|pythonw)\.exe$' -and $_.CommandLine -match 'Tools[/\\]Integration[/\\](?!MuzzleFlashV1[/\\])[^\s"]+[/\\](?:run_|launch_)[^\s"]+' }){throw 'Foreign integration launcher appeared; preserve preparation without launch'}
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArguments -WindowStyle Hidden -PassThru
$taskHandle=$taskProcess.Handle
Write-Output "Muzzle asset gate owned PID $($taskProcess.Id), identity $Identity"
$taskDeadline=(Get-Date).AddMinutes(5)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
$taskTimedOut=-not $taskProcess.HasExited
if($taskTimedOut){Stop-Process -Id $taskProcess.Id;$taskProcess.WaitForExit()}
$taskProcess.Refresh()
@{identity=$Identity;pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json') -Encoding utf8
$taskReport=Get-Content -LiteralPath (Join-Path $taskEvidence 'result.json') -Raw|ConvertFrom-Json
$taskErrors=@(Select-String -LiteralPath $taskLog -Pattern 'Error:|Fatal error:|Ensure condition failed|Assertion failed:')
@{strict_errors=$taskErrors.Count;exit_code=$taskProcess.ExitCode;timed_out=$taskTimedOut}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskEvidence 'log_validation.json') -Encoding utf8
$taskReport|Select-Object status,errors,systems|ConvertTo-Json -Depth 8
if($taskTimedOut -or $taskProcess.ExitCode -ne 0 -or $taskErrors.Count -or $taskReport.errors.Count -or $taskReport.status -notlike 'pass_*'){throw 'Purchased asset gate failed; retain original/candidate evidence'}
