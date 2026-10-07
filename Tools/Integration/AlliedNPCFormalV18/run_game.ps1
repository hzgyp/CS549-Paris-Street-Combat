$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve existing editor'}
$taskLog=Join-Path $taskRoot 'tmp/allied-npc-formal-v18/ordinary_game_v1.log'
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied game entry'}
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskJson=Get-Content -LiteralPath $taskProject -Raw|ConvertFrom-Json
if(-not ($taskJson.Plugins|Where-Object {$_.Name -eq 'ParisNPCGripV15' -and $_.Enabled})){throw 'Formal plugin must be enabled'}
$taskArgs='"'+$taskProject+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -game -DisablePlugins=ParisEditorBridge,PythonScriptPlugin -NoP4 -NoSplash -windowed -ResX=1280 -ResY=720 -seconds=35 -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity='ordinary_game_v1';python_disabled=$true}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity='ordinary_game_v1'}|ConvertTo-Json | Set-Content -LiteralPath "$taskLog.exit.json"
if($taskProcess.ExitCode -ne 0){throw 'Ordinary game failed'}
$taskReady=@(Select-String -LiteralPath $taskLog -Pattern 'PARIS_ALLIED_GRIP_READY')
if($taskReady.Count -ne 2 -or (Select-String -LiteralPath $taskLog -Pattern 'PARIS_ALLIED_GRIP_FAILURE')){throw 'Both saved Allies must bind natively'}
$taskReady.Line
