"""Offer a separate real tested-journal entry; ordinary new-game saves stay empty."""
from pathlib import Path
import shutil,json
from prepare import OUT,ROOT,load,sha
def main():
 r=load(OUT/'RUNTIME.json');v=load(OUT/'verification.json');assert v['status'].startswith('pass_') and r['game_sha256']==v['game_sha256']
 target=OUT/'manual-checkpoint';assert not target.exists(),'Preserve existing user review'
 user=target/'User';saved=user/'Saved/SaveGames';saved.mkdir(parents=True)
 seed=OUT/'checks/checkpoint_v2/User/Saved/SaveGames/ParisTeamP1_checkpoint_v2_A.sav'
 prefix='ParisCheckpointDialogReview';copy=saved/(prefix+'_A.sav');shutil.copyfile(seed,copy);assert sha(copy)==sha(seed)
 package=Path(r['path']);normal=(package/'PLAY_G1_REVISION.cmd').read_text(encoding='utf-8-sig')
 old='%LOCALAPPDATA%/ParisStreetCombat/'+r['user_directory'];assert normal.count(old)==1
 script=normal.replace(old,str(user).replace('\\','/')).replace('-ParisSavePrefix=ParisG1PlaytestV5','-ParisSavePrefix='+prefix)
 assert not any(k in script for k in ['ParisUXTest','ParisInteractionProbe','ParisAVAuditOut','ParisDemo'])
 entry=package/'PLAY_CHECKPOINT_REVIEW.cmd';assert not entry.exists();entry.write_text(script,encoding='utf-8')
 receipt=dict(status='isolated_manual_checkpoint_entry_prepared',entry=entry.relative_to(ROOT).as_posix(),source='Actual verified serial3 journal after old-V5 load and two explicit saves, not a fresh combat run',seed_sha256=sha(seed),user_directory=str(user),save_prefix=prefix,game_sha256=r['game_sha256'])
 (target/'review_fixture.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 (package/'README_CHECKPOINT_QUICK_REVIEW.md').write_text('PLAY_CHECKPOINT_REVIEW.cmd starts the normal menu with a separate completed-checkpoint test save.\nSelect LOAD CHECKPOINT, leave the circle and re-enter to test E, saving and the result modal.\nThis uses the real verified serial3 test journal. All guards are already dead in this fixture.\nIt does not overwrite ordinary new-game or previous user saves.\nFor actual combat and retained corner NPC layout, use PLAY_G1_REVISION.cmd.\n',encoding='utf-8')
 print(json.dumps(receipt))
if __name__=='__main__':main()
