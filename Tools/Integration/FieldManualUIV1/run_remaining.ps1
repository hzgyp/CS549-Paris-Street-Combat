param([string]$Revision='candidate_field_manual_v1',[string]$Epoch='field_v1')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskBase=Join-Path $taskRoot 'tmp/g1-tactical-equipment-20261010'
foreach($taskMode in @('pause','equipment_pause','confirm')){
 & (Join-Path $taskRoot 'Tools/Integration/CombatUIV1/launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity ('ui_'+$taskMode+'_'+$Epoch)
}
foreach($taskMode in @('menu','enemy_clear','p1','throw','smoke','interactions','mine_range','mine_post_clear','mine_post_clear_frag','save_equipment','restore_equipment','restore_legacy','restore_v16_equipment','performance')){
 $taskIdentity=$taskMode+'_ui_'+$Epoch
 $taskParameters=@{Revision=$Revision;Mode=$taskMode;Identity=$taskIdentity}
 if($taskMode -eq 'restore_equipment'){
  $taskParameters.SeedDirectory=Join-Path $taskBase ('checks/save_equipment_ui_'+$Epoch+'/User/Saved/SaveGames')
  $taskParameters.SeedPrefix='ParisEquipment_save_equipment_ui_'+$Epoch
 }elseif($taskMode -eq 'restore_legacy'){
  $taskParameters.SeedDirectory=Join-Path $env:LOCALAPPDATA 'ParisStreetCombat/G1EnemyClearv320261010/Saved/SaveGames'
  $taskParameters.SeedPrefix='ParisG1PlaytestV5'
 }elseif($taskMode -eq 'restore_v16_equipment'){
  $taskParameters.Mode='restore_equipment'
  $taskParameters.SeedDirectory=Join-Path $taskBase 'checks/save_equipment_v16_early/User/Saved/SaveGames'
  $taskParameters.SeedPrefix='ParisEquipment_save_equipment_v16_early'
 }
 & (Join-Path $taskRoot 'Tools/Integration/TacticalEquipmentV1/launch_check.ps1') @taskParameters
 $taskResult=Get-Content -LiteralPath (Join-Path $taskBase ('checks/'+$taskIdentity+'/RESULT.json')) -Raw | ConvertFrom-Json
 if($taskResult.status -notlike 'pass*'){throw ('Stopped failed regression: '+$taskMode)}
}
