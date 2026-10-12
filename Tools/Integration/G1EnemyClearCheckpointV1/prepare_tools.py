"""Derive bounded build/entry wrappers without changing prior tooling or receipts."""
from prepare import ROOT
def main():
 here=ROOT/'Tools/Integration/G1EnemyClearCheckpointV1';old=ROOT/'Tools/Integration/G1CheckpointDialogV1'
 build=(old/'build.ps1').read_text(encoding='utf-8-sig').replace('tmp/g1-checkpoint-dialog-20261010','tmp/g1-enemy-clear-checkpoint-20261010').replace('Game-only bounded interaction','Game-only enemy-clear checkpoint admission')
 assert not (here/'build.ps1').exists();(here/'build.ps1').write_text(build,encoding='utf-8-sig')
 launch=(old/'launch_check.ps1').read_text(encoding='utf-8-sig').replace("[ValidateSet('menu','checkpoint','restore')]","[ValidateSet('menu','enemy_clear','restore','legacy_restore')]")
 launch=launch.replace('tmp/g1-checkpoint-dialog-20261010','tmp/g1-enemy-clear-checkpoint-20261010').replace("$SeedIdentity='checkpoint_v1'","$SeedIdentity='clearance_v2'").replace('ParisTeamP1_','ParisEnemyClear_')
 launch=launch.replace("if($Mode -eq 'checkpoint'){","if($Mode -eq 'legacy_restore'){").replace("('-ParisInteractionProbe='+$Mode)","('-ParisInteractionProbe='+$(if($Mode -eq 'legacy_restore'){'restore'}else{$Mode}))")
 launch=launch.replace("$taskReceipt=[ordered]@{status='running'","$taskReceipt=[ordered]@{status='running'")
 assert not (here/'launch_check.ps1').exists();(here/'launch_check.ps1').write_text(launch,encoding='utf-8-sig')
 print('Independent build/finite test wrappers prepared')
if __name__=='__main__':main()
