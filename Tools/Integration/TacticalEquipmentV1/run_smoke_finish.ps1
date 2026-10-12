param([string]$Revision='candidate_full_v16',[string]$Suffix='v16_early')
$ErrorActionPreference='Stop'
foreach($taskMode in @('smoke','save_equipment','restore_equipment','restore_legacy','performance')){
 $taskIdentity=$taskMode+'_'+$Suffix
 if($taskMode -eq 'restore_equipment'){
  & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity -SeedDirectory (Join-Path $PSScriptRoot ('../../../tmp/g1-tactical-equipment-20261010/checks/save_equipment_'+$Suffix+'/User/Saved/SaveGames')) -SeedPrefix ('ParisEquipment_save_equipment_'+$Suffix)
 }elseif($taskMode -eq 'restore_legacy'){
  & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity -SeedDirectory 'C:/Users/hzgyp/AppData/Local/ParisStreetCombat/G1EnemyClearv320261010/Saved/SaveGames' -SeedPrefix ParisG1PlaytestV5
 }else{& (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity}
 $taskResult=Get-Content -LiteralPath (Join-Path $PSScriptRoot ('../../../tmp/g1-tactical-equipment-20261010/checks/'+$taskIdentity+'/RESULT.json')) -Raw | ConvertFrom-Json
 if($taskResult.status -notlike 'pass*'){throw ('Stop failed check: '+$taskIdentity)}
}
