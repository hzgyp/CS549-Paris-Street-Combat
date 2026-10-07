# Explicit human-viewing entry; never calls or unlocks the AN007 proof launcher.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor owns the serialized slot; preserve it'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'Lane A native slot claimed.*V19 human')){throw 'Human V19 slot not claimed'}
$taskIdentity='human_v19_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot "tmp/fp-upper-body-v19/$taskIdentity.log"
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FPUpperBodyV19/$taskIdentity"
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskEvidence)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_FP_V19_HUMAN_ID=$taskIdentity
$taskScript=(Join-Path $PSScriptRoot 'ue_human_preview.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -DisablePlugins=ParisEditorBridge -EnablePlugins=ParisGripBindingV18 -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
# A visible interactive window was explicitly requested by the user.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity;log=$taskLog;result=(Join-Path $taskEvidence 'result.json');view_only=$true}|ConvertTo-Json
# No automatic shutdown: once ready, this editor belongs to the user.
