param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Another engine owns native slot; no concurrent writer'}
$taskGuards=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadRepairV5/checkpoint_v1/guards.json') -Raw | ConvertFrom-Json
$taskB=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/Development/NPCInteractionV1/NPC_INTERACTION_V1_DRAFT_INVENTORY_20261004.json') -Raw | ConvertFrom-Json
$taskRows=@($taskGuards.files)+@($taskB.files)
if($taskRows.Count -ne 528){throw 'Expected all528 guards'}
foreach($taskRow in $taskRows){
    $taskPath=Join-Path $taskRoot $taskRow.path
    if((Get-Item -LiteralPath $taskPath).Length -ne $taskRow.size_bytes -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLower() -ne $taskRow.sha256){throw "Changed guarded file: $($taskRow.path)"}
}
if($CheckOnly){Write-Output '528 exact native guards; viewing only';return}
$env:CS549_RELOAD_HUMAN_ID='human_v5_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot ('tmp/reload-repair-v5/'+$env:CS549_RELOAD_HUMAN_ID+'.log')
$taskOut=Join-Path $taskRoot ('Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadRepairV5/'+$env:CS549_RELOAD_HUMAN_ID)
if((Test-Path -LiteralPath $taskLog)-or(Test-Path -LiteralPath $taskOut)){throw 'Preserve occupied identity'}
$taskScript=Join-Path $PSScriptRoot 'ue_human_preview.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
    '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',
    ('-ExecCmds="py '+$taskScript.Replace('\','/')+'"'),('-abslog="'+$taskLog+'"'))
# Explicitly requested visible interactive review; do not add RenderOffscreen/unattended.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$env:CS549_RELOAD_HUMAN_ID;log=$taskLog;result=(Join-Path $taskOut 'result.json');user_owned=$true;map_saved=$false;scope='explicit_human_view_only'} | ConvertTo-Json
