param([string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if($Identity -notmatch '^[A-Za-z0-9_]+$'){throw 'Unique identity required'}
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve current editor/slot'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'CLAIMED.*German.*translation')){throw 'Explicit current Lane A capture claim required'}
$taskLog=Join-Path $taskRoot "tmp/german-npc-grip-v1/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied identity'}
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $PSScriptRoot 'common.py')
if($LASTEXITCODE -ne 0){throw 'Current guard preflight failed'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_GERMAN_GRIP_ID=$Identity
$taskScript=(Join-Path $PSScriptRoot 'ue_translation.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -DisablePlugins=ParisEditorBridge -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;identity=$Identity;log=$taskLog}|ConvertTo-Json
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;identity=$Identity;exit_code=$taskProcess.ExitCode}|ConvertTo-Json|Set-Content -LiteralPath "$taskLog.exit.json"
Get-Content -LiteralPath "$taskLog.exit.json"
if($taskProcess.ExitCode -ne 0){throw 'Native entry failed; preserve evidence'}
