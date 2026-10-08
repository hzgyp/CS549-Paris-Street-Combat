param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidateSet('capability','author','test','b1_author','b1_test','b1_sight_author','b1_sight_test','b1_stop_test','b1_sight_author_v2','b1_sight_test_v2','b1_sight_author_v3','b1_sight_test_v3','b1_sight_author_v4','b1_sight_test_v4','sight_causal','sight_verified','behavior_author','behavior_config_author','behavior_test','search_author','search_test','squad_author','squad_test','friendly_fire_author','friendly_fire_exec_repair','combat_regression','selected_combat_regression','action_gate_author','action_gate_test','action_combat_test','autonomous_author','autonomous_test')][string]$Mode='capability',
    [ValidatePattern('^[A-Za-z0-9_]+$')][string]$AuthorIdentity='',
    [ValidatePattern('^V[0-9]+$')][string]$BehaviorVersion='V1'
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Another Unreal process owns the native slot'}
$taskHandoffTop=Get-Content -LiteralPath (Join-Path $taskRoot 'HANDOFF.md') -TotalCount 24
$taskUserPreviewReady=$taskHandoffTop | Where-Object {$_ -match '^\*\*User-owned .* preview READY'} | Select-Object -First 1
$taskSlotLine=$taskHandoffTop | Where-Object {$_ -match 'Lane [AB].*native slot (claimed|released)'} | Select-Object -First 1
if(-not $taskUserPreviewReady -and $taskSlotLine -match 'Lane A.*native slot claimed'){
    throw 'HANDOFF says Lane A still owns the native slot; process absence is not a release'
}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NPCInteractionV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/npc-interaction-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied NPC evidence identity'}
New-Item -ItemType Directory -Path (Split-Path $taskLog) -Force | Out-Null
$taskPython=(Get-Command python -ErrorAction Stop).Source
& $taskPython (Join-Path $PSScriptRoot 'preflight.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Offline guard/contract preflight failed'}
$taskExpectedGuards=(Get-Content -LiteralPath (Join-Path $taskOut 'result.json') -Raw | ConvertFrom-Json).protected_count
$env:CS549_NPC_IDENTITY=$Identity
$env:CS549_NPC_BEHAVIOR_VERSION=$BehaviorVersion
$env:CS549_NPC_MODE=$Mode
$taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'capability'){'ue_bt_capability_probe.py'}elseif($Mode -eq 'author'){'ue_b0_author.py'}elseif($Mode -eq 'test'){'ue_b0_test.py'}elseif($Mode -eq 'b1_author'){'ue_b1_author.py'}elseif($Mode -eq 'b1_test'){'ue_b1_test.py'}elseif($Mode -eq 'b1_stop_test'){'ue_b1_stop_test.py'}elseif($Mode -eq 'b1_sight_author'){'ue_b1_sight_author.py'}elseif($Mode -eq 'b1_sight_test'){'ue_b1_sight_test.py'}elseif($Mode -eq 'b1_sight_author_v2'){'ue_b1_sight_author_v2.py'}elseif($Mode -eq 'b1_sight_test_v2'){'ue_b1_sight_test_v2.py'}elseif($Mode -eq 'b1_sight_author_v3'){'ue_b1_sight_author_v3.py'}elseif($Mode -eq 'b1_sight_test_v3'){'ue_b1_sight_test_v3.py'}elseif($Mode -eq 'b1_sight_author_v4'){'ue_b1_sight_author_v4.py'}else{'ue_b1_sight_test_v4.py'})
if($Mode -eq 'sight_causal'){$taskScript=Join-Path $PSScriptRoot 'ue_sight_causal_probe.py'}
if($Mode -eq 'sight_verified'){$taskScript=Join-Path $PSScriptRoot 'ue_sight_verified_test.py'}
if($Mode -eq 'behavior_author'){$taskScript=Join-Path $PSScriptRoot 'ue_behavior_author.py'}
if($Mode -eq 'behavior_config_author'){$taskScript=Join-Path $PSScriptRoot 'ue_behavior_config_author.py'}
if($Mode -eq 'search_author'){$taskScript=Join-Path $PSScriptRoot 'ue_search_author.py'}
if($Mode -eq 'search_test'){$taskScript=Join-Path $PSScriptRoot 'ue_search_test.py'}
if($Mode -eq 'squad_author'){$taskScript=Join-Path $PSScriptRoot 'ue_squad_author.py'}
if($Mode -eq 'squad_test'){$taskScript=Join-Path $PSScriptRoot 'ue_squad_test.py'}
if($Mode -eq 'friendly_fire_author'){$taskScript=Join-Path $PSScriptRoot 'ue_friendly_fire_author.py'}
if($Mode -eq 'friendly_fire_exec_repair'){$taskScript=Join-Path $PSScriptRoot 'ue_ff_exec_repair.py'}
if($Mode -in @('combat_regression','selected_combat_regression')){$taskScript=Join-Path $PSScriptRoot 'ue_combat_regression.py'}
if($Mode -eq 'action_gate_author'){$taskScript=Join-Path $PSScriptRoot 'ue_action_gate_author.py'}
if($Mode -eq 'action_gate_test'){$taskScript=Join-Path $PSScriptRoot 'ue_action_gate_test.py'}
if($Mode -eq 'action_combat_test'){$taskScript=Join-Path $PSScriptRoot 'ue_action_combat_test.py'}
if($Mode -eq 'autonomous_author'){$taskScript=Join-Path $PSScriptRoot 'ue_autonomous_combat_author.py'}
if($Mode -eq 'autonomous_test'){$taskScript=Join-Path $PSScriptRoot 'ue_autonomous_combat_test.py'}
if($Mode -eq 'behavior_test'){$taskScript=Join-Path $PSScriptRoot 'ue_behavior_test.py'}
$taskMap=if($Mode -in @('test','b1_test','b1_stop_test','b1_sight_test','b1_sight_test_v2','b1_sight_test_v3','b1_sight_test_v4')){'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'}else{'/Engine/Maps/Entry'}
# Each runtime entry explicitly loads the city once; avoid duplicate startup load.
$taskMap='/Engine/Maps/Entry'
if($Mode -in @('test','b1_test','b1_stop_test','b1_sight_test','b1_sight_test_v2','b1_sight_test_v3','b1_sight_test_v4')){
    if(-not $AuthorIdentity){throw 'Test mode requires -AuthorIdentity'}
    $env:CS549_NPC_AUTHOR_IDENTITY=$AuthorIdentity
}
if($Mode -in @('sight_verified','behavior_test','search_test','squad_test','action_gate_test')){
    if(-not $AuthorIdentity){throw 'Verified sight test requires -AuthorIdentity'}
    $env:CS549_NPC_AUTHOR_IDENTITY=$AuthorIdentity
}
$taskArgs=@(
    ('"'+(Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject')+'"'),
    $taskMap,'-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',
    ('-ExecCmds="py '+($taskScript -replace '\\','/')+'"'),('-abslog="'+$taskLog+'"')
)
# Graph-only authors need no rendered material view. Runtime tests retain real RHI.
$taskGraphOnly=$Mode -in @('behavior_author','behavior_config_author','search_author','squad_author','friendly_fire_author','friendly_fire_exec_repair','action_gate_author','autonomous_author')
if($taskGraphOnly){$taskArgs+='-NullRHI'}
$taskBridgeDisabled=$Mode -in @('combat_regression','selected_combat_regression','action_gate_test','action_combat_test','autonomous_test')
if($taskBridgeDisabled){$taskArgs+='-DisablePlugins=ParisEditorBridge'}
@{mode=$Mode;graph_only_null_rhi=$taskGraphOnly;editor_authoring_bridge_disabled=$taskBridgeDisabled;runtime_visual_acceptance=$false;script=$taskScript}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'launch_scope.json')
Copy-Item -LiteralPath $taskScript -Destination (Join-Path $taskOut 'native_source.py')
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'common.py') -Destination (Join-Path $taskOut 'guard_source.py')
if(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'ue_graph.py')){Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_graph.py') -Destination (Join-Path $taskOut 'graph_source.py')}
if(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'ue_equipment_fixture.py')){Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_equipment_fixture.py') -Destination (Join-Path $taskOut 'equipment_fixture_source.py')}
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "NPCInteractionV1 $Mode PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(4)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw "Task-owned NPC $Mode job timed out; evidence retained"}
@{pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode;mode=$Mode;identity=$Identity}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
$taskResult=Join-Path $taskOut $(if($Mode -eq 'capability'){'native_capability.json'}elseif($Mode -eq 'author'){'native_author.json'}elseif($Mode -eq 'test'){'b0_runtime.json'}elseif($Mode -eq 'b1_author'){'b1_author.json'}elseif($Mode -eq 'b1_test'){'b1_runtime.json'}elseif($Mode -eq 'b1_stop_test'){'b1_stop_runtime.json'}elseif($Mode -eq 'b1_sight_author'){'b1_sight_author.json'}elseif($Mode -eq 'b1_sight_test'){'b1_sight_runtime.json'}elseif($Mode -eq 'b1_sight_author_v2'){'b1_sight_author_v2.json'}elseif($Mode -eq 'b1_sight_test_v2'){'b1_sight_runtime_v2.json'}elseif($Mode -eq 'b1_sight_author_v3'){'b1_sight_author_v3.json'}elseif($Mode -eq 'b1_sight_test_v3'){'b1_sight_runtime_v3.json'}elseif($Mode -eq 'b1_sight_author_v4'){'b1_sight_author_v4.json'}else{'b1_sight_runtime_v4.json'})
if($Mode -eq 'sight_causal'){$taskResult=Join-Path $taskOut 'sight_causal.json'}
if($Mode -eq 'sight_verified'){$taskResult=Join-Path $taskOut 'sight_verified.json'}
if($Mode -eq 'behavior_author'){$taskResult=Join-Path $taskOut 'behavior_author.json'}
if($Mode -eq 'behavior_config_author'){$taskResult=Join-Path $taskOut 'behavior_author.json'}
if($Mode -eq 'search_author'){$taskResult=Join-Path $taskOut 'search_author.json'}
if($Mode -eq 'search_test'){$taskResult=Join-Path $taskOut 'search_runtime.json'}
if($Mode -eq 'squad_author'){$taskResult=Join-Path $taskOut 'squad_author.json'}
if($Mode -eq 'squad_test'){$taskResult=Join-Path $taskOut 'squad_runtime.json'}
if($Mode -eq 'friendly_fire_author'){$taskResult=Join-Path $taskOut 'friendly_fire_author.json'}
if($Mode -eq 'friendly_fire_exec_repair'){$taskResult=Join-Path $taskOut 'friendly_fire_author.json'}
if($Mode -in @('combat_regression','selected_combat_regression')){$taskResult=Join-Path $taskOut 'combat_regression.json'}
if($Mode -eq 'action_gate_author'){$taskResult=Join-Path $taskOut 'action_gate_author.json'}
if($Mode -eq 'action_gate_test'){$taskResult=Join-Path $taskOut 'action_gate_runtime.json'}
if($Mode -eq 'action_combat_test'){$taskResult=Join-Path $taskOut 'action_combat_runtime.json'}
if($Mode -eq 'autonomous_author'){$taskResult=Join-Path $taskOut 'autonomous_combat_author.json'}
if($Mode -eq 'autonomous_test'){$taskResult=Join-Path $taskOut 'autonomous_combat_runtime.json'}
if($Mode -eq 'behavior_test'){$taskResult=Join-Path $taskOut 'behavior_runtime.json'}
if(-not (Test-Path -LiteralPath $taskResult)){throw "No native $Mode result; process exit is not acceptance"}
$result=Get-Content -LiteralPath $taskResult -Raw|ConvertFrom-Json
$result | Select-Object identity,status,protected_count,protected_guards_unchanged,errors,native_acquisition,loss | ConvertTo-Json -Depth 8
$taskGuardsPass=$result.protected_guards_unchanged
if($Mode -in @('friendly_fire_author','friendly_fire_exec_repair')){
    $taskGuardsPass=$result.protected_guards_unchanged_except_authorized_mutations -and $result.authorized_shared_mutations_verified
}
if($taskProcess.ExitCode -ne 0 -or $result.status -notlike 'pass_*' -or -not $taskGuardsPass -or $result.protected_count -ne $taskExpectedGuards){throw "$Mode gate failed; evidence retained for causal repair"}
