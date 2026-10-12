param([string]$Revision='candidate_death_v6',[string]$Epoch='death_v6')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
foreach($taskMode in @('pages','pages_small')){
 & (Join-Path $taskRoot 'Tools/Integration/CombatUIV1/launch_check.ps1') -Revision $Revision -Mode $taskMode -Identity ('ui_'+$taskMode+'_'+$Epoch)
}
& (Join-Path $taskRoot 'Tools/Integration/FieldManualUIV1/run_remaining.ps1') -Revision $Revision -Epoch $Epoch
