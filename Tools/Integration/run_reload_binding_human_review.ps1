param([switch]$CheckOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Existing Unreal process: no concurrent staging writer'}
$taskPreflight=Get-Content -LiteralPath (Join-Path $taskRoot 'tmp/weapon-animation-reuse/preflight_v1.json') -Raw | ConvertFrom-Json
$taskOldDrafts=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json') -Raw | ConvertFrom-Json
$taskProof=Get-Content -LiteralPath (Join-Path $taskRoot 'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json') -Raw | ConvertFrom-Json
$taskRecords=@($taskPreflight.files)+@($taskOldDrafts.files)+@($taskProof.files)
if($taskRecords.Count -ne 514){throw 'Expected 514 recorded native guards'}
foreach($taskRecord in $taskRecords){
    $taskPath=Join-Path $taskRoot $taskRecord.path
    if((Get-Item -LiteralPath $taskPath).Length -ne $taskRecord.size_bytes -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLower() -ne $taskRecord.sha256){throw "Changed native guard: $($taskRecord.path)"}
}
if($CheckOnly){Write-Output '514 native bytes verified; human view only, no launch/save/repair';return}
$env:CS549_RELOAD_REVIEW_IDENTITY='human_reload_binding_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot ('tmp/reload-contact-binding-v3/'+$env:CS549_RELOAD_REVIEW_IDENTITY+'.log')
$taskOutput=Join-Path $taskRoot ('Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadContactBindingV3/'+$env:CS549_RELOAD_REVIEW_IDENTITY)
if((Test-Path -LiteralPath $taskLog) -or (Test-Path -LiteralPath $taskOutput)){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskScript=Join-Path $PSScriptRoot 'ue_reload_binding_human_review.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
    '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',
    ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
# Visible interactive window explicitly requested by the user; old proof launcher stays locked.
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Normal -PassThru
@{pid=$taskProcess.Id;identity=$env:CS549_RELOAD_REVIEW_IDENTITY;log=$taskLog;result=(Join-Path $taskOutput 'result.json');user_owned=$true;map_saved=$false;scope='human_view_only'} | ConvertTo-Json
