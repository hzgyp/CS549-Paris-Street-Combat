param([string]$Revision='candidate_full_v13',[string]$Suffix='v13')
$ErrorActionPreference='Stop'
foreach($taskMode in @('smoke','hazard','throw','frag_blast','interactions','sites','ally_trap','blast_occlusion','save_equipment','restore_equipment','restore_legacy','menu','enemy_clear','p1','performance')){
 $taskIdentity=$taskMode+'_'+$Suffix
 $taskResultPath=Join-Path $PSScriptRoot ('../../../tmp/g1-tactical-equipment-20261010/checks/'+$taskIdentity+'/RESULT.json')
 if(Test-Path -LiteralPath $taskResultPath){
  $taskLaunch=Get-Content -LiteralPath (Join-Path (Split-Path $taskResultPath) 'launch.json') -Raw | ConvertFrom-Json
  $taskRuntime=Get-Content -LiteralPath (Join-Path $PSScriptRoot ('../../../tmp/g1-tactical-equipment-20261010/'+$Revision+'/runtime.json')) -Raw | ConvertFrom-Json
  if($taskLaunch.exit_code -ne 0 -or $taskLaunch.game_sha256 -ne $taskRuntime.game_sha256){throw 'Existing identity mismatches completed current Game'}
 }elseif($taskMode -eq 'restore_equipment'){
  & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity -SeedDirectory (Join-Path $PSScriptRoot ('../../../tmp/g1-tactical-equipment-20261010/checks/save_equipment_'+$Suffix+'/User/Saved/SaveGames')) -SeedPrefix ('ParisEquipment_save_equipment_'+$Suffix)
 }elseif($taskMode -eq 'restore_legacy'){
  & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity -SeedDirectory 'C:/Users/hzgyp/AppData/Local/ParisStreetCombat/G1EnemyClearv320261010/Saved/SaveGames' -SeedPrefix ParisG1PlaytestV5
 }else{
  & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity $taskIdentity
 }
 $taskResult=Get-Content -LiteralPath $taskResultPath -Raw | ConvertFrom-Json
 if($taskResult.status -notlike 'pass*'){throw ('Stop failed check: '+$taskIdentity)}
}
