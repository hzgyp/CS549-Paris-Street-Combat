param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_]+$')][string]$Identity,
    [ValidateSet('bootstrap_author','bootstrap_test','formal_author','formal_test','plain_game')][string]$Mode='bootstrap_author',
    [ValidatePattern('^V[0-9]+$')][string]$Version='V1',
    [ValidatePattern('^[A-Za-z0-9_]+$')][string]$EarlyIdentity=''
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor* -ErrorAction SilentlyContinue){throw 'Another UE process owns native slot'}
$taskOut=Join-Path $taskRoot "Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NPCInteractionV1/$Identity"
$taskLog=Join-Path $taskRoot "tmp/npc-interaction-v1/$Identity.log"
if((Test-Path -LiteralPath $taskOut) -or (Test-Path -LiteralPath $taskLog)){throw 'Preserve occupied evidence'}
& python (Join-Path $PSScriptRoot 'preflight.py') --identity $Identity
if($LASTEXITCODE -ne 0){throw 'Current protection preflight failed'}
$env:CS549_NPC_IDENTITY=$Identity
$env:CS549_NPC_BEHAVIOR_VERSION=$Version
$env:CS549_NPC_MODE=$Mode
if($Mode -eq 'formal_author'){
    if(-not $EarlyIdentity){throw 'Formal map save requires an explicit passed early-test identity'}
    $env:CS549_NPC_EARLY_IDENTITY=$EarlyIdentity
}
$taskProject=Join-Path $taskRoot 'Unreal/ParisStreetCombat/WW2FranceLiberation.uproject'
$taskArgs=@(('"'+$taskProject+'"'),'/Engine/Maps/Entry','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound',('-abslog="'+$taskLog+'"'))
$taskResults=@{bootstrap_author='formal_bootstrap_author.json';bootstrap_test='formal_combat_runtime.json';formal_author='formal_combat_author.json';formal_test='formal_combat_runtime.json';plain_game='plain_game.json'}
if($Mode -eq 'plain_game'){
    $taskArgs=@(('"'+$taskProject+'"'),'/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1','-game','-RenderOffscreen','-unattended','-NoP4','-NoSplash','-NoSound','-windowed','-ResX=1280','-ResY=720','-seconds=25','-DisablePlugins=ParisEditorBridge','-DisablePython',('-abslog="'+$taskLog+'"'))
}else{
    $taskScript=Join-Path $PSScriptRoot $(if($Mode -eq 'bootstrap_author'){'ue_formal_bootstrap_author.py'}elseif($Mode -eq 'formal_author'){'ue_formal_combat_author.py'}else{'ue_formal_combat_test.py'})
    $taskArgs+=('-ExecCmds="py '+($taskScript -replace '\\','/')+'"')
    if($Mode -in @('bootstrap_author','formal_author')){$taskArgs+='-NullRHI'}else{$taskArgs+='-DisablePlugins=ParisEditorBridge'}
    Copy-Item -LiteralPath $taskScript -Destination (Join-Path $taskOut 'native_source.py')
}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $taskOut 'launcher_source.ps1')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'common.py') -Destination (Join-Path $taskOut 'guard_source.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_graph.py') -Destination (Join-Path $taskOut 'graph_source.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ue_formal_roster.py') -Destination (Join-Path $taskOut 'roster_source.py')
@{identity=$Identity;mode=$Mode;version=$Version;python_behavior_driver=$false;visual_acceptance=$false;publication=$false}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'scope.json')
$taskProcess=Start-Process -FilePath 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
Write-Output "$Mode owned PID $($taskProcess.Id), log $taskLog"
$taskDeadline=(Get-Date).AddMinutes(4)
while(-not $taskProcess.HasExited -and (Get-Date) -lt $taskDeadline){$taskProcess.WaitForExit(1000)|Out-Null;$taskProcess.Refresh()}
if(-not $taskProcess.HasExited){Stop-Process -Id $taskProcess.Id;throw 'Owned job timed out; preserve evidence'}
@{identity=$Identity;mode=$Mode;pid=$taskProcess.Id;exit_code=$taskProcess.ExitCode}|ConvertTo-Json|Set-Content -LiteralPath ($taskLog+'.exit.json')
if($Mode -eq 'plain_game'){
    & python (Join-Path $PSScriptRoot 'validate_plain_game.py') --identity $Identity --log $taskLog --exit-code $taskProcess.ExitCode
    if($LASTEXITCODE -ne 0){throw 'Ordinary game validation failed'}
}
$taskResult=Get-Content -LiteralPath (Join-Path $taskOut $taskResults[$Mode]) -Raw|ConvertFrom-Json
$taskResult|Select-Object identity,status,protected_count,protected_guards_unchanged,protected_guards_unchanged_except_authorized_map,errors,checks|ConvertTo-Json -Depth 6
$taskGuardsPass=$taskResult.protected_guards_unchanged
if($Mode -eq 'formal_author'){$taskGuardsPass=$taskResult.protected_guards_unchanged_except_authorized_map -and $taskResult.authorized_map_mutation_verified}
if($taskProcess.ExitCode -ne 0 -or $taskResult.status -notlike 'pass_*' -or -not $taskGuardsPass){throw 'Native gate failed; evidence retained'}
