param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close existing Unreal sessions first'}
$taskLog=Join-Path $taskRoot "tmp/continuous-arms-v3/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$env:CS549_CONTINUOUS_ARMS_IDENTITY=$Identity
$env:CS549_PLAYER_AIM_PREVIEW='0';$env:CS549_FIRST_PERSON_VIEW_PREVIEW='0'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecutePythonScript="'+(Join-Path $PSScriptRoot 'ue_continuous_arms_static_v3.py')+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Continuous arms static probe PID $($taskProcess.Id)"
$taskDeadline=(Get-Date).AddMinutes(7)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned probe timeout'}
@{exit_code=$taskProcess.ExitCode;identity=$Identity;log=$taskLog}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
