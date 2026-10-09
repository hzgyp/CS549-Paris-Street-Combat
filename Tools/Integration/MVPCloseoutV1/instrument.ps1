param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Identity,
 [string]$CookIdentity='package_v2',[switch]$NativeRouteCandidate,[switch]$AgentFeetCandidate)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if(Get-Process UnrealEditor*,WW2FranceLiberation*,UnrealBuildTool,AutomationTool -ErrorAction SilentlyContinue){throw 'Preserve active processes'}
$taskCook=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$CookIdentity)
if((Get-Content (Join-Path $taskCook 'build.json') -Raw|ConvertFrom-Json).status -ne 'built_runtime_unverified'){throw 'Complete successful cook first'}
$taskPython='C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython (Join-Path $PSScriptRoot 'prepare_build.py') $Identity
if($LASTEXITCODE -ne 0){throw 'Prepare failed'}
$taskOut=Join-Path $taskRoot ('tmp/mvp-closeout-20261008/'+$Identity)
$taskProject=Join-Path $taskOut 'Project'
if($NativeRouteCandidate){
 & $taskPython (Join-Path $PSScriptRoot 'apply_runtime_candidate.py') $Identity
 if($LASTEXITCODE -ne 0){throw 'Candidate prerequisite or exact source transform failed'}
}
if($AgentFeetCandidate){
 if(-not $NativeRouteCandidate){throw 'Agent candidate requires native route wrapper'}
 & $taskPython (Join-Path $PSScriptRoot 'apply_agent_candidate.py') $Identity
 if($LASTEXITCODE -ne 0){throw 'Agent candidate proof or exact transform failed'}
}
New-Item -ItemType Directory -Path (Join-Path $taskProject 'Source/WW2FranceLiberation')|Out-Null
Copy-Item (Join-Path $taskCook 'Project/Intermediate/Source/WW2FranceLiberation.cpp') (Join-Path $taskProject 'Source/WW2FranceLiberation/WW2FranceLiberation.cpp')
Copy-Item (Join-Path $PSScriptRoot 'CloseoutGame.cpp') (Join-Path $taskProject 'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp') -Force
$taskMissionBuild=Join-Path $taskProject 'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/ParisBridgeMissionV1.Build.cs'
$taskMissionText=Get-Content $taskMissionBuild -Raw
$taskMissionText=$taskMissionText.Replace('"AIModule",', '"MovieSceneCapture", "Slate", "SlateCore", "RenderCore", "AIModule",')
if($taskMissionText -notmatch 'MovieSceneCapture'){throw 'Explicit diagnostic build dependency insertion failed'}
$taskMissionText|Set-Content $taskMissionBuild -Encoding utf8
Copy-Item (Join-Path $taskCook 'Project/Intermediate/Source/WW2FranceLiberation.Target.cs') (Join-Path $taskProject 'Source/WW2FranceLiberation.Target.cs')
$taskModule=@'
using UnrealBuildTool;
public class WW2FranceLiberation : ModuleRules {
 public WW2FranceLiberation(ReadOnlyTargetRules Target):base(Target) {
  PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;
  PrivateDependencyModuleNames.AddRange(new string[]{"Core"});
 }
}
'@
$taskModule|Set-Content (Join-Path $taskProject 'Source/WW2FranceLiberation/WW2FranceLiberation.Build.cs') -Encoding utf8
$taskDescriptor=Get-Content (Join-Path $taskProject 'WW2FranceLiberation.uproject') -Raw|ConvertFrom-Json
$taskDescriptor|Add-Member -NotePropertyName Modules -NotePropertyValue @(@{Name='WW2FranceLiberation';Type='Runtime';LoadingPhase='Default'})
$taskDescriptor|ConvertTo-Json -Depth 8|Set-Content (Join-Path $taskProject 'WW2FranceLiberation.uproject') -Encoding utf8
$taskArgs=@('WW2FranceLiberation','Win64','Development',('-Project='+$taskProject+'/WW2FranceLiberation.uproject'),'-WaitMutex','-NoHotReload')
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' @taskArgs 2>&1|Tee-Object (Join-Path $taskOut 'instrument_build.log')
$taskExit=$LASTEXITCODE
@{exit_code=$taskExit;arguments=$taskArgs;diagnostic_source_sha256=(Get-FileHash (Join-Path $PSScriptRoot 'CloseoutGame.cpp')).Hash.ToLower();cook_identity=$CookIdentity;native_route_candidate=[bool]$NativeRouteCandidate;agent_feet_candidate=[bool]$AgentFeetCandidate;scope=if($AgentFeetCandidate){'Private G1 two-file native route/agent-start/far-bank settling candidate plus opt-in observer/build wiring; original other BT topology, models, weapon logic and cooked bytes exact'}elseif($NativeRouteCandidate){'Private native G1 two-file candidate plus opt-in observer/build wiring; all other runtime/model/weapon/AI and cooked bytes exact'}else{'Opt-in observer in isolated mission module startup; original mission/weapon/AI/pose implementation and cooked bytes exact; two wrapper-only diagnostic wiring files differ'}}|ConvertTo-Json -Depth 5|Set-Content (Join-Path $taskOut 'instrument.json')
if($taskExit -ne 0){throw 'Preserve failed instrumented build identity'}
Copy-Item (Join-Path $taskCook 'Archive') (Join-Path $taskOut 'Archive') -Recurse
$taskBinary=Get-ChildItem (Join-Path $taskOut 'Archive') -Recurse -Filter WW2FranceLiberation.exe|Where-Object {$_.DirectoryName -match 'Binaries\\Win64$'}
if(@($taskBinary).Count -ne 1){throw 'Ambiguous archive binary'}
Copy-Item (Join-Path $taskProject 'Binaries/Win64/WW2FranceLiberation.exe') $taskBinary.FullName -Force
Write-Output ('Instrumented private archive prepared: '+$taskOut)
