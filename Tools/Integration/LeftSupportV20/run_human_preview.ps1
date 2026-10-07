# User-requested visible viewing only; never calls/unlocks AN007 full proof.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing editor owns serialized slot; preserve it'}
if(-not ((Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 5) -match 'Lane A native slot claimed.*V20 human')){throw 'V20 human slot not claimed'}
$taskIdentity='human_v20_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot "tmp/left-support-v20/$taskIdentity.log"
$taskEvidence=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/LeftSupportV20/$taskIdentity"
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskEvidence)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_LEFT_SUPPORT_V20_HUMAN_ID=$taskIdentity
$taskScript=(Join-Path $PSScriptRoot 'ue_human_preview.py').Replace('\','/')
$taskArgs='"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'" /Game/ParisCombat/Maps/LV_ParisStreetCombat_V1 -DisablePlugins=ParisEditorBridge -EnablePlugins=ParisGripBindingV18 -NoP4 -NoSplash -ExecCmds="py '+$taskScript+'" -abslog="'+$taskLog+'"'
# Visible interactive window explicitly requested by the user.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$taskIdentity;log=$taskLog;result=(Join-Path $taskEvidence 'result.json');view_only=$true}|ConvertTo-Json
# User-owned preview: no automated shutdown or save.
