# Separate explicit human entry, not a stopped automated-proof invocation.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,blender* -ErrorAction SilentlyContinue){throw 'Preserve current editor/serialized slot'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'CLAIMED.*Allied.*human')){throw 'Human slot must be claimed'}
& 'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $PSScriptRoot 'common.py')
if($LASTEXITCODE -ne 0){throw 'Exact current guards failed'}
$taskIdentity='human_allied_v16_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot "tmp/allied-npc-ue-v15/$taskIdentity.log"
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCUEV15/$taskIdentity"
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskEvidence)){throw 'Preserve occupied human entry'}
$env:CS549_ALLIED_HUMAN_ID=$taskIdentity
$taskScript=(Join-Path $PSScriptRoot 'ue_human_preview.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -EnablePlugins=ParisNPCGripV15 -DisablePlugins=ParisEditorBridge -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
# User explicitly requests a visible interactive UE acceptance window.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity;log=$taskLog;result=(Join-Path $taskEvidence 'result.json');view_only=$true}|ConvertTo-Json
# Once prepared this editor belongs to the user. No automatic shutdown/save.
