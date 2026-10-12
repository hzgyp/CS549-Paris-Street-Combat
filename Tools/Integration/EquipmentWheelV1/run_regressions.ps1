param([string]$Revision='candidate_equipment_wheel_build_v1',[string]$Epoch='wheelv1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
foreach($taskMode in @('throw','smoke','p1','enemy_clear','interactions','save_equipment','restore_equipment','restore_legacy')){
 $taskIdentity=$taskMode+'_'+$Epoch
 $taskParameters=@{Revision=$Revision;Mode=$taskMode;Identity=$taskIdentity}
 if($taskMode -eq 'restore_equipment'){
  $taskParameters.SeedDirectory=Join-Path $taskBase ('checks/save_equipment_'+$Epoch+'/User/Saved/SaveGames');$taskParameters.SeedPrefix='ParisEquipment_save_equipment_'+$Epoch
 }elseif($taskMode -eq 'restore_legacy'){
  $taskParameters.SeedDirectory=Join-Path $env:LOCALAPPDATA 'ParisStreetCombat/G1EnemyClearv320261010/Saved/SaveGames';$taskParameters.SeedPrefix='ParisG1PlaytestV5'
 }
 & (Join-Path $taskRoot 'Tools/Integration/TacticalEquipmentV1/launch_check.ps1') @taskParameters
 $taskResult=Get-Content -LiteralPath (Join-Path $taskBase ('checks/'+$taskIdentity+'/RESULT.json')) -Raw | ConvertFrom-Json
 if($taskResult.status -notlike 'pass*'){throw ('Stop failed regression: '+$taskMode)}
}
foreach($taskMode in @('equipment_pause','pages','pause','confirm')){
 & (Join-Path $taskRoot 'Tools/Integration/CombatUIV1/launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity ('ui_'+$taskMode+'_'+$Epoch)
 $taskResult=Get-Content -LiteralPath (Join-Path $taskRoot ('tmp/g1-combat-ui-20261011/checks/ui_'+$taskMode+'_'+$Epoch+'/RESULT.json')) -Raw | ConvertFrom-Json
 if($taskResult.status -notlike 'pass*'){throw ('Stop failed UI regression: '+$taskMode)}
}
& (Join-Path $taskRoot 'Tools/Integration/PlayerDeathV1/launch_check.ps1') -Revision $Revision -Mode frag -Identity ('frag_'+$Epoch)
