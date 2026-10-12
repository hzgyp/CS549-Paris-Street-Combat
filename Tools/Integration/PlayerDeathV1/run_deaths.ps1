param([string]$Revision='candidate_death_v3',[string]$Suffix='v3',[switch]$IncludeMine)
$ErrorActionPreference='Stop'
$taskDeathModes=if($IncludeMine){@('mine','frag','damage','crouch','prone')}else{@('frag','damage','crouch','prone')}
foreach($taskDeathMode in $taskDeathModes){
 & (Join-Path $PSScriptRoot 'launch_check.ps1') -Revision $Revision -Mode $taskDeathMode -Identity ($taskDeathMode+'_'+$Suffix)
}
