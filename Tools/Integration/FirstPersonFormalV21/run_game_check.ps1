# Ordinary saved -game smoke check; Python/bridge disabled; engine exits itself.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor owns slot'}
$taskIdentity='ordinary_game_v1'
$taskLog=Join-Path $taskRoot "tmp/first-person-formal-v21/$taskIdentity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied ordinary-entry identity'}
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskConfig=Get-Content -LiteralPath $taskProject -Raw|ConvertFrom-Json
if(-not ($taskConfig.Plugins|Where-Object {$_.Name -eq 'ParisGripBindingV18' -and $_.Enabled})){throw 'Runtime plugin not enabled in saved project'}
$taskArgs='"'+$taskProject+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -game -DisablePlugins=ParisEditorBridge,PythonScriptPlugin -NoP4 -NoSplash -windowed -ResX=1280 -ResY=720 -seconds=45 -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity;python_disabled=$true;native_timed_exit=$true}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity=$taskIdentity}|ConvertTo-Json
if($taskProcess.ExitCode -ne 0){throw 'Ordinary game exited with nonzero status'}
