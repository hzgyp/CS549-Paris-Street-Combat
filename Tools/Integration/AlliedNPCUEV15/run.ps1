param([string]$Identity,[ValidateSet('v15','v16')][string]$Variant='v15',[ValidateSet('early','motion','reload')][string]$Mode='early')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if($Identity -notmatch '^[A-Za-z0-9_]+$'){throw 'Unique identity required'}
if($Mode -eq 'motion'){throw 'Full-city motion proof STOPPED. Read AN008 and write a different bounded lifecycle/timing plan first.'}
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve current editor'}
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $PSScriptRoot 'common.py')
if($LASTEXITCODE -ne 0){throw 'Exact current guards failed'}
$taskLog=Join-Path $taskRoot "tmp/allied-npc-ue-v15/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied evidence identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_ALLIED_UE_V15_ID=$Identity
$env:CS549_ALLIED_UE_VARIANT=$Variant
$env:CS549_ALLIED_UE_MODE=$Mode
$taskScript=(Join-Path $PSScriptRoot 'ue_entry.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -EnablePlugins=ParisNPCGripV15 -DisablePlugins=ParisEditorBridge -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity=$Identity}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;identity=$Identity}|ConvertTo-Json | Set-Content -LiteralPath "$taskLog.exit.json"
Get-Content -LiteralPath "$taskLog.exit.json"
