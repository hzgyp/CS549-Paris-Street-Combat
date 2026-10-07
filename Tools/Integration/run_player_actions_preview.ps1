param([string]$EngineEditor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe',[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
# Verify the unchanged published foundation, without launching it.
& (Join-Path $PSScriptRoot 'run_paris_native_preview.ps1') -EngineEditor $EngineEditor -CheckOnly
$taskInventoryPath=Join-Path $taskRoot 'Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json'
$taskInventory=Get-Content -LiteralPath $taskInventoryPath -Raw|ConvertFrom-Json
if(-not $taskInventory.functional_verified){throw 'Action draft functional regression is not verified; read the action result before preview'}
foreach($taskRecord in @($taskInventory.source_evidence.author,$taskInventory.source_evidence.owner)+@($taskInventory.validation)){
    $taskProofPath=Join-Path $taskRoot $taskRecord.path
    if((Get-FileHash -LiteralPath $taskProofPath -Algorithm SHA256).Hash.ToLower() -ne $taskRecord.sha256){throw 'Local action evidence changed/missing'}
}
$taskAuthor=Get-Content -LiteralPath (Join-Path $taskRoot $taskInventory.source_evidence.author.path) -Raw|ConvertFrom-Json
foreach($taskGuard in $taskAuthor.source_guards){
    if((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskGuard.path) -Algorithm SHA256).Hash.ToLower() -ne $taskGuard.sha256){throw 'Source animation differs from the action trial'}
}
foreach($taskFile in $taskInventory.files){
    $taskPath=Join-Path $taskRoot $taskFile.path
    if((Get-Item -LiteralPath $taskPath).Length -ne $taskFile.size_bytes -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLower() -ne $taskFile.sha256){throw "Changed action draft: $($taskFile.path)"}
}
if($CheckOnly){Write-Output 'Local unpublished action drafts verified; no preview launched';return}
$env:CS549_ACTION_SOURCE=$taskInventory.action_source
$env:CS549_ACTION_OWNER_SOURCE=$taskInventory.owner_source
$env:CS549_ACTION_IDENTITY='human_actions_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$taskLog=Join-Path $taskRoot ('tmp/player-actions/'+$env:CS549_ACTION_IDENTITY+'.log')
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$taskScript=Join-Path $PSScriptRoot 'ue_player_actions_preview.py'
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-DisablePlugins=ParisEditorBridge','-NoP4','-NoSplash',
 ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"'))
# Explicit user review entry point. Python only stages unsaved actors and unregisters at ready.
$taskProcess=Start-Process -FilePath $EngineEditor -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;log=$taskLog;user_owned=$true;map_saved=$false;runtime='native Blueprint'}|ConvertTo-Json
Write-Output 'Click viewport: WASD, Shift run, Alt slow, Space jump, Ctrl crouch, Z prone; mouse/left click/R standing. Esc ends PIE. Do not save the staged map.'
