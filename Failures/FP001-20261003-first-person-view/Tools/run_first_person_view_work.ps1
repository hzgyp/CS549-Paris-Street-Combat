param([Parameter(Mandatory=$true)][ValidateSet('Author','Refine','Cloth','Near','MaterialAudit','Mask','WorldMask','MaskFlags','Combat')][string]$Mode,
 [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_]+$')][string]$Identity)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Close competing Unreal sessions first'}
$taskLog=Join-Path $taskRoot "tmp/paris-first-person-view-20261002/$Identity.log"
if(Test-Path -LiteralPath $taskLog){throw 'Preserve occupied identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force|Out-Null
$env:CS549_FP_IDENTITY=$Identity
$env:CS549_COMBAT_PIE_IDENTITY=$Identity
$env:CS549_CITY_NATIVE_CHECKPOINT='CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'
$env:CS549_FIRST_PERSON_VIEW_PREVIEW='1'
$env:CS549_PLAYER_AIM_PREVIEW='0'
$taskMap=if($Mode -ne 'Combat'){'/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001'}else{'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}
$taskPlugin=if($Mode -ne 'Combat'){'-EnablePlugins=ParisEditorBridge'}else{'-DisablePlugins=ParisEditorBridge'}
$taskScript=if($Mode -eq 'Author'){'ue_first_person_view_author.py'}elseif($Mode -eq 'Refine'){'ue_first_person_view_refine.py'}elseif($Mode -eq 'Cloth'){'ue_first_person_view_cloth.py'}elseif($Mode -eq 'Near'){'ue_first_person_view_near.py'}elseif($Mode -eq 'MaterialAudit'){'ue_first_person_view_material_audit.py'}elseif($Mode -eq 'Mask'){'ue_first_person_view_mask.py'}elseif($Mode -eq 'WorldMask'){'ue_first_person_view_world_mask.py'}elseif($Mode -eq 'MaskFlags'){'ue_first_person_view_mask_flags.py'}else{'ue_paris_combat_pie.py'}
$taskRendering=if($Mode -notin @('Combat','MaskFlags')){'-NullRHI'}else{'-RenderOffscreen'}
$taskArgs=@(('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
 $taskMap,$taskPlugin,$taskRendering,'-unattended','-NoP4','-NoSplash','-NoSound',
 ('-ExecutePythonScript="'+(Join-Path $PSScriptRoot $taskScript)+'"'),('-abslog="'+$taskLog+'"'))
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "$Mode PID $($taskProcess.Id); log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(7)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Task-owned engine timeout'}
[pscustomobject]@{exit_code=$taskProcess.ExitCode;log=$taskLog;mode=$Mode}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
Get-Content -LiteralPath ($taskLog+'.exit.json')
