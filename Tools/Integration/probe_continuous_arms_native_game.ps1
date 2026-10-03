param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close existing editors first'}
if(-not(Test-Path -LiteralPath (Join-Path $taskRoot 'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'))){throw 'Native map selection required'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsNativeV1/$Identity"
if(Test-Path -LiteralPath $taskOut){throw 'Preserve occupied game proof identity'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$taskLog=Join-Path $taskRoot "tmp/continuous-arms-native/$Identity.log"
$taskShot=Join-Path $taskOut 'game.png'
# Engine CSV command supplies finite frames + clean exit. No Python, test input or quality changes.
$taskCommands='csvprofile EXITONCOMPLETION,csvprofile FRAMES=600,Shot SHOWUI -nosuffix filename='+($taskShot -replace '\\','/')
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-game','-DisablePlugins=ParisEditorBridge,PythonScriptPlugin',
 '-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-windowed','-ResX=1280','-ResY=720',
 ('-ExecCmds="'+$taskCommands+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "Task-owned native -game without Python PID $($taskProcess.Id)"
$taskDeadline=(Get-Date).AddMinutes(8)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Native game proof timed out; preserve log'}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;log=$taskLog;game_mode=$true;python_disabled=$true;editor_bridge_disabled=$true;shot_exists=(Test-Path -LiteralPath $taskShot);performance_acceptance=$false;note='600 engine frames for startup/clean exit, not warmed movement or stress performance acceptance'}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'result.json')
Get-Content -LiteralPath (Join-Path $taskOut 'result.json')
